import google.generativeai as genai
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def get_vehicle_identifier(vehicle_data):
    """Get the vehicle identifier (license plate or serial number)"""
    if "license_plate" in vehicle_data:
        return vehicle_data["license_plate"]
    elif "serial_number" in vehicle_data:
        return vehicle_data["serial_number"]
    return "Véhicule Inconnu"


def get_collaborateur_details(cdata):
    """Get collaborateur details based on available fields"""
    details = []

    # Basic info
    details.append(f"- Nom: {cdata.get('nom', 'N/A')}")
    details.append(f"- Prénom: {cdata.get('prenom', 'N/A')}")

    # Dates
    if cdata.get('ifo'):
        details.append(f"- IFO: {cdata.get('ifo')}")
    if cdata.get('caces'):
        details.append(f"- CACES: {cdata.get('caces')}")
    if cdata.get('airr'):
        details.append(f"- AIRR: {cdata.get('airr')}")
    if cdata.get('hgo'):
        details.append(f"- HGO: {cdata.get('hgo')}")
    if cdata.get('bo'):
        details.append(f"- BO: {cdata.get('bo')}")
    if cdata.get('visite_med'):
        details.append(f"- Visite médicale: {cdata.get('visite_med')}")
    if cdata.get('brevet_secour'):
        details.append(f"- Brevet secouriste: {cdata.get('brevet_secour')}")

    # Comments
    details.append(f"- Commentaire: {cdata.get('commentaire', 'Aucun commentaire')}")

    return details


def generate_email_content(vehicle, notifications):
    """Generate email content using Gemini AI (compatible shapes)."""
    try:
        # Normalize notifications to a list
        notif_list = notifications if isinstance(notifications, list) else [notifications]

        # Determine if any notification is urgent (0-4 days)
        urgent_inspections = [
            n for n in (notif_list or []) if isinstance(n, dict) and n.get("days_until", 999) <= 4
        ]
        is_urgent = len(urgent_inspections) > 0

        # Determine collaborateur data:
        # - Prefer the explicit 'vehicle' dict if it's a mapping of collaborateur fields.
        # - Fallback to row_data embedded inside notifications (backwards compatibility).
        collaborateur_data = {}
        if isinstance(vehicle, dict) and vehicle:
            collaborateur_data = vehicle
        else:
            # Look for row_data inside the first notification dict
            for n in (notif_list or []):
                if isinstance(n, dict) and "row_data" in n and isinstance(n["row_data"], dict):
                    collaborateur_data = n["row_data"]
                    break

        # Build a safe list of collaborator details
        details_block = (
            chr(10).join(get_collaborateur_details(collaborateur_data))
            if collaborateur_data
            else "Aucune information disponible"
        )

        # Prepare notifications summary text
        notifications_text = []
        for n in (notif_list or []):
            if not isinstance(n, dict):
                continue
            urgency_flag = "🚨 URGENT" if n.get("days_until", 999) <= 4 else ""
            notifications_text.append(
                f"- {urgency_flag} {n.get('field', 'Type inconnu')} prévu pour le {n.get('due_date', 'Date inconnue')} : {n.get('message', '')}"
            )

        # Subject prefix
        subject_prefix = "URGENT - RAPPEL" if is_urgent else "Rappel"
        subject = f"{subject_prefix} - {collaborateur_data.get('nom', 'N/A')} {collaborateur_data.get('prenom', '')}".strip()

        # Collaborator info block for email body
        if collaborateur_data:
            cdata = collaborateur_data
            collaborateur_info = [
f"""
╔══════════════════════════════════════════════╗
║     INFORMATIONS DU COLLABORATEUR            ║
╠══════════════════════════════════════════════╣
║ Nom: {cdata.get('nom', 'N/A'):<37} ║
║ Prénom: {cdata.get('prenom', 'N/A'):<34} ║
╚══════════════════════════════════════════════╝
{details_block}"""
            ]
        else:
            collaborateur_info = ["Informations du collaborateur non disponibles"]

        # Generate body
        if is_urgent:
            body = f"""🚨🚨🚨 ALERTE URGENTE 🚨🚨🚨

Bonjour,

⚠️ ACTION IMMÉDIATE REQUISE ⚠️

{chr(10).join(collaborateur_info)}

🔴 NOTIFICATIONS URGENTES :
{chr(10).join(notifications_text)}

🚫 ACTION REQUISE IMMÉDIATEMENT :
- PRENDRE CONTACT AVEC LE COLLABORATEUR CONCERNÉ
- PLANIFIER LA FORMATION OU LE RENDEZ-VOUS NÉCESSAIRE
- CONFIRMER LA PLANIFICATION PAR RETOUR DE MAIL

⚖️ RISQUES LÉGAUX ET DE SÉCURITÉ :
- Non-conformité avec les obligations légales
- Risques pour la sécurité du collaborateur et de l'entreprise

Merci de confirmer la réception et la planification par retour de mail.

URGENT - Agent Artificiel de Surveillance"""
        else:
            body = f"""Bonjour,

{chr(10).join(collaborateur_info)}

Notifications :
{chr(10).join(notifications_text)}

Merci de planifier les actions nécessaires.

Cordialement,

Agent Artificiel de Surveillance"""

        return subject, body

    except Exception as e:
        logging.error(f"Error generating email content: {str(e)}")
        raise
