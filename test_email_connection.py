import os
import imaplib
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Email configuration
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_SERVER = os.getenv("EMAIL_SERVER")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 993))

def test_email_connection():
    """Test connection to the email server"""
    print("Email connection test script")
    print(f"Email server: {EMAIL_SERVER}")
    print(f"Email port: {EMAIL_PORT}")
    print(f"Email user: {EMAIL_USER}")
    print(f"Email password: {'*' * len(EMAIL_PASSWORD) if EMAIL_PASSWORD else 'None'}")
    
    try:
        # Alternative login method - write directly to avoid any issues
        print("\nTrying to connect with raw parameters...")
        with open('.env', 'r') as f:
            for line in f:
                if line.startswith('EMAIL_PASSWORD='):
                    raw_pwd = line[len('EMAIL_PASSWORD='):].strip()
                    if (raw_pwd.startswith('"') and raw_pwd.endswith('"')) or \
                       (raw_pwd.startswith("'") and raw_pwd.endswith("'")):
                        raw_pwd = raw_pwd[1:-1]
                elif line.startswith('EMAIL_USER='):
                    raw_user = line[len('EMAIL_USER='):].strip()
                    if (raw_user.startswith('"') and raw_user.endswith('"')) or \
                       (raw_user.startswith("'") and raw_user.endswith("'")):
                        raw_user = raw_user[1:-1]
        
        print(f"Raw user: {raw_user}")
        print(f"Raw password: {'*' * len(raw_pwd) if raw_pwd else 'None'}")
        
        # Attempt connection with raw values
        print("\nAttempting connection...")
        mail = imaplib.IMAP4_SSL(EMAIL_SERVER, EMAIL_PORT)
        print("Server connected")
        
        # Try login with raw values
        print("Attempting login with raw values...")
        mail.login(raw_user, raw_pwd)
        print("Login successful!")
        
        # Check available mailboxes
        print("\nAvailable mailboxes:")
        status, mailboxes = mail.list()
        for mailbox in mailboxes:
            print(f"  {mailbox.decode()}")
        
        # Logout
        mail.logout()
        print("\nTest completed successfully!")
        return True
        
    except Exception as e:
        print(f"\nError during test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_email_connection()