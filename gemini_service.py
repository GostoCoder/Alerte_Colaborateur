import google.generativeai as genai
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

def get_vehicle_identifier(vehicle_data):
    """Get the vehicle identifier (license plate or serial number)"""
    if 'license_plate' in vehicle_data:
        return vehicle_data['license_plate']
    elif 'serial_number' in vehicle_data:
        return vehicle_data['serial_number']
    return 'Véhicule Inconnu'

def get_vehicle_details(vdata):
    """Get vehicle details based on available fields"""
    details = []
    
    # Basic info
    details.append(f"- Marque/Modèle: {vdata.get('brand', 'N/A')} {vdata.get('commercial_type', 'N/A')}")
    details.append(f"- Type: {vdata.get('vehicle_type', 'N/A')}")
    details.append(f"- Groupe: {vdata.get('group_number', 'N/A')}")
    
    # Technical details - database 4
    if 'engine_type' in vdata:
        details.extend([
            f"- Type de moteur: {vdata.get('engine_type', 'N/A')}",
            f"- Puissance: {vdata.get('power', 'N/A')}",
            f"- Poids: {vdata.get('weight', 'N/A')}",
            f"- Heures: {vdata.get('hours', 'N/A')}"
        ])
    
    # Technical details - database 2 & 3
    if 'payload' in vdata:
        details.extend([
            f"- Charge utile: {vdata.get('payload', 'N/A')}",
            f"- PTAC: {vdata.get('gvw', 'N/A')}",
            f"- PTRA: {vdata.get('mam', 'N/A')}"
        ])
    
    # Common fields
    details.extend([
        f"- Carrosserie: {vdata.get('body_type', 'N/A')}",
        f"- Travaille avec: {vdata.get('work_with', 'Non spécifié')}",
        f"- Kilométrage: {vdata.get('kilometers', 'N/A')}",
        f"- Commentaires: {vdata.get('comments', 'Aucun commentaire')}"
    ])
    
    return details

