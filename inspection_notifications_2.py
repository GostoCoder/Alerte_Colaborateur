import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta, date
import os
from dotenv import load_dotenv
from zoneinfo import ZoneInfo
from sqlalchemy import create_engine, and_, or_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from models_2 import CollaborateurPoidsLouud as Collaborateur
import logging
from gemini_service import generate_email_content
#from chatgpt_service import generate_email_content

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Email configuration with validation
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = os.getenv('SMTP_PORT')
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')
RECIPIENT_EMAIL_2 = os.getenv('RECIPIENT_EMAIL_2')

# Validate email configuration
if not all([SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL]):
    raise ValueError("Missing email configuration. Please check your .env file.")

if not RECIPIENT_EMAIL_2:
    logger.warning("RECIPIENT_EMAIL_2 not configured. Second recipient notifications will be disabled.")

try:
    SMTP_PORT = int(SMTP_PORT) if SMTP_PORT is not None else 587
except (TypeError, ValueError):
    raise ValueError("SMTP_PORT must be a valid integer")

# Database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///database_management_2.db"
try:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    logger.error(f"Failed to create database engine: {e}")
    raise

# Time zone configuration
TIMEZONE = ZoneInfo("Europe/Paris")

def get_current_date():
    """Get the current date in the correct timezone."""
    try:
        current_time = datetime.now(TIMEZONE)
        return current_time.date()
    except Exception as e:
        logger.error(f"Error getting current date: {e}")
        raise

# Current date variable
TODAY = get_current_date()

def get_db():
    """Create a database session."""
    db = None
    try:
        db = SessionLocal()
        return db
    except SQLAlchemyError as e:
        logger.error(f"Database connection error: {e}")
        if db:
            db.close()
        raise

def validate_date_field(date_obj):
    """Validate that a date object is valid and not too far in the future."""
    if not isinstance(date_obj, date):
        # Attempt to parse if it's a string
        if isinstance(date_obj, str):
            try:
                date_obj = datetime.strptime(date_obj, '%Y-%m-%d').date()
            except ValueError:
                logger.warning(f"Invalid date string format: {date_obj}")
                return False
        else:
            logger.warning(f"Invalid date type: {type(date_obj)}")
            return False
    
    max_future_date = get_current_date() + timedelta(days=365*2)  # 2 years max
    return date_obj <= max_future_date


def parse_date(value):
    """Parse a value as a date, supporting date, datetime, and string formats."""
    if value is None:
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
            try:
                return datetime.strptime(value.strip(), fmt).date()
            except Exception:
                continue
    return None

def get_collaborateur_notifications(collaborateur, today, two_weeks_later):
    """Extract notifications for a collaborateur (date_validite only)."""
    notifications = []
    # Only scan the date_validite field
    for field, label in [
        ("date_validite", "Date de validité"),
    ]:
        raw = getattr(collaborateur, field, None)
        expiry_date = parse_date(raw)
        if expiry_date and validate_date_field(expiry_date) and today <= expiry_date <= two_weeks_later:
            days_until = (expiry_date - today).days
            notifications.append({
                'type': label,
                'collaborateur_id': collaborateur.id,
                'vehicle_data': {
                    'license_plate': f"{collaborateur.nom} {collaborateur.prenom}",
                    'comments': getattr(collaborateur, 'commentaire', None)
                },
                'due_date': expiry_date.strftime('%Y-%m-%d'),
                'message': f'{label} à renouveler dans {days_until} jours',
                'days_until': days_until
            })
    return notifications

