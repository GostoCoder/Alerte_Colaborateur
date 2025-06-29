import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

def send_test_email(recipient_email='eto@go-storage.com'):
    """Send a test email using SMTP configuration from .env file"""
    
    # Get configuration from environment variables
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT'))
    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('SENDER_PASSWORD')
    
    print(f"Sending test email to: {recipient_email}")
    print(f"From: {sender_email}")
    print(f"Using SMTP: {smtp_server}:{smtp_port}")
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
        
        # Create SMTP session and send email
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, message.as_string())
        
        print("✅ Email sent successfully!")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Authentication Error: {e}")
        return False
        
    except smtplib.SMTPRecipientsRefused as e:
        print(f"❌ Recipient Error: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("=== Simple SMTP Test ===")
    
    # Test with corrected email (note: original had typo 'go-storzge.com')
    success = send_test_email('eto@go-storage.com')
    
    if success:
        print("\n✅ SMTP configuration is working!")
        print("Email sent to eto@go-storage.com")
    else:
        print("\n❌ SMTP test failed!")
