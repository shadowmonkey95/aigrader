import os
import re
import imaplib
import email
from email.header import decode_header
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Email configuration
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_SERVER = os.getenv("EMAIL_SERVER")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 993))

def fetch_emails():
    """Fetch and list unread emails"""
    print("Email fetching test script")
    print(f"Email server: {EMAIL_SERVER}")
    print(f"Email port: {EMAIL_PORT}")
    print(f"Email user: {EMAIL_USER}")
    print(f"Email password: {'*' * len(EMAIL_PASSWORD) if EMAIL_PASSWORD else 'None'}")
    
    try:
        # Read raw values directly from .env file
        raw_user = EMAIL_USER
        raw_pwd = EMAIL_PASSWORD
        
        # Try to read directly from .env file if needed
        if not raw_user or not raw_pwd:
            try:
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
            except Exception as e:
                print(f"Error reading .env file directly: {e}")
        
        print("\nAttempting connection...")
        mail = imaplib.IMAP4_SSL(EMAIL_SERVER, EMAIL_PORT)
        print("Server connected")
        
        print("Attempting login...")
        mail.login(raw_user, raw_pwd)
        print("Login successful!")
        
        # Select inbox
        print("\nSelecting inbox...")
        mail.select('inbox')
        
        # Search for unread emails
        print("Searching for unread emails...")
        status, email_ids = mail.search(None, 'UNSEEN')
        
        if status != 'OK':
            print("No unread emails found or search failed")
            mail.logout()
            return
        
        # Process each email
        email_count = 0
        for e_id in email_ids[0].split():
            email_count += 1
            print(f"\nFetching email {e_id.decode()}...")
            status, email_data = mail.fetch(e_id, '(RFC822)')
            
            if status != 'OK':
                print(f"Failed to fetch email {e_id.decode()}")
                continue
            
            msg = email.message_from_bytes(email_data[0][1])
            subject = decode_header(msg["Subject"])[0][0]
            
            if isinstance(subject, bytes):
                subject = subject.decode()
                
            print(f"Subject: {subject}")
            
            # Look for attachments
            attachment_count = 0
            for part in msg.walk():
                if part.get_content_maintype() == "multipart":
                    continue
                
                filename = part.get_filename()
                if not filename:
                    continue
                
                filename = decode_header(filename)[0][0]
                if isinstance(filename, bytes):
                    filename = filename.decode()
                
                print(f"  Attachment: {filename}")
                attachment_count += 1
                
            if attachment_count == 0:
                print("  No attachments found")
                
        print(f"\nFound {email_count} unread emails")
        
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
    fetch_emails()