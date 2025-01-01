import requests

def get_tickets(domain, auth):
    """
    Récupère tous les tickets ouverts/non fermés depuis Freshdesk.
    """
    url = f"https://{domain}.freshdesk.com/api/v2/tickets"
    response = requests.get(url, auth=auth)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erreur {response.status_code} - {response.text}")
        return []

def update_ticket_field(domain, auth, ticket_id, field_name, value):
    """
    Met à jour un champ personnalisé d'un ticket.
    """
    url = f"https://{domain}.freshdesk.com/api/v2/tickets/{ticket_id}"
    payload = {"custom_fields": {field_name: value}}
    response = requests.put(url, json=payload, auth=auth)

    # Affichage des détails de la réponse pour débogage
    print(f"Code de réponse : {response.status_code}")
    print(f"Contenu de la réponse : {response.text}")

    if response.status_code == 200:
        print(f"Ticket {ticket_id} mis à jour avec succès.")
        return True
    else:
        print(f"Erreur lors de la mise à jour : {response.status_code} - {response.text}")
        return False


def get_ticket_conversations(domain, auth, ticket_id):
    """
    Récupère toutes les conversations associées à un ticket.
    Utile pour rechercher les immatriculations dans les tickets fusionnés.
    """
    url = f"https://{domain}.freshdesk.com/api/v2/tickets/{ticket_id}/conversations"
    response = requests.get(url, auth=auth)
    if response.status_code == 200:
        return response.json()  # Liste des conversations
    else:
        print(f"Erreur {response.status_code} - {response.text}")
        return []