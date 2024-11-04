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

def get_div_content(html_content, div_id):
    # Adjusted pattern to be non-greedy and handle nested divs
    pattern = rf'<div[^>]*id="{div_id}"[^>]*?>(.*?)</div>\s*</div>'
    match = re.search(pattern, html_content, re.DOTALL)
    if match:
        return match.group(1)
    else:
        return ''

def extract_internal_links(html_content):
    mw_pages_content = get_div_content(html_content, 'mw-pages')
    if not mw_pages_content:
        return []
    link_pattern = r'<li[^>]*>\s*<a href="(/wiki/[^":#]+)"[^>]* title="([^"]+)">[^<]+</a>'
    links = re.findall(link_pattern, mw_pages_content)
    article_links = []
    for href, title in links:
        if not href.startswith('/wiki/Kategoria:') and not href.startswith('/wiki/Specjalna:'):
            article_links.append((href, title))
            if len(article_links) == 2:
                break
    return article_links

def extract_data_from_article(url):
    html_content = get_html_content(url)
    content_div = get_div_content(html_content, 'mw-content-text')

    # Extract internal links
    internal_links_pattern = r'<a href="(/wiki/[^":#]+)"[^>]* title="([^"]+)"[^>]*>([^<]+)</a>'
    internal_links_matches = re.findall(internal_links_pattern, content_div)
    internal_links = []
    seen_titles = set()
    for href, title, link_text in internal_links_matches:
        if not href.startswith('/wiki/Kategoria:') and not href.startswith('/wiki/Specjalna:'):
            if title not in seen_titles:
                internal_links.append(title)
                seen_titles.add(title)
            if len(internal_links) == 5:
                break
    formatted_internal_links = " | ".join(internal_links)

    # Extract images
    images_pattern = r'<img[^>]+src="(//upload\.wikimedia\.org[^"]+\.(?:jpg|jpeg|png|svg))"[^>]*>'
    images = re.findall(images_pattern, content_div)
    formatted_images = " | ".join(img for img in images[:3])

    # Extract external links
    external_links = []
    # First, try to find 'Przypisy' section
    references_pattern = r'<h2[^>]*>\s*<span[^>]*id="Przypisy"[^>]*>.*?</h2>(.*?)<h2'
    references_match = re.search(references_pattern, html_content, re.DOTALL)
    if references_match:
        references_content = references_match.group(1)
        external_links_pattern = r'<a[^>]+href="(https?://[^"]+)"[^>]*>'
        external_links = re.findall(external_links_pattern, references_content)
    # If not enough links, get from entire content
    if len(external_links) < 3:
        external_links_pattern = r'<a[^>]+href="(https?://[^"]+)"[^>]*>'
        external_links += re.findall(external_links_pattern, content_div)
    formatted_external_links = " | ".join(external_links[:3])

    # Extract categories
    catlinks_div = get_div_content(html_content, 'catlinks')
    category_pattern = r'<a href="/wiki/Kategoria:[^"]+"[^>]*>([^<]+)</a>'
    categories = re.findall(category_pattern, catlinks_div)
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
    internal_links, images, external_links, categories = extract_data_from_article(article_url)
    output += f"{internal_links}\n{images}\n{external_links}\n{categories}\n"

print(output.strip())
