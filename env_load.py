#!/usr/bin/env python3
"""
Script to force a fresh load of environment variables from .env file
"""

import os
import imaplib
from dotenv import load_dotenv, find_dotenv, dotenv_values

def force_reload_env():
    """Force reload environment variables from .env file"""
    print("=== Forcing reload of .env file ===")
    
    # Clear any cached dotenv values
    if 'EMAIL_USER' in os.environ:
        print("Removing existing environment variables...")
        for key in list(os.environ.keys()):
            if key in ['EMAIL_USER', 'EMAIL_PASSWORD', 'EMAIL_SERVER', 'EMAIL_PORT', 
                      'DEEPSEEK_API_KEY', 'DEEPSEEK_API_BASE']:
                del os.environ[key]
    
    # Find the .env file
    env_file = find_dotenv()
    print(f"Found .env file at: {env_file}")
    
    # Load directly with dotenv_values (bypasses caching)
    env_values = dotenv_values(env_file)
    print("Direct values from .env file:")
    for key, value in env_values.items():
        masked_value = value
        if key in ['EMAIL_PASSWORD', 'DEEPSEEK_API_KEY']:
            if value:
                masked_value = '*' * len(value)
        print(f"  {key} = {masked_value}")
    
    # Force reload with load_dotenv
    print("\nReloading with load_dotenv(override=True)...")
    load_dotenv(override=True)
    
    # Verify loaded values
    print("Environment variables after reload:")
    for key in ['EMAIL_USER', 'EMAIL_PASSWORD', 'EMAIL_SERVER', 'EMAIL_PORT', 
               'DEEPSEEK_API_KEY', 'DEEPSEEK_API_BASE']:
        value = os.getenv(key)
        masked_value = value
        if key in ['EMAIL_PASSWORD', 'DEEPSEEK_API_KEY'] and value:
            masked_value = '*' * len(value)
        print(f"  {key} = {masked_value}")
    
    return env_values

def test_email_connection(user, password, server='imap.gmail.com', port=993):
    """Test email connection with fresh values"""
    print("\n=== Testing email connection with fresh values ===")
    print(f"Server: {server}")
    print(f"Port: {port}")
    print(f"User: {user}")
    print(f"Password length: {len(password) if password else 0}")
    
    try:
        print("Connecting to server...")
        mail = imaplib.IMAP4_SSL(server, port)
        
        print("Attempting login...")
        mail.login(user, password)
        
        print("Login successful!")
        
        # List mailboxes to verify connection
        print("\nAvailable mailboxes:")
        status, mailboxes = mail.list()
        for i, mailbox in enumerate(mailboxes[:5]):  # Show first 5
            print(f"  {mailbox.decode()}")
        
        if len(mailboxes) > 5:
            print(f"  ...and {len(mailboxes) - 5} more")
        
        # Logout
        mail.logout()
        print("\nEmail connection test completed successfully!")
        return True
    except Exception as e:
        print(f"Error connecting to email: {e}")
        return False

def main():
    """Main function"""
    # Force reload environment variables
    env_values = force_reload_env()
    
    # Test email connection with fresh values
    test_email_connection(
        user=env_values.get('EMAIL_USER', ''),
        password=env_values.get('EMAIL_PASSWORD', ''),
        server=env_values.get('EMAIL_SERVER', 'imap.gmail.com'),
        port=int(env_values.get('EMAIL_PORT', '993'))
    )

if __name__ == "__main__":
    main()