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
from models_2 import Vehicle2 as Vehicle, Base  # Renamed Vehicle to Vehicle2
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


def check_inspection_dates():
    """Check vehicle inspection dates and send notifications if needed."""
    db = None
    try:
        db = get_db()
        today = get_current_date()
        two_weeks_later = today + timedelta(days=14)
        
        logger.info(f"Checking inspections between {today} and {two_weeks_later} for database_management_2.db")
        
        # Query vehicles that need inspection notifications using efficient filtering
        # Only get vehicles that have due dates within the 2-week window and no corresponding completion dates
        vehicles = db.query(Vehicle).filter(
            or_(
                and_(
                    Vehicle.ct_soeco_date.isnot(None),
                    Vehicle.ct_soeco_date >= today,
                    Vehicle.ct_soeco_date <= two_weeks_later,
                    Vehicle.date_technical_inspection.is_(None)
                ),
                and_(
                    Vehicle.euromaster_chrono.isnot(None),
                    Vehicle.euromaster_chrono >= today,
                    Vehicle.euromaster_chrono <= two_weeks_later,
                    Vehicle.date_chrono.is_(None)
                ),
                and_(
                    Vehicle.euromaster_limiteur.isnot(None),
                    Vehicle.euromaster_limiteur >= today,
                    Vehicle.euromaster_limiteur <= two_weeks_later,
                    Vehicle.date_limiteur.is_(None)
                ),
                and_(
                    Vehicle.ned92_chrono.isnot(None),
                    Vehicle.ned92_chrono >= today,
                    Vehicle.ned92_chrono <= two_weeks_later,
                    Vehicle.date_chrono.is_(None)
                ),
                and_(
                    Vehicle.ned92_limiteur.isnot(None),
                    Vehicle.ned92_limiteur >= today,
                    Vehicle.ned92_limiteur <= two_weeks_later,
                    Vehicle.date_limiteur.is_(None)
                )
            )
        ).all()
        
        if not vehicles:
            logger.info(f"No notifications needed for {today}")
            return
        
        logger.info(f"Found {len(vehicles)} vehicles requiring notifications")
        
        # Helper function to create notification entry
        def create_notification_entry(vehicle, inspection_type, due_date_field, actual_date_field, message_text, notifications, today, two_weeks_later):
            due_date = getattr(vehicle, due_date_field, None)
            actual_date = getattr(vehicle, actual_date_field, None)

            if due_date and validate_date_field(due_date):
                # Ensure due_date is a date object after validation
                if isinstance(due_date, str):
                    due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
                
                if today <= due_date <= two_weeks_later and not actual_date:
                    days_until = (due_date - today).days
                    notifications.append({
                        'type': inspection_type,
                        'vehicle_data': {
                            'id': vehicle.id,
                            'license_plate': vehicle.license_plate,
                            'vehicle_type': vehicle.vehicle_type,
                            'brand': vehicle.brand,
                            'commercial_type': vehicle.commercial_type,
                            'group_number': vehicle.group_number,
                            'work_with': getattr(vehicle, 'work_with', None),
                            'kilometer_additional_inspection': getattr(vehicle, 'kilometer_additional_inspection', None),
                            'ct_soeco_date': vehicle.ct_soeco_date.strftime('%Y-%m-%d') if vehicle.ct_soeco_date else None,
                            'euromaster_chrono': vehicle.euromaster_chrono.strftime('%Y-%m-%d') if vehicle.euromaster_chrono else None,
                            'euromaster_limiteur': vehicle.euromaster_limiteur.strftime('%Y-%m-%d') if vehicle.euromaster_limiteur else None,
                            'ned92_chrono': vehicle.ned92_chrono.strftime('%Y-%m-%d') if vehicle.ned92_chrono else None,
                            'ned92_limiteur': vehicle.ned92_limiteur.strftime('%Y-%m-%d') if vehicle.ned92_limiteur else None,
                            'date_technical_inspection': vehicle.date_technical_inspection.strftime('%Y-%m-%d') if vehicle.date_technical_inspection else None,
                            'date_chrono': vehicle.date_chrono.strftime('%Y-%m-%d') if vehicle.date_chrono else None,
                            'date_limiteur': vehicle.date_limiteur.strftime('%Y-%m-%d') if vehicle.date_limiteur else None,
                            'comments': vehicle.comments,
                            'created_at': vehicle.created_at.strftime('%Y-%m-%d %H:%M:%S') if vehicle.created_at else None,
                            'updated_at': vehicle.updated_at.strftime('%Y-%m-%d %H:%M:%S') if vehicle.updated_at else None
                        },
                        'due_date': due_date.strftime('%Y-%m-%d'),
                        'message': f'{message_text} dans {days_until} jours',
                        'days_until': days_until,
                        'comments': vehicle.comments
                    })

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
                    return

                for vehicle in vehicles:
                    try:
                        notifications = []
                        
                        create_notification_entry(vehicle, 'CT SOECO', 'ct_soeco_date', 'date_technical_inspection', 'Contrôle technique SOECO à effectuer', notifications, today, two_weeks_later)
                        create_notification_entry(vehicle, 'Euromaster Chrono', 'euromaster_chrono', 'date_chrono', 'Contrôle chronotachygraphe Euromaster à effectuer', notifications, today, two_weeks_later)
                        create_notification_entry(vehicle, 'Euromaster Limiteur', 'euromaster_limiteur', 'date_limiteur', 'Contrôle limiteur Euromaster à effectuer', notifications, today, two_weeks_later)
                        create_notification_entry(vehicle, 'NED92 Chrono', 'ned92_chrono', 'date_chrono', 'Contrôle chronotachygraphe NED92 à effectuer', notifications, today, two_weeks_later)
                        create_notification_entry(vehicle, 'NED92 Limiteur', 'ned92_limiteur', 'date_limiteur', 'Contrôle limiteur NED92 à effectuer', notifications, today, two_weeks_later)

                        if notifications:
                            send_notification_email(server, vehicle, notifications)
                
                    except Exception as e:
                        logger.error(f"Error processing vehicle {getattr(vehicle, 'license_plate', 'N/A')} (ID: {getattr(vehicle, 'id', 'N/A')}): {e}")
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

def send_notification_email(server, vehicle, notifications):
    """Send notification email for a specific vehicle."""
    try:
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
        logger.info(f"Notification email sent to {RECIPIENT_EMAIL} for vehicle {getattr(vehicle, 'license_plate', 'N/A')} (ID: {getattr(vehicle, 'id', 'N/A')})")
        
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
                logger.info(f"Urgent notification email sent to {RECIPIENT_EMAIL_2} for vehicle {getattr(vehicle, 'license_plate', 'N/A')} (ID: {getattr(vehicle, 'id', 'N/A')}) ({len(urgent_notifications)} urgent inspection(s))")
        
    except Exception as e:
        logger.error(f"Failed to send notification email for vehicle {getattr(vehicle, 'license_plate', 'N/A')} (ID: {getattr(vehicle, 'id', 'N/A')}): {e}")
        # Not re-raising here to allow other vehicles to be processed
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
