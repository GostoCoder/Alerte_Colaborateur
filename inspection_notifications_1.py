import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from datetime import datetime, timedelta, date
import os
from dotenv import load_dotenv
from zoneinfo import ZoneInfo
from sqlalchemy import create_engine, and_, or_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import MetaData, Table
import logging
from gemini_service import generate_email_content
# ChatGPT service is unused and import removed

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
NOTIFY_DRY_RUN = os.getenv('NOTIFY_DRY_RUN', 'false').lower() == 'true'

# Validate email configuration
if not all([SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL]):
    raise ValueError("Missing email configuration. Please check your .env file.")

if not RECIPIENT_EMAIL_2:
    logger.warning("RECIPIENT_EMAIL_2 not configured. Second recipient notifications will be disabled.")

if SMTP_PORT is None:
    raise ValueError("SMTP_PORT must be set in .env")
try:
    SMTP_PORT = int(SMTP_PORT)
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
    
    max_future_date = get_current_date() + timedelta(days=365*2)  # 2 years max
    return date_obj <= max_future_date

def _parse_date_string(s):
    import re
    s = str(s).strip().replace('\xa0', ' ')
    tokens = s.split()
    candidates = [s]
    if tokens:
        candidates.append(tokens[0])
    formats = [
        "%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d", "%d.%m.%Y",
        "%d/%m/%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"
    ]
    for candidate in candidates:
        for fmt in formats:
            try:
                return datetime.strptime(candidate, fmt).date()
            except Exception:
                continue
        try:
            return datetime.fromisoformat(candidate).date()
        except Exception:
            continue
    try:
        from dateutil.parser import parse as dateutil_parse
        return dateutil_parse(s).date()
    except Exception:
        pass
    return None

