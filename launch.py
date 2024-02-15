from time import sleep
import nltk
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import random
from nltk.corpus import words

edge_options = Options()
# edge_options.add_argument('--headless')
driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()))
# , options=edge_options
# driver.capabilities("--enable-chrome-browser-cloud-management")
driver.maximize_window()
count = 1
driver.get("https://www.bing.com")
search_query = "Your search query here"
sleep(60)
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
    icount=driver.find_element(By.ID,"id_rc").text
    print(icount)
    search_input = driver.find_element(By.NAME, "q")
    search_input.send_keys(random_word)
    search_input.send_keys(Keys.RETURN)
    sleep(15)
    driver.refresh()
    driver.implicitly_wait(20)
    rcount2=driver.find_element(By.ID,"id_rc").text
    print(rcount2)
    driver.find_element(By.NAME,"q").click()
    driver.find_element(By.ID,"sw_clx").click()
    if(count > 5 and icount == rcount2):
        exit(1)
        # rcount=driver.find_element(By.ID,"id_rc").text
    else:
        print(count)
        count = count + 1
# Close the browser
# driver.quit()
