Installation et utilisation du scraper Books to Scrape
---------------------------------------------------

1. Créer l'environnement virtuel :
python -m venv env

2. Activer l'environnement virtuel :
Sur Windows : env\Scripts\activate
Sur Linux/Mac : source env/bin/activate

3. Installer les dépendances :
pip install -r requirements.txt

4. Lancer le script :
python main.py

Le script va créer :
- Un dossier 'data/' avec les fichiers CSV (un par catégorie)
- Un dossier 'images/' avec les images des livres 