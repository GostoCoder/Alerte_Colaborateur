import openai
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")


def get_collaborateur_summary(row):
    """Return a short summary string for a collaborator row_data dict"""
    if not isinstance(row, dict):
        return "Nom: N/A  Prénom: N/A  Commentaires: Aucun commentaire"
    nom = row.get("nom", "N/A")
    prenom = row.get("prenom", "N/A")
    commentaire = row.get("commentaire", "Aucun commentaire")
    return f"Nom: {nom}  Prénom: {prenom}  Commentaires: {commentaire}"


def get_collaborateur_details(row):
    """Get collaborateur details from a row_data dict"""
    details = []
    if not isinstance(row, dict):
        return details
    details.append(f"- Nom: {row.get('nom', 'N/A')}")
    details.append(f"- Prénom: {row.get('prenom', 'N/A')}")
    if row.get("habilitations"):
        details.append(f"- Habilitations: {row.get('habilitations')}")
    if row.get("commentaire"):
        details.append(f"- Commentaire: {row.get('commentaire')}")
    return details


def generate_email_content(vehicle, notifications):
    """Generate email content using ChatGPT"""
    try:
        # Create a detailed prompt for ChatGPT in French
        prompt = f"""
        Tu es une intelligence artificielle qui rédige des mails en français.
        Tu es spécialisée dans la gestion des habilitations du personnel pour
        l'entreprise Bourgeois Travaux Publics, une PME familiale fondée en 1929
        et située à Saint-Denis. Cette entreprise, dirigée par les fils
        Frédéric et Nicolas GERNEZ, compte 57 salariés.

        Ta mission est d'envoyer des e-mails de rappel au responsable RH ou au
        destinataire concerné (Commence par saluer Chantal) pour informer des
        dates imminentes de validité d'habilitations des collaborateurs.

        Informations détaillées du Collaborateur :
        {chr(10).join([
            f"- Nom: {n.get('row_data', {}).get('nom','N/A')}  Prénom: {n.get('row_data', {}).get('prenom','N/A')}  |  Habilitation: {n.get('field','Habilitation')}  |  Validité: {n.get('due_date','Date inconnue')}"
            for n in notifications
        ]) if isinstance(notifications, list) else str(notifications)}
        
        Notifications et Dates Limites :
        {chr(10).join([
            f"- {n.get('field','Type inconnu')} pour {n.get('row_data', {}).get('nom','N/A')} {n.get('row_data', {}).get('prenom','N/A')} prévu pour le {n.get('due_date','Date inconnue')} : {n.get('message','')}"
            for n in notifications
        ]) if isinstance(notifications, list) else str(notifications)}
        """

        # Call OpenAI API
        response = openai.chat.completions.create(
            model="gpt-4",  # or "gpt-3.5-turbo" depending on your needs
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI assistant specialized in writing "
                    "professional emails in French for personnel habilitations management.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=1000,
        )

        # Extract the generated content
        email_content = response.choices[0].message.content
        return email_content

    except Exception as e:
        logging.error(f"Error generating email content with ChatGPT: {str(e)}")
        return f"Erreur lors de la génération du contenu de l'email: {str(e)}"
