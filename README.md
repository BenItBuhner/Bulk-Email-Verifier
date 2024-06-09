# Bulk-Email-Verifier

### Prerequisites
1. **Python Installation**: Ensure you have Python installed on your system. You can download it from [python.org](https://www.python.org/).
2. **VS Code Installation**: Ensure you have Visual Studio Code installed. You can download it from [code.visualstudio.com](https://code.visualstudio.com/).

### Step-by-Step Instructions

#### Step 1: Set Up Your Environment
1. **Open VS Code**: Launch Visual Studio Code.
2. **Create a New Workspace**:
   - Go to `File` > `Open Folder...`.
   - Select or create a folder where you want to store your script and files.

#### Step 2: Create the Python Script
1. **Create a New File**:
   - Click on the `New File` icon in the Explorer panel or press `Ctrl+N`.
   - Name the file `email_verifier.py`.

2. **Copy the Script**: Copy the provided Python script into `email_verifier.py`.

#### Step 3: Configure SMTP Details
1. **Edit the SMTP Details**:
   - Replace `SMTP_SUBDOMAIN`, `SMTP_EMAIL`, and `SMTP_PASSWORD` with your actual SMTP subdomain, email, and password.
   ```python
   # SMTP details
   SMTP_SUBDOMAIN = "smtp.example.com"
   SMTP_EMAIL = "your_email@example.com"
   SMTP_PASSWORD = "your_password"
   ```

#### Step 4: Install Required Libraries
1. **Open Terminal in VS Code**:
   - Go to `Terminal` > `New Terminal`.

2. **Install Libraries**:
   - Run the following commands to install the required Python libraries:
   ```bash
   pip install smtplib dnspython tqdm
   ```

#### Step 5: Prepare Your CSV File
1. **Create or Obtain a CSV File**:
   - Ensure you have a CSV file named `emails.csv` in the same directory as your script.
   - The CSV file should have a header `Email` and list the emails underneath it.

2. **Sample CSV Format**:
   ```csv
   Email
   example1@example.com
   example2@example.com
   ```

#### Step 6: Run the Script
1. **Run the Script in VS Code**:
   - Open the terminal in VS Code.
   - Navigate to the directory containing your script if you're not already there.
   - Run the script using the following command:
   ```bash
   python email_verifier.py
   ```

2. **Monitor the Progress**:
   - The script will display a progress bar indicating the verification progress, using the `tqdm` library.

#### Step 7: Review the Output Files
1. **Locate Output Files**:
   - The script generates several CSV files in the same directory:
     - `all_emails.csv`
     - `valid_emails.csv`
     - `invalid_emails.csv`
     - `spam_trap_emails.csv`
     - `business_emails.csv`
     - `blocked_emails.csv`

2. **Open and Review CSV Files**:
   - Open these files to review the categorized email verification results.

### Troubleshooting Tips
- **Ensure Correct SMTP Details**: Make sure your SMTP details (subdomain, email, password) are correct and have the necessary permissions to perform email verification.
- **Check CSV File Format**: Ensure your `emails.csv` file is correctly formatted with the header `Email` and valid email addresses listed below it.
- **Library Installations**: If you encounter issues with missing libraries, double-check the installation commands and ensure they complete successfully.

### Customization Tips
- **Adjust Number of Workers**: You can adjust the number of workers/threads by changing the `NUM_WORKERS` variable to optimize the script's performance based on your system's capabilities.
  ```python
  NUM_WORKERS = 10
  ```

- **Add More Business Keywords**: You can expand the `BUSINESS_KEYWORDS` list to include additional keywords for business email identification.
  ```python
  BUSINESS_KEYWORDS = ["info", "help", "support", "contact", "forgotpassword", "passwordhelp", "sales", "admin", "office"]
  ```

Note: These instructions were made with VS Code in mind.
