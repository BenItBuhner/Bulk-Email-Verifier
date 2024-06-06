import csv
import re
import smtplib
import threading
import queue
import socket
from tqdm import tqdm

# Email details for SMTP connection
SMTP_USERNAME = "ben.scott@gmail.com"
SMTP_PASSWORD = "PrettyFartSprinkles69"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587  # Using port 587 for STARTTLS

# Regex pattern for basic email validation
EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")

# Define categories for email verification results
categories = {
    "valid": [],
    "invalid": [],
    "blocked_unsure": [],
    "typos": [],
    "spam_trap_temporary": [],
    "business": [],
    "role_based": [],
}

# Helper function to validate email format
def validate_email_format(email):
    return re.match(EMAIL_REGEX, email) is not None

# Helper function to categorize emails based on SMTP response
def categorize_email(email, response, category):
    categories[category].append((email, response, category))

# Helper function to check if the email is a business or role-based email
def is_role_based_email(email):
    local_part = email.split('@')[0]
    role_based_keywords = ["info", "help", "support", "contact", "sales", "admin"]
    return any(keyword in local_part for keyword in role_based_keywords)

# Helper function to verify email using SMTP
def verify_email_smtp(email):
    try:
        smtp = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        smtp.ehlo_or_helo_if_needed()  # Send EHLO or HELO command
        smtp.starttls()
        smtp.ehlo_or_helo_if_needed()  # Send EHLO or HELO again after STARTTLS
        smtp.login(SMTP_USERNAME, SMTP_PASSWORD)  # Authenticate

        smtp.mail(SMTP_USERNAME)
        code, message = smtp.rcpt(email)

        smtp.quit()

        if code == 250:
            return "valid", message.decode()
        elif code == 550:
            return "invalid", message.decode()
        elif code in {421, 450, 451, 452}:
            # Transient errors
            return "blocked_unsure", message.decode()
        else:
            return "blocked_unsure", message.decode()
    except smtplib.SMTPRecipientsRefused as e:
        return "invalid", str(e)
    except (smtplib.SMTPServerDisconnected, smtplib.SMTPConnectError) as e:
        return "blocked_unsure", str(e)
    except Exception as e:
        return "blocked_unsure", str(e)

# Function to check if the domain is valid by checking MX records
def is_valid_domain(email):
    domain = email.split('@')[1]
    try:
        mx_records = socket.gethostbyname(domain)
        return True
    except socket.gaierror:
        return False

# Function to handle email verification for a thread
def worker(q, pbar, lock, save_interval):
    processed = 0
    while not q.empty():
        email = q.get()
        if not validate_email_format(email):
            categorize_email(email, "Invalid format", "typos")
        elif is_role_based_email(email):
            categorize_email(email, "Role-based email", "role_based")
        elif not is_valid_domain(email):
            categorize_email(email, "Invalid domain", "invalid")
        else:
            category, response = verify_email_smtp(email)
            categorize_email(email, response, category)
        
        processed += 1
        if processed % save_interval == 0:
            with lock:
                write_results_to_csv()
        
        pbar.update(1)
        q.task_done()

# Function to read emails from CSV file
def read_emails_from_csv(file_path):
    emails = []
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            emails.append(row['email'])
    return emails

# Function to write results to CSV files
def write_results_to_csv():
    for category, emails in categories.items():
        with open(f"{category}.csv", 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["email", "response", "category"])
            for email, response, category in emails:
                writer.writerow([email, response, category])

# Main function to initiate email verification process
def main():
    emails = read_emails_from_csv("emails.csv")
    q = queue.Queue()
    for email in emails:
        q.put(email)

    pbar = tqdm(total=len(emails), desc="Verifying emails", unit="email")

    threads = []
    num_threads = 50  # Adjust as needed
    save_interval = 50  # Save results after every 50 emails
    lock = threading.Lock()

    for _ in range(num_threads):
        thread = threading.Thread(target=worker, args=(q, pbar, lock, save_interval))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    pbar.close()
    write_results_to_csv()

if __name__ == "__main__":
    main()
