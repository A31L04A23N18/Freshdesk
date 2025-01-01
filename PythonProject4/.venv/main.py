from config.settings import DOMAIN, AUTH
from utils.freshdesk_api import get_tickets
from modules import creation_cartes, opposition_cartes, suivi_livraisons, gestion_sinistres
from utils.ai import classify_ticket_openai
from utils.file_utils import download_attachment, extract_text_from_pdf
from config.keywords import DIRECT_KEYWORDS, MODULES
import os,requests

def detect_keywords_in_text(text, keywords_dict):
    """
    Détecte les mots-clés dans un texte et retourne la catégorie correspondante.
    """
    for keyword, category in keywords_dict.items():
        if keyword.lower() in text.lower():
            return category
    return None


def get_ticket_conversations(ticket_id, domain, auth):
    """
    Récupère les conversations ou notes associées à un ticket depuis Freshdesk.
    """
    url = f"https://{domain}.freshdesk.com/api/v2/tickets/{ticket_id}?include=description_text"
    response = requests.get(url, auth=auth)

    if response.status_code == 200:
        ticket_data = response.json()
        description_text = ticket_data.get("description_text", "Description_text non disponible")
        description = ticket_data.get("description", "Description non disponible")

        if not description_text:
            print(f"Ticket ID {ticket_id} : aucune description_text trouvée (réponse vide).")
        if not description:
            print(f"Ticket ID {ticket_id} : aucune description trouvée (réponse vide).")
        return description_text, description  # Retourne les conversations
    else:
        print(f"Erreur lors de la récupération des conversations pour le ticket {ticket_id} : {response.status_code}")
        print(f"Contenu de la réponse : {response.text}")
        return []



def process_ticket(ticket, auth, domain, max_characters=500):
    """
    Traite un ticket en vérifiant les mots-clés et appelant OpenAI si nécessaire.
    """

    # Ignorer les tickets résolus ou fermés
    if ticket.get("status") in ["resolved", "closed"]:
        print(f"Ticket ID {ticket['id']} - Ignoré (statut fermé).")
        return

    # Récupération des conversations
    conversations = get_ticket_conversations(ticket["id"], domain, auth)
    content = " ".join(conv.get("body_text", "") for conv in conversations if "body_text" in conv) if conversations else None

    ticket_id = ticket["id"]

    # Récupération de la description
    description_text = get_ticket_conversations(ticket_id, domain, auth)

    # Debug : Affichez la description récupérée
    print(f"Ticket ID {ticket_id} - Description finale : {description_text}")

    # Priorité à description_text, fallback sur conversations
    description_text = ticket.get("description_text") or content or "Description non disponible"
    print(f"Ticket ID {ticket['id']} - Description : {description_text}")

    # Analyse des pièces jointes
    attachment_text = None
    if ticket.get("attachments"):
        for attachment in ticket["attachments"]:
            if attachment["content_type"] == "application/pdf":
                file_path = download_attachment(attachment["attachment_url"], auth)
                if file_path:
                    attachment_text = extract_text_from_pdf(file_path)
                    break

    # Vérification des mots-clés
    combined_text = f"{description_text} {attachment_text or ''}"
    direct_category = detect_keywords_in_text(combined_text, DIRECT_KEYWORDS)
    if direct_category:
        print(f"Ticket ID {ticket['id']} - Catégorie détectée par mots-clés : {direct_category}")
        ticket["type"] = direct_category
        return

    # Appel à OpenAI
    ticket_type, confidence = classify_ticket_openai(
        title=ticket.get("subject", "Sujet non spécifié"),
        content=combined_text,
        attachment_text=attachment_text
    )

    if confidence >= 80:
        print(f"Ticket ID {ticket['id']} - Catégorie validée : {ticket_type} (Confiance : {confidence}%)")
        ticket["type"] = ticket_type
    else:
        print(f"Ticket ID {ticket['id']} - Confiance trop faible ({confidence}%). Attribution de 'N/A'.")
        ticket["type"] = "N/A"



def main():
    """
    Fonction principale : récupère et traite les tickets.
    """
    print("Récupération des tickets...")
    tickets = get_tickets(DOMAIN, AUTH)  # Récupère les tickets via l'API

    for ticket in tickets:
        print(f"Traitement du ticket ID {ticket['id']}...")
        # Ajout de DOMAIN comme argument
        process_ticket(ticket, AUTH, DOMAIN)

if __name__ == "__main__":
        main()