def check_inspection_dates():
    """Check all date fields in all tables and send notifications if needed."""
    db = None
    try:
        db = get_db()
        today = get_current_date()
        window_end = today + timedelta(days=14)
        logger.info(f"Checking all date fields between {today} and {window_end} (inclusive)")

        metadata = MetaData()
        metadata.reflect(bind=engine)
        notifications_by_row = {}

        for table_name, table in metadata.tables.items():
            logger.info(f"Scanning table: {table_name}")
            # Find date-like columns
            date_columns = [col for col in table.columns if (
                "date" in col.name.lower() or "limit" in col.name.lower() or "expiry" in col.name.lower() or "ifo" in col.name.lower() or "caces" in col.name.lower() or "airr" in col.name.lower() or "hgo" in col.name.lower() or "bo" in col.name.lower() or "visite_med" in col.name.lower() or "brevet_secour" in col.name.lower()
            )]
            # For each row in the table
            rows = db.execute(table.select()).fetchall()
            for row in rows:
                # Robust conversion for SQLAlchemy Row objects
                if hasattr(row, "_mapping"):
                    row_dict = dict(row._mapping)
                elif hasattr(row, "items"):
                    row_dict = dict(row.items())
                else:
                    row_dict = {col.name: row[idx] for idx, col in enumerate(table.columns)}
                due_items = []
                for col in date_columns:
                    date_val = row_dict.get(col.name)
                    if not date_val:
                        continue
                    # Try to parse date
                    try:
                        if isinstance(date_val, str):
                            date_obj = _parse_date_string(date_val)
                        elif isinstance(date_val, datetime):
                            date_obj = date_val.date()
                        elif isinstance(date_val, date):
                            date_obj = date_val
                        else:
                            continue
                        if date_obj is None:
                            logger.warning(f"Could not parse date for {col.name} in {table_name}: {date_val}")
                            continue
                    except Exception:
                        logger.warning(f"Could not parse date for {col.name} in {table_name}: {date_val}")
                        continue
                    if not validate_date(date_obj):
                        continue
                    # Inclusive range check
                    if today <= date_obj <= window_end:
                        # If there is a matching completion column, check if completed
                        completion_col = None
                        if col.name.startswith("limit_"):
                            completion_col = "date_" + col.name[len("limit_"):]
                        elif col.name.startswith("Limit "):
                            completion_col = "Date " + col.name[len("Limit "):]
                        if completion_col and completion_col in row_dict and row_dict[completion_col]:
                            continue  # Already completed
                        days_until = (date_obj - today).days
                        due_items.append({
                            "field": col.name,
                            "due_date": date_obj.strftime("%Y-%m-%d"),
                            "days_until": days_until,
                            "comments": row_dict.get("comments", ""),
                            "message": f"{col.name} due in {days_until} days"
                        })
                if due_items:
                    notifications_by_row[(table_name, row_dict.get("id"))] = {
                        "table": table_name,
                        "row_id": row_dict.get("id"),
                        "row_data": row_dict,
                        "due_items": due_items
                    }

        if not notifications_by_row:
            logger.info(f"No notifications needed for {today}")
            return

        logger.info(f"Found {len(notifications_by_row)} rows requiring notifications")

        # Prepare and send emails (or log if dry-run)
        for key, notif in notifications_by_row.items():
            subject, body = generate_email_content(notif["row_data"], notif["due_items"])
            if NOTIFY_DRY_RUN:
                logger.info(f"[DRY RUN] Would send email to {RECIPIENT_EMAIL} for table {notif['table']} row {notif['row_id']}:\nSubject: {subject}\nBody:\n{body}")
                urgent_items = [item for item in notif["due_items"] if item["days_until"] <= 4]
                if RECIPIENT_EMAIL_2 and urgent_items:
                    logger.info(f"[DRY RUN] Would send URGENT email to {RECIPIENT_EMAIL_2} for table {notif['table']} row {notif['row_id']}")
                continue
            try:
                smtp_server = str(SMTP_SERVER) if SMTP_SERVER is not None else ""
                smtp_port = int(SMTP_PORT) if SMTP_PORT is not None else 0
                if not SMTP_SERVER or not SMTP_PORT or smtp_server == "" or smtp_port == 0:
                    logger.error("SMTP server or port not configured. Skipping email send.")
                    continue
                logger.info(f"Connecting to SMTP server {SMTP_SERVER}:{SMTP_PORT} using SSL...")
                import socket
                try:
                    with smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=30) as server:
                        logger.info("SMTP_SSL connection established, attempting login...")
                        try:
                            server.login(str(SENDER_EMAIL), str(SENDER_PASSWORD))
                            logger.info("SMTP login successful")
                        except smtplib.SMTPAuthenticationError as e:
                            logger.error(f"Email authentication failed: {e}")
                            continue

                        from email.utils import formataddr
                        msg = MIMEMultipart()
                        msg['From'] = formataddr((str(Header("Alerte Collaborateur", 'utf-8')), str(SENDER_EMAIL or "")))
                        msg['To'] = formataddr((str(Header("", 'utf-8')), str(RECIPIENT_EMAIL or "")))
                        msg['Subject'] = str(Header(str(subject or ""), 'utf-8'))
                        msg.attach(MIMEText(str(body), 'plain', 'utf-8'))
                        try:
                            server.send_message(msg, from_addr=str(SENDER_EMAIL or ""), to_addrs=[str(RECIPIENT_EMAIL or "")], mail_options=('SMTPUTF8',))
                            logger.info(f"Notification email sent to {RECIPIENT_EMAIL} for table {notif['table']} row {notif['row_id']}")
                        except Exception as e:
                            logger.error(f"Email sendmail error: {e}\nFrom: {repr(msg['From'])}\nTo: {repr(msg['To'])}\nSubject: {repr(msg['Subject'])}\nBody: {repr(body)}")
                        # Urgent notification to second recipient
                        urgent_items = [item for item in notif["due_items"] if item["days_until"] <= 4]
                        if RECIPIENT_EMAIL_2 and urgent_items:
                            urgent_subject = f"URGENT - {subject}"
                            urgent_body = body
                            msg2 = MIMEMultipart()
                            msg2['From'] = formataddr((str(Header("Alerte Collaborateur", 'utf-8')), str(SENDER_EMAIL or "")))
                            msg2['To'] = formataddr((str(Header("", 'utf-8')), str(RECIPIENT_EMAIL_2 or "")))
                            msg2['Subject'] = str(Header(str(urgent_subject or ""), 'utf-8'))
                            msg2.attach(MIMEText(str(urgent_body), 'plain', 'utf-8'))
                            try:
                                server.send_message(msg2, from_addr=str(SENDER_EMAIL or ""), to_addrs=[str(RECIPIENT_EMAIL_2 or "")], mail_options=('SMTPUTF8',))
                                logger.info(f"Urgent notification email sent to {RECIPIENT_EMAIL_2} for table {notif['table']} row {notif['row_id']}")
                            except Exception as e:
                                logger.error(f"Urgent email sendmail error: {e}\nFrom: {repr(msg2['From'])}\nTo: {repr(msg2['To'])}\nSubject: {repr(msg2['Subject'])}\nBody: {repr(urgent_body)}")
                except (socket.gaierror, smtplib.SMTPConnectError, OSError) as e:
                    logger.error(f"SMTP connection failed for host {smtp_server}:{smtp_port}: {e}. Skipping email send.")
                    continue
            except Exception as e:
                logger.error(f"Error sending notification for table {notif['table']} row {notif['row_id']}: {e}")
                continue

    except Exception as e:
        logger.error(f"Error in check_inspection_dates: {e}")
    finally:
        if db:
            db.close()

