"""Module to scrape 5-min personal weather station data from Weather Underground.

Usage is:
>>> python scrape_wunderground.py   STATION    DATE

where station is a personal weather station (e.g., KCAJAMES3) and date is in the 
format YYYY-MM-DD. 

Alternatively, each function below can be imported and used in a separate python
script. Note that a working version of chromedriver must be installed and the absolute 
path to executable has to be updated below ("chromedriver_path").

Zach Perzan, 2021-07-28"""

import time
import sys

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup as BS
from selenium import webdriver


# Set the absolute path to chromedriver
chromedriver_path = '/usr/local/bin/chromedriver'


def render_page(url):
    """Given a url, render it with chromedriver and return the html source
    
    Parameters
    ----------
        url : str
            url to render
    
    Returns
    -------
        r : 
            rendered page source
    """
    
    driver = webdriver.Chrome(chromedriver_path)
    driver.get(url)
    time.sleep(3) # Could potentially decrease the sleep time
    r = driver.page_source
    driver.quit()

    return r


def scrape_wunderground(station, date):
    """Given a PWS station ID and date, scrape that day's data from Weather 
    Underground and return it as a dataframe.
    
    Parameters
    ----------
        station : str
            The personal weather station ID
        date : str
            The date for which to acquire data, formatted as 'YYYY-MM-DD'
            
    Returns
    -------
        df : dataframe or None
            A dataframe of weather observations, with index as pd.DateTimeIndex 
            and columns as the observed data
    """
    
    # Render the url and open the page source as BS object
    url = 'https://www.wunderground.com/dashboard/pws/%s/table/%s/%s/daily' % (station,
                                                                               date, date)
    r = render_page(url)
    soup = BS(r, "html.parser",)

    container = soup.find('lib-history-table')
    
    # Check that lib-history-table is found
    if container is None:
        raise ValueError("could not find lib-history-table in html source for %s" % url)
    
    # Get the timestamps and data from two separate 'tbody' tags
    all_checks = container.find_all('tbody')
    time_check = all_checks[0]
    data_check = all_checks[1]

    # Iterate through 'tr' tags and get the timestamps
    hours = []
    for i in time_check.find_all('tr'):
        trial = i.get_text()
        hours.append(trial)

    # For data, locate both value and no-value ("--") classes
    classes = ['wu-value wu-value-to', 'wu-unit-no-value ng-star-inserted']

    # Iterate through span tags and get data
    data = []
    for i in data_check.find_all('span', class_=classes):
        trial = i.get_text()
        data.append(trial)

    columns = ['Temperature', 'Dew Point', 'Humidity', 'Wind Speed', 
               'Wind Gust', 'Pressure', 'Precip. Rate', 'Precip. Accum.']

    # Convert NaN values (stings of '--') to np.nan
    data_nan = [np.nan if x == '--' else x for x in data]

    # Convert list of data to an array
    data_array = np.array(data_nan, dtype=float)
    data_array = data_array.reshape(-1, len(columns))

    timestamps = ['%s %s' % (date, t) for t in hours]
    ts = pd.DataFrame({'timestamps': timestamps})

    # Convert to dataframe
    da = pd.DataFrame(data_array,columns=columns)
    df = pd.concat([ts, da], axis=1)
    
    return df


def scrape_multiattempt(station, date, attempts=4, wait_time=5.0):
    """Try to scrape data from Weather Underground. If there is an error on the 
    first attempt, try again.
    
    Parameters
    ----------
        station : str
            The personal weather station ID
        date : str
            The date for which to acquire data, formatted as 'YYYY-MM-DD'
        attempts : int, default 4
            Maximum number of times to try accessing before failuer
        wait_time : float, default 5.0
            Amount of time to wait in between attempts
            
    Returns
    -------
        df : dataframe or None
            A dataframe of weather observations, with index as pd.DateTimeIndex 
            and columns as the observed data
    """
    
    # Try to download data limited number of attempts
    for n in range(attempts):
        try:
            df = scrape_wunderground(station, date)
        except:
            # if unsuccessful, pause and retry
            time.sleep(wait_time)
        else: 
            # if successful, then break
            break
    # If all attempts failed, return empty df
    else:
        df = pd.DataFrame()
        
    return df
