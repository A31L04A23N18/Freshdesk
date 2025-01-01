import openai
import requests
from PyPDF2 import PdfReader
from config.keywords import DIRECT_KEYWORDS, CATEGORIES
import os

# Clé API OpenAI
openai.api_key = ""

def detect_keywords_in_text(text, keywords_dict):
    """
    Détecte les mots-clés dans un texte et retourne la catégorie correspondante.
    """
    for keyword, category in keywords_dict.items():
        if keyword.lower() in text.lower():
            return category
    return None


classification_cache = {}


def download_attachment(attachment_url, auth):
    """
    Télécharge un fichier attaché depuis Freshdesk.
    """
    response = requests.get(attachment_url, auth=auth)
    if response.status_code == 200:
        filename = attachment_url.split("/")[-1]
        with open(filename, "wb") as f:
            f.write(response.content)
        return filename
    else:
        print(f"Erreur lors du téléchargement de l'attachement : {response.status_code}")
        return None

def get_ticket_conversations(ticket_id, domain, auth):
    """
    Récupère les conversations ou notes associées à un ticket depuis Freshdesk.
    """
    url = f"https://{domain}.freshdesk.com/api/v2/tickets/{ticket_id}/conversations"
    response = requests.get(url, auth=auth)
    if response.status_code == 200:
        return response.json()  # Liste des conversations
    else:
        print(f"Erreur lors de la récupération des conversations pour le ticket {ticket_id} : {response.status_code}")
        return []

def extract_text_from_pdf(file_path):
    """
    Extrait le texte utile de la première page d'un fichier PDF.
    """
    try:
        reader = PdfReader(file_path)
        first_page = reader.pages[0]
        text = first_page.extract_text()

        # Nettoyage du texte
        lines = text.splitlines()
        useful_lines = [
            line for line in lines if not any(
                ignore in line.lower() for ignore in ["cgv", "adresse", "contact", "téléphone"]
            )
        ]
        return " ".join(useful_lines)
    except Exception as e:
        print(f"Erreur lors de l'extraction du texte PDF : {e}")
        return None


def classify_with_keywords(title, description):
    """
    Vérifie les mots-clés dans le titre et la description.
    """
    text = f"{title} {description}".lower()
    for keyword, category in DIRECT_KEYWORDS.items():
        if keyword in text:
            return category
    return None

def classify_ticket_openai(title, content, attachment_text=None, max_length=500):
    """
    Utilise GPT pour classifier un ticket avec une limitation de longueur de texte.
    """

    combined_text = f"{title} {content} {attachment_text or ''}"
    if len(combined_text) > max_length:
        combined_text = combined_text[:max_length] + "..."

    # Préparer le prompt
    prompt = f"""
    Vous êtes un assistant chargé de classifier les tickets d'un service client. Voici un ticket à classifier :

    Titre : {title}
    Contenu : {content}
    Texte extrait de la pièce jointe : {attachment_text[:max_length] if attachment_text else 'Aucune pièce jointe'}

    Les catégories possibles sont : Sinistre, Mécanique, Bris de glace, Entretien / Maintenance, Pneumatique, Cartes essence / Badge télépéage, Commande / Livraison, Pool car, Amende, Offre / Devis, Pub, N/A.

    Répondez uniquement avec :
    - La catégorie la plus probable (exemple : "Sinistre").
    - Un score de confiance en pourcentage (exemple : "Confiance : 85%").
    """
    print("\n=== Prompt envoyé à OpenAI ===")
    print(prompt)
    print("===============================")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Vous êtes un assistant de classification de tickets."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.2
        )

        message_content = response['choices'][0]['message']['content'].strip()
        print(f"Réponse brute : {message_content}")

        # Extraire catégorie et confiance
        lines = message_content.split("\n")
        category, confidence = None, 0

        for line in lines:
            if "Catégorie" in line:
                category = line.split(":")[1].strip()
            if "Confiance" in line:
                try:
                    confidence = int(line.split(":")[1].strip().replace("%", ""))
                except ValueError:
                    confidence = 0

        if category not in CATEGORIES:
            category = "N/A"

        return category, confidence

    except Exception as e:
        print(f"Erreur lors de la classification OpenAI : {e}")
        return "N/A", 0





