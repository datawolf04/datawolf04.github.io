import time
import sys

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup as BS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_url(station,date):
    """Given a PWS station ID and date, get the URL for that station ID and date
    
    Parameters
    ----------
        station : str
            The personal weather station ID
        date : str
            The date for which to acquire data, formatted as 'YYYY-MM-DD'
            
    Returns
    -------
        url : str
            The URL for that station ID and date
    """
    
    url = 'https://www.wunderground.com/dashboard/pws/%s/table/%s/%s/daily' % (station,
                                                                               date, date)

    return url

def print_tables(station,date):
    driver = webdriver.Chrome()
    driver.get(get_url(station,date))
    tables = WebDriverWait(driver,3).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "table")))

    for table in tables:
        newTable = pd.read_html(table.get_attribute('outerHTML'))
        if newTable:
            print(newTable[0].fillna(''))
    driver.quit()
