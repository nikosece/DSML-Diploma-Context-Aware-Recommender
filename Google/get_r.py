from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import FirefoxOptions, FirefoxProfile
from seleniumrequests import Firefox
from selenium.webdriver.common.action_chains import ActionChains
import time


class WebDriver:
    location_data = {}

    def __init__(self):
        self.PATH = "/home/anonymous/Documents/Diploma-Recommender/Google/geckodriver"
        self.options = FirefoxOptions()
        self.profile = FirefoxProfile('/home/anonymous/.mozilla/firefox/gxkovqyl.default-esr')

        #   Try adding this line if you get the error of chrome chrashed
        #   self.options.binary_location = "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"
        self.options.add_argument("--headless")
        self.driver = Firefox(executable_path='/home/anonymous/Documents/Diploma-Recommender/Google/geckodriver',
                              options=self.options,
                              firefox_profile=self.profile,
                              service_log_path='/tmp/geckodriver.log')

        self.location_data["rating"] = "NA"
        self.location_data["reviews_count"] = "NA"
        self.location_data["Reviews"] = []

    def get_location_data(self):
        try:
            avg_rating = self.driver.find_element_by_class_name("section-star-display")
            total_reviews = self.driver.find_element_by_class_name("section-rating-term")
        except:
            pass

        try:
            self.location_data["rating"] = avg_rating.text
            total_reviews = total_reviews.text[0:-1].split(" ")[0]
            if '.' in total_reviews:
                d = total_reviews.split('.')
                total_reviews = ''.join(d)
            self.location_data["reviews_count"] = total_reviews
        except:
            pass

    def click_all_reviews_button(self):
        try:
            WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "allxGeDnJMl__button")))

            element = self.driver.find_element_by_class_name("allxGeDnJMl__button")
            element.click()

        except:
            self.driver.quit()
            return False

        return True

    def scroll_the_page(self):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "section-layout-root")))  # Waits for the page to load.
            pause_time = 2  # Waiting time after each scroll.
            max_count = 5  # Number of times we will scroll the scroll bar to the bottom.
            x = 0

            while x < max_count:
                scrollable_div = self.driver.find_element_by_css_selector(
                    'div.section-layout.section-scrollbox.scrollable-y.scrollable-show')  # It gets the section of the scroll bar.
                try:
                    self.driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight',
                                               scrollable_div)  # Scroll it to the bottom.
                except:
                    pass

                time.sleep(pause_time)  # wait for more reviews to load.
                x = x + 1

        except:
            self.driver.quit()

    def get_reviews_data(self):
        try:
            review_names = self.driver.find_elements_by_class_name(
                "section-review-reviewer-link")  # Its a list of all the HTML sections with the reviewer name.
            # review_text = self.driver.find_elements_by_class_name(
            #     "section-review-review-content")  # Its a list of all the HTML sections with the reviewer reviews.
            review_stars = self.driver.find_elements_by_css_selector(
                "[class='section-review-stars']")  # Its a list of all the HTML sections with the reviewer rating.

            review_stars_final = []

            for i in review_stars:
                review_stars_final.append(i.get_attribute("aria-label"))

            review_names_list = [a.get_attribute('href').split('/')[5] for a in review_names]
            # review_text_list = [a.text for a in review_text]
            review_stars_list = [a for a in review_stars_final]
            review_stars_list = [int(a.split('αστέρια')[0][1]) for a in review_stars_list]
            for (a, d) in zip(review_names_list, review_stars_list):
                self.location_data["Reviews"].append({"user_id": a, "rating": d})

        except Exception as e:
            pass

    def scrape(self, url):  # Passed the URL as a variable
        try:
            self.driver.get(url)  # Get is a method that will tell the driver to open at that particular URL

        except Exception as e:
            self.driver.quit()
            return

        time.sleep(10)  # Waiting for the page to load.

        self.get_location_data()  # Calling the function to get all the location data.

        if not self.click_all_reviews_button():  # Clicking the all reviews button and redirecting the driver to the all reviews page.
            return self.location_data

        time.sleep(5)  # Waiting for the all reviews page to load.

        self.scroll_the_page()  # Scrolling the page to load all reviews.
        self.get_reviews_data()  # Getting all the reviews data.

        self.driver.quit()  # Closing the driver instance.

        return self.location_data  # Returning the Scraped Data.
