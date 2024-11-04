import re
import requests
from urllib.parse import quote
from html.parser import HTMLParser

class CategoryPageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_mw_pages = False
        self.article_links = []
        self.data_collected = False

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == 'div' and attrs_dict.get('id') == 'mw-pages':
            self.in_mw_pages = True
        elif self.in_mw_pages and tag == 'a':
            href = attrs_dict.get('href', '')
            title = attrs_dict.get('title', '')
            if href.startswith('/wiki/') and title and not href.startswith('/wiki/Kategoria:') and not href.startswith('/wiki/Specjalna:'):
                self.article_links.append((href, title))
                if len(self.article_links) == 2:
                    self.data_collected = True
                    self.in_mw_pages = False  # Stop parsing further

    def handle_endtag(self, tag):
        if tag == 'div' and self.in_mw_pages:
            self.in_mw_pages = False

class ArticlePageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_content = False
        self.in_catlinks = False
        self.internal_links = []
        self.images = []
        self.external_links = []
        self.categories = []
        self.seen_titles = set()
        self.seen_external_links = set()
        self.seen_categories = set()
        self.internal_links_collected = False
        self.images_collected = False
        self.external_links_collected = False
        self.categories_collected = False

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        # Start of content
        if tag == 'div' and attrs_dict.get('id') == 'mw-content-text':
            self.in_content = True
        # Categories
        elif tag == 'div' and attrs_dict.get('id') == 'catlinks':
            self.in_catlinks = True

        if self.in_content and not self.internal_links_collected:
            if tag == 'a':
                href = attrs_dict.get('href', '')
                title = attrs_dict.get('title', '')
                if href.startswith('/wiki/') and title and not href.startswith('/wiki/Kategoria:') and not href.startswith('/wiki/Specjalna:'):
                    if title not in self.seen_titles:
                        self.internal_links.append(title)
                        self.seen_titles.add(title)
                        if len(self.internal_links) == 5:
                            self.internal_links_collected = True
            elif tag == 'img' and not self.images_collected:
                src = attrs_dict.get('src', '')
                if src.startswith('//upload.wikimedia.org'):
                    if src not in self.images:
                        self.images.append(src)
                        if len(self.images) == 3:
                            self.images_collected = True

        if not self.external_links_collected:
            if tag == 'a':
                href = attrs_dict.get('href', '')
                if href.startswith('http') and href not in self.seen_external_links:
                    self.external_links.append(href)
                    self.seen_external_links.add(href)
                    if len(self.external_links) == 3:
                        self.external_links_collected = True

        if self.in_catlinks and not self.categories_collected:
            if tag == 'a':
                href = attrs_dict.get('href', '')
                title = attrs_dict.get('title', '')
                if href.startswith('/wiki/Kategoria:') and title and title not in self.seen_categories:
                    category_name = title.replace('Kategoria:', '')
                    self.categories.append(category_name)
                    self.seen_categories.add(title)
                    if len(self.categories) == 3:
                        self.categories_collected = True

    def handle_endtag(self, tag):
        if tag == 'div' and self.in_content:
            self.in_content = False
        if tag == 'div' and self.in_catlinks:
            self.in_catlinks = False

def get_html_content(url):
    response = requests.get(url)
    response.encoding = 'utf-8'  # Ensure correct encoding
    if response.status_code == 200:
        return response.text
    else:
        raise Exception("Błąd podczas pobierania strony.")

category_query = input().strip()
category_url = f"https://pl.wikipedia.org/wiki/Kategoria:{quote(category_query.replace(' ', '_'))}"
category_html_content = get_html_content(category_url)

# Parse category page to get article links
category_parser = CategoryPageParser()
category_parser.feed(category_html_content)
article_links = category_parser.article_links

output = ""
for href, title in article_links:
    article_url = f"https://pl.wikipedia.org{href}"
    article_html_content = get_html_content(article_url)
    article_parser = ArticlePageParser()
    article_parser.feed(article_html_content)

    # Collect first 5 internal links
    internal_links = " | ".join(article_parser.internal_links[:5])
    # Collect first 3 images
    images = " | ".join(article_parser.images[:3])
    # Collect first 3 external links
    external_links = " | ".join(article_parser.external_links[:3])
    # Collect first 3 categories
    categories = " | ".join(article_parser.categories[:3])

    output += f"{internal_links}\n{images}\n{external_links}\n{categories}\n"

print(output.strip())
