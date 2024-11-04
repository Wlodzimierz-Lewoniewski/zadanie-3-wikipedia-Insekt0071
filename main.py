import requests
from bs4 import BeautifulSoup
import re

def get_category_links(category_name):
    url = f"https://pl.wikipedia.org/wiki/Kategoria:{category_name.replace(' ', '_')}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    article_links = [
        link.get('href') for link in soup.select('.mw-category-group a')[:2]
    ]
    return article_links

def extract_data_from_article(article_url):
    url = f"https://pl.wikipedia.org{article_url}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Linki wewnętrzne
    internal_links = [
        link.text for link in soup.select("a[href^='/wiki/']:not([href*=':'])")[:5]
    ]
    
    # Obrazki
    image_urls = [
        img.get('src') for img in soup.select("img[src^='//upload.wikimedia.org']")[:3]
    ]
    
    # Linki zewnętrzne
    external_links = [
        a.get('href') for a in soup.select("a[href^='http']")[:3]
    ]
    
    # Kategorie
    categories = [
        cat.text for cat in soup.select("#mw-normal-catlinks ul li")[:3]
    ]
    
    return {
        "internal_links": internal_links,
        "image_urls": image_urls,
        "external_links": external_links,
        "categories": categories
    }

def main():
    category_name = input("Podaj nazwę kategorii: ")
    article_links = get_category_links(category_name)
    
    for article_link in article_links:
        data = extract_data_from_article(article_link)
        print(" | ".join(data["internal_links"]))
        print(" | ".join(data["image_urls"]))
        print(" | ".join(data["external_links"]))
        print(" | ".join(data["categories"]))

if __name__ == "__main__":
    main()
