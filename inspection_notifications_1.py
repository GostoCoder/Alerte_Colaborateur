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
from models_1 import Vehicle, Base
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

def check_inspection_dates():
    """Check vehicle inspection dates and send notifications if needed."""
    db = None
    try:
        db = get_db()
        today = get_current_date()
        two_weeks_later = today + timedelta(days=14)
        
        logger.info(f"Checking inspections between {today} and {two_weeks_later}")
        
        # Query vehicles that need inspection notifications using SQLAlchemy
        # Fixed: Use IS NULL instead of == None, and separate OR conditions
        vehicles = db.query(Vehicle).filter(
            or_(
                and_(
                    Vehicle.limit_periodic_inspection >= today,
                    Vehicle.limit_periodic_inspection <= two_weeks_later,
                    Vehicle.date_periodic_inspection.is_(None)
                ),
                and_(
                    Vehicle.limit_additional_inspection >= today,
                    Vehicle.limit_additional_inspection <= two_weeks_later, 
                    Vehicle.date_additional_inspection.is_(None)
                )
            )
        ).all()
        
        if not vehicles:
            logger.info(f"No notifications needed for {today}")
            return
        
        logger.info(f"Found {len(vehicles)} vehicles requiring notifications")
        
        # Prepare and send emails
        try:
            logger.info(f"Connecting to SMTP server {SMTP_SERVER}:{SMTP_PORT} using SSL...")
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=30) as server:
                logger.info("SMTP_SSL connection established, attempting login...")
                try:
                    server.login(SENDER_EMAIL, SENDER_PASSWORD)
                    logger.info("SMTP login successful")
                except smtplib.SMTPAuthenticationError as e:
                    logger.error(f"Email authentication failed: {e}")
                    return
                
                for vehicle in vehicles:
                    try:
                        notifications = []
                        
                        # Check periodic inspection
                        if (vehicle.limit_periodic_inspection and 
                            validate_date(vehicle.limit_periodic_inspection) and
                            today <= vehicle.limit_periodic_inspection <= two_weeks_later and 
                            not vehicle.date_periodic_inspection):
                            days_until = (vehicle.limit_periodic_inspection - today).days
                            notifications.append({
                                'type': 'Contrôle technique périodique',
                                'vehicle_data': {
                                    'id': vehicle.id,
                                    'license_plate': vehicle.license_plate,
                                    'vehicle_type': vehicle.vehicle_type,
                                    'brand': vehicle.brand,
                                    'commercial_type': vehicle.commercial_type,
                                    'group_number': vehicle.group_number,
                                    'limit_periodic_inspection': vehicle.limit_periodic_inspection.strftime('%Y-%m-%d'),
                                    'kilometer_periodic_inspection': vehicle.kilometer_periodic_inspection,
                                    'limit_additional_inspection': vehicle.limit_additional_inspection.strftime('%Y-%m-%d') if vehicle.limit_additional_inspection else None,
                                    'kilometer_additional_inspection': vehicle.kilometer_additional_inspection,
                                    'date_periodic_inspection': None,
                                    'date_additional_inspection': vehicle.date_additional_inspection.strftime('%Y-%m-%d') if vehicle.date_additional_inspection else None,
                                    'comments': vehicle.comments,
                                    'created_at': vehicle.created_at.strftime('%Y-%m-%d %H:%M:%S') if vehicle.created_at else None,
                                    'updated_at': vehicle.updated_at.strftime('%Y-%m-%d %H:%M:%S') if vehicle.updated_at else None
                                },
                                'due_date': vehicle.limit_periodic_inspection.strftime('%Y-%m-%d'),
                                'message': f'Contrôle technique périodique à effectuer dans {days_until} jours',
                                'days_until': days_until,
                                'comments': vehicle.comments
                            })
                        
                        # Check additional inspection
                        if (vehicle.limit_additional_inspection and 
                            validate_date(vehicle.limit_additional_inspection) and
                            today <= vehicle.limit_additional_inspection <= two_weeks_later and 
                            not vehicle.date_additional_inspection):
                            days_until = (vehicle.limit_additional_inspection - today).days
                            notifications.append({
                                'type': 'Contrôle technique complémentaire',
                                'vehicle_data': {
                                    'id': vehicle.id,
                                    'license_plate': vehicle.license_plate,
                                    'vehicle_type': vehicle.vehicle_type,
                                    'brand': vehicle.brand,
                                    'commercial_type': vehicle.commercial_type,
                                    'group_number': vehicle.group_number,
                                    'limit_periodic_inspection': vehicle.limit_periodic_inspection.strftime('%Y-%m-%d') if vehicle.limit_periodic_inspection else None,
                                    'kilometer_periodic_inspection': vehicle.kilometer_periodic_inspection,
                                    'limit_additional_inspection': vehicle.limit_additional_inspection.strftime('%Y-%m-%d'),
                                    'kilometer_additional_inspection': vehicle.kilometer_additional_inspection,
                                    'date_periodic_inspection': vehicle.date_periodic_inspection.strftime('%Y-%m-%d') if vehicle.date_periodic_inspection else None,
                                    'date_additional_inspection': None,
                                    'comments': vehicle.comments,
                                    'created_at': vehicle.created_at.strftime('%Y-%m-%d %H:%M:%S') if vehicle.created_at else None,
                                    'updated_at': vehicle.updated_at.strftime('%Y-%m-%d %H:%M:%S') if vehicle.updated_at else None
                                },
                                'due_date': vehicle.limit_additional_inspection.strftime('%Y-%m-%d'),
                                'message': f'Contrôle technique complémentaire à effectuer dans {days_until} jours',
                                'days_until': days_until,
                                'comments': vehicle.comments
                            })
                        
                        if notifications:
                            send_notification_email(server, vehicle, notifications)
                    
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
    """Send notification email for a specific vehicle."""
    try:
        # Generate email content using Gemini AI
        subject, body = generate_email_content(vehicle, notifications)
        
        # Always send to first recipient
        msg = MIMEMultipart()
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
                msg2['From'] = SENDER_EMAIL
                msg2['To'] = RECIPIENT_EMAIL_2
                msg2['Subject'] = f"URGENT - {urgent_subject}"
                msg2.attach(MIMEText(urgent_body, 'plain'))
                
                server.send_message(msg2)
                logger.info(f"Urgent notification email sent to {RECIPIENT_EMAIL_2} for vehicle {vehicle.license_plate} ({len(urgent_notifications)} urgent inspection(s))")
        
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
