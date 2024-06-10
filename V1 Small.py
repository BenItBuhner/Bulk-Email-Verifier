import csv
import requests
import smtplib
import threading
import re
import logging
from tqdm import tqdm
from collections import defaultdict

# Configuration
EMAIL = "your-email@example.com"
PASSWORD = "your-password"
PORT = 25
THREAD_COUNT = 10
SERVER_TIMEOUT = 10

# Logging setup
logging.basicConfig(filename='email_verification.log', level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s:%(message)s')

# Predefined lists for spam traps and business emails
SPAM_TRAP_DOMAINS = {"spamtrap.com", "temp-mail.org", "10minutemail.com", "guerrillamail.com", "mailinator.com", "yopmail.com", "trashmail.com", "getnada.com", "maildrop.cc", "fakemail.net", "emailondeck.com", "dispostable.com", "mailcatch.com", "moakt.com", "burnermail.io", "tempmailaddress.com", "fakeinbox.com", "mytemp.emai", "safetymail.info", "tempmailo.com"}
BUSINESS_KEYWORDS = ["info", "help", "support", "contact", "forgotpassword", "passwordhelp", "sales", "team", "legal", "press", "privacy", "feedback", "noreply", "marketing", "service", "compliance", "orders", "techsupport", "projects", "development", "partnerships", "newsletter", "returns", "security", "shipping", "management", "complaints", "fincance", "orders"]

# SMTP Response Codes
VALID_CODES = [250]
INVALID_CODES = [550, 551, 552, 553, 554]

# Regex for basic email validation
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

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
    return domain in SPAM_TRAP_DOMAINS

# Function to get MX record for a domain using Google DoH API
def get_mx_record(domain):
    url = f"https://dns.google/resolve?name={domain}&type=MX"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if 'Answer' in data:
            mx_record = data['Answer'][0]['data'].split()[-1].rstrip('.')
            return mx_record
        else:
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
        server = smtplib.SMTP(mx_record, PORT, timeout=SERVER_TIMEOUT)
        server.set_debuglevel(0)
        server.ehlo()
        
        from_response = server.mail(EMAIL)
        to_response = server.rcpt(email)
        
        server.quit()
        
        return (to_response[0], mx_record, from_response, to_response)
    except smtplib.SMTPServerDisconnected:
        return "server_block", None, None, None
    except Exception as e:
        logging.error(f"Error verifying email {email}: {e}")
        return "no_server_response", None, None, None

# Multithreading worker function
def worker(emails, results, pbar):
    for email in emails:
        if not is_valid_email_syntax(email):
            results["invalid"].append(email)
        elif is_spam_trap(email):
            results["spam_trap"].append(email)
        elif is_business_email(email):
            results["business"].append(email)
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
        pbar.update(1)

# Main function to handle CSV import/export and threading
def main():
    emails = []
    with open("emails.csv", newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            emails.append(row["Email"])

    results = defaultdict(list)
    email_batches = [emails[i::THREAD_COUNT] for i in range(THREAD_COUNT)]
    threads = []
    pbar = tqdm(total=len(emails), desc="Verifying emails", ncols=100)

    for batch in email_batches:
        thread = threading.Thread(target=worker, args=(batch, results, pbar))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    pbar.close()

    with open("valid_emails.csv", "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Email"])
        writer.writerows([[email] for email in results["valid"]])

    with open("invalid_emails.csv", "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Email"])
        writer.writerows([[email] for email in results["invalid"]])

    with open("spam_trap_emails.csv", "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Email"])
        writer.writerows([[email] for email in results["spam_trap"]])

    with open("business_emails.csv", "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Email"])
        writer.writerows([[email] for email in results["business"]])

    with open("all_emails.csv", "w", newline='') as csvfile:
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

if __name__ == "__main__":
    main()
