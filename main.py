import requests
from bs4 import BeautifulSoup
import csv
import os
from urllib.parse import urljoin
import time
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

#test

#Malheuresement il y'a pas de sitemap.xml donc pas cool sinon ça serait trop facile 

# Verrou pour les écritures dans les fichiers
fichier_lock = Lock()

def recup_page(url):
    """Recupere et parse une page web"""
    try:
        reponse = requests.get(url)
        reponse.raise_for_status()
        return BeautifulSoup(reponse.content, 'html.parser')
    except requests.RequestException as e:
        print(f"Problème avec l'URL {url}: {e}")
        return None

def nettoie_texte(texte):
    """vire les caractères chelous"""
    return texte.strip().replace('£', '').replace('Â', '')

def compte_stock(texte):
    """Recupere le nombre de livres dispo"""
    match = re.search(r'\d+', texte)
    return match.group() if match else "0"

def recup_infos_livre(url_livre):
    """Chope toutes les infos d'un livre"""
    page = recup_page(url_livre)
    if not page:
        return None
        
    try:
        # Les infos de base
        titre = page.select_one('div.product_main h1').text
        infos_produit = {ligne.th.text: ligne.td.text for ligne in page.select('table tr')}
        
        # La description
        bloc_description = page.select_one('#product_description + p')
        description = bloc_description.text if bloc_description else "Pas de description"
        
        # Catégorie et note
        categorie = page.select('ul.breadcrumb li')[2].text.strip()
        notes = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}
        etoiles = page.select_one('p.star-rating')
        note = notes[etoiles['class'][1]] if etoiles else 0
        
        # L'image
        url_base = "http://books.toscrape.com/"
        url_image = urljoin(url_base, page.select_one('div.item.active img')['src'])
        nom_image = f"images/{categorie}/{infos_produit['UPC']}.jpg"
        
        # On crée le dossier si besoin
        with fichier_lock:  # Protection pour la création du dossier
            os.makedirs(f"images/{categorie}", exist_ok=True)
        
        # On télécharge l'image
        reponse_image = requests.get(url_image)
        with fichier_lock:  # Protection pour l'écriture du fichier
            with open(nom_image, 'wb') as f:
                f.write(reponse_image.content)
            
        return {
            'product_page_url': url_livre,
            'universal_product_code': infos_produit['UPC'],
            'title': titre,
            'price_including_tax': nettoie_texte(infos_produit['Price (incl. tax)']),
            'price_excluding_tax': nettoie_texte(infos_produit['Price (excl. tax)']),
            'number_available': compte_stock(infos_produit['Availability']),
            'product_description': description,
            'category': categorie,
            'review_rating': note,
            'image_url': url_image
        }
    except Exception as e:
        print(f"Problème avec le livre {url_livre}: {e}")
        return None

def recup_categorie(url_categorie, nom_categorie):
    """Récupère tous les livres d'une catégorie"""
    livres = []
    urls_livres = []
    num_page = 1
    url_base = "http://books.toscrape.com/"
    
    # D'abord on récupère toutes les URLs des livres
    while True:
        if num_page == 1:
            url_page = url_categorie
        else:
            url_page = url_categorie.replace('index.html', f'page-{num_page}.html')
            
        try:
            page = recup_page(url_page)
            if not page:
                if num_page == 1:  # Si même la première page échoue
                    print(f"Impossible d'accéder à la catégorie {nom_categorie}")
                    return
                break  # Si c'est une page suivante, on arrête simplement la pagination
                
            liens_livres = page.select('h3 a')
            if not liens_livres:
                break
                
            print(f"Je récupère les URLs de {nom_categorie} - page {num_page}...")
            
            for lien in liens_livres:
                url_livre = urljoin(url_base + 'catalogue/', lien['href'].replace('../../../', ''))
                urls_livres.append(url_livre)
                    
            # Vérifie s'il y a une page suivante avant de continuer
            page_suivante = page.select_one('li.next')
            if not page_suivante:
                break
                
            num_page += 1
            
        except Exception as e:
            print(f"Erreur sur la page {num_page} de {nom_categorie}: {e}")
            if num_page == 1:
                return
            break
    
    if not urls_livres:
        print(f"Aucun livre trouvé dans la catégorie {nom_categorie}")
        return
        
    print(f"Traitement de {len(urls_livres)} livres dans {nom_categorie}...")
    
    # Ensuite on traite les livres en parallèle
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(recup_infos_livre, url) for url in urls_livres]
        for future in as_completed(futures):
            resultat = future.result()
            if resultat:
                livres.append(resultat)
                print(f"Livre traité: {resultat['title']}")
    
    # Sauvegarde des données dans un CSV si on a des livres
    if livres:
        with fichier_lock:  # Protection pour l'écriture du CSV
            os.makedirs('data', exist_ok=True)
            nom_fichier = f"data/{nom_categorie.lower().replace(' ', '_')}.csv"
            with open(nom_fichier, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=livres[0].keys())
                writer.writeheader()
                writer.writerows(livres)
        print(f"Cool! J'ai trouvé {len(livres)} livres dans {nom_categorie}")
    else:
        print(f"Pas de livres trouvés dans {nom_categorie}")

def lance_lescraper():
    """Le grand chef qui gère tout le bazar"""
    url_base = "http://books.toscrape.com/"
    page = recup_page(url_base)
    if not page:
        print("Impossible d'accéder au site, désolé!")
        return
        
    categories = page.select('div.side_categories ul.nav-list > li > ul > li > a')
    
    # On traite les catégories en parallèle
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        for cat in categories:
            nom_cat = cat.text.strip()
            url_cat = urljoin(url_base, cat['href'])
            futures.append(executor.submit(recup_categorie, url_cat, nom_cat))
        
        # Attendre que toutes les catégories soient traitées
        for future in as_completed(futures):
            future.result()

if __name__ == "__main__":
    lance_lescraper()