def generate_email_content(vehicle, notifications):
    """Generate email content using Gemini AI"""
    try:
        # Create a detailed prompt for Gemini in French
        # Check if any inspection is urgent (0-4 days)
        urgent_inspections = [n for n in notifications if isinstance(notifications, list) and n.get('days_until', 999) <= 4]
        is_urgent = len(urgent_inspections) > 0
        
        prompt = f"""
        Tu es une intelligence artificielle qui rédige des mails en français. Tu es spécialisée dans la gestion de la maintenance des véhicules pour l'entreprise Bourgeois Travaux Publics, une PME familiale fondée en 1929 et située à Saint-Denis.
        Cette entreprise, dirigée par les fils Frédéric et Nicolas GERNEZ, compte 57 salariés et intervient dans des domaines tels que le terrassement, l'assainissement, la voirie, le pavage, le revêtement et le dallage.

        Ta mission est d'envoyer des e-mails de rappel au mécanicien responsable de l'entretien des véhicules de l'entreprise, afin de l'informer des dates imminentes de contrôle technique pour chaque véhicule.

        Informations détaillées du Véhicule :
        {chr(10).join(get_vehicle_details(notifications[0]['vehicle_data'])) if isinstance(notifications, list) and notifications else 'Aucune information disponible'}
        
        Notifications et Dates Limites :
        {chr(10).join([f"- {n['type']} pour {get_vehicle_identifier(n['vehicle_data'])} prévu pour le {n['due_date']} : {n['message']}" for n in notifications]) if isinstance(notifications, list) else str(notifications)}

        Structure de l'email à générer :

        Commence par saluer le mécanicien par son prénom (José)
        Dans le mail tu vas donnée le maximum d'information possible sur le véhicule qui est sujet au controle technique. 
        Le but des détails donnés sur le véhicules sera de bien informer le mécanicien responsable de l'entretien.
        Tu feras des encadonnements pour bien mettre en valeur les informations concernant le véhicule.
        Tu mettras en en encadrement les informations suivantes : type du véhicule, marque, modèle. Tu peux rajouter d'autres informations si c'est nécessaire.
        Tu prendras en compte la partie commentaire qui est trés importainte pour te donner un regard critique sur le mail que tu envoies, la paartie commentaire peut aussi te donner un contexte sur le véhicule en question.
        
        **IMPORTANT: Si la date est dans un intervalle de 0 à 4 jours tu change la structure de l'email et tu demandes d'immobiliser le véhicule tout de suite. Dans ce cas, tu dois:**
        - Mettre un ton URGENT dans tout l'email
        - Demander explicitement l'immobilisation immédiate du véhicule 
        - Expliquer que le véhicule ne doit plus circuler jusqu'au contrôle technique
        - Préciser les risques légaux et de sécurité
        - Demander une confirmation rapide de l'immobilisation
        
        En suite tu termines par une formule de politesse appropriée. et tu signes "Agent artificielle chargé des véhiles Bourgeois Travaux Publics".
        
        Status actuel: {'URGENT - Immobilisation requise' if is_urgent else 'Rappel standard'}
        """
        #1. Objet de l'email :
        # - Inclure l'identifiant du véhicule et la date du prochain contrôle technique

        # 2. Corps de l'email :

        # # - Saluer le mécanicien par son prénom (José)
        # # - Rappeler l'identifiant du véhicule concerné
        # # - Inclure toutes les informations détaillées du véhicule
        # # - Préciser la date limite du prochain contrôle technique
        # # - Souligner l'importance de réaliser le contrôle avant cette date
        # # - Si des commentaires sur l'état du véhicule sont présents, inclure une section dédiée qui met en évidence ces points d'attention pour le contrôle technique
        # # - Suggérer de planifier un rendez-vous au centre de contrôle technique agréé
        # # - Proposer une assistance pour toute information supplémentaire
        # # - Conclure par une formule de politesse appropriée

        # Formatez la réponse comme suit : OBJET|||CORPS



        # Call Gemini API (placeholder)
        # In a real implementation, you would make an API call here
        # For now, we'll use a fallback format
        
        # Fallback content
        vehicle_data = notifications[0]['vehicle_data'] if isinstance(notifications, list) and notifications else {}
        identifier = get_vehicle_identifier(vehicle_data)
        
        # Check if urgent for subject line
        subject_prefix = "🚨 URGENT - IMMOBILISATION REQUISE" if is_urgent else "Rappel d'Inspection"
        subject = f"{subject_prefix} - {identifier}"
        
        vehicle_info = []
        notifications_text = []
        
        if isinstance(notifications, list) and notifications:
            # Get vehicle info only once (from the first notification)
            vdata = notifications[0]['vehicle_data']
            vehicle_info.append(f"""
╔══════════════════════════════════════════════╗
║         INFORMATIONS DU VÉHICULE             ║
╠══════════════════════════════════════════════╣
║ Identifiant: {get_vehicle_identifier(vdata):<29} ║
║ Type: {vdata.get('vehicle_type', 'N/A'):<36} ║
║ Marque: {vdata.get('brand', 'N/A'):<34} ║
║ Modèle: {vdata.get('commercial_type', 'N/A'):<34} ║
╚══════════════════════════════════════════════╝
{chr(10).join(get_vehicle_details(vdata))}""")
            
            # Process all notifications
            for n in notifications:
                urgency_flag = "🚨 URGENT" if n.get('days_until', 999) <= 4 else ""
                notifications_text.append(f"- {urgency_flag} {n['type']} prévu pour le {n['due_date']} : {n['message']}")
        else:
            vehicle_info = ["Informations du véhicule non disponibles"]
            notifications_text = [str(notifications)]

        # Generate appropriate body based on urgency
        if is_urgent:
            body = f"""🚨🚨🚨 ALERTE URGENTE 🚨🚨🚨

Bonjour José,

⚠️ IMMOBILISATION IMMÉDIATE REQUISE ⚠️

{chr(10).join(vehicle_info)}

🔴 NOTIFICATIONS D'INSPECTION URGENTES :
{chr(10).join(notifications_text)}

🚫 ACTION REQUISE IMMÉDIATEMENT :
- IMMOBILISER LE VÉHICULE TOUT DE SUITE
- LE VÉHICULE NE DOIT PLUS CIRCULER
- PROGRAMMER LE CONTRÔLE TECHNIQUE EN URGENCE
- CONFIRMER L'IMMOBILISATION PAR RETOUR DE MAIL

⚖️ RISQUES LÉGAUX ET DE SÉCURITÉ :
- Circulation avec un contrôle technique expiré = INFRACTION
- Risques d'accident et de responsabilité
- Sanctions possibles de l'inspection du travail

Merci de confirmer la réception et l'immobilisation par retour de mail.

URGENT - Agent artificielle chargé des véhicules Bourgeois Travaux Publics"""
        else:
            body = f"""Bonjour José,

{chr(10).join(vehicle_info)}

Notifications d'inspection :
{chr(10).join(notifications_text)}

Merci de planifier les contrôles techniques nécessaires.

Cordialement,

Agent artificielle chargé des véhicules Bourgeois Travaux Publics"""
        
        return subject, body
        
    except Exception as e:
        logging.error(f"Error generating email content: {str(e)}")
        raise
