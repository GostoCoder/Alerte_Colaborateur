import openai
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure OpenAI API
openai.api_key = os.getenv('OPENAI_API_KEY')

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
    """Generate email content using ChatGPT"""
    try:
        # Create a detailed prompt for ChatGPT in French
        prompt = f"""
        Tu es une intelligence artificielle qui rédige des mails en français. Tu es spécialisée dans la gestion de la maintenance des véhicules pour l'entreprise Bourgeois Travaux Publics, une PME familiale fondée en 1929 et située à Saint-Denis.
        Cette entreprise, dirigée par les fils Frédéric et Nicolas GERNEZ, compte 57 salariés et intervient dans des domaines tels que le terrassement, l'assainissement, la voirie, le pavage, le revêtement et le dallage.

        Ta mission est d'envoyer des e-mails de rappel au mécanicien responsable de l'entretien des véhicules de l'entreprise, afin de l'informer des dates imminentes de contrôle technique pour chaque véhicule.

        Informations détaillées du Véhicule :
        {chr(10).join([f"- {get_vehicle_identifier(n['vehicle_data'])} ({n['vehicle_data']['brand']} {n['vehicle_data']['commercial_type']}):" + chr(10) +
                       chr(10).join(f"  * {detail}" for detail in get_vehicle_details(n['vehicle_data']))
                       for n in notifications]) if isinstance(notifications, list) else str(notifications)}
        
        Notifications et Dates Limites :
        {chr(10).join([f"- {n['type']} pour {get_vehicle_identifier(n['vehicle_data'])} prévu pour le {n['due_date']} : {n['message']}" for n in notifications]) if isinstance(notifications, list) else str(notifications)}
        """

        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-4",  # or "gpt-3.5-turbo" depending on your needs
            messages=[
                {"role": "system", "content": "You are an AI assistant specialized in writing professional emails in French for vehicle maintenance management."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )

        # Extract the generated content
        email_content = response.choices[0].message.content
        return email_content

    except Exception as e:
        logging.error(f"Error generating email content with ChatGPT: {str(e)}")
        return f"Erreur lors de la génération du contenu de l'email: {str(e)}"
