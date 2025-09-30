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
from models_1 import Collaborateur
import logging
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from gemini_service import generate_email_content
# from chatgpt_service import generate_email_content

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
SQLALCHEMY_DATABASE_URL = "sqlite:///database_management_1.db"
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


def validate_date(date_obj):
    """Validate that a date object is valid and not too far in the future."""
    if not isinstance(date_obj, date):
        return False

    max_future_date = get_current_date() + timedelta(days=365 * 2)  # 2 years max
    return date_obj <= max_future_date


def parse_date(date_str):
    """Try to parse a date string in several formats."""
    from datetime import datetime
    if not date_str or not isinstance(date_str, str):
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except Exception:
            continue
    return None

def get_vehicle_notifications(vehicle, today, two_weeks_later):
    """Extract notifications for a collaborateur (expiry fields)."""
    notifications = []
    expiry_fields = {
        'fimo': 'FIMO',
        'caces': 'CACES',
        'aipr': 'AIPR',
        'hg0b0': 'Habilitation H0B0',
        'visite_med': 'Visite médicale',
        'brevet_secour': 'Brevet secouriste'
    }
    for field, label in expiry_fields.items():
        value = getattr(vehicle, field, None)
        expiry_date = parse_date(value)
        if expiry_date and validate_date(expiry_date) and today <= expiry_date <= two_weeks_later:
            days_until = (expiry_date - today).days
            notifications.append({
                'type': label,
                'due_date': expiry_date.strftime('%Y-%m-%d'),
                'days_until': days_until
            })
    return notifications


def check_inspection_dates():
    """Check vehicle inspection dates and send notifications if needed."""
    db = None
    try:
        db = get_db()
        today = get_current_date()
        two_weeks_later = today + timedelta(days=14)

        logger.info(f"Checking inspections between {today} and {two_weeks_later}")

        # Query vehicles that need inspection notifications using SQLAlchemy
        # Fixed: Use proper SQLAlchemy column comparisons and IS NULL
        vehicles = db.query(Collaborateur).filter(
            or_(
                Collaborateur.fimo.isnot(None),
                Collaborateur.caces.isnot(None),
                Collaborateur.aipr.isnot(None),
                Collaborateur.hg0b0.isnot(None),
                Collaborateur.visite_med.isnot(None),
                Collaborateur.brevet_secour.isnot(None)
            )
        ).all()

        if not vehicles:
            logger.info(f"No notifications needed for {today}")
            return

        logger.info(f"Found {len(vehicles)} vehicles requiring notifications")

        # Prepare and send emails
        try:
            # Type checking for SMTP parameters
            if SMTP_SERVER is None or SMTP_PORT is None:
                raise ValueError("SMTP_SERVER and SMTP_PORT must be configured")
            
            logger.info(f"Connecting to Gmail SMTP server {SMTP_SERVER}:{SMTP_PORT} using STARTTLS...")
            with smtplib.SMTP(SMTP_SERVER, int(SMTP_PORT), timeout=30) as server:
                server.starttls()  # Enable security for Gmail
                logger.info("STARTTLS enabled, attempting login...")
                try:
                    # Type checking for authentication parameters
                    if SENDER_EMAIL is None or SENDER_PASSWORD is None:
                        raise ValueError("SENDER_EMAIL and SENDER_PASSWORD must be configured")
                    server.login(SENDER_EMAIL, SENDER_PASSWORD)
                    logger.info("SMTP login successful")
                except smtplib.SMTPAuthenticationError as e:
                    logger.error(f"Gmail authentication failed: {e}")
                    logger.error("TROUBLESHOOTING STEPS:")
                    logger.error("1. Verify Gmail password/app password is correct in .env file")
                    logger.error("2. Enable 2-Factor Authentication and generate an app password")
                    logger.error("3. Verify 'Less secure app access' is disabled (use app password instead)")
                    logger.error("4. Check Gmail account settings allow IMAP/SMTP access")
                    logger.info("Continuing without sending emails - notifications identified:")

                    # Log what notifications would have been sent
                    for vehicle in vehicles:
                        notifications = get_vehicle_notifications(vehicle, today, two_weeks_later)
                        if notifications:
                            msg = f"WOULD SEND: Vehicle {vehicle.license_plate} - {len(notifications)} notification(s)"
                            logger.info(msg)
                            for notif in notifications:
                                msg = f"  - {notif['type']}: Due {notif['due_date']} ({notif['days_until']} days)"
                                logger.info(msg)
                    return

                for vehicle in vehicles:
                    try:
                        # Use the existing get_vehicle_notifications function
                        notifications = get_vehicle_notifications(vehicle, today, two_weeks_later)
                        enhanced_notifications = []
                        for notif in notifications:
                            enhanced_notifications.append({
                                'type': notif['type'],
                                'collaborateur_data': {
                                    'id': vehicle.id,
                                    'nom': vehicle.nom,
                                    'prenom': vehicle.prenom,
                                    'commentaire': getattr(vehicle, 'commentaire', None)
                                },
                                'due_date': notif['due_date'],
                                'message': f'{notif["type"]} à renouveler dans {notif["days_until"]} jours',
                                'days_until': notif['days_until']
                            })
                        if enhanced_notifications:
                            send_notification_email(server, vehicle, enhanced_notifications)

                    except Exception as e:
                        logger.error(f"Error processing vehicle {vehicle.license_plate}: {e}")
                        continue

        except smtplib.SMTPServerDisconnected as e:
            logger.error(f"SMTP server disconnected: {e}. Email notifications will be skipped.")
            logger.info("Continuing without sending emails - notifications have been identified but not sent.")
            return
        except smtplib.SMTPConnectError as e:
            logger.error(f"SMTP connection error: {e}. Email notifications will be skipped.")
            logger.info("Continuing without sending emails - notifications have been identified but not sent.")
            return
        except ConnectionRefusedError as e:
            logger.error(f"Connection refused: {e}. Check if the SMTP server is accessible.")
            logger.info("Continuing without sending emails - notifications have been identified but not sent.")
            return
        except (smtplib.SMTPException, ConnectionError, OSError) as e:
            logger.error(f"SMTP connection failed: {e}. Email notifications will be skipped.")
            logger.info("Continuing without sending emails - notifications have been identified but not sent.")
            return
        except Exception as e:
            logger.error(f"Unexpected error with email server: {e}")
            return

    except Exception as e:
        logger.error(f"Error in check_inspection_dates: {e}")
    finally:
        if db:
            db.close()


