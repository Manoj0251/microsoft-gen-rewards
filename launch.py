import sys
from time import sleep
import nltk
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import random
from nltk.corpus import words

def getCount(driver):
    val_totalRewards = 150
    count = 5
    driver.get("https://rewards.bing.com/pointsbreakdown")
    sleep(10)
    val_dailyRewards = driver.find_element(By.XPATH, "//a[contains(text(),'PC search')]/../../..//*[@class='pointsDetail c-subheading-3 ng-binding']/b").text
    print(val_dailyRewards)
    if( val_totalRewards == val_dailyRewards ):
        return count
    else:
        count = 1
        print("Executing Search")
        return count


# edge_options.add_argument('--headless')
# driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()))
# , options=edge_options
# driver.capabilities("--enable-chrome-browser-cloud-management")


edge_options = Options()
edge_options.add_argument("--start-maximized")
service = Service("./msedgedriver.exe")
driver = webdriver.Edge(service=service, options=edge_options)

driver.maximize_window()
count = getCount(driver)
if(count == 1):
    driver.get("https://www.bing.com")
    search_query = "Your search query here"
    sleep(10)
    search_input = driver.find_element(By.NAME, "q")
    search_input.send_keys(search_query)
    search_input.send_keys(Keys.RETURN)
    sleep(15)
    nltk.download('words')
    # Get the list of English words
    dictionary_words = words.words()
    # Loop to generate random dictionary words
    for _ in range(40):
        random_word = random.choice(dictionary_words)
        print(random_word)
        icount=driver.find_element(By.CLASS_NAME,"points-container").text
        print(icount)
        search_input = driver.find_element(By.NAME, "q")
        search_input.send_keys(random_word)
        search_input.send_keys(Keys.RETURN)
        sleep(15)
        driver.refresh()
        driver.implicitly_wait(20)
        rcount2=driver.find_element(By.CLASS_NAME,"points-container").text
        print(rcount2)
        driver.find_element(By.NAME,"q").click()
        driver.find_element(By.ID,"sw_clx").click()
        if(count > 5 and icount == rcount2):
            sys.exit(1)
            driver.quit()
        else:
            print(count)
            count = count + 1
else:
    print("Search Rewards completed")
    driver.quit()
    sys.exit(0)