#import libraries
import time
import re
import math
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
#from selenium.webdriver.chrome.service import Service
from selenium.webdriver.firefox.service import Service
#from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver import Firefox, Chrome
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
#from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

options = Options()
#options.headless = True
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.add_argument("start-maximized")

s = Service(GeckoDriverManager().install())
driver = Firefox(service=s, options=options)

#start web browser using chrome
#s = Service(ChromeDriverManager().install())
#driver = Chrome(service=s, options=options)

# define various property types
property_type = ["apartment", "furnished-apartment", "chalet", "villa", "land-or-farm", "building", 
                "administrative", "commercial", "medical", "shared-rooms", "land-or-commercial"]

#define search parameters for price
prices = [100000, 110000, 120000, 130000, 140000, 150000, 160000, 170000, 180000, 190000, 
          200000, 250000, 300000, 350000, 400000, 450000,
          500000, 600000, 700000, 800000, 900000, 1000000, 1250000, 1500000, 1750000, 2000000, 2250000,
          2500000, 2750000, 3000000, 3250000, 3500000, 3750000, 4000000,
          5000000, 6000000, 8000000, 10000000, 15000000, 20000000,
          30000000, 40000000, 50000000]

price_range = []

#creates various minimum and maximum price combination
for i,j in enumerate(prices):
    try:
        if i == 0:
            price_range.append((prices[i], prices[i+1]))
        else:
            price_range.append((prices[i] + 1 , prices[i+1]))
    except:
        pass
    
#define search parameters for area    
area = [10, 20, 30, 40, 50, 80, 100, 120, 150, 180, 200, 250, 300, 500, 1000, 5000]

area_range = []

#creates various minimum and maximum area combination
for i,j in enumerate(area):
    try:
        if i == 0:
            area_range.append((area[i], area[i+1]))
        else:
            area_range.append((area[i] + 1 , area[i+1]))
    except:
        pass    

#creates unique link for various combination of property type, area and price
links = []
for pt in property_type:
    
    for pr in price_range:
        minprice, maxprice = pr
        for ar in area_range:
            minarea, maxarea = ar
            url = "https://aqarmap.com.eg/en/for-sale/" + str(pt) + "/?minPrice=" +  \ str(minprice) + "&maxPrice=" + str(maxprice) + "&minArea=" + str(minarea) + "&maxArea=" + str(maxarea) + "&page=1"
            links.append(url)

#loop through unique pages to generate extended pages for each
extended_links = []
for lk in links:
    driver.get(lk)
    time.sleep(1)
    
    p = re.compile(r"Best Apartments For sale in .* (.*) Apartments of different .*")
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    text = soup.select("meta[name=description]")[0]["content"]

    no_items = int(p.match(text).group(1))
    no_pages = math.ceil(no_items/15)
    
    if i > 0:
        pg_range = np.arange(1, no_pages+1)
        for pg in pg_range:
            new_url = driver.current_url + "&page=" + str(pg)
            extended_links.append(new_url)

#generates property links
property_link = []
for xl in extended_links:
    driver.get(xl)
    
    time.sleep(3)
    prop_link = driver.find_elements(By.CSS_SELECTOR, "section.searchResultsPage > div ul.cta-option-1 a.search-listing-card__container__link")
    prop_link = [i.get_attribute("href") for i in prop_link]
    for lk in prop_link:
        property_link.append(lk)

result_list = []

#loops through property links to extract data
print("***********************************************")
print(len(property_link),"unique properties were found!")
print("Extracting data for each")
print("***********************************************")

