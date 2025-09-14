import io
import os
import random
import zipfile

import requests
from bs4 import BeautifulSoup


def extract_html5up_samples():
    response = requests.get("https://html5up.net/")
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    articles = soup.select("div#items article.item")
    
    item_names = []
    for article in articles:
        download_button = article.select_one("a.button.alt.download")
        if download_button and download_button.get("data-name"):
            item_names.append(download_button["data-name"])

    return item_names

def download_html5up_sample(extract_path):
    url_template = "https://html5up.net/{}/download"
    options = extract_html5up_samples()
    choice = random.choice(options)
    url = url_template.format(choice)
    print(f"Downloading HTML5UP sample from: {url}")

    
    response = requests.get(url)
    response.raise_for_status()
    zip_bytes = response.content

    os.makedirs(extract_path, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        z.extractall(extract_path)
    