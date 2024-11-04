import requests
import re

def get_category_links(category_name):
    url = f"https://pl.wikipedia.org/wiki/Kategoria:{category_name.replace(' ', '_')}"
    response = requests.get(url)
    html = response.text
    
    # Wyszukiwanie pierwszych dwóch linków do artykułów
    links = re.findall(r'href="(/wiki/[^":]*?)"', html)
    article_links = [link for link in links if ':' not in link][:2]
    return article_links

def extract_data_from_article(article_url):
    url = f"https://pl.wikipedia.org{article_url}"
    response = requests.get(url)
    html = response.text
    
    # Linki wewnętrzne (pierwsze 5)
    internal_links = re.findall(r'<a href="(/wiki/[^":]*?)"[^>]*?>([^<]*?)</a>', html)
    internal_links = [text for _, text in internal_links if ':' not in _][:5]
    
    # Obrazki (pierwsze 3) - usunięcie duplikatów
    image_urls = re.findall(r'src="(//upload\.wikimedia\.org[^"]*?\.(jpg|png|svg))"', html)
    image_urls = list(dict.fromkeys(["https:" + url[0] for url in image_urls]))[:3]
    
    # Linki zewnętrzne (pierwsze 3)
    external_links = re.findall(r'href="(https?://[^"]*?)"', html)
    external_links = external_links[:3]
    
    # Kategorie (pierwsze 3)
    categories = re.findall(r'<a href="/wiki/Kategoria:[^"]*?" title="Kategoria:[^"]*?">(.*?)</a>', html)
    categories = categories[:3]
    
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
