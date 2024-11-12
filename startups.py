import requests
from bs4 import BeautifulSoup
import json

# Base URLs for the featured startups pages
base_urls = [
    'https://websummit.com/startups/featured-startups/page/',
    *[f'https://websummit.com/startups/featured-startups/search/{letter}/page/' for letter in 'abcdefghijklmnopqrstuvwxyz']
]

# Headers to mimic a browser request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
}

# Set to track unique startup names and list to store extracted items
unique_names = set()
all_items = []

# Iterate through each base URL
for base_url in base_urls:
    # Check up to 20 pages for each base URL
    for page_number in range(1, 21):
        # Construct the URL for the current page
        url = f'{base_url}{page_number}/'

        # Send a GET request to the page
        response = requests.get(url, headers=headers)

        # Stop fetching pages if the response indicates no more content
        if response.status_code != 200:
            print(f'Failed to retrieve or no more pages found at {url}')
            break

        # Parse the page content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the <script> element with id="__NEXT_DATA__"
        script_tag = soup.find('script', id='__NEXT_DATA__', type='application/json')

        if script_tag:
            # Extract JSON data from the script tag
            json_data = script_tag.string

            # Parse JSON data
            try:
                data = json.loads(json_data)
            except json.JSONDecodeError as e:
                print(f'Error decoding JSON on page {page_number} of {base_url}: {e}')
                continue

            # Navigate to the desired array
            try:
                flexible_content = data['props']['pageProps']['data']['page']['template']['customPage']['flexibleContent']
            except KeyError as e:
                print(f'Missing key {e} on page {page_number} of {base_url}')
                continue

            # Iterate over items in the flexibleContent array
            for item in flexible_content:
                if item.get('__typename') == 'DefaultTemplate_Custompage_FlexibleContent_AttendeeList':
                    list_items = item.get('listItems', [])
                    for list_item in list_items:
                        name = list_item.get('name', 'N/A')
                        if name not in unique_names:  # Check if name is unique
                            unique_names.add(name)
                            elevator_pitch = list_item.get('elevatorPitch', 'N/A')
                            industry = list_item.get('industry', 'N/A')
                            track = list_item.get('track', 'N/A')
                            country = list_item.get('country', 'N/A')
                            all_items.append({
                                'name': name,
                                'elevatorPitch': elevator_pitch,
                                'industry': industry,
                                'track': track,
                                'country': country
                            })

            print(f'Page {page_number} of {base_url} processed successfully.')
        else:
            print(f'No JSON data found on page {page_number} of {base_url}.')
            break

# Sort all items by 'name'
all_items_sorted = sorted(all_items, key=lambda x: x['name'])

# Save to a TXT file
with open('startups.txt', 'w', encoding='utf-8') as txt_file:
    for item in all_items_sorted:
        txt_file.write(f"Name: {item['name']}\n")
        txt_file.write(f"Elevator Pitch: {item['elevatorPitch']}\n")
        txt_file.write(f"Industry: {item['industry']}\n")
        txt_file.write(f"Track: {item['track']}\n")
        txt_file.write(f"Country: {item['country']}\n")
        txt_file.write('---\n')

# Save to a JSON file
with open('startups.json', 'w', encoding='utf-8') as json_file:
    json.dump(all_items_sorted, json_file, ensure_ascii=False, indent=4)

print(f"Processed {len(all_items_sorted)} unique items. Results saved to 'startups.txt' and 'startups.json'.")
