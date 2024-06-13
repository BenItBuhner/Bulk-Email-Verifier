import csv
import smtplib
import re
import logging
import os
from tqdm import tqdm
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import dns.resolver

# Configuration
EMAIL = "placeholder@example.com"
PASSWORD = "examplepass"
PORT = 25
THREAD_COUNT = 50
SERVER_TIMEOUT = 25

# Logging setup
logging.basicConfig(filename='email_verification.log', level=logging.INFO, 
                    format='%(asctime)s %(levelname)s:%(message)s')

# Predefined lists for spam traps and business emails
SPAM_TRAP_DOMAINS = {"spamtrap.com", "temp-mail.org", "10minutemail.com", "guerrillamail.com", "mailinator.com", "yopmail.com", "trashmail.com", "getnada.com", "maildrop.cc", "fakemail.net", "emailondeck.com", "dispostable.com", "mailcatch.com", "moakt.com", "burnermail.io", "tempmailaddress.com", "fakeinbox.com", "mytemp.emai", "safetymail.info", "tempmailo.com"}
BUSINESS_KEYWORDS = ["info", "help", "support", "contact", "forgotpassword", "passwordhelp", "sales", "team", "legal", "press", "privacy", "feedback", "noreply", "marketing", "service", "compliance", "orders", "techsupport", "projects", "development", "partnerships", "newsletter", "returns", "security", "shipping", "management", "complaints", "finance", "orders"]

# SMTP Response Codes
VALID_CODES = [250]
INVALID_CODES = [550, 551, 552, 553, 554]

# Regex for basic email validation
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

# Cache for MX records
mx_record_cache = {
    "outlook.com": "outlook-com.olc.protection.outlook.com",
    "hotmail.com": "hotmail-com.olc.protection.outlook.com"
}

# Domain corrections
DOMAIN_CORRECTIONS = {
    "hotmail.com": [
        "hotmnail.com", "hotmail.net", "hotmaill.com", "hotmial.com", "hotmil.com", "hotmai.com", "hotmaul.com", "hotmal.com"
    ],
    "gmail.com": [
        "gmail.net", "gmnail.com", "gmail.co", "gmial.com", "gamil.com", "gmaill.com", "gmial.com", "gmaol.com", "gmaik.com", "gmaio.com"
    ],
    "outlook.com": [
        "uotlook.com", "outlook.net", "outllook.com", "otulook.com", "outllok.com", "otlook.com", "outlok.com", "oulook.com"
    ]
}

# Function to check email syntax
def is_valid_email_syntax(email):
    return re.match(EMAIL_REGEX, email) is not None

# Function to correct common domain typos
def correct_domain(email):
    local_part, domain = email.split('@')
    for correct_domain, typos in DOMAIN_CORRECTIONS.items():
        if domain == correct_domain:
            return email
        if domain in typos:
            corrected_email = f"{local_part}@{correct_domain}"
            logging.info(f"Corrected domain for {email} to {corrected_email}")
            return corrected_email
    return email

# Function to filter business emails
def is_business_email(email):
    local_part = email.split('@')[0]
    return any(keyword in local_part for keyword in BUSINESS_KEYWORDS)

# Function to filter spam traps and temp emails
def is_spam_trap(email):
    domain = email.split('@')[1]
    return domain in SPAM_TRAP_DOMAINS

# Function to get MX record for a domain using dnspython
def get_mx_record(domain):
    if domain in mx_record_cache:
        return mx_record_cache[domain]

    resolver = dns.resolver.Resolver(configure=False)
    resolver.nameservers = ['8.8.8.8', '8.8.4.4']  # Google's DNS servers

    logging.debug(f"Attempting to resolve MX record for domain: {domain}")

    try:
        answers = resolver.resolve(domain, 'MX')
        mx_record = str(answers[0].exchange).rstrip('.')
        mx_record_cache[domain] = mx_record
        logging.debug(f"Resolved MX record for {domain}: {mx_record}")
        return mx_record
    except dns.resolver.NXDOMAIN:
        logging.error(f"MX record for domain {domain} does not exist.")
        return None
    except dns.resolver.Timeout:
        logging.error(f"Timed out while fetching MX record for domain {domain}.")
        return None
    except dns.resolver.NoAnswer:
        logging.error(f"No answer for MX query for domain {domain}.")
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
def worker(email, results):
    corrected_email = correct_domain(email)
    if not is_valid_email_syntax(corrected_email):
        results["invalid"].append(email)
    elif is_spam_trap(corrected_email):
        results["spam_trap"].append(email)
    elif is_business_email(corrected_email):
        results["business"].append(email)
    else:
        result, mx_record, from_response, to_response = verify_email(corrected_email)
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
            "Corrected Email": corrected_email,
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

    # Ensure all emails contain the '@' character
    emails = [email for email in emails if '@' in email]

    # Lookup and cache MX records before verification
    domains = {email.split('@')[1] for email in emails}
    for domain in tqdm(domains, desc="Looking up MX records", ncols=100):
        get_mx_record(domain)

    results = defaultdict(list)
    pbar = tqdm(total=len(emails), desc="Verifying emails", ncols=100)

    with ThreadPoolExecutor(max_workers=THREAD_COUNT) as executor:
        futures = {executor.submit(worker, email, results): email for email in emails}
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
        fieldnames = ["Email", "Corrected Email", "MX Record", "SMTP Handshake", "SMTP FROM", "SMTP RCPT", "Interpretation"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for entry in results["all"]:
            writer.writerow({
                "Email": entry["Email"],
                "Corrected Email": entry["Corrected Email"],
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
