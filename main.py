import requests
import re


class WikipediaScraper:
    def __init__(self, category, num_articles=2, num_images=3, num_external_links=3, num_categories=3):
        self.category = category
        self.num_articles = num_articles
        self.num_images = num_images
        self.num_external_links = num_external_links
        self.num_categories = num_categories
        self.base_url = "https://pl.wikipedia.org"

    def fetch_html(self, url):
        response = requests.get(url)
        response.raise_for_status()
        return response.text

    def extract_with_regex(self, pattern, source, max_count=None):
        matches = re.findall(pattern, source)
        if max_count:
            return matches[:max_count]
        return matches

    def get_article_links_and_titles(self, source):
        pattern = r'<a href="(\/wiki\/[^:]*?)".*?title="(.*?)"'
        links_titles = self.extract_with_regex(pattern, source, self.num_articles)
        links, titles = zip(*links_titles) if links_titles else ([], [])
        return list(links), list(titles)

    def get_image_urls(self, source):
        pattern = r'<img.*src="(\/\/upload\.wikimedia\.org.*?)"'
        urls = self.extract_with_regex(pattern, source, self.num_images)
        return urls

    def get_external_links(self, source):
        external_section = re.search(r'<h2 id="Przypisy">(.*)<h2 id="Linki_zewnętrzne">', source, re.DOTALL)
        if external_section:
            pattern = r'class="external text".*?href="(.*?)">'
            return self.extract_with_regex(pattern, external_section.group(1), self.num_external_links)
        return []
    def get_category_names(self, source):
        cat_section = re.search(r'<div id="catlinks".*', source, re.DOTALL)
        if cat_section:
            pattern = r'<a href="\/wiki\/Kategoria:.*?title="Kategoria:(.*?)">'
            return self.extract_with_regex(pattern, cat_section.group(), self.num_categories)
        return []

    def print_info_from_article(self, article_src):
        _, titles = self.get_article_links_and_titles(article_src)
        img_urls = self.get_image_urls(article_src)
        exts = self.get_external_links(article_src)
        cats = self.get_category_names(article_src)

        print(" | ".join(titles))
        print(" | ".join(img_urls))
        print(" | ".join(exts))
        print(" | ".join(cats))

    def scrape_category(self):
        category_url = f"{self.base_url}/wiki/Kategoria:{self.category}"
        category_html = self.fetch_html(category_url)
        page_content = re.search(r'<div id="mw-pages">.*', category_html, re.DOTALL).group()
        article_links, _ = self.get_article_links_and_titles(page_content)

        for link in article_links:
            article_url = f"{self.base_url}{link}"
            article_html = self.fetch_html(article_url)
            main_content = re.search(r'class="mw-body-content".*', article_html, re.DOTALL).group()
            self.print_info_from_article(main_content)

category = input("Podaj nazwę kategorii: ").strip()
scraper = WikipediaScraper(category)
scraper.scrape_category()
