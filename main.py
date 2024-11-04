import re
import requests
from urllib.parse import quote
from html.parser import HTMLParser

class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_content = False
        self.in_catlinks = False
        self.in_mw_pages = False
        self.article_links = []
        self.internal_links = []
        self.images = []
        self.external_links = []
        self.categories = []
        self.seen_internal_links = set()
        self.seen_images = set()
        self.seen_external_links = set()
        self.seen_categories = set()
        self.data_collected = False

    def handle_starttag(self, tag, attrs):
        if self.data_collected:
            return

        attrs_dict = dict(attrs)
        if tag == 'div':
            if attrs_dict.get('id') == 'bodyContent':
                self.in_content = True
            elif attrs_dict.get('id') == 'catlinks':
                self.in_catlinks = True
            elif attrs_dict.get('id') == 'mw-pages':
                self.in_mw_pages = True

        if self.in_mw_pages and tag == 'a':
            href = attrs_dict.get('href', '')
            title = attrs_dict.get('title', '')
            if href.startswith('/wiki/') and title and ':' not in href:
                self.article_links.append((href, title))
                if len(self.article_links) == 2:
                    self.data_collected = True

        if self.in_content:
            if tag == 'a':
                href = attrs_dict.get('href', '')
                title = attrs_dict.get('title', '')
                if href.startswith('/wiki/') and title and ':' not in href:
                    if title not in self.seen_internal_links:
                        self.internal_links.append((href, title))
                        self.seen_internal_links.add(title)
                elif href.startswith('http') and href not in self.seen_external_links:
                    self.external_links.append(href)
                    self.seen_external_links.add(href)
            elif tag == 'img':
                src = attrs_dict.get('src', '')
                if src.startswith('//upload.wikimedia.org') and src not in self.seen_images:
                    self.images.append(src)
                    self.seen_images.add(src)

        if self.in_catlinks and tag == 'a':
            href = attrs_dict.get('href', '')
            title = attrs_dict.get('title', '')
            if href.startswith('/wiki/Kategoria:') and title and title not in self.seen_categories:
                category_name = title.replace('Kategoria:', '')
                self.categories.append(category_name)
                self.seen_categories.add(title)

    def handle_endtag(self, tag):
        if tag == 'div':
            if self.in_content:
                self.in_content = False
            if self.in_catlinks:
                self.in_catlinks = False
            if self.in_mw_pages:
                self.in_mw_pages = False

def get_html_content(url):
    response = requests.get(url)
    response.encoding = 'utf-8'  # Ensure correct encoding
    if response.status_code == 200:
        return response.text
    elif response.status_code == 404:
        return None  # Page not found
    else:
        raise Exception("Błąd podczas pobierania strony.")

category_query = input().strip()
query_encoded = quote(category_query.replace(' ', '_'))

# First, try to access the category page
category_url = f"https://pl.wikipedia.org/wiki/Kategoria:{query_encoded}"
category_html_content = get_html_content(category_url)

if category_html_content:
    # It's a category page
    parser = PageParser()
    parser.feed(category_html_content)
    article_links = parser.article_links
else:
    # Not a category, treat as an article
    article_url = f"https://pl.wikipedia.org/wiki/{query_encoded}"
    article_html_content = get_html_content(article_url)
    if not article_html_content:
        print("Nie znaleziono strony.")
        exit()
    parser = PageParser()
    parser.feed(article_html_content)
    # Use internal links from the article as article_links
    article_links = parser.internal_links[:2]

output = ""
for href, title in article_links:
    article_url = f"https://pl.wikipedia.org{href}"
    article_html_content = get_html_content(article_url)
    if not article_html_content:
        continue
    parser = PageParser()
    parser.feed(article_html_content)

    # Collect first 5 internal links
    internal_links_titles = [t for h, t in parser.internal_links[:5]]
    internal_links = " | ".join(internal_links_titles)

    # Collect first 3 images
    images = " | ".join(parser.images[:3])

    # Collect first 3 external links
    external_links = " | ".join(parser.external_links[:3])

    # Collect first 3 categories
    categories = " | ".join(parser.categories[:3])

    output += f"{internal_links}\n{images}\n{external_links}\n{categories}\n"

print(output.strip())
