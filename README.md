# Bulk-Email-Verifier
CURRENTLY NOT UP-TO-DATE: WILL BE REFRESHED LATER

Bulk email verifier, made with the help of GPT-4, that supports the importing of CSV files with emails, and will export four different CSVs, varying by validity.

How to use:

Put the Python script into a select folder. Then, rename the email list to verify as “emails.csv”, but ensure it originates as a CSV file to prevent corruption or properly convert the file. Then, run the Python script, preferably in VS Code, for an easier to understand interface.

Follow the instructions on start-up and let the rest do the work.

Upon completion, there should be additional CSV files in the selected folder in which you chose to run the Python script in. Each is named as they contain their corresponding email outputs. 

Note: Many email domains & servers will block interactions to local IPs and their usage of ports such as port 25, so the use of a proxy, VPN, or remote VM/VPS could help resolve high unsure email rates, as this blocking is a frequent practice.

UPDATE: Altered script now runs on port 587 with a secure & encrpyted TTL encryption protocol, which more providers allow, than port 25. 

What to import via command line:

pip install email_validator dnspython tqdm

Alt import (if script is "invalid"):

pip install email-validator dnspython tqdm

Attempt to install all of these, as one or two may not work properly, as GPT-4 provided different libraries to import, and was never sure. Yes, this was made mostly with ChatGPT in Microsoft’s Copilot!