def send_notification_email(server, vehicle, notifications):
    """Send notification email for a specific vehicle."""
    try:
        # Generate email content using Gemini AI
        subject, body = generate_email_content(vehicle, notifications)
        
        # Always send to first recipient
        from email.utils import formataddr
        msg = MIMEMultipart()
        msg['From'] = formataddr((str(Header("Alerte Collaborateur", 'utf-8')), str(SENDER_EMAIL or "")))
        msg['To'] = formataddr((str(Header("", 'utf-8')), str(RECIPIENT_EMAIL or "")))
        msg['Subject'] = str(Header(str(subject or ""), 'utf-8'))
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        try:
            server.send_message(msg, from_addr=str(SENDER_EMAIL or ""), to_addrs=[str(RECIPIENT_EMAIL or "")])
            logger.info(f"Notification email sent to {RECIPIENT_EMAIL} for vehicle {vehicle.license_plate}")
        except Exception as e:
            logger.error(f"Email sendmail error: {e}\nFrom: {repr(msg['From'])}\nTo: {repr(msg['To'])}\nSubject: {repr(msg['Subject'])}\nBody: {repr(body)}")
        
        # Check if second recipient should receive notification (within 4 days)
        if RECIPIENT_EMAIL_2:
            urgent_notifications = [notif for notif in notifications if notif['days_until'] <= 4]
            
            if urgent_notifications:
                # Generate content for urgent notifications only
                urgent_subject, urgent_body = generate_email_content(vehicle, urgent_notifications)
                
                msg2 = MIMEMultipart()
                msg2['From'] = formataddr((str(Header("Alerte Collaborateur", 'utf-8')), str(SENDER_EMAIL or "")))
                msg2['To'] = formataddr((str(Header("", 'utf-8')), str(RECIPIENT_EMAIL_2 or "")))
                msg2['Subject'] = str(Header(str(f"URGENT - {urgent_subject}" or ""), 'utf-8'))
                msg2.attach(MIMEText(urgent_body, 'plain', 'utf-8'))
                try:
                    server.send_message(msg2, from_addr=str(SENDER_EMAIL or ""), to_addrs=[str(RECIPIENT_EMAIL_2 or "")])
                    logger.info(f"Urgent notification email sent to {RECIPIENT_EMAIL_2} for vehicle {vehicle.license_plate} ({len(urgent_notifications)} urgent inspection(s))")
                except Exception as e:
                    logger.error(f"Urgent email sendmail error: {e}\nFrom: {repr(msg2['From'])}\nTo: {repr(msg2['To'])}\nSubject: {repr(msg2['Subject'])}\nBody: {repr(urgent_body)}")
        
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
