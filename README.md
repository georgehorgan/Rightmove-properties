# [Rightmove Property Analysis](https://github.com/georgehorgan/Rightmove-properties)

This project aims to gain insights into the renters market by gathering information from [Rightmove.co.uk](http://Rightmove.co.uk). 

### Gather the data:

I built a scraper that takes data from the list of apartments that show up when I type in London on the search bar. Then the scraper continues page by page until it runs out of pages to scrape through. I design it to collect the following:

**Rent -** price of rent per month

**Location** - street address of the property

**Property link** - returns a link to the property

**Property type** - the type of property it is

**Bedrooms** - number of bedrooms at the property

```python
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
```

### Returned data:

[Returned data (unclean)](https://www.dropbox.com/scl/fi/3fs00rau6br2vq5zrsq8i/rightmove_data_uncleaned.csv?rlkey=wc4azmbhsdo37rwmde8z8ix9q&dl=0)

### Import data:

```python
import pandas as pd
import numpy as np
import chardet
import re
```

```python
file_path = r"C:\Users\georg\Desktop\Data Centre\DataPython\Projects\London Rent Prices\rightmove_data_uncleaned.csv"

with open(file_path, 'rb') as f:
    content = f.read()
result = chardet.detect(content)
encoding = result['encoding']

print("Detected Encoding:", encoding)
print("Confidence:", result['confidence'])

data = pd.read_csv(file_path, encoding = encoding, header = 0)

print(data.head())
```

```
Detected Encoding: Windows-1252
Confidence: 0.73
   £5,250 pcm                Newark House, Loughborough Junction         Flat  \
0  £1,600 pcm                          Bulwer Court Road, London  Ground Flat   
1  £2,900 pcm           Vandome Close, Custom House, London, E16        House   
2  £1,900 pcm  Royal Tower Lodge, Cartwright Street, St Kathe...         Flat   
3  £2,390 pcm                       Arlingford Road, London, SW2     Terraced   
4  £3,500 pcm                    Beechcroft Avenue, London, NW11         Flat   

    /properties/86194638#/?channel=RES_LET    4  
0  /properties/136242707#/?channel=RES_LET  2.0  
1  /properties/135790637#/?channel=RES_LET  4.0  
2  /properties/123122660#/?channel=RES_LET  1.0  
3  /properties/136242695#/?channel=RES_LET  2.0  
4  /properties/136242698#/?channel=RES_LET  4.0
```

```python
properties = pd.DataFrame(data)
```

```python
columns = ["Price", "Location", "Type", "Link", "Bedrooms"]
properties.columns = columns
properties.head()
```

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/ccc467b0-3826-4acf-9b3d-e71ae5c53dea/Untitled.png)

### **Data cleaning:**

To do:

1. Check for null values and decide what to do with them if found.
2. Price - remove string values and create integer values.
3. Location - Extract postcode into a different column called "Postcode".
4. Link - Add "Rightmove.co.uk" to the beginning of each value.
5. Bedrooms - convert to integer value.

1.

```python
def null_values(properties):
    null_count= properties.isnull().sum()
    null_data= pd.DataFrame({'Column': null_count.index, 'Null values': null_count.values})
return null_data
```

```python
null= null_values(properties)
print(null)
```

```
     Column  Null values
0     Price            0
1  Location            0
2      Type            0
3      Link            0
4  Bedrooms           20
```

```python
properties.info()
```

```
<class 'pandas.core.frame.DataFrame'>
RangeIndex: 1024 entries, 0 to 1023
Data columns (total 5 columns):
 #   Column    Non-Null Count  Dtype
---  ------    --------------  -----
 0   Price     1024 non-null   object
 1   Location  1024 non-null   object
 2   Type      1024 non-null   object
 3   Link      1024 non-null   object
 4   Bedrooms  1004 non-null   float64
dtypes: float64(1), object(4)
memory usage: 40.1+ KB
```

```python
properties.dropna(inplace = True, axis = 0)
null_values(properties)
```

2.

```python
properties["Price"] = properties["Price"].str.replace("£", "").str.replace("pcm", "").str.replace(",","")
properties["Price"] = properties["Price"].astype(int)
properties["Price"]
```

```
0       1600
1       2900
2       1900
3       2390
4       3500
        ...
1019    2708
1020    1550
1021    4914
1022    1250
1023    3450
Name: Price, Length: 1004, dtype: int32
```

3.

```python
def extract_postcode(text):
    pattern= r"London,\s*([A-Za-z0-9]+)"
    match= re.search(pattern, text)
if match:
return match.group(1)
else:
return pd.NA

properties["Postcode"]= properties["Location"].apply(extract_postcode)
```

```python
null_values(properties)
```

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/cda5ffac-bbcb-4868-b1aa-209ef0ddd166/Untitled.png)

```python
properties.drop(columns = "Postcode", inplace = True) 

# Too many null values to be deemed viable
```

4.

```python
domain= "rightmove.co.uk"
properties["Link"]= domain+ properties["Link"]
```

5.

```python
properties["Bedrooms"] = properties["Bedrooms"].astype(int)
properties["Bedrooms"]
```

```
0       2
1       4
2       1
3       2
4       4
       ..
1019    2
1020    1
1021    1
1022    1
1023    2
Name: Bedrooms, Length: 1004, dtype: int32
```

Save the cleaned data:

