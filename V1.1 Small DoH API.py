import csv
import requests
import smtplib
import re
import logging
import os
from tqdm import tqdm
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

# Configuration
EMAIL = "placeholder@example.com"
PASSWORD = "ExamplePass"
PORT = 25
THREAD_COUNT = 50
SERVER_TIMEOUT = 25

# Logging setup
logging.basicConfig(filename='email_verification.log', level=logging.INFO, 
                    format='%(asctime)s %(levelname)s:%(message)s')

# Predefined lists for spam traps and business emails
SPAM_TRAP_DOMAINS = {"spamtrap.com", "temp-mail.org", "10minutemail.com", "guerrillamail.com", "mailinator.com", "yopmail.com", "trashmail.com", "getnada.com", "maildrop.cc", "fakemail.net", "emailondeck.com", "dispostable.com", "mailcatch.com", "moakt.com", "burnermail.io", "tempmailaddress.com", "fakeinbox.com", "mytemp.emai", "safetymail.info", "tempmailo.com"}
BUSINESS_KEYWORDS = ["info", "help", "support", "contact", "forgotpassword", "passwordhelp", "sales", "team", "legal", "press", "privacy", "feedback", "noreply", "marketing", "service", "compliance", "orders", "techsupport", "projects", "development", "partnerships", "newsletter", "returns", "security", "shipping", "management", "complaints", "finance", "orders", "questions"]

# Read spam domains from file
def load_spam_domains():
    spam_domains = set()
    with open("spam-domains.txt", "r") as file:
        for line in file:
            spam_domains.add(line.strip())
    return spam_domains

SPAM_DOMAINS = load_spam_domains()

# SMTP Response Codes
VALID_CODES = [250]
INVALID_CODES = [550, 551, 552, 553, 554]

# Regex for basic email validation
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

# Cache for MX records
mx_record_cache = {}

# Function to check email syntax
def is_valid_email_syntax(email):
    return re.match(EMAIL_REGEX, email) is not None

# Function to filter business emails
def is_business_email(email):
    local_part = email.split('@')[0]
    return any(keyword in local_part for keyword in BUSINESS_KEYWORDS)

# Function to filter spam traps and temp emails
def is_spam_trap(email):
    domain = email.split('@')[1]
    return domain in SPAM_TRAP_DOMAINS or domain in SPAM_DOMAINS

# Function to get MX record for a domain using Google DoH API
def get_mx_record(domain):
    if domain in mx_record_cache:
        return mx_record_cache[domain]

    url = f"https://dns.google/resolve?name={domain}&type=MX"
    try:
        response = requests.get(url, timeout=SERVER_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        if 'Answer' in data:
            mx_record = data['Answer'][0]['data'].split()[-1].rstrip('.')
            mx_record_cache[domain] = mx_record
            return mx_record
        return None
    except Exception as e:
        logging.error(f"Error fetching MX record for {domain}: {e}")
        return None

# SMTP verification function
def verify_email(email):
    domain = email.split('@')[1]
    mx_record = get_mx_record(domain)
    if not mx_record:
        return "no_server_response", None, None, None

    try:
        with smtplib.SMTP(mx_record, PORT, timeout=SERVER_TIMEOUT) as server:
            server.set_debuglevel(0)
            server.ehlo()
            from_response = server.mail(EMAIL)
            to_response = server.rcpt(email)
            return (to_response[0], mx_record, from_response, to_response)
    except smtplib.SMTPServerDisconnected:
        return "server_block", None, None, None
    except Exception as e:
        logging.error(f"Error verifying email {email}: {e}")
        return "no_server_response", None, None, None

# Multithreading worker function
def worker(email, results, lock):
    if not is_valid_email_syntax(email):
        results["invalid"].append(email)
    elif is_spam_trap(email):
        results["spam_trap"].append(email)
    elif is_business_email(email):
        results["business"].append(email)
    else:
        domain = email.split('@')[1]
        with lock:
            mx_record = get_mx_record(domain)
        if not mx_record:
            results["no_server_response"].append(email)
        else:
            result, mx_record, from_response, to_response = verify_email(email)
            if result == "no_server_response":
                results["no_server_response"].append(email)
            elif result == "server_block":
                results["server_block"].append(email)
            elif result in VALID_CODES:
                results["valid"].append(email)
            else:
                results["invalid"].append(email)
            results["all"].append({
                "Email": email,
                "MX Record": mx_record,
                "SMTP Handshake": from_response,
                "SMTP FROM": from_response,
                "SMTP RCPT": to_response,
                "Interpretation": result
            })

# Main function to handle CSV import/export and threading
def main():
    emails = []
    with open("emails.csv", newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        emails = [row["Email"] for row in reader]

    results = defaultdict(list)
    pbar = tqdm(total=len(emails), desc="Verifying emails", ncols=100)
    
    from threading import Lock
    lock = Lock()

    with ThreadPoolExecutor(max_workers=THREAD_COUNT) as executor:
        futures = {executor.submit(worker, email, results, lock): email for email in emails}
        for future in tqdm(futures, total=len(futures), desc="Processing", ncols=100):
            future.result()
            pbar.update(1)

    pbar.close()

    if not os.path.exists("Exports"):
        os.makedirs("Exports")

    def save_results(filename, data):
        with open(f"Exports/{filename}", "w", newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Email"])
            writer.writerows([[email] for email in data])

    save_results("valid_emails.csv", results["valid"])
    save_results("invalid_emails.csv", results["invalid"])
    save_results("spam_trap_emails.csv", results["spam_trap"])
    save_results("business_emails.csv", results["business"])

    with open("Exports/all_emails.csv", "w", newline='') as csvfile:
        fieldnames = ["Email", "MX Record", "SMTP Handshake", "SMTP FROM", "SMTP RCPT", "Interpretation"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for entry in results["all"]:
            writer.writerow({
                "Email": entry["Email"],
                "MX Record": entry["MX Record"],
                "SMTP Handshake": entry["SMTP Handshake"],
                "SMTP FROM": entry["SMTP FROM"],
                "SMTP RCPT": entry["SMTP RCPT"],
                "Interpretation": entry["Interpretation"]
            })

    total_emails = len(emails)
    for category, emails in results.items():
        if category != "all":
            count = len(emails)
            percentage = (count / total_emails) * 100
            print(f"{category.capitalize()} emails: {count} ({percentage:.2f}%)")

if __name__ == "__main__":
    main()
