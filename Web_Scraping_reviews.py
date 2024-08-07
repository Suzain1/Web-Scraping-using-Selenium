#!/usr/bin/env python
# coding: utf-8

# In[1]:


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
import re
from datetime import datetime


# In[2]:


def setup_driver():
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    wait = WebDriverWait(driver, 15)  # Initialize WebDriverWait with a 10-second timeout
    return driver, wait


# In[3]:


def search_product(driver, wait, serial_number):
    driver.get('https://www.google.com')
    search_box = wait.until(EC.presence_of_element_located((By.NAME, 'q')))
    search_query = f"site:amazon.in {serial_number}"
    search_box.send_keys(search_query)
    search_box.send_keys(Keys.RETURN)
    time.sleep(1)
    try:
        first_result = wait.until(EC.element_to_be_clickable((By.XPATH, "(//h3[@class='LC20lb MBeuO DKV0Md'])[1]")))
        first_result.click()
        time.sleep(1)
    except:
        return "Currently unavailable"


# In[4]:


def check_name(driver,wait,serial_number):
    try:
        time.sleep(1)
        check_name_element=driver.find_element(By.XPATH,'//h1//span[@id="productTitle"]')
        check_name=check_name_element.text
        check_name=check_name.upper()
        combinations = [serial_number]
        
        dot_pos = serial_number.find('.')
        dash_pos = serial_number.find('-')
        if dot_pos != -1:
            combinations.append(serial_number[:dot_pos])
        if dash_pos != -1 and dash_pos != 2:
            combinations.append(serial_number[:dash_pos])
        if dash_pos != -1 and dot_pos != -1:
            middle_portion = serial_number[dash_pos + 1:dot_pos]
            if len(middle_portion)>2:
                combinations.append(middle_portion) 
            
        for item in combinations:
            if item in check_name:
                return True
        return False  
    except Exception:
        return False


# In[7]:


def scrape_reviews_and_stars(driver, wait):
    review_texts = []
    star_ratings = []

    try:
        see_more_reviews_button = wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, 'See more reviews')))
        driver.execute_script("arguments[0].scrollIntoView(true);", see_more_reviews_button)
        driver.execute_script("arguments[0].click();", see_more_reviews_button)
        print("Clicked on See more reviews")
    except TimeoutException:
        print("Timed out waiting for See more reviews button")
        return [], []
    except NoSuchElementException:
        print("See more reviews button not found")
        return [], []

    try:
        while True:
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'review-text')))
            reviews = driver.find_elements(By.CSS_SELECTOR, 'div.a-section.review')
            for review in reviews:
                try:
                    review_text = review.find_element(By.CSS_SELECTOR, 'span[data-hook="review-body"]').text.strip()
                    review_texts.append(review_text)
                    
                    star_rating_element = review.find_element(By.CSS_SELECTOR, 'span.a-icon-alt')
                    star_rating = star_rating_element.get_attribute('innerHTML').split()[0]
                    star_ratings.append(star_rating)
                except StaleElementReferenceException:
                    print("StaleElementReferenceException: Retrying element retrieval...")
                    # Retry fetching the elements
                    review = WebDriverWait(driver, 10).until(EC.visibility_of(review))
                    review_text = review.find_element(By.CSS_SELECTOR, 'span[data-hook="review-body"]').text.strip()
                    review_texts.append(review_text)
                    
                    star_rating_element = review.find_element(By.CSS_SELECTOR, 'span.a-icon-alt')
                    star_rating = star_rating_element.get_attribute('innerHTML').split()[0]
                    star_ratings.append(star_rating)
                except NoSuchElementException:
                    print("Review text or star rating element not found")

            try:
                next_button = driver.find_element(By.CSS_SELECTOR, '.a-last > a')
                if next_button:
                    driver.execute_script("arguments[0].click();", next_button)
                    WebDriverWait(driver, 20).until(EC.staleness_of(reviews[-1]))  
                else:
                    break  
            except NoSuchElementException:
                break 

        return review_texts, star_ratings

    except TimeoutException:
        print("Timed out waiting for reviews to load")
        return [], []
    except NoSuchElementException:
        print("Reviews not found")
        return [], []


# In[8]:


def save_to_excel(data, output_file):
    try:
        existing_df = pd.read_excel(output_file)
        updated_df = pd.concat([existing_df, data], ignore_index=True)
    except FileNotFoundError:
        updated_df = data

    updated_df.to_excel(output_file, index=False)
    print(f"Data has been written to {output_file}")


# In[9]:


def main(person_name, excel_file_path):
    # Read the Excel file to find the serial numbers assigned to the given person
    df = pd.read_excel(excel_file_path)
    serial_numbers = df[df['Assigned To'] == person_name]['Sales Model Code'].tolist()
    output_file = 'C:\\Users\\suzai\\reviews.xlsx'

    Reviews = []
    Stars = []
    
    all_serial_numbers = []
    sources = []


    for sn in serial_numbers:
        driver, wait = setup_driver()
        search_product(driver, wait, sn)
        
        
        reviews, stars = scrape_reviews_and_stars(driver, wait)
        Reviews.extend(reviews)  # Flatten the Reviews list by directly extending it
        Stars.extend(stars)
        all_serial_numbers.extend([sn] * len(reviews))
        
        
        sources.extend(["Amazon"] * len(reviews))


        driver.quit()
        if reviews and stars:
            data = {
                'Source': ["Amazon"] * len(reviews),
                'Model Number': [sn] * len(reviews),
                'Review': reviews,
                'Stars': stars
            }
            for key, value in data.items():
                print(f"Length of '{key}': {len(value)}")
    

            max_length = max(len(v) for v in data.values())
    
   
            for key, value in data.items():
                if not isinstance(value, list):
                   data[key] = [value]  # Convert non-list values to list
                if len(data[key]) < max_length:
                    data[key].extend([None] * (max_length - len(data[key])))

            df = pd.DataFrame(data)
            save_to_excel(df, output_file)

        driver.quit()
    
  


# In[10]:


person_name = "Suzain Rashid"  # Replace this your name
excel_file_path = 'C:\\Users\\suzai\\product_list_2.xlsx' #Replace with the path to your Excel file
main(person_name,excel_file_path)


# In[ ]:





# In[ ]:





# In[ ]:




