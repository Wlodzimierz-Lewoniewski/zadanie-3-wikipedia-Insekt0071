import re
import requests
from urllib.parse import quote

# Przyjęcie hasła od użytkownika
query = input("Podaj hasło do wyszukania na Wikipedii: ")
url = f"https://pl.wikipedia.org/wiki/{quote(query)}"

# Pobieranie strony
response = requests.get(url)

if response.status_code == 200:
    html_content = response.text
    print(f"Kod HTML strony '{query}' pobrany pomyślnie.\n")
else:
    print("Błąd podczas pobierania strony.")
    exit()

# Wzorzec dla odnośników wewnętrznych
pattern = r'href="(/wiki/[^":#]+)"'
links = re.findall(pattern, html_content)

print("Znalezione odnośniki wewnętrzne:")
for link in links[:5]:
    print("https://pl.wikipedia.org" + link)

# Wzorzec dla adresów URL obrazków
image_pattern = r'src="(//upload\.wikimedia\.org[^"]+\.(jpg|jpeg|png|svg))"'
images = re.findall(image_pattern, html_content)

print("\nZnalezione URL obrazków:")
for img in images[:3]:
    print("https:" + img[0])  # Dodajemy "https:" na początku URL

# Wzorzec dla URL źródeł zewnętrznych
external_link_pattern = r'href="(https?://[^"]+)"'
external_links = re.findall(external_link_pattern, html_content)

print("\nZnalezione URL źródeł zewnętrznych:")
for link in external_links[:3]:
    print(link)

# Wzorzec dla kategorii
category_pattern = r'href="/wiki/Kategoria:[^":#]+" title="([^"]+)"'
categories = re.findall(category_pattern, html_content)

print("\nZnalezione kategorie artykułu:")
for category in categories[:3]:
    print(category)
