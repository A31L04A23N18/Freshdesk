from requests.auth import HTTPBasicAuth

DOMAIN = "keyence-help"  # Domaine Freshdesk
API_KEY = "Ff9vceA9znJlDlgmv2Ju"  # Clé API Freshdesk
AUTH = HTTPBasicAuth(API_KEY, "X")  # Authentification pour les requêtes API
