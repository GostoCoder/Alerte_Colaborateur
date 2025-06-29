import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

def test_smtp_connection(recipient_email='eto@go-storage.com'):
    """Test SMTP connection and send a test email"""
    
    # Get configuration from environment variables
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT'))
    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('SENDER_PASSWORD')
    
    print(f"SMTP Server: {smtp_server}")
    print(f"SMTP Port: {smtp_port}")
    print(f"Sender Email: {sender_email}")
    print(f"Recipient Email: {recipient_email}")
    print("-" * 50)
    
    try:
        # Create message
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = recipient_email
        message['Subject'] = "SMTP Test Email - Vehicle Management System"
        
        # Email body
        body = f"""
        Hello,
        
        This is a test email from the Vehicle Management System.
        
        Test Details:
        - Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        - Sender: {sender_email}
        - SMTP Server: {smtp_server}:{smtp_port}
        
        If you receive this email, the SMTP configuration is working correctly.
        
        Best regards,
        Vehicle Management System
        """
        
        message.attach(MIMEText(body, 'plain'))
        
        # Create SMTP session
        print("Connecting to SMTP server...")
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        
        # Enable debug output (optional)
        server.set_debuglevel(1)
        
        # Login
        print("Logging in...")
        server.login(sender_email, sender_password)
        
        # Send email
        print("Sending email...")
        text = message.as_string()
        server.sendmail(sender_email, recipient_email, text)
        
        # Close connection
        server.quit()
        
        print("✅ Email sent successfully!")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ SMTP Authentication Error: {e}")
        print("Please check your email credentials.")
        return False
        
    except smtplib.SMTPConnectError as e:
        print(f"❌ SMTP Connection Error: {e}")
        print("Please check your SMTP server settings.")
        return False
        
    except smtplib.SMTPRecipientsRefused as e:
        print(f"❌ Recipient Error: {e}")
        print("The recipient email address was rejected by the server.")
        print("This could be due to:")
        print("- Invalid domain name")
        print("- Non-existent email address")
        print("- Server restrictions")
        return False
        
    except smtplib.SMTPException as e:
        print(f"❌ SMTP Error: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

def send_custom_email(subject, body, recipient='eto@go-storage.com'):
    """Send a custom email with specified subject and body"""
    
    # Load environment variables
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT'))
    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('SENDER_PASSWORD')
    
    try:
        # Create message
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = recipient
        message['Subject'] = subject
        
        message.attach(MIMEText(body, 'plain'))
        
        # Create SMTP session
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(sender_email, sender_password)
        
        # Send email
        text = message.as_string()
        server.sendmail(sender_email, recipient, text)
        server.quit()
        
        print(f"✅ Custom email sent successfully to {recipient}!")
        return True
        
    except Exception as e:
        print(f"❌ Error sending custom email: {e}")
        return False

if __name__ == "__main__":
    print("=== SMTP Email Test ===")
    print()
    
    print("Available test options:")
    print("1. Test with corrected email: eto@go-storage.com")
    print("2. Test with original email: eto@go-storzge.com (will likely fail)")
    print("3. Enter custom email address")
    print()
    
    choice = input("Enter your choice (1-3): ").strip()
    
    if choice == "1":
        recipient = 'eto@go-storage.com'
        print(f"Testing with corrected email: {recipient}")
    elif choice == "2":
        recipient = 'eto@go-storzge.com'
        print(f"Testing with original email: {recipient}")
    elif choice == "3":
        recipient = input("Enter recipient email address: ").strip()
        print(f"Testing with custom email: {recipient}")
    else:
        recipient = 'eto@go-storage.com'
        print(f"Invalid choice. Using default: {recipient}")
    
    print()
    
    # Test basic SMTP connection and send test email
    success = test_smtp_connection(recipient)
    
    if success:
        print("\n" + "="*50)
        print("SMTP configuration is working correctly!")
        print("You can now use this configuration for sending emails.")
        
        # Ask if user wants to send a custom email
        print("\nWould you like to send a custom email? (y/n)")
        user_input = input().lower().strip()
        
        if user_input == 'y' or user_input == 'yes':
            print("\nEnter email subject:")
            custom_subject = input()
            print("\nEnter email body:")
            custom_body = input()
            
            send_custom_email(custom_subject, custom_body)
    else:
        print("\n" + "="*50)
        print("SMTP configuration failed. Please check your settings.")
