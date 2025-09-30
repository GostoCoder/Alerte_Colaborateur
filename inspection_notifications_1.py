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

from config_1 import SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL, RECIPIENT_EMAIL_2

# Validate email configuration
if not all([SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL]):
    raise ValueError("Missing email configuration. Please check your .env file.")

if not RECIPIENT_EMAIL_2:
    logger.warning("RECIPIENT_EMAIL_2 not configured. Second recipient notifications will be disabled.")

try:
    SMTP_PORT = int(SMTP_PORT) if SMTP_PORT is not None else 587
except (TypeError, ValueError):
    raise ValueError("SMTP_PORT must be a valid integer")

from config_1 import SQLALCHEMY_DATABASE_URL
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

def get_date_fields_from_model(model):
    """Return list of (attr_name, label) for all Date columns in the model."""
    from sqlalchemy import Date
    fields = []
    label_map = {
        'fimo': 'FIMO',
        'caces': 'CACES',
        'aipr': 'AIPR',
        'hg0b0': 'Habilitation H0B0',
        'visite_med': 'Visite médicale',
        'brevet_secour': 'Brevet secouriste'
    }
    for col in model.__table__.columns:
        if isinstance(col.type, Date):
            name = col.name
            label = label_map.get(name, name.replace('_', ' ').title())
            fields.append((name, label))
    return fields

def get_collaborateur_notifications(collaborateur, today, two_weeks_later):
    """Extract notifications for a collaborateur (all date fields)."""
    notifications = []
    for field, label in get_date_fields_from_model(Collaborateur):
        raw = getattr(collaborateur, field, None)
        expiry_date = parse_date(raw)
        if expiry_date and validate_date(expiry_date) and today <= expiry_date <= two_weeks_later:
            days_until = (expiry_date - today).days
            notifications.append({
                'type': label,
                'field': field,
                'due_date': expiry_date.strftime('%Y-%m-%d'),
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

        logger.info(f"Checking inspections between {today} and {two_weeks_later}")

        collaborateurs = db.query(Collaborateur).filter(
            or_(
                Collaborateur.fimo.isnot(None),
                Collaborateur.caces.isnot(None),
                Collaborateur.aipr.isnot(None),
                Collaborateur.hg0b0.isnot(None),
                Collaborateur.visite_med.isnot(None),
                Collaborateur.brevet_secour.isnot(None)
            )
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
                    logger.info("Continuing without sending emails - notifications identified:")

                    for collaborateur in collaborateurs:
                        notifications = get_collaborateur_notifications(collaborateur, today, two_weeks_later)
                        if notifications:
                            msg = f"WOULD SEND: Collaborateur {collaborateur.nom} {collaborateur.prenom} - {len(notifications)} notification(s)"
                            logger.info(msg)
                            for notif in notifications:
                                msg = f"  - {notif['type']}: Due {notif['due_date']} ({notif['days_until']} days)"
                                logger.info(msg)
                    return

                for collaborateur in collaborateurs:
                    try:
                        notifications = get_collaborateur_notifications(collaborateur, today, two_weeks_later)
                        enhanced_notifications = []
                        for notif in notifications:
                            enhanced_notifications.append({
                                'type': notif['type'],
                                'vehicle_data': {
                                    'id': collaborateur.id,
                                    'nom': collaborateur.nom,
                                    'prenom': collaborateur.prenom,
                                    'commentaire': getattr(collaborateur, 'commentaire', None)
                                },
                                'due_date': notif['due_date'],
                                'message': f'{notif["type"]} à renouveler dans {notif["days_until"]} jours',
                                'days_until': notif['days_until']
                            })
                        if enhanced_notifications:
                            send_notification_email(server, collaborateur, enhanced_notifications)

                    except Exception as e:
                        logger.error(f"Error processing collaborateur {collaborateur.nom} {collaborateur.prenom}: {e}")
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
        logger.info(f"Notification email sent to {RECIPIENT_EMAIL} for collaborateur {collaborateur.nom} {collaborateur.prenom}")

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
                msg = f"Urgent notification email sent to {RECIPIENT_EMAIL_2} for collaborateur {collaborateur.nom} {collaborateur.prenom} ({len(urgent_notifications)} urgent inspection(s))"
                logger.info(msg)

    except Exception as e:
        logger.error(f"Failed to send notification email for collaborateur {collaborateur.nom} {collaborateur.prenom}: {e}")
        raise

def main():
    """Main function to run the notification system."""
    try:
        logger.info("Starting Collaborateur Inspection Notification System")
        current_date = get_current_date()
        logger.info(f"Current date: {current_date}")

        check_inspection_dates()
        logger.info("Notification check completed successfully")

    except Exception as e:
        logger.error(f"Error in main function: {e}")
        raise

if __name__ == "__main__":
    main()
