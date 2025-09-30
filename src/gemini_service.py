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
    """Generate email content using Gemini AI"""
    try:
        # Create a detailed prompt for Gemini in French
        # Check if any inspection is urgent (0-4 days)
        urgent_inspections = [
            n
            for n in notifications
            if isinstance(notifications, list) and n.get("days_until", 999) <= 4
        ]
        is_urgent = len(urgent_inspections) > 0

        prompt = f"""
        Tu es une intelligence artificielle qui rédige des mails en français. Tu es spécialisée dans la gestion de la maintenance des véhicules pour l'entreprise Bourgeois Travaux Publics, une PME familiale fondée en 1929 et située à Saint-Denis.
        Cette entreprise, dirigée par les fils Frédéric et Nicolas GERNEZ, compte 57 salariés et intervient dans des domaines tels que le terrassement, l'assainissement, la voirie, le pavage, le revêtement et le dallage.

        Ta mission est d'envoyer des e-mails de rappel au responsable RH ou au destinataire concerné pour informer des dates imminentes de validité d'habilitations des collaborateurs.

        Informations détaillées du Collaborateur :
        {chr(10).join(get_collaborateur_details(notifications[0]['row_data'])) if isinstance(notifications, list) and notifications and 'row_data' in notifications[0] else 'Aucune information disponible'}
        
        Notifications et Dates Limites :
        {chr(10).join([f"- {n.get('field', 'Type inconnu')} prévu pour le {n.get('due_date', 'Date inconnue')} : {n.get('message', '')}" for n in notifications]) if isinstance(notifications, list) else str(notifications)}

        Structure de l'email à générer :

        Commence par saluer le mécanicien par son prénom (Chantal)
        Dans le mail tu fourniras le maximum d'informations pertinentes sur le collaborateur et l'habilitation concernée (type d'habilitation, date de validité, commentaires).
        L'objectif est d'informer clairement le responsable des actions à mener.
        Tu mettras en valeur les informations importantes concernant l'habilitation.
        Tu mettras en encadrement les informations suivantes : type d'habilitation, date de validité, observations et commentaires. Tu peux ajouter d'autres informations si nécessaire.
        Prends en compte la partie commentaire qui peut donner un contexte utile pour prioriser les actions.
        
        **IMPORTANT: Si la date est dans un intervalle de 0 à 4 jours tu changes la structure de l'email et tu demandes une action immédiate. Dans ce cas, tu dois:**
        - Utiliser un ton URGENT dans tout l'email
        - Demander explicitement la suspension des activités nécessitant l'habilitation concernée
        - Expliquer les risques légaux et de sécurité liés à l'absence de validité
        - Demander une confirmation rapide des mesures prises
        
        En suite tu termines par une formule de politesse appropriée et tu signes "Agent artificiel chargé des habilitations - Bourgeois Travaux Publics".
        
        Status actuel: {'URGENT - Immobilisation requise' if is_urgent else 'Rappel standard'}
        """
        # 1. Objet de l'email :
        # - Inclure le nom du collaborateur et la date de validité d'habilitations

        # 2. Corps de l'email :

        # # - Saluer le destinataire par son prénom (Chantal)
        # # - Rappeler le nom du collaborateur concerné
        # # - Inclure toutes les informations détaillées du collaborateur et de l'habilitation
        # # - Préciser la date limite de validité de l'habilitation
        # # - Souligner l'importance de prendre les mesures nécessaires avant cette date
        # # - Si des commentaires pertinents sont présents, inclure une section dédiée qui met en évidence ces points d'attention pour l'habilitation
        # # - Suggérer les actions nécessaires (formation, renouvellement, rendez-vous)
        # # - Proposer une assistance pour toute information supplémentaire
        # # - Conclure par une formule de politesse appropriée

        # Formatez la réponse comme suit : OBJET|||CORPS

        # Call Gemini API (placeholder)
        # In a real implementation, you would make an API call here
        # For now, we'll use a fallback format

        # Fallback content
        collaborateur_data = (
            notifications[0]["row_data"]
            if isinstance(notifications, list)
            and notifications
            and "row_data" in notifications[0]
            else {}
        )
        identifier = get_vehicle_identifier(collaborateur_data)

        # Check if urgent for subject line
        subject_prefix = (
            "URGENT - RAPPEL" if is_urgent else "Rappel"
        )
        subject = f"{subject_prefix} - {collaborateur_data.get('nom')} {collaborateur_data.get('prenom')}"

        collaborateur_info = []
        notifications_text = []

        if isinstance(notifications, list) and notifications:
            # Get vehicle info only once (from the first notification)
            cdata = (
                notifications[0]["row_data"]
                if "row_data" in notifications[0]
                else {}
            )
            collaborateur_info.append(
                f"""
╔══════════════════════════════════════════════╗
║     INFORMATIONS DU COLLABORATEUR            ║
╠══════════════════════════════════════════════╣
║ Nom: {cdata.get('nom', 'N/A'):<37} ║
║ Prénom: {cdata.get('prenom', 'N/A'):<34} ║
╚══════════════════════════════════════════════╝
{chr(10).join(get_collaborateur_details(cdata))}"""
            )

            # Process all notifications
            for n in notifications:
                urgency_flag = "🚨 URGENT" if n.get("days_until", 999) <= 4 else ""
                notifications_text.append(
                    f"- {urgency_flag} {n.get('field', 'Type inconnu')} "
                    f"prévu pour le {n['due_date']} : {n['message']}"
                )
        else:
            collaborateur_info = ["Informations du collaborateur non disponibles"]
            notifications_text = [str(notifications)]

        # Generate appropriate body based on urgency
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
