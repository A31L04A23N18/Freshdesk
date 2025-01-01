import requests
from PyPDF2 import PdfReader

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
