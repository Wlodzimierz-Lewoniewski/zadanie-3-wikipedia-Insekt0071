import re
import requests

url = "https://pl.wikipedia.org/wiki/Pomoc:Przestrze%C5%84_nazw"
response = requests.get(url)

if response.status_code == 200:
    html_content = response.text
    print("Kod HTML strony pomocniczej pobrany pomyślnie.")
else:
    print("Błąd podczas pobierania strony.")

#wzorzec do patternów
pattern = r'href="(/wiki/[^":#]+)"'

# Znalezienie wszystkich dopasowań wzorca w kodzie HTML
links = re.findall(pattern, html_content)

# Wyświetlenie pierwszych pięciu dopasowań
print("Znalezione odnośniki wewnętrzne:")
for link in links[:5]:
    print("https://pl.wikipedia.org" + link)

# Wzorzec dla adresów URL obrazków
image_pattern = r'src="(//upload\.wikimedia\.org[^"]+\.(jpg|jpeg|png|svg))"'

# Znalezienie dopasowań dla obrazów
images = re.findall(image_pattern, html_content)

# Wyświetlenie pierwszych trzech URL obrazków
print("Znalezione URL obrazków:")
for img in images[:3]:
    print("https:" + img[0])  # Dodajemy "https:" na początku URL