def check_inspection_dates():
    """Check collaborateur inspection dates and send notifications if needed."""
    db = None
    try:
        db = get_db()
        today = get_current_date()
        two_weeks_later = today + timedelta(days=14)

        logger.info(f"Checking inspections between {today} and {two_weeks_later} for database_management_2.db")

        collaborateurs = db.query(Collaborateur).filter(
            Collaborateur.date_validite.isnot(None)
        ).all()

        if not collaborateurs:
            logger.info(f"No notifications needed for {today}")
            return

        logger.info(f"Found {len(collaborateurs)} collaborateurs requiring notifications")

        try:
            if SMTP_SERVER is None or SMTP_PORT is None:
                raise ValueError("SMTP_SERVER and SMTP_PORT must be configured")

            port = int(SMTP_PORT) if SMTP_PORT is not None else 587
            if port == 465:
                logger.info(f"Connecting to SMTP server {SMTP_SERVER}:{port} using SSL...")
                server = smtplib.SMTP_SSL(SMTP_SERVER, port, timeout=30)
            else:
                logger.info(f"Connecting to SMTP server {SMTP_SERVER}:{port} using STARTTLS...")
                server = smtplib.SMTP(SMTP_SERVER, port, timeout=30)
                server.ehlo()
                server.starttls()
                server.ehlo()
            with server:
                try:
                    if SENDER_EMAIL is None or SENDER_PASSWORD is None:
                        raise ValueError("SENDER_EMAIL and SENDER_PASSWORD must be configured")
                    sender_password = SENDER_PASSWORD.strip()
                    server.login(SENDER_EMAIL, sender_password)
                    logger.info("SMTP login successful")
                except smtplib.SMTPAuthenticationError as e:
                    logger.error(f"Gmail authentication failed: {e}")
                    logger.error("TROUBLESHOOTING STEPS:")
                    logger.error("1. Verify Gmail password/app password is correct in .env file")
                    logger.error("2. Enable 2-Factor Authentication and generate an app password")
                    logger.error("3. Verify 'Less secure app access' is disabled (use app password instead)")
                    logger.error("4. Check Gmail account settings allow IMAP/SMTP access")
                    return

                for collaborateur in collaborateurs:
                    try:
                        notifications = get_collaborateur_notifications(collaborateur, today, two_weeks_later)
                        if notifications:
                            send_notification_email(server, collaborateur, notifications)

                    except Exception as e:
                        logger.error(f"Error processing collaborateur {getattr(collaborateur, 'nom', 'N/A')} {getattr(collaborateur, 'prenom', 'N/A')} (ID: {getattr(collaborateur, 'id', 'N/A')}): {e}")
                        continue
        except smtplib.SMTPException as e:
            logger.error(f"Email server error in check_inspection_dates: {e}")

    except SQLAlchemyError as e:
        logger.error(f"Database error in check_inspection_dates: {e}")
    except Exception as e:
        logger.error(f"Error in check_inspection_dates: {e}")
    finally:
        if db:
            db.close()

def send_notification_email(server, collaborateur, notifications):
    """Send notification email for a specific collaborateur."""
    try:
        subject, body = generate_email_content(collaborateur, notifications)

        msg = MIMEMultipart()
        if SENDER_EMAIL is None or RECIPIENT_EMAIL is None:
            raise ValueError("SENDER_EMAIL and RECIPIENT_EMAIL must be configured")
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server.send_message(msg)
        logger.info(f"Notification email sent to {RECIPIENT_EMAIL} for collaborateur {getattr(collaborateur, 'nom', 'N/A')} {getattr(collaborateur, 'prenom', 'N/A')} (ID: {getattr(collaborateur, 'id', 'N/A')})")

        if RECIPIENT_EMAIL_2:
            urgent_notifications = [notif for notif in notifications if notif['days_until'] <= 4]

            if urgent_notifications:
                urgent_subject, urgent_body = generate_email_content(collaborateur, urgent_notifications)

                msg2 = MIMEMultipart()
                if SENDER_EMAIL is None:
                    raise ValueError("SENDER_EMAIL must be configured")
                msg2['From'] = SENDER_EMAIL
                msg2['To'] = RECIPIENT_EMAIL_2
                msg2['Subject'] = f"URGENT - {urgent_subject}"
                msg2.attach(MIMEText(urgent_body, 'plain'))

                server.send_message(msg2)
                logger.info(f"Urgent notification email sent to {RECIPIENT_EMAIL_2} for collaborateur {getattr(collaborateur, 'nom', 'N/A')} {getattr(collaborateur, 'prenom', 'N/A')} (ID: {getattr(collaborateur, 'id', 'N/A')}) ({len(urgent_notifications)} urgent inspection(s))")

    except Exception as e:
        logger.error(f"Failed to send notification email for collaborateur {getattr(collaborateur, 'nom', 'N/A')} {getattr(collaborateur, 'prenom', 'N/A')} (ID: {getattr(collaborateur, 'id', 'N/A')}): {e}")
        # Not re-raising here to allow other collaborateurs to be processed
        # raise # Uncomment if one email failure should stop all

def main():
    """Main function to run the notification system."""
    try:
        logger.info("Starting Vehicle Inspection Notification System for database_management_2.db")
        current_date_val = get_current_date()
        logger.info(f"Current date: {current_date_val}")
        
        check_inspection_dates()
        logger.info("Notification check completed successfully for database_management_2.db")
        
    except Exception as e:
        logger.error(f"Error in main function (database_management_2.db): {e}")
        # raise # Uncomment if main function error should stop the script

if __name__ == "__main__":
    main()