```python
properties.to_csv(r"C:\Users\georg\Desktop\Data Centre\DataPython\Projects\London Rent Prices\rightmove_data.csv",
                  encoding= "UTF-8")
```

### Analyse the data:

Running queries on the data using PostgresSQL

```sql
SELECT * FROM properties
LIMIT 10;

-- Average rent of a property in London.
SELECT AVG(Price) AS AveragePrice
FROM properties;

-- Highest rent per month.
SELECT *
FROM properties
WHERE Price = (SELECT MAX(Price) FROM properties);

-- Top 10 Highest per month
SELECT * 
FROM properties
ORDER BY Price DESC
LIMIT 10;

-- Lowest rent per month. (property doesn't match the link, and the value is semi unrealisitic compared to the other lowest values)
SELECT *
FROM properties
WHERE Price = (SELECT MIN(Price) FROM properties);

-- Properties with the lowest rent per month.
SELECT *
FROM properties
ORDER BY Price ASC
LIMIT 10;

-- Deleting it from the table.
DELETE FROM properties
WHERE Price = 95;

-- Most bedrooms (this has returned incorrect data, not because of the scraping, but because it has been input incorrectly on the website).
SELECT *
FROM properties
WHERE Bedrooms = (SELECT MAX(Bedrooms) FROM properties);

-- We check to see if there are more unrealistic values...
SELECT *
FROM properties
ORDER BY Bedrooms DESC;

-- We remove it from the table.
DELETE FROM properties
WHERE Bedrooms = 1800;

-- Running the orginal query again.
SELECT *
FROM properties
WHERE Bedrooms = (SELECT MAX(Bedrooms) FROM properties);

-- Number of properties by property type.
SELECT Type, COUNT(*) AS PropertyCount
FROM properties
GROUP BY Type;

-- Average rent by property type.
SELECT Type, AVG(Price) AS AverageRent
FROM properties
GROUP BY Type;

-- Show properties located in a specific area.
SELECT *
FROM properties
WHERE Location LIKE '%Westminster%';

-- The average rent per bedroom.
SELECT Bedrooms, ROUND(AVG(Price), 2) AS AverageRentPerBedroom
FROM properties
GROUP BY Bedrooms
ORDER BY Bedrooms ASC;
```

### Using my street addresses to return geospacial co-ordinates using GoogleMaps API:

```sql
from googlemaps import Client as GoogleMaps
import pandas as pd 
import time
```

```sql
gmaps = GoogleMaps('APIKEY')
```

```python
file = r"C:\Users\georg\Desktop\Development\Data Centre\DataPython\Projects\London Rent Prices\rightmove_data.csv"
data= pd.read_csv(file)
data.head()
```

```python
data['longitude'] = ""
data['latitude'] = ""
```

```python
for x in range(len(data)):
    try:
        time.sleep(1) #to add delay in case of large DFs
        geocode_result = gmaps.geocode(data['Location'][x])
        data['latitude'][x] = geocode_result[0]['geometry']['location'] ['lat']
        data['longitude'][x] = geocode_result[0]['geometry']['location']['lng']
    except IndexError:
        print("Address was wrong...")
    except Exception as e:
        print("Unexpected error occurred.", e )
data.head()
```

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/f43d4479-c25b-4c4f-b43d-4851008b56c1/Untitled.png)

```python
new_file = r"C:\Users\georg\Desktop\Development\Data Centre\DataPython\Projects\London Rent Prices\geocords.csv"

data.to_csv(new_file)
```

### Cleaned CSV:

[Complete dataset.csv](https://www.dropbox.com/scl/fi/cmieklf841zpsv6cz6bkz/rightmove_geo.xlsx?rlkey=lnneox9vy86r0nkpoaf9vq67z&dl=0)

### Visualise:

Power BI - No filter on report

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/2a50deec-fca5-4f9e-8990-57cc0511d817/Untitled.png)

Power BI - Filtered by Apartment

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/5e067923-8f56-4147-b710-83876de8e7d6/Untitled.png)

Power BI - Filtered by House

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/7137dd28-cb6b-4391-8a85-299d1b9069cb/Untitled.png)

For access to the file:  [Power BI file](https://www.dropbox.com/scl/fi/iyykvcr3wytwygnyz2apx/rightmove.pbix?rlkey=0byczbzc05j27sa812ss1fmfq&dl=0)

### Tableau Viz:

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/3b766071-c9ae-422d-83d0-4c4e8a2099f3/Untitled.png)

Full version: [Tableau Viz](https://public.tableau.com/app/profile/george.horgan/viz/LondonpropertiesfromRightmovefilteredbypricepermonth/Sheet1)

![]([https://s3-us-west-2.amazonaws.com/secure.notion-static.com/c46d0eef-ae8c-498f-8276-d8e743b93eb1/Untitled.png](https://github.com/georgehorgan/Rightmove-properties/blob/main/images/rightmove_img8.png))

Full version: [Tableau Viz [2]](https://public.tableau.com/app/profile/george.horgan/viz/Rightmovesample-top10mostvsleastexpensivepropertiesforsale/Sheet1)

### Conclusions:

We found there are far more apartments/flats in London than any other living space, the average rent being £2,900.

We found little correlation between house prices and number of bedrooms, no relationship at all when reaching 4+ bedrooms.

Richer areas are far more concentrated within the city, whereas the cheaper area are more widely spread.

