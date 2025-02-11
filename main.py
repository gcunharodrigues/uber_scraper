import selenium.webdriver as webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from week_ranges import generate_week_ranges
from datetime import datetime
from itertools import chain
import json
import time
import os
import csv
from db_manager import insert_batch_data
import sqlite3
from dateutil import parser


def get_newest_date(database):
    db = sqlite3.connect(database)
    cursor = db.cursor()
    cursor.execute("SELECT DISTINCT date FROM ride_data")
    dates = cursor.fetchall()

    dates_list = []
    for date_str in dates:
        if len(date_str[0]) == 0:
            continue
        else:
            date = parser.parse(date_str[0]).strftime('%Y-%m-%d')
            dates_list.append(date)

    if dates_list:
        dates_list.sort()  # Sorts in ascending order
        newest_date = dates_list[-1]
    else:
        print("No dates found in the database.")

    db.close()
    return newest_date


def login(driver, otp, username, password):
    print("passing username")
    insert_username = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "PHONE_NUMBER_or_EMAIL_ADDRESS"))
    )
    insert_username.send_keys(username)
    driver.find_element(By.ID, "forward-button").click()

    time.sleep(1)
    if otp:
        print("passing OTP")
        for index, value in enumerate(otp):
            driver.find_element(By.ID, f"TOTP-{index}").send_keys(value)
    time.sleep(1)

    print("passing password")
    insert_password = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "PASSWORD"))
    )
    insert_password.send_keys(password)
    time.sleep(1)
    driver.find_element(By.ID, "forward-button").click()

    return print("Logged in!")


def load_more(driver):
    print("Loading more data")
    while True:
        try:
            # Wait until the "Load More" button is clickable
            load_more_button = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//button[text()="Load More"]'))
            )
            load_more_button.click()
            print("Clicked the 'Load More' button")

            # Optionally, wait for a brief period to ensure data loads
            time.sleep(1)

        except TimeoutException:
            # Exit the loop if the button is no longer found
            print("No more 'Load More' button found")
            break
    return print("All data loaded!")


def get_pages(driver):
    # Get all <a> elements on the page using By.TAG_NAME
    links = driver.find_elements(By.TAG_NAME, 'a')

    # Extract and print all href attributes
    hrefs = [link.get_attribute(
        'href') for link in links if link.get_attribute('href') is not None]
    hrefs = list(dict.fromkeys(hrefs))

    return hrefs


def get_data(driver):
    time.sleep(2)
    titles = driver.find_elements(By.CLASS_NAME, '_css-gFhnMl')
    info = [title.text for title in titles]
    if len(info) == 0:
        info = [None, None, None]
    else:
        info = info[0].split('\n')
        info = info[0].split(' • ')

    titles = driver.find_elements(By.CLASS_NAME, '_css-ctxyEy')
    details = [title.text for title in titles]
    if len(details) == 0:
        details = [None, None]
    else:
        details = details[0].split('\n')
        details = [details[1], details[3]]

    titles = driver.find_elements(By.CLASS_NAME, '_css-bqVtgW')
    address = [title.text for title in titles]
    if len(address) == 0:
        address = [None, None]
    else:
        address = address[0].split('\n')

    titles = driver.find_elements(By.CLASS_NAME, '_css-gukmVq')
    fare_driver = [title.text for title in titles]
    if len(fare_driver) == 0:
        fare_driver = [None, None]
    else:
        fare_driver = fare_driver[0].split('\n')
        fare_driver = [fare_driver[1], fare_driver[3]]

    titles = driver.find_elements(By.CLASS_NAME, '_css-dTqljZ')
    fare_details = [title.text for title in titles]
    if len(fare_details) == 0:
        fare_details = [None, None, None]
    else:
        fare_details = [fare_details[i:i + 2] for i in
                        range(0, len(fare_details), 2)]
        indexes_str = ['Total customer fare',
                       'Your earnings', 'Amount paid to Uber']
        fare_details = [fare_detail[1] for fare_detail in fare_details
                        if fare_detail[0] in indexes_str]

    rides_details = info+details+address+fare_driver+fare_details
    print("Got all data")

    return rides_details


def scrape_data(hrefs, driver):
    all_rides = []
    for index, href in enumerate(hrefs):
        try:
            # Navigate to the href
            driver.get(href)
            print(f"Visiting page {index + 1}: {href}")

            # Wait for the page to load (adjust as needed)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
            )

            # Find and click all expandable buttons
            expand_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "_css-hSdPIu"))
            )
            expand_button.click()
            print("Clicked 'More details' button to expand the section")

        except NoSuchElementException:
            print("No 'More details' button to expand the section")

        except TimeoutException:
            print("Page exceeded time to load.")

        finally:
            all_rides.append(get_data(driver))
            continue

    print("Scraping finished")

    return all_rides


def get_hrefs(driver, week_ranges, hrefs_all=[]):
    """
    Collect all hrefs from the given week ranges.

    Given a chrome driver and a list of week ranges, this function will navigate
    to each week, load all possible ride records, and return a list of all the
    hrefs of the ride records.

    :param driver: A chrome driver for navigating the web page.
    :param week_ranges: A list of week ranges in the form of "YYYY-MM-DD,YYYY-MM-DD"
    :param hrefs_all: An optional list to store the hrefs collected so far. Defaults to an empty list.
    :return: A list of all the hrefs of the ride records
    """
    time.sleep(5)  # Needs a better time handler

    for week in week_ranges:
        date_menu = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (driver.find_element(By.CLASS_NAME, "_css-fTDZjy")))
        )
        date_menu.click()
        date_menu.send_keys(Keys.CONTROL + 'a')
        date_menu.send_keys(week)
        print("Selected new date")
        load_more(driver)
        week_href = get_pages(driver)
        hrefs_all.append(week_href)

    hrefs_all = list(chain.from_iterable(hrefs_all))
    print(f"Got {len(hrefs_all)} pages.")

    return hrefs_all


def main():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    filepath = current_directory + '/login_data.json'
    with open(filepath, "r") as file:
        credentials = json.load(file)
    # Access the data
    username = credentials['username']
    password = credentials['password']

    otp = input("Please insert OTP: ")
    url = "https://drivers.uber.com/"

    # Options to avoid browser detection
    options = Options()
    options.add_argument("start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    # options.add_argument('--disable-gpu')

    chrome_path = r"C:\Users\guicr\OneDrive\Carreira\selenium_drivers\chromedriver.exe"
    driver = webdriver.Chrome(service=Service(chrome_path), options=options)

    driver.get(url)

    login(driver, otp, username, password)

    # start_date = datetime(2025, 2, 10)
    start_date = get_newest_date('ride_data.db')
    end_date = datetime(2025, 2, 10)
    week_ranges = generate_week_ranges(start_date, end_date)
    hrefs = get_hrefs(driver, week_ranges)
    rides = scrape_data(hrefs, driver)
    insert_batch_data('ride_data.db', rides)

    driver.quit()

    # with open(current_directory + '/output_test.csv', 'w', newline='') as file:
    #     writer = csv.writer(file)
    #     writer.writerows(rides)


if __name__ == "__main__":
    main()
