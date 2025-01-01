from modules import creation_cartes, opposition_cartes, suivi_livraisons, gestion_sinistres

DIRECT_KEYWORDS = {
    "sinistre": "Sinistre",
    "panne": "Mécanique",
    "bris de glace": "Bris de glace",
    "entretien": "Entretien / Maintenance",
    "pneumatique": "Pneumatique",
    "carte carburant": "Cartes essence / Badge télépéage",
    "livraison": "Commande / Livraison",
    "pool car": "Pool car",
    "amende": "Amende",
    "offre": "Offre / Devis",
    "pub": "Pub",
    "newsletter": "Pub"
}

MODULES = {
    "creation_cartes": creation_cartes,
    "opposition_cartes": opposition_cartes,
    "suivi_livraisons": suivi_livraisons,
    "gestion_sinistres": gestion_sinistres,
}

# Catégorie "Type" de ticket dans Freshdesk
CATEGORIES = [
    "Sinistre",
    "Mécanique",
    "Bris de glace",
    "Entretien / Maintenance",
    "Pneumatique",
    "Cartes essence / Badge télépéage",
    "Commande / Livraison",
    "Pool car",
    "Amende",
    "Offre / Devis",
    "Pub",
    "N/A"
]