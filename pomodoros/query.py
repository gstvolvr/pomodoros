from collections import defaultdict
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import configparser
import os
import time

def query_storage_sync():
    """
    query firefox's browser.storage.sync to pomodoro data from firefox "tomator clock" plugin
    """
    config = configparser.ConfigParser()
    config.read('config.ini')

    options = Options()
    options.headless = True

    profile = webdriver.FirefoxProfile(config['pomodoros']['profile_path'])
    driver = webdriver.Firefox(firefox_profile=profile, options=options)
    driver.implicitly_wait(100)

    try:
        url = config['pomodoros']['url']
        output_path = config['pomodoros']['output_path']

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

        if not output:
            driver.quit()
            raise ValueError("results are empty!")
            return
    except Exception as e:
        driver.quit()
        raise e

    elements = filter(lambda d: d['type'] == 'tomato', output['timeline'])
    days = defaultdict(int)

    for element in elements:
        date_obj = datetime.strptime(element['date'], "%a %b %d %Y %H:%M:%S %Z%z (Eastern Daylight Time)")
        day = datetime.strftime(date_obj, '%Y-%m-%d')
        days[day] += 1

    override_output_path = False
    if not os.path.exists(output_path):
        override_output_path = True
    else:
        with open(output_path, "r") as r:
            r.readline() # skip header
            processed = dict(map(lambda x: x.strip().split(','), r.readlines()))

    if override_output_path or len(processed.keys() & days.keys()) >= len(processed):
        with open(output_path, "w") as w:
            w.write("date,value\n")

            for d, v in sorted(days.items()):
                w.write(f"{d},{v}\n")
    else:
        print("something's up")

    driver.quit()
    return

if __name__ == '__main__':
    query_storage_sync()
