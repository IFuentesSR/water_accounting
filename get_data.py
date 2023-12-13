import pandas as pd
import time
from selenium import webdriver
from concurrent import futures
from selenium.webdriver.common.by import By


driver = webdriver.Chrome()
url = 'https://snia.mop.gob.cl/cExtracciones2/#/detalleObraBP/'


def get_CE(url_station):
    driver = webdriver.Chrome()
    driver.get(url_station)
    time.sleep(50)
    driver.refresh()
    time.sleep(8)
    driver.find_element(By.XPATH, '/html/body/app-root/div/div[2]/div/div/app-detalleobrabp/form/div[1]/div/accordion/accordion-group[1]/div/div[1]/div/div/button').click()
    time.sleep(2)
    test = driver.find_element(By.XPATH, '/html/body/app-root/div/div[2]/div/div/app-detalleobrabp/form/div[1]/div/accordion/accordion-group[1]/div/div[2]/div/div/div/div[10]/label[2]')
    time.sleep(2)
    if test.text == 'Superficial':
        driver.find_element(By.XPATH, '/html/body/app-root/div/div[2]/div/div/app-detalleobrabp/form/div[1]/div/accordion/accordion-group[9]/div/div[1]/div/div/button').click() #superficial
    else:
        driver.find_element(By.XPATH, '/html/body/app-root/div/div[2]/div/div/app-detalleobrabp/form/div[1]/div/accordion/accordion-group[10]/div/div[1]/div/div/button').click() #subterranea
    
    time.sleep(2)
    driver.find_element(By.NAME, 'inicio_periodo').send_keys('01/01/2011')
    time.sleep(2)
    driver.find_element(By.NAME, 'fin_periodo').send_keys('12/29/2022')
    time.sleep(2)
    driver.find_element(By.CSS_SELECTOR, 'button.buttons-nav:nth-child(2)').click()
    time.sleep(80)
    driver.close()
    time.sleep(10)



DF = pd.read_csv('data/CE_stations.csv')
points = DF['Código Obra'].tolist()
urls = [url+n for n in points]


## Runing on parallel (16 threads)
vals = list(range(0,len(urls),16))
for i,n in enumerate(vals[:]):
    with futures.ThreadPoolExecutor() as executor: # default/optimized number of threads
        titles = list(executor.map(get_CE, urls[n:n+16]))