def send_notification_email(server, vehicle, notifications):
    """Send notification email for a specific collaborateur."""
    try:
        # Generate email content using Gemini AI
        subject, body = generate_email_content(vehicle, notifications)

        # Always send to first recipient
        msg = MIMEMultipart()
        if SENDER_EMAIL is None or RECIPIENT_EMAIL is None:
            raise ValueError("SENDER_EMAIL and RECIPIENT_EMAIL must be configured")
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server.send_message(msg)
        logger.info(f"Notification email sent to {RECIPIENT_EMAIL} for vehicle {vehicle.license_plate}")

        # Check if second recipient should receive notification (within 4 days)
        if RECIPIENT_EMAIL_2:
            urgent_notifications = [notif for notif in notifications if notif['days_until'] <= 4]

            if urgent_notifications:
                # Generate content for urgent notifications only
                urgent_subject, urgent_body = generate_email_content(vehicle, urgent_notifications)


                msg2 = MIMEMultipart()
                if SENDER_EMAIL is None:
                    raise ValueError("SENDER_EMAIL must be configured")
                msg2['From'] = SENDER_EMAIL
                msg2['To'] = RECIPIENT_EMAIL_2
                msg2['Subject'] = f"URGENT - {urgent_subject}"
                msg2.attach(MIMEText(urgent_body, 'plain'))

                server.send_message(msg2)
                msg = f"Urgent notification email sent to {RECIPIENT_EMAIL_2} for vehicle {vehicle.license_plate} ({len(urgent_notifications)} urgent inspection(s))"
                logger.info(msg)


    except Exception as e:
        logger.error(f"Failed to send notification email for vehicle {vehicle.license_plate}: {e}")
        raise


def main():
    """Main function to run the notification system."""
    try:
        logger.info("Starting Vehicle Inspection Notification System")
        current_date = get_current_date()
        logger.info(f"Current date: {current_date}")

        check_inspection_dates()
        logger.info("Notification check completed successfully")

    except Exception as e:
        logger.error(f"Error in main function: {e}")
        raise


if __name__ == "__main__":
    main()
