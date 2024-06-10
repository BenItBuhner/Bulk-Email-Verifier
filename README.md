# Bulk-Email-Verifier

### Prerequisites
- Python 3.x installed on your system.
- `requests` and `tqdm` libraries installed. You can install them using pip:
  ```bash
  pip install requests tqdm
  ```

### Configuration
1. **Set Up Your Credentials**: Replace `your-email@example.com` and `your-password` with your actual SMTP credentials.
2. **Specify the SMTP Port**: The default port is set to `25`. Change it if your SMTP server uses a different port.
3. **Adjust Thread Count**: `THREAD_COUNT` is set to `10`. Modify this number based on your system's capabilities and the number of emails you plan to verify.
4. **Server Timeout**: `SERVER_TIMEOUT` is set to `10` seconds. Adjust this value based on the expected response time of the SMTP servers you're querying.

### Logging
- The script logs its activity to `email_verification.log`. Ensure you have write permissions in the script's directory.

### Running the Script
1. **Prepare Your Email List**: Create a CSV file named `emails.csv` with a single column header `Email` followed by the list of emails you want to verify.
2. **Execute the Script**: Run the script from the command line:
   ```bash
   python bulk_email_verification.py
   ```
3. **Monitor Progress**: The script uses `tqdm` to show a progress bar in the terminal.

### Output Files
- The script generates several CSV files as output:
  - `valid_emails.csv`: Contains emails that passed the verification.
  - `invalid_emails.csv`: Contains emails that failed the verification.
  - `spam_trap_emails.csv`: Contains emails identified as spam traps.
  - `business_emails.csv`: Contains emails identified as business-related.
  - `all_emails.csv`: Contains all emails with detailed verification results.

### Notes
- **Rate Limiting**: Be aware of rate limiting on SMTP servers. If you send too many requests in a short period, your IP might be temporarily blocked. VPNs & proxies with port 25 open are safe alternatives to use when/if blocked.
- **Error Handling**: The script logs errors to the log file. Review this file if you encounter issues during execution.

