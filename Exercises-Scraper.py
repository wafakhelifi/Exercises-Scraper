import os
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import random


# Function to classify difficulty
def classify_difficulty():
    difficulty = random.choice(['easy', 'medium', 'hard'])
    return difficulty

# Retry mechanism with exponential backoff
retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
session = requests.Session()
session.mount('https://', HTTPAdapter(max_retries=retries))


# Function to download exams based on URLs and subject
def download_exercises(subject, quarters_urls, year_directory):
    # Iterate through each quarter URL
    for index, url in enumerate(quarters_urls, start=1):
        # Send an HTTP request to the website
        try:
            response = session.get(url, timeout=(3, 30))  # Increase timeout to 30 seconds (connect, read)

            # Check if the request was successful
            response.raise_for_status()

            # Parse the HTML content
            soup = BeautifulSoup(response.content, 'html.parser')

            # Define the base directory to save the downloaded exercices
            base_download_directory = os.path.join(year_directory, subject, f'Quarter {index}')
            os.makedirs(base_download_directory, exist_ok=True)

            # Find all exam entries within table cells
            exam_entries = soup.find_all('td', class_='attachment-title')

            # Extract exam information and download links
            for entry in exam_entries:
                # Find the link and title
                link_tag = entry.find('a', class_='attachment-link')
                if link_tag:
                    title = link_tag.text.strip()
                    link = link_tag['href'].strip()

                    # Classify difficulty
                    difficulty = classify_difficulty()

                    # Create subfolder based on difficulty
                    download_directory = os.path.join(base_download_directory, difficulty)
                    os.makedirs(download_directory, exist_ok=True)

                    # Send a request to download the file
                    try:
                        file_response = session.get(link, timeout=(3, 30))  # Increased timeout for download
                        file_response.raise_for_status()  # Raise an exception for bad response status

                        # Clean the title to create a valid filename
                        filename = title.replace(' ', '_').replace('/', '_').replace('\\', '_') + '.pdf'
                        filepath = os.path.join(download_directory, filename)

                        # Save the file
                        try:
                            with open(filepath, 'wb') as file:
                                file.write(file_response.content)
                            print(f"Downloaded: {title} (Subject: {subject}, Difficulty: {difficulty})")
                        except Exception as e:
                            print(f"Failed to save {title}: {e}")
                    except requests.exceptions.RequestException as e:
                        print(f"Failed to download {title}: {e}")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching URL {url}: {e}")

try:
    # Main directory for all exercices within the user's home directory
    home_directory = os.path.expanduser('~')
    main_directory = os.path.join(home_directory, 'Exercices')
    os.makedirs(main_directory, exist_ok=True)

    # URLs for exercises
    years_urls = {
        '9éme année en 2023': {
            'Mathématiques': [
                'https://www.ecoles.com.tn/sites/default/files/devoirs/files/concours_9eme_2023_math.pdf',
            ],
            'Science': [
                'https://www.ecoles.com.tn/sites/default/files/devoirs/files/concours_9eme_2023_svt.pdf',
            ],
            'Francais': [
                'https://www.ecoles.com.tn/sites/default/files/devoirs/files/concours_9eme_2023_francais.pdf',
            ],
            'Arabe': [
                'https://www.ecoles.com.tn/sites/default/files/devoirs/files/concours_9eme_2023_arabe.pdf',
            ],
            'Anglais': [
                'https://www.ecoles.com.tn/sites/default/files/devoirs/files/concours_9eme_anglais_0.pdf',
            ],
        },

        '9éme année en 2022': {
            'Anglais': [
                'https://www.ecoles.com.tn/sites/default/files/devoirs/files/concours-9eme-2022-anglais.pdf',
            ],
            'Science': [
                'https://www.ecoles.com.tn/sites/default/files/devoirs/files/concours-9eme-2022-svt.pdf',
            ],
            'Arabe': [
                'https://www.ecoles.com.tn/sites/default/files/devoirs/files/concours-9eme-2022-arabe.pdf',
            ],
            'Francais': [
                'https://www.ecoles.com.tn/sites/default/files/devoirs/files/concours-9eme-2022-francais.pdf',
            ],
            'Mathématiques': [
                'https://www.ecoles.com.tn/sites/default/files/devoirs/files/concours-9eme-2022-math.pdf',
            ],
        },

        '9éme année en 2021': {
            'Mathématiques': [
                'https://www.ecoles.com.tn/sites/default/files/devoirs/files/concours_9eme_2021_francais_corrige.pdf',
                'https://www.ecoles.com.tn/sites/default/files/devoirs/files/concours_9eme_math.pdf',
            ],
            'Anglais': [
                'https://www.ecoles.com.tn/sites/default/files/devoirs/files/concours_9eme_anglais_corrige.pdf',
            ],
            'Science': [
                'https://www.ecoles.com.tn/sites/default/files/devoirs/files/concours_9eme_svt.pdf',
            ],
            'Francais': [
                'https://www.ecoles.com.tn/sites/default/files/devoirs/files/concours_9eme_2021_francais.pdf',
            ],
        },
    }

    # Iterate through each year and subject, download exercises
    for year, subjects in years_urls.items():
        year_directory = os.path.join(main_directory, year)
        os.makedirs(year_directory, exist_ok=True)
        for subject, urls in subjects.items():
            download_exercises(subject, urls, year_directory)

except Exception as e:
    print(f"An error occurred: {e}")
finally:
    session.close()  # Close the session
