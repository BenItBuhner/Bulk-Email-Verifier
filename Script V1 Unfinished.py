import csv
import smtplib
import dns.resolver
import threading
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor

# Define categories
VALID = "Valid"
INVALID = "Invalid"
SPAM_TRAP = "Spam Traps & Temporary Inboxes"
BUSINESS = "Business Emails"
BLOCKED = "Server Block & Timeout"

# Business email keywords
BUSINESS_KEYWORDS = ["info", "help", "support", "contact", "forgotpassword", "passwordhelp", "sales"]

# Sample list of spam trap and temporary inbox domains
SPAM_TRAP_DOMAINS = ["mailinator.com", "10minutemail.com", "guerrillamail.com"]

# File names
INPUT_FILE = "emails.csv"
OUTPUT_FILE_ALL = "all_emails.csv"
OUTPUT_FILE_VALID = "valid_emails.csv"
OUTPUT_FILE_INVALID = "invalid_emails.csv"
OUTPUT_FILE_SPAM_TRAP = "spam_trap_emails.csv"
OUTPUT_FILE_BUSINESS = "business_emails.csv"
OUTPUT_FILE_BLOCKED = "blocked_emails.csv"

# SMTP details
SMTP_SUBDOMAIN = "smtp.example.com"
SMTP_EMAIL = "your_email@example.com"
SMTP_PASSWORD = "your_password"

# Thread/worker count
NUM_WORKERS = 10

def load_emails(filename):
    emails = []
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            emails.append(row['Email'])
    return emails

def save_emails(filename, email_data):
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['Email', 'MX', 'HELO1', 'FROM1', 'RCPT1', 'HELO2', 'FROM2', 'RCPT2', 'Interpretation']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for data in email_data:
            writer.writerow(data)

def syntax_check(email):
    return "@" in email and "." in email.split("@")[1]

def is_spam_trap(email):
    domain = email.split('@')[1]
    return domain in SPAM_TRAP_DOMAINS

def is_business_email(email):
    user = email.split('@')[0]
    return any(keyword in user for keyword in BUSINESS_KEYWORDS)

def mx_lookup(domain):
    try:
        records = dns.resolver.resolve(domain, 'MX')
        return records[0].exchange.to_text()
    except:
        return None

def smtp_verify(email, mx_record):
    try:
        server = smtplib.SMTP(SMTP_SUBDOMAIN)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.ehlo_or_helo_if_needed()
        from_response = server.mail(SMTP_EMAIL)
        rcpt_response = server.rcpt(email)
        server.quit()
        return from_response[0], rcpt_response[0]
    except:
        return None, None

def verify_email(email):
    result = {
        'Email': email,
        'MX': '',
        'HELO1': '',
        'FROM1': '',
        'RCPT1': '',
        'HELO2': '',
        'FROM2': '',
        'RCPT2': '',
        'Interpretation': ''
    }
    domain = email.split('@')[1]
    result['MX'] = mx_lookup(domain)
    if not result['MX']:
        result['Interpretation'] = INVALID
        return result

    result['HELO1'], result['RCPT1'] = smtp_verify(email, result['MX'])
    if result['RCPT1'] == 250:
        result['Interpretation'] = VALID
    elif result['RCPT1'] == 550:
        result['Interpretation'] = INVALID
    else:
        result['HELO2'], result['RCPT2'] = smtp_verify(email, result['MX'])
        if result['RCPT2'] == 250:
            result['Interpretation'] = VALID
        else:
            result['Interpretation'] = BLOCKED

    return result

def categorize_email(email):
    if is_spam_trap(email):
        return {'Email': email, 'Interpretation': SPAM_TRAP}
    elif is_business_email(email):
        return {'Email': email, 'Interpretation': BUSINESS}
    return None

def worker(email):
    result = {
        'Email': email,
        'MX': '',
        'HELO1': '',
        'FROM1': '',
        'RCPT1': '',
        'HELO2': '',
        'FROM2': '',
        'RCPT2': '',
        'Interpretation': ''
    }
    if not syntax_check(email):
        result['Interpretation'] = INVALID
    else:
        categorized = categorize_email(email)
        if categorized:
            result.update(categorized)
        else:
            result = verify_email(email)
    return result

def verify_emails(emails):
    results = []
    with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
        for result in tqdm(executor.map(worker, emails), total=len(emails), desc="Verifying emails"):
            results.append(result)
    return results

def save_results(results):
    valid_emails = [r for r in results if r['Interpretation'] == VALID]
    invalid_emails = [r for r in results if r['Interpretation'] == INVALID]
    spam_trap_emails = [r for r in results if r['Interpretation'] == SPAM_TRAP]
    business_emails = [r for r in results if r['Interpretation'] == BUSINESS]
    blocked_emails = [r for r in results if r['Interpretation'] == BLOCKED]

    save_emails(OUTPUT_FILE_ALL, results)
    save_emails(OUTPUT_FILE_VALID, valid_emails)
    save_emails(OUTPUT_FILE_INVALID, invalid_emails)
    save_emails(OUTPUT_FILE_SPAM_TRAP, spam_trap_emails)
    save_emails(OUTPUT_FILE_BUSINESS, business_emails)
    save_emails(OUTPUT_FILE_BLOCKED, blocked_emails)

if __name__ == "__main__":
    emails = load_emails(INPUT_FILE)
    results = verify_emails(emails)
    save_results(results)
