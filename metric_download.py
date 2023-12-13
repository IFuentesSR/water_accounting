import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time




"""This code was done to automatically download rasters from the eeflux platform.
It needs calibration according to different user needs since it's hardcoded
based on our requirements"""


down_path = "user_defined_path_to_store_data"
tile_imgs = '233083' ## change accordingly
date_start = '2020-01-01'
date_end = '2020-12-31'

## setting profiler preferences 
profile = webdriver.FirefoxProfile()
profile.set_preference("browser.download.folderList", 2)
profile.set_preference("browser.download.manager.showWhenStarting", False)
profile.set_preference("browser.download.dir", down_path)
profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/x-gzip")

## loading driver
driver = webdriver.Firefox(profile)


url = 'https://eeflux-level1.appspot.com/'
driver.get(url)
time.sleep(1)







"""To find and store images"""
##maximises window
driver.maximize_window()
time.sleep(1)

##finds and fills boxes (modify dates as required)
driver.find_element(By.XPATH,
                    '//*[@id="date_start"]').clear()
driver.find_element(By.XPATH,
                    '//*[@id="date_start"]').send_keys(date_start)
time.sleep(2)
driver.find_element(By.XPATH,
                    '//*[@id="date_end"]').clear()
driver.find_element(By.XPATH,
                    '//*[@id="date_end"]').send_keys(date_end)


button = '/html/body/div[1]/div[2]/div/div/div[3]/div[1]/div[1]/div[4]/div[2]/img'
map = '/html/body/div[1]/div[2]/div/div/div/div[2]'
source1 = driver.find_element(By.XPATH, map)
action = ActionChains(driver)

##Coordinates for drag_and_drop_by_offset need to be changed accordingly
action.drag_and_drop_by_offset(source1, -200, -200).perform() 

time.sleep(1)

##Coordinates for drag_and_drop_by_offset need to be changed accordingly
source2 = driver.find_element(By.XPATH, button)
action = ActionChains(driver)
action.drag_and_drop_by_offset(source2, 350, 600).perform()

time.sleep(1)

##Coordinates for drag_and_drop_by_offset need to be changed accordingly
source3 = driver.find_element(By.XPATH, map)
action = ActionChains(driver)
action.drag_and_drop_by_offset(source1, 0, -200).perform()

time.sleep(1)

##Coordinates for drag_and_drop_by_offset need to be changed accordingly
source4 = driver.find_element(By.XPATH, button)
action = ActionChains(driver)
action.drag_and_drop_by_offset(source4, 10, 425).perform()

time.sleep(1)

imgs = '//*[@id="searchForImages"]'
driver.find_element(By.XPATH, imgs).click()
time.sleep(1)
dropdown = '//*[@id="dropdown"]'
driver.find_element(By.XPATH, dropdown).click()
time.sleep(1)
dd = '/html/body/div[1]/div[1]/div[7]/ul'


imgs_list = driver.find_elements(By.PARTIAL_LINK_TEXT, tile_imgs)








"""To Download images"""
for i, n in enumerate(imgs_list[:]):
    driver.find_element(By.XPATH, dropdown).click()
    time.sleep(2)
    n.click()
    time.sleep(2)

    etr = "/html/body/div[1]/div[1]/div[9]/div[2]/ul/li[12]/div[1]/button[3]/span"
    driver.find_element(By.XPATH, etr).click()
    time.sleep(15)
    try:
        action = ActionChains(driver)
        action.send_keys(Keys.TAB)
        
        action.send_keys(Keys.ENTER)
        action.perform()
    except:
        pass

    time.sleep(150)
    
    driver.find_element(By.XPATH, etr).click()
    time.sleep(15)
    if len([n for n in os.listdir(down_path) if n.endswith('.tif')]) < 2*i + 1:
        try:
            action = ActionChains(driver)
            action.send_keys(Keys.TAB)
            
            action.send_keys(Keys.ENTER)
            action.perform()
        except:
            pass
    time.sleep(30)
    while len([n for n in os.listdir(down_path) if n.endswith('.tif')]) < 2*i + 1:
        time.sleep(180)

        driver.find_element(By.XPATH, etr).click()
        time.sleep(15)
        if len([n for n in os.listdir(down_path) if n.endswith('.tif')]) < 2*i + 1:
            try:
                action = ActionChains(driver)
                action.send_keys(Keys.TAB)
                
                action.send_keys(Keys.ENTER)
                action.perform()
            except:
                pass
    time.sleep(30)
    

    etrf = "/html/body/div[1]/div[1]/div[9]/div[2]/ul/li[14]/div[1]/button[3]/span"
    time.sleep(2)
    driver.find_element(By.XPATH, etrf).click()
    time.sleep(15)
    try:
        action = ActionChains(driver)
        action.send_keys(Keys.TAB)
        
        action.send_keys(Keys.ENTER)
        action.perform()
    except:
        pass
    
    time.sleep(300)

    driver.find_element(By.XPATH, etrf).click()
    time.sleep(15)
    if len([n for n in os.listdir(down_path) if n.endswith('.tif')]) < 2*i + 2:
        try:
            action = ActionChains(driver)
            action.send_keys(Keys.TAB)
            
            action.send_keys(Keys.ENTER)
            action.perform()
        except:
            pass
    time.sleep(30)
    while len([n for n in os.listdir(down_path) if n.endswith('.tif')]) < 2*i + 2:
        time.sleep(180)

        driver.find_element(By.XPATH, etrf).click()
        time.sleep(15)
        if len([n for n in os.listdir(down_path) if n.endswith('.tif')]) < 2*i + 2:
            try:
                action = ActionChains(driver)
                action.send_keys(Keys.TAB)
                
                action.send_keys(Keys.ENTER)
                action.perform()
            except:
                pass
        time.sleep(30)
    
    time.sleep(2)
