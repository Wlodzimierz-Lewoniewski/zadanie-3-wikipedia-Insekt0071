import re
import requests
from urllib.parse import quote

def get_html_content(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception("Błąd podczas pobierania strony.")

def extract_internal_links(html_content):
    pattern = r'href="(/wiki/[^":#]+)"'
    links = re.findall(pattern, html_content)
    article_links = [link for link in links if not link.startswith('/wiki/Kategoria:')]
    return article_links[:2]

def extract_data_from_article(url):
    html_content = get_html_content(url)

    internal_links_pattern = r'href="(/wiki/[^":#]+)"'
    internal_links = re.findall(internal_links_pattern, html_content)
    formatted_internal_links = " | ".join(link.split('/')[-1].replace('_', ' ') for link in internal_links[:5])

    image_pattern = r'src="(//upload\.wikimedia\.org[^"]+\.(jpg|jpeg|png|svg))"'
    images = re.findall(image_pattern, html_content)
    formatted_images = " | ".join("https:" + img[0] for img in images[:3])

    external_link_pattern = r'href="(https?://[^"]+)"'
    external_links = re.findall(external_link_pattern, html_content)
    formatted_external_links = " | ".join(external_links[:3])

    category_pattern = r'href="/wiki/Kategoria:[^":#]+" title="([^"]+)"'
    categories = re.findall(category_pattern, html_content)
    formatted_categories = " | ".join(categories[:3])

    return formatted_internal_links, formatted_images, formatted_external_links, formatted_categories

category_query = input()
category_url = f"https://pl.wikipedia.org/wiki/{quote(category_query)}"
category_html_content = get_html_content(category_url)

article_links = extract_internal_links(category_html_content)

output = ""
for link in article_links:
    article_url = f"https://pl.wikipedia.org{link}"
    internal_links, images, external_links, categories = extract_data_from_article(article_url)
    output += f"{internal_links}\n{images}\n{external_links}\n{categories}\n"

print(output.strip())
