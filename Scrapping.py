import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import csv
import time
import re


url = 'https://www.swiggy.com/restaurants/baskin-robbins-indiranagar-bangalore-176851'
driver = webdriver.Chrome(executable_path='C:/Users/Shreya/PycharmProject/RestaurantScrapping.py/venv/chromedriver-Windows')


driver.get(url)
time.sleep(0.2)

# Create a list to store scraped data
scraped_data = []

# Create a directory to store downloaded images if it doesn't exist
image_dir = 'downloaded_images'
if not os.path.exists(image_dir):
    os.mkdir(image_dir)

try:
    # Use BeautifulSoup to parse the page source
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Find the main container
    main_container = soup.find('div', class_='nDVxx')

    # Initialize item code
    item_code = 1

    # Open the CSV file for writing with 'utf-8-sig' encoding
    with open('menu_data.csv', 'w', newline='', encoding='utf-8-sig') as csv_file:
        writer = csv.writer(csv_file)

        # Write the header row
        writer.writerow(
            ['Item Code', 'Item Name', 'Item Price', 'Additional Info 1', 'Additional Info 2', 'Veg', 'Non-Veg',
             'Image File'])

        # Iterate through elements within the main container
        for element in main_container.find_all('div', recursive=False):

            # Find elements for items within the category (you may need to adjust this)
            item_divs = element.find_all('div', class_='styles_container__-kShr')

            # Iterate through items and store them
            for item_div in item_divs:
                item_name_element = item_div.find('h3', class_='styles_itemNameText__3ZmZZ')
                item_price_element = item_div.find('span', class_='rupee')
                item_description_element = item_div.find('div', class_='styles_itemDesc__3vhM0')
                item_image = item_div.find('img', class_='styles_itemImage__3CsDL')
                icon_class = item_div.find('i', class_='styles_icon__m6Ujp')

                item_name = item_name_element.text if item_name_element else ''
                item_price = item_price_element.text if item_price_element else ''
                item_description = item_description_element.text if item_description_element else ''

                # Split item_description into "Additional Info 1" and "Additional Info 2"
                additional_info1 = ""
                additional_info2 = ""

                # Initialize image details
                img_file_name = ''
                img_file_path = ''

                # Find the item image if it exists
                if item_image:
                    item_image_url = item_image['src']
                    img_data = requests.get(item_image_url).content
                    img_file_name = f"{item_code}.jpg"
                    img_file_path = os.path.join(image_dir, img_file_name)
                    with open(img_file_path, 'wb') as img_file:
                        img_file.write(img_data)

                # Use regular expressions to extract "Serves" information
                serves_match = re.search(r"(Serves \d+)", item_description)
                if serves_match:
                    additional_info2 = serves_match.group(1)
                    additional_info1 = item_description.replace(additional_info2, "").strip()
                else:
                    additional_info1 = item_description.strip()

                # Determine Veg or Non-Veg based on the icon class
                is_veg = 'Yes' if 'icon-Veg' in icon_class['class'] else 'No'
                is_nonveg = 'Yes' if 'icon-NonVeg' in icon_class['class'] else 'No'

                # Write the data to the CSV file, including the image file name and Veg/Non-Veg columns
                writer.writerow(
                    [item_code, item_name, item_price, additional_info1, additional_info2, is_veg, is_nonveg,
                     img_file_name])

                # Increment the item code for the next item
                item_code += 1

    print("Data saved in menu_data.csv")
    print(f"{item_code - 1} items and images downloaded")

except Exception as e:
    print("An error occurred:", str(e))

finally:
    # Close the WebDriver
    driver.quit()