from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

import csv
import time

# Reference: https://stackoverflow.com/questions/75171579/how-to-extract-all-the-google-reviews-from-google-map

# specify the url of the business page on Google
url = 'https://www.google.com/maps/place/Tim+Hortons/@45.4618595,-73.8564478,14z/data=!4m12!1m2!2m1!1stim+horton!3m8!1s0x4cc93baa64205939:0xb5f74f9f8d78044f!8m2!3d45.4618595!4d-73.818339!9m1!1b1!15sCgp0aW0gaG9ydG9uIgOIAQFaDCIKdGltIGhvcnRvbpIBC2NvZmZlZV9zaG9w4AEA!16s%2Fg%2F1wtbthxn?entry=ttu'

# create an instance of the Chrome driver
driver = webdriver.Chrome()
driver.maximize_window()

# navigate to the specified url
driver.get(url)

# Wait for the reviews to load
wait = WebDriverWait(driver, 1000) # increased the waiting time

n_reviews_selector = "div.Bd93Zb div.fontBodySmall"
review_span_selector = "div.MyEned span.wiI7pd"
rating_span_class = "kvMYJc"
reviewer_name_class = "d4r55"
parent_container_selector = "div.k7jAl.miFGmb.lJ3Kh div.e07Vkf.kA9KIf div.aIFcqe div.m6QErb.WNBkOb.XiKgde"
container_selector = "div.m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde"
see_more_btn_selector = "div.MyEned span button"
see_more_btn_text = "See more"

def update_loop():
    reviews = {}
    reviewers = {}
    ratings = {}

    review_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, review_span_selector)))
    review_ratings = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, rating_span_class)))
    reviewer_names = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, reviewer_name_class)))

    for i, (rev, rating, name) in enumerate(zip(review_elements, review_ratings, reviewer_names)):
        reviews[i] = rev.get_attribute("textContent")
        reviewers[i] = name.text
        ratings[i] = rating.get_attribute("aria-label").split(" ")[0]

    # Scroll down and wait.
    parents = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, parent_container_selector)))
    for el in parents:
        if el.get_attribute("aria-label") == "Tim Hortons":
            container = el.find_element(By.CSS_SELECTOR, container_selector)
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", container)
            time.sleep(1)

    return reviews, reviewers, ratings

def click_all_buttons():
    see_more_btns = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, see_more_btn_selector)))
    for btn in see_more_btns:
        if btn.get_attribute("aria-label") == see_more_btn_text:
            btn.click()

n_reviews = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, n_reviews_selector))).get_attribute("textContent").split(' ')[0].replace(',','').replace('.','')

print("Number of ratings: ", n_reviews)

n_found = 0
reviews = {}
reviewers = {}
ratings = {}

while n_found < int(n_reviews):
    reviews, reviewers, ratings = update_loop()
    
    print("Found: ", len(reviews))

    # Quit when there are ratings remaining but no review.
    if n_found == len(reviews):
        break

    n_found = len(reviews)

    time.sleep(.5)    

# See all full reviews.
click_all_buttons()

# Perform one last loop.
reviews, reviewers, ratings = update_loop()

# Export to csv.
fields = ["Author", "Rating", "Review"]
with open('data/reviews.csv', 'w', newline='', encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(fields)
    for i in range(len(reviews)):
        writer.writerow([reviewers[i], ratings[i], reviews[i]])

driver.quit()