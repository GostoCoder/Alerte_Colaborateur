import google.generativeai as genai
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

def get_collaborateur_identifier(collaborateur_data):
    """Get the collaborateur identifier (nom + prenom)"""
    if isinstance(collaborateur_data, dict):
        # From notification dict
        if 'license_plate' in collaborateur_data:
            return collaborateur_data['license_plate']
        nom = collaborateur_data.get('nom', '')
        prenom = collaborateur_data.get('prenom', '')
        return f"{nom} {prenom}".strip() or "Collaborateur Inconnu"
    # SQLAlchemy object
    nom = getattr(collaborateur_data, 'nom', '')
    prenom = getattr(collaborateur_data, 'prenom', '')
    return f"{nom} {prenom}".strip() or "Collaborateur Inconnu"

def get_collaborateur_details(cdata):
    """Get collaborateur details based on available fields"""
    details = []
    # Support dict or SQLAlchemy object
    get = lambda k, default=None: cdata.get(k, default) if isinstance(cdata, dict) else getattr(cdata, k, default)
    details.append(f"- Nom: {get('nom', 'N/A')}")
    details.append(f"- Prénom: {get('prenom', 'N/A')}")
    # Add certifications/validations if present
    for field, label in [
        ('fimo', 'FIMO'),
        ('caces', 'CACES'),
        ('aipr', 'AIPR'),
        ('hg0b0', 'H0B0'),
        ('visite_med', 'Visite médicale'),
        ('brevet_secour', 'Brevet secouriste'),
        ('date_renouvellement', 'Date de renouvellement'),
        ('date_validite', 'Date de validité')
    ]:
        val = get(field)
        if val:
            details.append(f"- {label}: {val}")
    commentaire = get('commentaire', None)
    details.append(f"- Commentaires: {commentaire if commentaire else 'Aucun commentaire'}")
    return details

