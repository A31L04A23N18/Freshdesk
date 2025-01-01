import re
from utils.freshdesk_api import update_ticket_field, get_ticket_conversations

# Regex pour détecter les immatriculations françaises
FRENCH_PLATE_REGEX = r"\b[A-Z]{2}-?\d{3}-?[A-Z]{2}\b"

def extract_last_plate_by_alpha(text):
    """
    Extrait toutes les immatriculations françaises d'un texte donné
    et retourne la dernière par ordre alphabétique.
    """
    plates = re.findall(FRENCH_PLATE_REGEX, text)
    return max(plates) if plates else None

def handle_ticket(ticket, domain, auth):
    """
    Gère les tickets liés à la création de cartes pour les commandes/livraisons.
    """
    print(f"Traitement du ticket ID {ticket['id']} pour création de cartes.")

    # Condition 1 : Vérifier le type du ticket
    if ticket.get("type") != "Commande / Livraison":
        print(f"Ticket ID {ticket['id']} - Type non valide. Ignoré.")
        return

    # Condition 2 : Vérifier le nom du ticket
    if "nouveau véhicule" not in ticket.get("subject", "").lower():
        print(f"Ticket ID {ticket['id']} - Sujet non valide. Ignoré.")
        return

    # Recherche des immatriculations dans le ticket et ses conversations
    description = ticket.get("description_text", "")  # Description principale
    conversations = get_ticket_conversations(domain, auth, ticket["id"])  # Récupération des conversations fusionnées
    all_text = description + " ".join(conv.get("body", "") for conv in conversations)

    last_plate = extract_last_plate_by_alpha(all_text)
    if not last_plate:
        print(f"Ticket ID {ticket['id']} - Aucune immatriculation détectée. Ignoré.")
        return

    print(f"Ticket ID {ticket['id']} - Immatriculation détectée : {last_plate}")

    # Condition 3 : Vérifier si le champ "Cartes Créées" est False
    if ticket.get("custom_fields", {}).get("cf_cartes"):
        print(f"Ticket ID {ticket['id']} - Champ 'Cartes Créées' déjà coché. Ignoré.")
        return

    # Action : Effectuer le traitement de création de cartes
    print(f"Ticket ID {ticket['id']} - Création de cartes en cours pour l'immatriculation {last_plate}...")

    # Action : Mettre à jour le champ "Cartes Créées" à True
    print(f"Ticket ID {ticket['id']} - Mise à jour du champ 'Cartes Créées'.")
    success = update_ticket_field(domain, auth, ticket["id"], "cf_cartes", True)

    if success:
        print(f"Ticket ID {ticket['id']} - Champ 'Cartes Créées' mis à jour avec succès.")
    else:
        print(f"Ticket ID {ticket['id']} - Échec de la mise à jour du champ 'Cartes Créées'.")
