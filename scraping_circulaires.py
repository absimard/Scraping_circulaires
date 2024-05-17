import os
import requests
import re
from bs4 import BeautifulSoup
import pandas as pd

# Define the base URL for the website
base_url = 'https://www.supermarches.ca/pages/Aubaines.asp'

# Define the filename for the Excel file
filename = os.path.abspath('circulaires.xlsx')

# Initialize an empty list to store the circulars
circulars = []

def scrape_circulars(num_pages):
    """
    Scrape circulars from the website.

    Args:
        num_pages (int): The number of pages to scrape.

    Returns:
        None
    """
    for page in range(1, num_pages+1):
        # Construct the URL for each page
        url = f'{base_url}?page={page}'
        print(f"Scraping page {page} - URL: {url}")

        # Send a GET request to the URL
        response = requests.get(url)

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all anchor tags with the title "Cliquez ici pour ajouter cet article à votre liste d'épicerie"
        anchor_tags = soup.find_all('a', title="Cliquez ici pour ajouter cet article à votre liste d'épicerie")

        # Iterate over the anchor tags
        for anchor_tag in anchor_tags:
            # Find the parent table of the anchor tag
            table = anchor_tag.find_parent('table')

            # If a table is found, break the loop
            if table is not None:
                break

        # If no table is found, print a message
        if table is None:
            print("Aucune table trouvée.")

        # Iterate over the rows in the table
        for row in table.find_all('tr')[1:]:
            # Initialize an empty dictionary to store the circular data
            circular = {}

            # Find all the columns in the row
            columns = row.find_all('td')

            # Extract the data from the columns and store it in the circular dictionary
            circular['Magasin'] = columns[7].text.strip().replace('Circ. - Mag.', '')
            circular['Description'] = columns[1].text.strip()
            circular['Format'] = columns[2].text.strip()
            circular['Origine'] = columns[3].text.strip()
            circular['Prix ($)'] = columns[4].text.strip()
            circular['Rabais ($)'] = float(columns[5].text.strip().split('\xa0')[0].replace(' ','').replace('$',''))
            circular['Rabais (%)'] = columns[5].text.strip().split('\xa0')[1].replace('(','').replace(')','')
            circular['Début/Fin'] = columns[6].text.strip()
            circular['Lien'] = columns[7].find_all('a')[0]['href']

            # Add the circular to the circulars list
            circulars.append(circular)

    # Create a new Excel workbook
    df = pd.DataFrame(circulars)

    # Save the workbook to the file
    df.to_excel(filename, index=False)
    print(f"Data exported to {filename}")

def main():
    # Send a GET request to the base URL
    response = requests.get(base_url)

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the page info
    page_info = soup.find('td', string=lambda text: text and 'Page' in text)

    # If the page info is found
    if page_info:
        # Extract the page text
        page_text = page_info.text.replace('\xa0', '').replace(' ', '')

        # Search for the number of pages
        match = re.search(r'sur(\d+)\)', page_text)

        # If the number of pages is found
        if match:
            # Extract the number of pages
            num_pages = int(match.group(1))
            print(f"Nombre de pages : {num_pages}")

            # Scrape the circulars
            scrape_circulars(num_pages)

        # If the number of pages is not found
        else:
            print("Impossible de trouver le nombre de pages")

    # If the page info is not found
    else:
        print("Impossible de trouver le nombre de pages")

if __name__ == '__main__':
    main()