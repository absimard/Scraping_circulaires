import os
import requests
import re
import openpyxl
from bs4 import BeautifulSoup
import pandas as pd
import argparse

class Circular:
    """
    A class representing the circulars parsed/to parse.
    """

    def __init__(self, url):
        """
        Initialize the object.

        Args:
            url (str, optional): The url for the circulars. Defaults to 'https://www.supermarches.ca/pages/Aubaines.asp'.
        """
        self.url = url
        self.content = []

    def scrape(self):
        """
        Scrape the circulars from the url.
        """
        self.soup = visitWebsite(self.url)

        # Find the page info
        page_info = self.soup.find('td', string=lambda text: text and 'Page' in text)

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
                for page in range(1, num_pages+1):
                    # Construct the URL for each page
                    page_url = f'{self.url}?page={page}'
                    print(f"Scraping page {page} - URL: {page_url}")

                    soup = visitWebsite(page_url)

                    # Find all anchor tags representing an article
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

                        # Add the circular to the object content
                        self.content.append(circular)

            # If the number of pages is not found
            else:
                print("Impossible de trouver le nombre de pages")

        # If the page info is not found
        else:
            print("Impossible de trouver le nombre de pages")

class ExcelFile:
    """
    A class representing an Excel file.
    """

    def __init__(self, filename=os.path.abspath('circulaires.xlsx'), content=[]):
        """
        Initialize the Excel file with a filename and optional content.

        Args:
            filename (str, optional): The filename for the Excel file. Defaults to 'circulaires.xlsx' in the current working directory.
            content (list, optional): The initial content for the Excel file. Defaults to an empty list.
        """
        self.filename = filename
        # Initialize an empty list to store the circulars
        self.content = content

    def write(self):
        """
        Write the content to the Excel file.
        """
        # Create a new Excel workbook
        df = pd.DataFrame(self.content)

        # Save the workbook to the file
        df.to_excel(self.filename, index=False)

        # Open the workbook with openpyxl to modify column widths
        wb = openpyxl.load_workbook(self.filename)
        ws = wb.active

        # Set all column widths 25
        for col in ws.columns:
            col_letter = col[0].column_letter
            ws.column_dimensions[col_letter].width = 25

        wb.save(self.filename)
        print(f"Data exported to {self.filename}")

def visitWebsite(url):
    """
    Using BeatifulSoup in a session (reduces the network charge), returns the content of the website
    """
    # Send a GET request to the base URL
    response = requests.get(url)

    # Parse the HTML content using BeautifulSoup
    return BeautifulSoup(response.content, 'html.parser')

def main():
    # Parse the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", help="Spécifiez l'URL où on prend les circulaires", default="https://www.supermarches.ca/pages/Aubaines.asp")
    args = parser.parse_args()
    # Create an empty Circular instance
    circulars = Circular(args.url)
    # Parse the website
    circulars.scrape()    
    # Sort from best to worst rebate
    sorted_circulars = sorted(circulars.content, key=lambda x: float(x['Rabais (%)'].replace('%', '').strip()), reverse=True)
    # Create and fill an Excel spreadsheet
    excel_file = ExcelFile(content=sorted_circulars)
    excel_file.write()

if __name__ == '__main__':
    main()
