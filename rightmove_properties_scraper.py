import csv
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException


def rent(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    prices = soup.find_all("span", class_="propertyCard-priceValue")
    return [price.text.strip() for price in prices]

def location(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    metas = soup.find_all("meta", itemprop="streetAddress")
    return [meta["content"] for meta in metas]

def get_property_link(tag):
    link_element = tag.find("a", class_="propertyCard-link")
    if link_element is not None and "href" in link_element.attrs:
        property_link = link_element["href"]
        return property_link
    return None

def get_property_types(url):
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    property_types = []
    try:
        property_info_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "property-information"))
        )
        for prop_info in property_info_elements:
            prop_type_text = prop_info.find_element(By.CLASS_NAME, "text").text.strip()
            property_types.append(prop_type_text)
    except TimeoutException:
        print("TimeoutException: Failed to find property types.")

    driver.quit()
    return property_types

def get_bedrooms(url):
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    property_info_elements = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "property-information"))
    )

    bedrooms = []
    for prop_info in property_info_elements:
        try:
            bedroom_element = prop_info.find_element(By.CSS_SELECTOR, 'span.text[aria-hidden="true"]')
            bedrooms.append(bedroom_element.text.strip())
        except NoSuchElementException:
            bedrooms.append('N/A')

    driver.quit()
    return bedrooms


base_url = "https://www.rightmove.co.uk/property-to-rent/find.html"
params = {
    "searchType": "RENT",
    "locationIdentifier": "REGION^87490",
    "insId": "1",
    "radius": "0.0",
    "minPrice": "",
    "maxPrice": "",
    "minBedrooms": "",
    "maxBedrooms": "",
    "displayPropertyType": "",
    "maxDaysSinceAdded": "",
    "sortByPriceDescending": "",
    "_includeLetAgreed": "on",
    "primaryDisplayPropertyType": "",
    "secondaryDisplayPropertyType": "",
    "oldDisplayPropertyType": "",
    "oldPrimaryDisplayPropertyType": "",
    "letType": "",
    "letFurnishType": "",
    "houseFlatShare": ""
}

next_page = True
page_number = 1

csv_file = "property_data.csv"

while next_page:
    params["index"] = str(page_number * 24)
    url = base_url + "?" + "&".join([f"{key}={value}" for key, value in params.items()])

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    property_cards = soup.find_all("div", class_="propertyCard")
    property_links = [get_property_link(card) for card in property_cards]

    prices = rent(url)
    street_addresses = location(url)
    property_types = get_property_types(url)
    bedrooms = get_bedrooms(url)

    with open(csv_file, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        for price, address, prop_type, prop_link, bedroom in zip(prices, street_addresses, property_types, property_links, bedrooms):
            writer.writerow([price, address, prop_type, prop_link, bedroom])

    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    next_page_button = driver.find_element(By.CLASS_NAME, "pagination-direction--next")
    if "disabled" in next_page_button.get_attribute("class"):
        next_page = False
    else:
        next_page_button.click()
        page_number += 1

    driver.quit()

print(f"Data saved to {csv_file}.")