def generate_email_content(collaborateur, notifications):
    """Generate email content using Gemini AI for collaborateur"""
    try:
        # Check if any notification is urgent (0-4 days)
        urgent_notifications = [n for n in notifications if isinstance(notifications, list) and n.get('days_until', 999) <= 4]
        is_urgent = len(urgent_notifications) > 0

        # Compose prompt (French, collaborateur-centric)
        prompt = f"""
        Tu es une intelligence artificielle qui rédige des mails en français. Tu es spécialisée dans la gestion des certifications et renouvellements des collaborateurs pour l'entreprise Bourgeois Travaux Publics, une PME familiale fondée en 1929 et située à Saint-Denis.
        Cette entreprise, dirigée par les fils Frédéric et Nicolas GERNEZ, compte des salariés et intervient dans des domaines tels que le terrassement, l'assainissement, la voirie, le pavage, le revêtement et le dallage.

        Ta mission est d'envoyer des e-mails de rappel au responsable RH ou a la direction, afin de l'informer des dates imminentes de renouvellement ou de validité de ses certifications ou visites médicales.

        Informations détaillées du Collaborateur :
        {chr(10).join(get_collaborateur_details(notifications[0]['vehicle_data'] if isinstance(notifications, list) and notifications and 'vehicle_data' in notifications[0] else collaborateur)) if notifications else 'Aucune information disponible'}

        Notifications et Dates Limites :
        {chr(10).join([f"- {n['type']} pour {get_collaborateur_identifier(n.get('vehicle_data', collaborateur))} prévu pour le {n['due_date']} : {n['message']}" for n in notifications]) if isinstance(notifications, list) else str(notifications)}

        Structure de l'email à générer :

        Commence par saluer Chantal qui est l'assistante de direction.
        Donne le maximum d'information possible sur le collaborateur et ses certifications/validations à renouveler.
        Mets en valeur les informations importantes (nom, prénom, type de certification, date limite).
        Prends en compte la partie commentaire qui peut donner un contexte sur la situation du collaborateur.

        **IMPORTANT: Si la date est dans un intervalle de 0 à 4 jours tu changes la structure de l'email et demandes de ne pas laisser le collaborateur exercer sans renouvellement. Dans ce cas, tu dois:**
        - Mettre un ton URGENT dans tout l'email
        - Demander explicitement de suspendre l'activité du collaborateur jusqu'au renouvellement
        - Expliquer les risques légaux et de sécurité
        - Demander une confirmation rapide de la suspension

        Termine par une formule de politesse appropriée et signe "Agent artificielle chargé des collaborateurs Bourgeois Travaux Publics".

        Status actuel: {'URGENT - Suspension requise' if is_urgent else 'Rappel standard'}
        """

        # Fallback content (local formatting)
        cdata = notifications[0]['vehicle_data'] if isinstance(notifications, list) and notifications and 'vehicle_data' in notifications[0] else collaborateur
        identifier = get_collaborateur_identifier(cdata)
        subject_prefix = "🚨 URGENT - SUSPENSION REQUISE" if is_urgent else "Rappel de Certification"
        subject = f"{subject_prefix} - {identifier}"

        collaborateur_info = []
        notifications_text = []

        if isinstance(notifications, list) and notifications:
            collaborateur_info.append(f"""
╔══════════════════════════════════════════════╗
║      INFORMATIONS DU COLLABORATEUR           ║
╠══════════════════════════════════════════════╣
║ Identifiant: {get_collaborateur_identifier(cdata):<29} ║
║ Nom: {getattr(cdata, 'nom', cdata.get('nom', 'N/A')):<34} ║
║ Prénom: {getattr(cdata, 'prenom', cdata.get('prenom', 'N/A')):<34} ║
╚══════════════════════════════════════════════╝
{chr(10).join(get_collaborateur_details(cdata))}""")
            for n in notifications:
                urgency_flag = "🚨 URGENT" if n.get('days_until', 999) <= 4 else ""
                notifications_text.append(f"- {urgency_flag} {n['type']} prévu pour le {n['due_date']} : {n['message']}")
        else:
            collaborateur_info = ["Informations du collaborateur non disponibles"]
            notifications_text = [str(notifications)]

        # Generate appropriate body based on urgency
        if is_urgent:
            body = f"""🚨🚨🚨 ALERTE URGENTE 🚨🚨🚨

Bonjour {getattr(cdata, 'prenom', cdata.get('prenom', ''))},

⚠️ SUSPENSION IMMÉDIATE REQUISE ⚠️

{chr(10).join(collaborateur_info)}

🔴 NOTIFICATIONS DE CERTIFICATION URGENTES :
{chr(10).join(notifications_text)}

🚫 ACTION REQUISE IMMÉDIATEMENT :
- SUSPENDRE L'ACTIVITÉ DU COLLABORATEUR TOUT DE SUITE
- NE PAS LAISSER EXERCER SANS RENOUVELLEMENT
- PROGRAMMER LE RENOUVELLEMENT EN URGENCE
- CONFIRMER LA SUSPENSION PAR RETOUR DE MAIL

⚖️ RISQUES LÉGAUX ET DE SÉCURITÉ :
- Exercice sans certification valide = INFRACTION
- Risques d'accident et de responsabilité
- Sanctions possibles de l'inspection du travail

Merci de confirmer la réception et la suspension par retour de mail.

URGENT - Agent artificielle chargé des collaborateurs Bourgeois Travaux Publics"""
        else:
            body = f"""Bonjour {getattr(cdata, 'prenom', cdata.get('prenom', ''))},

{chr(10).join(collaborateur_info)}

Notifications de certification :
{chr(10).join(notifications_text)}

Merci de planifier les renouvellements nécessaires.

Cordialement,

Agent artificielle chargé des collaborateurs Bourgeois Travaux Publics"""

        return subject, body

    except Exception as e:
        logging.error(f"Error generating email content: {str(e)}")
        raise
