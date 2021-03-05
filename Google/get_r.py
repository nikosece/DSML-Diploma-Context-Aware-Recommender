from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import FirefoxOptions, FirefoxProfile
from selenium.webdriver.common.action_chains import ActionChains
import os
import pickle
import sys
import time


def save_pickle(var, name):
    with open(name + '.pickle', 'wb') as fle:
        pickle.dump(var, fle, protocol=pickle.HIGHEST_PROTOCOL)


class WebDriver:
    location_data = {}

    def __init__(self):
        self.PATH = "/home/anonymous/Documents/Diploma-Recommender/Google/geckodriver"
        self.options = FirefoxOptions()
        self.profile = FirefoxProfile('/home/anonymous/.mozilla/firefox/gxkovqyl.default-esr')

        #   Try adding this line if you get the error of chrome crashed
        #   self.options.binary_location = "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"
        self.options.add_argument("--headless")
        self.driver = webdriver.Firefox(
            executable_path='/home/anonymous/Documents/Diploma-Recommender/Google/geckodriver',
            options=self.options,
            firefox_profile=self.profile,
            service_log_path='/tmp/geckodriver.log')

    def get_location_data(self):
        try:
            # avg_rating = self.driver.find_element_by_class_name("section-star-display")
            # total_reviews = self.driver.find_element_by_class_name("section-rating-term")
            phone_number = self.driver.find_element_by_css_selector("[data-tooltip='Copy phone number']")
            website = self.driver.find_element_by_css_selector("[data-item-id='authority']")
        except Exception as e:
            sys.exit(e)

        try:
            # self.location_data["rating"] = avg_rating.text
            # total_reviews = total_reviews.text[0:-1].split(" ")[0]
            # if '.' in total_reviews:
            #     d = total_reviews.split('.')
            #     total_reviews = ''.join(d)
            # self.location_data["reviews_count"] = total_reviews
            self.location_data["contact"] = phone_number.text
            self.location_data["website"] = website.text
        except Exception as e:
            print(e)
            pass

    def click_all_reviews_button(self):
        try:
            WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "allxGeDnJMl__button")))

            element = self.driver.find_element_by_class_name("allxGeDnJMl__button")
            element.click()

        except Exception as e:
            print(e)
            return False

        return True

    def click_open_close_time(self):

        if len(list(self.driver.find_elements_by_class_name("cX2WmPgCkHi__section-info-hour-text"))) != 0:
            element = self.driver.find_element_by_class_name("cX2WmPgCkHi__section-info-hour-text")
            self.driver.implicitly_wait(8)
            flag = True
            try:
                ActionChains(self.driver).move_to_element(element).click(element).perform()
            except Exception as e:
                flag = False
            return flag

    def get_location_open_close_time(self):

        try:
            days = self.driver.find_elements_by_class_name("lo7U087hsMA__row-header")
            times = self.driver.find_elements_by_class_name("lo7U087hsMA__row-interval")

            day = [a.text for a in days]
            open_close_time = [a.text for a in times]

            for i, j in zip(day, open_close_time):
                self.location_data["Time"][i] = j

        except:
            print('Failed inside function')
            pass

    def scroll_the_page(self):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "section-layout-root")))  # Waits for the page to load.
            pause_time = 2  # Waiting time after each scroll.
            x = 0
            x_l1 = 0
            print("Total reviews are: {}".format(int(self.location_data["reviews_count"])))
            while x < int(self.location_data["reviews_count"]):
                scrollable_div = self.driver.find_element_by_css_selector(
                    'div.section-layout.section-scrollbox.scrollable-y.scrollable-show')
                try:
                    self.driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight',
                                               scrollable_div)  # Scroll it to the bottom.
                except Exception as e:
                    print(e)
                    pass

                time.sleep(pause_time)  # wait for more reviews to load.
                x_l2 = x_l1
                x_l1 = x
                x = len(self.driver.find_elements_by_class_name("section-review-reviewer-link"))
                print("Reviews now: {}".format(x))
                if x == x_l1 == x_l2:
                    break

        except Exception as e:
            print(e)
            pass

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
            review_stars_list = [a for a in review_stars_final]
            review_stars_list = [int(a.split('αστέρια')[0][1]) for a in review_stars_list]
            for (a, d) in zip(review_names_list, review_stars_list):
                self.location_data["Reviews"].append({"user_id": a, "rating": d})

        except Exception as e:
            sys.exit(e)

    def scrape(self, url):  # Passed the URL as a variable
        # self.location_data["rating"] = "NA"
        # self.location_data["reviews_count"] = "NA"
        # self.location_data["Reviews"] = []
        # self.location_data["contact"] = "NA"
        # self.location_data["website"] = "NA"
        self.location_data["Time"] = {"Δευτέρα": "NA", "Τρίτη": "NA", "Τετάρτη": "NA", "Πέμπτη": "NA",
                                      "Παρασκευή": "NA", "Σάββατο": "NA", "Κυριακή": "NA"}
        try:
            self.driver.get(url)  # Get is a method that will tell the driver to open at that particular URL

        except Exception as e:
            self.driver.quit()
            sys.exit(e)

        time.sleep(3.5)  # Waiting for the page to load.
        f_r = self.click_open_close_time()
        # self.get_location_data()  # Calling the function to get all the location data.
        if f_r:
            self.get_location_open_close_time()
        else:
            print('Click failed')
        # if not self.click_all_reviews_button():
        #     return self.location_data
        #
        # time.sleep(2.5)  # Waiting for the all reviews page to load.
        #
        # self.scroll_the_page()  # Scrolling the page to load all reviews.
        # self.get_reviews_data()  # Getting all the reviews data.

        # self.driver.quit()  # Closing the driver instance.

        return self.location_data  # Returning the Scraped Data.


def get_keys():
    all_res1 = set()
    for file in os.listdir("./schedule"):
        if file.endswith(".pickle"):
            test = pickle.load(open('./schedule/'+file, "rb"))
            if test['Time']['Δευτέρα'] != 'NA':
                all_res1.add(file.split(".")[0])
    return all_res1


def my_job(thead_keys):
    url1 = 'https://www.google.com/maps/place/?q=place_id:'
    total_b = 0
    print("Initialing browser")
    x_web = WebDriver()
    print("Browser initialized")
    for b_id in thead_keys:
        if b_id not in get_keys():
            url2 = url1 + b_id
            result = x_web.scrape(url2)
            save_pickle(result, './schedule/' + b_id)
            time.sleep(2.5)
            total_b = total_b + 1
            print("checked {} out of {}".format(total_b, len(thead_keys)))
            if total_b % 100 == 0:
                print("Closing session")
                x_web.driver.close()
                del x_web
                x_web = WebDriver()
                print("session reopened")


keys = pickle.load(open('./missing.pickle', "rb"))
all_res = get_keys()
keys = set(keys)
keys = keys - all_res
keys = list(keys)
keys.sort()
print("Total businesses are: ", len(keys))
slice_size = len(keys) // 7
j = int(sys.argv[1])
if len(keys) > j:
    sleep_time = int(sys.argv[2])
    start = j * slice_size
    end = start + slice_size
    if j == 6 or j+1 == len(keys):
        argument = keys[start:]
    else:
        argument = keys[start:end]
    print('Total files to read: ', len(argument))
    time.sleep(sleep_time)
    my_job(argument)
