import re
import requests
from urllib.parse import quote

def get_html_content(url):
    response = requests.get(url)
    response.encoding = 'utf-8'  # Ensure correct encoding
    if response.status_code == 200:
        return response.text
    else:
        raise Exception("Błąd podczas pobierania strony.")

def extract_internal_links(html_content):
    # Pattern to find links in the category page
    link_pattern = r'<a href="(/wiki/[^":#]+)"[^>]* title="([^"]+)"'
    links = re.findall(link_pattern, html_content)
    article_links = []
    for href, title in links:
        if not href.startswith('/wiki/Kategoria:') and not href.startswith('/wiki/Specjalna:'):
            article_links.append((href, title))
            if len(article_links) == 2:
                break
    return article_links

def extract_data_from_article(html_content):
    # Extract internal links
    internal_links_pattern = r'<a href="(/wiki/[^":#]+)"[^>]* title="([^"]+)"'
    internal_links_matches = re.findall(internal_links_pattern, html_content)
    internal_links = []
    seen_titles = set()
    for href, title in internal_links_matches:
        if not href.startswith('/wiki/Kategoria:') and not href.startswith('/wiki/Specjalna:') and title not in seen_titles:
            internal_links.append(title)
            seen_titles.add(title)
            if len(internal_links) == 5:
                break
    formatted_internal_links = " | ".join(internal_links)

    # Extract images
    images_pattern = r'<img[^>]+src="(//upload\.wikimedia\.org[^"]+\.(?:jpg|jpeg|png|svg))"'
    images = re.findall(images_pattern, html_content)
    formatted_images = " | ".join(images[:3])

    # Extract external links
    external_links_pattern = r'<a[^>]+href="(https?://[^"]+)"[^>]*>'
    external_links = re.findall(external_links_pattern, html_content)
    formatted_external_links = " | ".join(external_links[:3])

    # Extract categories
    category_pattern = r'<a href="/wiki/Kategoria:[^"]+"[^>]*>([^<]+)</a>'
    categories = re.findall(category_pattern, html_content)
    formatted_categories = " | ".join(categories[:3])

    return formatted_internal_links, formatted_images, formatted_external_links, formatted_categories

category_query = input().strip()
# Adjust the URL to point to the category page
category_url = f"https://pl.wikipedia.org/wiki/Kategoria:{quote(category_query.replace(' ', '_'))}"
category_html_content = get_html_content(category_url)

article_links = extract_internal_links(category_html_content)

output = ""
for href, title in article_links:
    article_url = f"https://pl.wikipedia.org{href}"
    article_html_content = get_html_content(article_url)
    internal_links, images, external_links, categories = extract_data_from_article(article_html_content)
    output += f"{internal_links}\n{images}\n{external_links}\n{categories}\n"

print(output.strip())
