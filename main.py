import re
import requests
from urllib.parse import quote

def get_wiki_content(query):
    #wwyszukiwanie
    url = f"https://pl.wikipedia.org/wiki/{quote(query)}"
    response = requests.get(url)

    if response.status_code == 200:
        return response.text
    else:
        raise Exception("blad podczas pobierania strony.")

def extract_internal_links(html_content):
    pattern = r'href="(/wiki/[^":#]+)"'
    links = re.findall(pattern, html_content)
    formatted_links = [link.split('/')[-1].replace('_', ' ') for link in links]
    return " | ".join(formatted_links[:5])

def extract_images(html_content):
    image_pattern = r'src="(//upload\.wikimedia\.org[^"]+\.(jpg|jpeg|png|svg))"'
    images = re.findall(image_pattern, html_content)
    formatted_images = ["https:" + img[0] for img in images[:3]]
    return " | ".join(formatted_images)

def extract_external_links(html_content):
    external_link_pattern = r'href="(https?://[^"]+)"'
    external_links = re.findall(external_link_pattern, html_content)
    return " | ".join(external_links[:3])

def extract_categories(html_content):
    category_pattern = r'href="/wiki/Kategoria:[^":#]+" title="([^"]+)"'
    categories = re.findall(category_pattern, html_content)
    return " | ".join(categories[:3])

#pobieranie kou html
html_content = get_wiki_content("Miasta na prawach powiatu")

internal_links = extract_internal_links(html_content)
images = extract_images(html_content)
external_links = extract_external_links(html_content)
categories = extract_categories(html_content)

print(internal_links, images, external_links, categories)
#print(images)
#print(external_links)
#print(categories)
