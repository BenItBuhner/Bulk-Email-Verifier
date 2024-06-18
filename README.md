# Bulk-Email-Verifier

```markdown
# Bulk Email Verification Script

## Overview

This Python script verifies a list of email addresses, checking for syntax validity, spam traps, and business email patterns. It also verifies the existence of MX records and performs SMTP checks. Results are categorized and saved into different CSV files.

## Features

- Validates email syntax
- Corrects common domain typos
- Filters out spam traps based on a custom list
- Identifies business emails based on predefined keywords
- Performs MX record lookup and caching
- Conducts SMTP handshake to verify email addresses
- Supports multithreading for faster processing

## Prerequisites

- Python 3.x
- Required Python packages: `csv`, `smtplib`, `re`, `logging`, `os`, `tqdm`, `collections`, `concurrent.futures`, `dns.resolver`

## Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/bulk-email-verification.git
   cd bulk-email-verification
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install required packages**

   ```bash
   pip install tqdm dnspython
   ```

4. **Create required files**

   - `emails.csv`: This file should contain the email addresses to be verified, with a header `Email`.

     ```csv
     Email
     example1@example.com
     example2@example.com
     ```

   - `spam-domains.txt`: This file should contain a list of spam trap domains, one domain per line.

     ```txt
     spamtrap.com
     temp-mail.org
     ```

   - `MX_Records.csv` (optional): This file will be used to cache MX records. It will be generated automatically if not present.

## Configuration

Edit the script to configure the following settings as needed:

- **Email and Password**: For SMTP verification. Replace with appropriate values.
  ```python
  EMAIL = "your_email@gmail.com"
  PASSWORD = "your_password"
  ```

- **Port**: SMTP port, typically 25.
  ```python
  PORT = 25
  ```

- **Thread Count**: Number of threads for concurrent processing.
  ```python
  THREAD_COUNT = 175
  ```

- **Server Timeout**: Timeout duration for server response.
  ```python
  SERVER_TIMEOUT = 12
  ```

- **Refresh MX Records**: Set to `True` to refresh MX records.
  ```python
  REFRESH_MX_RECORDS = False
  ```

- **AOL/Yahoo Policy**: Set to either `valid` or `invalid` to automatically classify these domains.
  ```python
  AOL_YAHOO_POLICY = "valid"
  ```

## Usage

1. **Run the script**

   ```bash
   python email_verification.py
   ```

2. **Output**

   The script will generate and save results in the `Exports` directory with the following CSV files:

   - `valid_emails.csv`: List of valid emails.
   - `invalid_emails.csv`: List of invalid emails.
   - `spam_trap_emails.csv`: List of emails identified as spam traps.
   - `business_emails.csv`: List of business emails.
   - `all_emails.csv`: Detailed results for all processed emails.

## Maintenance

- **Updating Spam Domains**: Add or remove entries in the `spam-domains.txt` file as needed.
- **MX Record Cache**: Delete or edit the `MX_Records.csv` file to reset or update the cached MX records.
- **Log Files**: Check `email_verification.log` for detailed logs of the script's execution. Rotate or delete logs periodically to manage disk space.

## Troubleshooting

- **Script Errors**: Check the `email_verification.log` file for detailed error messages and troubleshooting information.
- **Dependency Issues**: Ensure all required packages are installed and up to date. Use `pip install -r requirements.txt` if a requirements file is provided.
- **Performance**: Adjust `THREAD_COUNT` and `SERVER_TIMEOUT` settings based on your server's performance and network conditions.

## Contributing

Feel free to fork this repository, make improvements, and submit pull requests. Contributions are welcome!

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```

## File Structure

Here's a suggested file structure for your repository:

```
bulk-email-verification/
│
├── email_verification.py    # Main script
├── emails.csv               # Email addresses to verify
├── spam-domains.txt         # List of spam trap domains
├── MX_Records.csv           # MX record cache (optional, will be generated)
├── Exports/                 # Directory for output files
├── README.md                # Instructions and documentation
├── requirements.txt         # Python package requirements
└── LICENSE                  # License file
```

## Example requirements.txt

Include a `requirements.txt` file for easy package installation:

```
tqdm
dnspython
```

This README provides a comprehensive guide to setting up, using, and maintaining the bulk email verification script. Adjust the instructions based on your specific use case and environment.
