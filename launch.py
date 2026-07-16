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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def getCount(driver, timeout=15):
    """Check current daily rewards value and decide how many searches to run.

    This attaches the existing webdriver to BingRewardsAutomator if possible so
    the automator can reuse the same browser session.
    Returns an integer count: 5 when no searches needed, 1 when searches should run.
    """
    val_total_rewards = 150
    default_count = 5

    driver.get("https://rewards.bing.com/pointsbreakdown")
    try:
        # Wait for the specific element to appear instead of sleeping a fixed time
        xpath = "//a[contains(text(),'PC search')]/../../..//*[@class='pointsDetail c-subheading-3 ng-binding']/b"
        el = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))
        text = el.get_attribute("textContent") or "0"
        try:
            val_daily_rewards = int(text.strip())
        except ValueError:
            print(f"Could not parse daily reward value from '{text}'. Assuming 0.")
            val_daily_rewards = 0
    except TimeoutException:
        print("Timed out waiting for rewards page element; assuming 0 daily rewards.")
        val_daily_rewards = 0

    print(f"Daily rewards: {val_daily_rewards}")

    # Create automator and attach the driver if possible (works whether or not the class accepts driver in ctor)
    automator = BingRewardsAutomator()
    # prefer a setter if available, otherwise set attribute directly
    try:
        if hasattr(automator, "set_driver"):
            automator.set_driver(driver)
        elif hasattr(automator, "driver"):
            automator.driver = driver
    except Exception:
        # If automator doesn't accept attaching driver, continue anyway.
        print("Could not attach driver to BingRewardsAutomator instance; proceeding without attaching.")

    # Run automator to complete any automated tasks it encapsulates
    try:
        automator.run()
    except Exception as e:
        print(f"BingRewardsAutomator.run() raised an exception: {e}")

    if val_daily_rewards == val_total_rewards:
        return default_count
    else:
        print("Executing Search")
        return 1

if __name__ == "__main__":
    edge_options = Options()
    edge_options.add_argument("--start-maximized")
    driver_path = Path(__file__).resolve().parent / "msedgedriver.exe"
    service = Service(str(driver_path))
    driver = webdriver.Edge(service=service, options=edge_options)

    driver.maximize_window()
    # count = getCount(driver)
    count = 1
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
