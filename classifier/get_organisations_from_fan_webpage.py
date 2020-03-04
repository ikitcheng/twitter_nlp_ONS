from selenium import webdriver
from selenium.webdriver.support.ui import Select
import time

# chrome driver
driver = webdriver.Chrome()
driver.get("https://fanpagelist.com/category/brands/view/list/sort/followers/")

screen_names = []

def get_screen_name():
    links = driver.find_elements_by_xpath("//a[@class='clicky_ignore' and @href]")
    for link in links:
        name = link.get_attribute("href").split("=")[1]
        screen_names.append(name)
        print(name)


# run for 2 hours
end = time.time() + 60 * 60 * 2
while time.time() < end:
    # pull all html and store screen names
    get_screen_name()

    # click button
    # button = driver.find_elements_by_class_name("nav_links")[0]
    # button = driver.find_element_by_link_text('Next')
    # button = driver.find_elements_by_xpath("//div[@class='nev_links']/strong/a")[0]
    button = driver.find_element_by_xpath("//a[@href and contains(text(), 'Next')]")
    button.click()

    # allow delay
    time.sleep(3)


import pandas as pd
my_df = pd.DataFrame(screen_names)
my_df.to_csv('screen_names_organisations_user_handle.csv', index=False, header=False)