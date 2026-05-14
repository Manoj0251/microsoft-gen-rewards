import sys
from time import sleep
import nltk
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from rewards_completer_v2 import BingRewardsAutomator
import random
from nltk.corpus import words
from pathlib import Path

def getCount(driver):
    val_totalRewards = 150
    count = 5
    driver.get("https://rewards.bing.com/pointsbreakdown")
    sleep(10)
    val_dailyRewards = int(driver.find_element(By.XPATH, "//a[contains(text(),'PC search')]/../../..//*[@class='pointsDetail c-subheading-3 ng-binding']/b").get_attribute("textContent"))
    print(val_dailyRewards)
    if val_totalRewards == val_dailyRewards:
        return count
    else:
        count = 1
        print("Executing Search")
        automator = BingRewardsAutomator()
        automator.run()
        return count

if __name__ == "__main__":
    edge_options = Options()
    edge_options.add_argument("--start-maximized")
    driver_path = Path(__file__).resolve().parent / "msedgedriver.exe"
    service = Service(str(driver_path))
    driver = webdriver.Edge(service=service, options=edge_options)

    driver.maximize_window()
    count = getCount(driver)
    if count == 1:
        driver.get("https://www.bing.com/?form=ML2XQD&OCID=ML2XQD&PUBL=RewardsDO&CREA=ML2XQD&toWww=1&redig=30BC9B06B18140EF83D3695DA99B5D4F")
        search_query = "Your search query here"
        sleep(10)
        search_input = driver.find_element(By.NAME, "q")
        search_input.send_keys(search_query)
        search_input.send_keys(Keys.RETURN)
        sleep(15)
        nltk.download('words')
        dictionary_words = words.words()
        for _ in range(40):
            random_word = random.choice(dictionary_words)
            print(random_word)
            icount = driver.find_element(By.CLASS_NAME, "points-container").text
            print(icount)
            search_input = driver.find_element(By.NAME, "q")
            search_input.send_keys(random_word)
            search_input.send_keys(Keys.RETURN)
            sleep(15)
            driver.refresh()
            driver.implicitly_wait(20)
            rcount2 = driver.find_element(By.CLASS_NAME, "points-container").text
            print(rcount2)
            driver.find_element(By.NAME, "q").click()
            driver.find_element(By.ID, "sw_clx").click()
            if count > 5 and icount == rcount2:
                sys.exit(1)
            else:
                print(count)
                count = count + 1
    else:
        print("Search Rewards completed")
        driver.quit()
        sys.exit(0)
