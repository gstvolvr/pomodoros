from selenium.webdriver.firefox.options import Options
from selenium import webdriver
from datetime import datetime
from collections import defaultdict

import configparser
import time

"""
query firefox's browser.storage.sync to pomodoro data from "tomator clock" plugin
"""

def query_storage_sync(config):
    options = Options()
    options.headless = True

    profile = webdriver.FirefoxProfile(config['pomodoros']['profile_path'])
    driver = webdriver.Firefox(profile, options=options)
    url = config['pomodoros']['url']

    driver.get(url)

    query = """
        const getStorageData = key =>
          new Promise((resolve, reject) =>
            browser.storage.sync.get(key, result =>
              browser.runtime.lastError
                ? reject(Error(browser.runtime.lastError.message))
                : resolve(result)
            )
          )

        const timeline = getStorageData('timeline')
        return timeline
    """

    output = driver.execute_script(query.strip())
    time.sleep(0.5)

    if not output:
        print("go home you're drunk")
        return

    elements = filter(lambda d: d['type'] == 'tomato', output['timeline'])
    days = defaultdict(int)

    for element in elements:
        date_obj = datetime.strptime(element['date'], "%a %b %d %Y %H:%M:%S %Z%z (Eastern Daylight Time)")
        day = datetime.strftime(date_obj, '%Y-%m-%d')
        days[day] += 1

    with open("stats.csv", "w") as f:
        f.write("date,value\n")
        for d, v in sorted(days.items()):
            f.write(f"{d},{v}\n")

    # driver.quit()
    # driver.close()

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')
    query_storage_sync(config)
