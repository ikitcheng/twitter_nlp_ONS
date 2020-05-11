from selenium import webdriver
from selenium.webdriver.support.ui import Select
import time

# chrome driver
driver = webdriver.Chrome()
driver.get("https://www.socialbakers.com/statistics/twitter/profiles/united-kingdom/brands")

# click 'show more button'
button = driver.find_element_by_link_text('Show More Brands Twitter Profiles in United Kingdom')
button.click()
time.sleep(10)

# fill form data
name = driver.find_elements_by_xpath("//input[@type='text' and @name='FullName']")[0].send_keys('UCL London')
email = driver.find_elements_by_xpath("//input[@type='email' and @name='Email']")[0].send_keys('disucl19@gmail.com')
phone = driver.find_elements_by_xpath("//input[@type='tel' and @name='Phone']")[0].send_keys('+44')
job = driver.find_elements_by_xpath("//input[@type='text' and @name='Job_Title__c']")[0].send_keys('job')
company = driver.find_elements_by_xpath("//input[@type='text' and @name='Company']")[0].send_keys('UCL')

# click 'submit' form data button
submit = driver.find_elements_by_xpath("//input[@type='submit' and @name='submitMktoForm']")[0]
submit.click()
time.sleep(10)

# run for 2 hours
end = time.time() + 60 * 60 * 2
# button = driver.find_element_by_link_text('Show More Brands Twitter Profiles in United Kingdom')
while time.time() < end:
    print("here")
    button = driver.find_element_by_link_text('Show More Brands Twitter Profiles in United Kingdom')
    button.click()
    time.sleep(3)
    
