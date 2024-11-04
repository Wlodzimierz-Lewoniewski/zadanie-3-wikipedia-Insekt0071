import re
import requests
from urllib.parse import quote
from html.parser import HTMLParser

class CategoryPageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_div_mw_pages = False
        self.article_links = []
        self.collect_links = False

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == 'div' and attrs_dict.get('id') == 'mw-pages':
            self.in_div_mw_pages = True
        elif self.in_div_mw_pages and tag == 'a' and not self.collect_links:
            href = attrs_dict.get('href', '')
            title = attrs_dict.get('title', '')
            if href.startswith('/wiki/') and title and not href.startswith('/wiki/Kategoria:') and not href.startswith('/wiki/Specjalna:'):
                self.article_links.append((href, title))
                if len(self.article_links) == 2:
                    self.collect_links = True  # Stop collecting more links

    def handle_endtag(self, tag):
        if tag == 'div' and self.in_div_mw_pages:
            self.in_div_mw_pages = False

class ArticlePageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_content = False
        self.in_body_content = False
        self.in_category = False
        self.internal_links = []
        self.images = []
        self.external_links = []
        self.categories = []
        self.seen_titles = set()
        self.seen_images = set()
        self.seen_external_links = set()
        self.seen_categories = set()
        self.internal_links_collected = False
        self.images_collected = False
        self.external_links_collected = False
        self.categories_collected = False
        self.all_data_collected = False

    def handle_starttag(self, tag, attrs):
        if self.all_data_collected:
            return  # Stop parsing if all data is collected

        attrs_dict = dict(attrs)
        # Start of content
        if tag == 'div' and attrs_dict.get('id') == 'bodyContent':
            self.in_body_content = True
        # Categories
        elif tag == 'div' and attrs_dict.get('id') == 'catlinks':
            self.in_category = True

        if self.in_body_content:
            if not self.internal_links_collected and tag == 'a':
                href = attrs_dict.get('href', '')
                title = attrs_dict.get('title', '')
                if href.startswith('/wiki/') and title and not href.startswith('/wiki/Kategoria:') and not href.startswith('/wiki/Specjalna:') and ':' not in href:
                    if title not in self.seen_titles:
                        self.internal_links.append(title)
                        self.seen_titles.add(title)
                        if len(self.internal_links) == 5:
                            self.internal_links_collected = True
            if not self.images_collected and tag == 'img':
                src = attrs_dict.get('src', '')
                if src.startswith('//upload.wikimedia.org'):
                    if src not in self.seen_images:
                        self.images.append(src)
                        self.seen_images.add(src)
                        if len(self.images) == 3:
                            self.images_collected = True

        if not self.external_links_collected and tag == 'a':
            href = attrs_dict.get('href', '')
            if href.startswith('http') and href not in self.seen_external_links:
                self.external_links.append(href)
                self.seen_external_links.add(href)
                if len(self.external_links) == 3:
                    self.external_links_collected = True

        if self.in_category and not self.categories_collected:
            if tag == 'a':
                href = attrs_dict.get('href', '')
                title = attrs_dict.get('title', '')
                if href.startswith('/wiki/Kategoria:') and title and title not in self.seen_categories:
                    category_name = title.replace('Kategoria:', '')
                    self.categories.append(category_name)
                    self.seen_categories.add(title)
                    if len(self.categories) == 3:
                        self.categories_collected = True

        # Check if all data is collected
        if (self.internal_links_collected and self.images_collected and
            self.external_links_collected and self.categories_collected):
            self.all_data_collected = True

    def handle_endtag(self, tag):
        if tag == 'div' and self.in_body_content:
            self.in_body_content = False
        if tag == 'div' and self.in_category:
            self.in_category = False

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
