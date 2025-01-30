# Scraper Books to Scrape 📚

Salut ! Ce script permet de récupérer toutes les infos des bouquins du site Books to Scrape. C'est un projet pour Books Online qui nous aide à suivre les prix de la concurrence.

## Comment ça marche ? 🤔

Le script est découpé en plusieurs fonctions qui font chacune leur petit boulot :

### 1. `recup_page(url)`
C'est la fonction qui va chercher les pages web. Il utilise requests pour récupérer la page et BeautifulSoup pour la rendre utilisable.

### 2. `nettoie_texte(texte)` et `compte_stock(texte)`
Les petites mains qui nettoient les données :
- `nettoie_texte` vire les caractères chelous (£, Â, etc.)
- `compte_stock` extrait juste le nombre de livres disponibles

### 3. `recup_infos_livre(url_livre)`
Le pro qui récupère toutes les infos d'un bouquin :
- Titre
- Prix (TTC et HT)
- Disponibilité
- Description
- Catégorie
- Note
- Image de couverture

### 4. `recup_categorie(url_categorie, nom_categorie)`
Le chef d'équipe qui :
- Parcourt toutes les pages d'une catégorie
- Récupère les infos de chaque livre
- Crée un fichier CSV avec toutes les données
- Télécharge les images

### 5. `lance_lescraper()`
Le grand patron qui :
- Récupère la liste de toutes les catégories
- Lance le boulot pour chaque catégorie




## Les modules utilisés 🔧

### Modules standards Python
- `urllib.parse` : Permet de gérer proprement les URLs
  - `urljoin` : Combine les URLs de base avec les URLs relatives 
  - Exemple : `urljoin("http://site.com/", "images/photo.jpg")` donne `"http://site.com/images/photo.jpg"`

- `re` (Regular Expressions) : Pour chercher des patterns dans le texte
  - Utilisé ici pour extraire les nombres du texte de disponibilité
  - Exemple : `"In stock (5 available)"` → extrait `"5"`

### Modules externes
- `requests` : Pour faire les requêtes HTTP vers le site
  - Plus simple que urllib.request
  - Gère automatiquement les headers, cookies, etc.

- `beautifulsoup4` : Pour parser le HTML facilement
  - Permet de naviguer dans la page comme dans un arbre
  - Trouve les éléments avec des sélecteurs CSS (comme `.select()`)

### Modules utilitaires
- `csv` : Pour créer les fichiers CSV
- `os` : Pour gérer les dossiers et fichiers
- `time` : Pour les pauses entre les requêtes