count = 1
for p_link in property_link:
    print(str(count))
    count +=1

    driver.get(p_link)
    time.sleep(1.5)

    url = p_link
    try:
        price = driver.find_element(By.XPATH, "//div[@class='listing-price-content']").text.replace("\n", " ")
    except:
        price = ""

    try:
        title = driver.find_element(By.XPATH, "//div[@id='listing-title-container']//h1").text
    except:
        title = ""    

    try:
        location = driver.find_element(By.XPATH, "//div[@id='listing-title-container']//div[@class='listing_attributes']").text
    except:
        location = ""    

    try:
        comb_pr_type = driver.find_elements(By.XPATH, "//div[@id='listing-units']//tr/td[1]")
        comb_pr_type = [i.text for i in comb_pr_type]
        compound_type = ""
        for i in comb_pr_type:
            compound_type += i +(", ")
        compound_type = compound_type[:-2]    
    except:
        compound_type = ""    

    try:
        comb_pr_price = driver.find_elements(By.XPATH, "//div[@id='listing-units']//tr/td[2]")
        comb_pr_price = [i.text for i in comb_pr_price]
        compound_price = ""
        for i in comb_pr_price:
            compound_price += i +(", ")
        compound_price = compound_price[:-2]    
    except:
        compound_price = ""    

    try:
        comb_pr_size = driver.find_elements(By.XPATH, "//div[@id='listing-units']//tr/td[4]")
        comb_pr_size = [i.text for i in comb_pr_size]
        compound_size = ""
        for i in comb_pr_size:
            compound_size += i +(", ")
        compound_size = compound_size[:-2]    
    except:
        compound_size = ""  

    try:
        price_per_meter = driver.find_element(By.XPATH, "//li/span[contains(text(), 'Price Per Meter')]/following-sibling::span").text
    except:
        price_per_meter = price    

    try:
        rooms = driver.find_element(By.XPATH, "//li/span[contains(text(), 'Room')]/following-sibling::span").text
    except:
        rooms = ""    

    try:
        baths = driver.find_element(By.XPATH, "//li/span[contains(text(), 'Baths')]/following-sibling::span").text
    except:
        baths = ""    

    try:
        size_in_meters = driver.find_element(By.XPATH, "//li/span[contains(text(), 'Size (in meters)')]/following-sibling::span").text
    except:
        size_in_meters = ""      

    try:
        finish_type = driver.find_element(By.XPATH, "//li/span[contains(text(), 'Finish Type')]/following-sibling::span").text
    except:
        finish_type = ""   

    try:
        view = driver.find_element(By.XPATH, "//li/span[contains(text(), 'View')]/following-sibling::span").text
    except:
        view = ""    

    try:
        year_built = driver.find_element(By.XPATH, "//li/span[contains(text(), 'Year Built / Deliver Year')]/following-sibling::span").text
    except:
        year_built = ""    

    try:
        payment_method = driver.find_element(By.XPATH, "//li/span[contains(text(), 'Payment Method')]/following-sibling::span").text
    except:
        payment_method = ""    

    try:
        seller_role = driver.find_element(By.XPATH, "//li/span[contains(text(), 'Seller Role')]/following-sibling::span").text
    except:
        seller_role = ""

    try:
        description = driver.find_element(By.CSS_SELECTOR, "#listingDescriptionText").text
    except:
        description = ""   

    try:
        developer_name = driver.find_element(By.XPATH, "//div[@class='listing-info-container']//div[@class='user-card__name']").text
    except:
        developer_name = ""

    try:
        developer_details = driver.find_element(By.XPATH, "//div[@class='listing-info-container']//div[@class='user-card__stat']").text
        developer_details = developer_details.split(",")
        developer_year = ""
        developer_projects = ""

        for d in developer_details:
            if "Since" in d:
                developer_year = d.strip()
            if "Project" in d:
                developer_projects = d.strip()   
    except:
        developer_year = ""
        developer_projects = ""    

    try:
        main_url = driver.find_element(By.XPATH, "//div[@id='rg-gallery']//div[@class='rg-image w-100']/img").get_attribute("src")
    except:
        main_url = ""    

    result_dict = {
        "Title": title,
        "Price": price,
        "Location": location,
        "Compound Type": compound_type,
        "Compound Price": compound_price,
        "Compound Size": compound_size,
        "Price Per Meter": price_per_meter,
        "Rooms": rooms,
        "Baths": baths,
        "Size in Meters": size_in_meters,
        "Finish Type": finish_type,
        "View": view,
        "Year Built": year_built,
        "Payment Method": payment_method,
        "Seller Role": seller_role,
        "Description": description,
        "Developer Name": developer_name,
        "Developer Year": developer_year,
        "Developer Projects": developer_projects,
        "Main URL": main_url,
        "Property Link": p_link
    }

    result_list.append(result_dict)

#saves extracted data into dataframe
df = pd.DataFrame(result_list)
#saves extracted data into excel worksheet
df.to_excel("properties.xlsx", index=False)

#closes and quits browser
driver.close()
driver.quit()