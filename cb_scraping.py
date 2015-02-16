from selenium import webdriver
from selenium.common.exceptions import WebDriverException
import time
import sys

# # development open
# import pdb

def timeout_check(driver, secs, ready):
    """If page is not loaded within the time requirement, then exit"""
    reload_counter = 0
    passed_interactive_phase = ready
    while True:
        time.sleep(3)
        reload_counter += 3
        print("The readyState is {0}".format(driver.execute_script("return document.readyState")))
        if reload_counter > secs:
            print("Error: Connection timeout")
            driver.quit()
            sys.exit(1)

        if driver.execute_script("return document.readyState") == 'interactive':
            passed_interactive_phase = True

        if driver.execute_script("return document.readyState") == 'complete'\
            and passed_interactive_phase:
            break
    return None

def page_down(driver, times):
    for i in range(times):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        timeout_check(driver, 5, True)

def get_cb_content(link, output_page, max_pages):
    try:
        driver = webdriver.Chrome()
    except WebDriverException as e:
        print("chromedriver is not downloaded or Chrome is not installed\n"
            "Trying Firefox")
    except Exception as e:
        print(e)
        driver.quit()
        sys.exit()
    try:
        driver = webdriver.Firefox()
    except Exception as e:
        print(e)
        #TI: implement a wrapper class around webdriver (__enter__, __exit__)
        #    so I can use with statement for it
        driver.quit()
        sys.exit()

    #implement page check
    driver.get(link)
    driver.set_window_position(0, 0)

    #TI: implement console feedback
    timeout_check(driver, 20, True) #wait 20 seconds max for content
    page_down(driver, max_pages) #Scroll down once
    timeout_check(driver, 20, True) #wait 20 seconds max for content

    page_html = driver.page_source
    driver.quit()
    if output_page is not None:
        with open(output_page, "w") as f:
            f.write(page_html)
    return page_html

if __name__ == "__main__":
    get_cb_content("https://www.crunchbase.com/funding-rounds", "cb_funding-rounds.html")

