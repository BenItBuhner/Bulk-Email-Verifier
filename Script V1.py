import csv
import smtplib
import concurrent.futures
from email_validator import validate_email, EmailNotValidError
import dns.resolver
from tqdm import tqdm

def verify_email(email):
    try:
        v = validate_email(email) # validate and get info
        email = v["email"] # replace with normalized form
        domain = v["domain"]
        mx_records = dns.resolver.resolve(domain, 'MX')
        mx_record = str(mx_records[0].exchange)
        server = smtplib.SMTP(mx_record, port=587, timeout=10) # Use port 587
        server.starttls() # Upgrade the connection to TLS
        server.set_debuglevel(0)
        server.ehlo()
        server.mail('')
        code, message = server.rcpt(str(email))
        server.quit()

        if code == 250:
            return (email, "valid")
        else:
            return (email, "invalid")
    except Exception as e:
        return (email, "unknown")

if __name__ == "__main__":
    with open('emails.csv', 'r') as f:
        reader = csv.reader(f)
        emails = list(reader)

    results = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        for result in tqdm(executor.map(verify_email, emails), total=len(emails), desc="Verifying emails"):
            results.append(result)

    valid_emails = [result for result in results if result[1] == "valid"]
    invalid_emails = [result for result in results if result[1] == "invalid"]
    unknown_emails = [result for result in results if result[1] == "unknown"]
    excluded_emails = [result for result in results if result[1] == "excluded"]

    print(f"Valid emails: {len(valid_emails)} ({len(valid_emails)/len(emails)*100:.2f}%)")
    print(f"Invalid emails: {len(invalid_emails)} ({len(invalid_emails)/len(emails)*100:.2f}%)")
    print(f"Unknown emails: {len(unknown_emails)} ({len(unknown_emails)/len(emails)*100:.2f}%)")
    print(f"Excluded emails: {len(excluded_emails)} ({len(excluded_emails)/len(emails)*100:.2f}%)")

    # Write to CSV files
    with open('valid_emails.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Email", "Server Response"])
        writer.writerows(valid_emails)

    with open('invalid_emails.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Email", "Server Response"])
        writer.writerows(invalid_emails)

    with open('unknown_emails.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Email", "Server Response"])
        writer.writerows(unknown_emails)

    with open('excluded_emails.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Email", "Server Response"])
        writer.writerows(excluded_emails)
