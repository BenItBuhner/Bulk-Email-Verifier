# Bulk-Email-Verifier
Bulk email verifier, made with the help of GPT-4, that supports the importing of CSV files with emails, and will export four different CSVs, varying by validity.

How to use:

Put the Python script into a select folder. Then, rename the email list to verify as “emails.csv”, but ensure it originates as a CSV file to prevent corruption or properly convert the file. Then, run the Python script, preferably in VS Code, for an easier to understand interface.

Follow the instructions on start-up and let the rest do the work.

Note: Many email domains & servers will block interactions to local IPs and their usage of ports such as port 25, so the use of a proxy, VPN, or remote VM/VPS could help resolve high unsure email rates, as this blocking is a frequent practice.

What to import via command line:

pip install email-validator dnspython,
pip install email_validator,
pip install dnspython,
pip install tqdm,

Attempt to install all of these, as one or two may not work properly, as GPT-4 provided different libraries to import, and was never sure. Yes, this was made mostly with ChatGPT in Microsoft’s Copilot!
