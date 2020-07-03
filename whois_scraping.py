import os
import glob
import zipfile
import time
from datetime import datetime
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

countries = {
    'CN':'China',
    'HK':'Hong Kong',
    'BH':'Bahrain',
    'CZ':'Czech Republic',
    'EG':'Egypt',
    'DE':'Germany',
    'KW':'Kuwait',
    'LY':'Libiya',
    'NG':'Nigeria',
    'OM':'Oman',
    'QA':'Qatar',
    'SA':'Saudia Arabia',
    'SG':'Singapore',
    'ZA':'South Africa',
    'AE':'UAE',
}
user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) ' \
             'Chrome/80.0.3987.132 Safari/537.36'
            
project_dir = os.path.dirname(os.path.realpath(__file__))

# create download and output directories if not exist
download_dir = os.path.join(project_dir, 'download')
output_dir = os.path.join(project_dir, 'output_111')

if not os.path.isdir(download_dir):
    os.mkdir(download_dir)
if not os.path.isdir(output_dir):
    os.mkdir(output_dir)
    
# download zip files
def download_zip(url=None, name=None):
    if url and name:
        name = os.path.join(download_dir, name)
        response  = requests.get(url, headers={'User-Agent': user_agent})

        with open(name, 'wb') as f:
            for chunk in response.iter_content(chunk_size=255): 
                if chunk:
                    f.write(chunk)

# get the names of downloaded zip files in specific directory
def get_zip_files(path):
    try:
        os.chdir(path)
        result_files = glob.glob('*.zip')
    except:
        result_files = []
    return result_files

# read text content of all downloaded zip files
def read_txt_in_zip(result_files):
    domain_names = []
    for result_file in result_files:
        with zipfile.ZipFile(result_file) as z:
            with z.open('domain-names.txt', 'r') as f:
                for line in f:
                    domain_names.append(line.decode("utf-8").replace('\r\n', ''))
    domain_names = list(dict.fromkeys(domain_names))
    return domain_names
    
# remove all downloaded zip files
def remove_zip_files(result_files):
    for result_file in result_files:
        os.remove(result_file)

# set new chrome driver
def set_driver():
    chrome_option = webdriver.ChromeOptions()
    chrome_option.add_argument('--no-sandbox')
    chrome_option.add_argument('--disable-dev-shm-usage')
    chrome_option.add_argument('--ignore-certificate-errors')
    chrome_option.add_argument("--disable-blink-features=AutomationControlled")
    chrome_option.add_argument(f'user-agent={user_agent}')
    chrome_option.headless = True
    
    driver = webdriver.Chrome(executable_path=os.path.join(project_dir, 'chromedriver.exe'), options = chrome_option)
    driver.set_page_load_timeout(30)
    return driver

# --- download the sample domain zip files ---
url = "https://www.whoisdatadownload.com/newly-registered-domains"
driver = set_driver()
driver.get(url)
time.sleep(2)
zip_file_link = '//td/a[contains(@href, "newly-registered-domains")]'
links = driver.find_elements_by_xpath(zip_file_link)

name = 'domain_zip'
i = 1
for link in links:
    href = link.get_attribute('href')
    zip_name = name + '_' + str(i) + '.zip'
    download_zip(href, zip_name)
    time.sleep(5)
    i += 1

# get downloaded zip files
zip_files = get_zip_files(download_dir)
# get domain names of every zip files
domain_names = read_txt_in_zip(zip_files)    
# remove downloaded zip files
remove_zip_files(zip_files)

# write csv file
for domain_name in domain_names:
    try:
        driver = set_driver()
        domain_url = 'https://www.whois.com/whois/' + domain_name
        driver.get(domain_url)
        time.sleep(3)
        
        # get row whois data
        raw_whois_data = driver.find_element_by_id('registrarData').get_attribute("innerHTML")
        
        # get phone number from row whois data
        phone = raw_whois_data.split('Phone:')[1].split('\n')[0].strip()
        
        # get two letter of country code from row whois data
        country_short_letter = raw_whois_data.split('Country:')[1].split('\n')[0].strip()
        country = countries.get(country_short_letter)
        
        # get registered date from row whois data
        reg_date = raw_whois_data.split('Creation Date:')[1].split('\n')[0].strip()
        registered_date = reg_date[:10]
        
        try:
            # get email address
            driver.get('https://whois.whoisxmlapi.com/lookup')
            wait = WebDriverWait(driver, 30)
            wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@class="inputs-wrapper"]/input'))).send_keys(domain_name, Keys.ENTER)
            time.sleep(3)
            whois_data_values = driver.find_elements_by_xpath('//div[@class="output-child-row"]/span[contains(text(), "@")]')
            emails = []
            for whois_value in whois_data_values:
                w_value = whois_value.get_attribute("innerHTML")
                if '@' in w_value:
                    emails.append(w_value)
            if len(emails) > 0:
                email = emails[0]
            else:
                email = ''            
        except:
            email = ''
        print (domain_name, registered_date, phone, email, country)
        if registered_date and country:
            outcsv_path = os.path.join(output_dir, country + '.csv')
            if not os.path.exists(outcsv_path):
                with open(outcsv_path, 'w') as file_object:
                    file_object.write('Domain,Registered Date,Email,Phone,Country')
                    file_object.write('\n')
            with open(outcsv_path, 'a') as file_object:
                file_object.write(domain_name + ',' + registered_date + ',' + email + ',' + phone + ',' + country)
                file_object.write('\n')
    except Exception as inst:
        print(inst)
        pass
        
        
