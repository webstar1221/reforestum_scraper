import requests
import sys
import time
import csv
from bs4 import BeautifulSoup
from selenium import webdriver

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Host': 'app.reforestum.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.2 Safari/605.1.15',
    'Accept-Language': 'en-gb',
    'Referer': 'https://app.reforestum.com/',
    'Connection': 'keep-alive',
}

login_url = 'https://app.reforestum.com/login/'

# get token
response = requests.get(login_url, headers=headers)
print('connecting to login page to get token..')
time.sleep(10)
soup = BeautifulSoup(response.content, 'html.parser')
try:
  token = soup.find('input', {'id':'_wpnonce'})['value']
  print(f'found token: {token}')
except:
  print('token not found.. exit')
  exit()

# login

cookies = {
    'PHPSESSID': '7pq0ohu5v4gvgf38p9umfirvot',
    '_ga': 'GA1.2.923748210.1611468192',
    '_gid': 'GA1.2.1435257517.1611468192',
    '_fbp': 'fb.1.1611468192145.947029952',
    '_mkto_trk': 'id:672-BAK-352&token:_mch-reforestum.com-1611468193546-81679',
    'wordpress_test_cookie': 'WP+Cookie+check',
    '_gat': '1',
}

headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'Origin': 'https://app.reforestum.com',
    'Content-Type': 'application/x-www-form-urlencoded',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document',
    'Referer': 'https://app.reforestum.com/login/',
    'Accept-Language': 'en-US,en;q=0.9',
}

data = {
  'username': 'foo',
  'password': 'bar',
  '_wpnonce': token,
  '_wp_http_referer': '/login/',
  'login': 'Login'
}

# start the session
s = requests.Session()

# post to page to login
s.post('https://app.reforestum.com/login/', headers=headers, cookies=cookies, data=data)
print('trying to login..')
time.sleep(10)

# check if login succesfull
print('check login success..')
response = s.get('https://app.reforestum.com/login/', headers=headers)
time.sleep(10)
soup = BeautifulSoup(response.content, 'html.parser')
# print(f"logged-in as {soup.find_all('a', {'class':'aboveHeaderLink'})[1].text}")

# collect projects
print('collecting projects..')

# use chrome browser with selenium
browser = webdriver.Chrome()
browser.get('https://app.reforestum.com/projects/discover/')
time.sleep(10)
soup = BeautifulSoup(browser.page_source, 'html.parser')

discover_results = soup.find('div', {'class' : 'discover__results'})
projects = discover_results.find_all('div', {'class' : 'discover__project__container'})
print(f'found {len(projects)} projects:')

base_url = 'https://app.reforestum.com'

# prepare list to store all projects
results = []
for row in range(len(projects)):        
    # prepare dict for each project    
    item = {}

    # collect title & url in each project
    print('collecting project tile & url..')
    item['Title'] = projects[row].find('div', {'class' : 'discover__project__title'}).text
    item['URL'] = base_url + projects[row].find('a', {'class' : 'discover__project__view-project'})['href']          
    
    # collect info details from each project
    print('collecting project info details..')
    project_info_blocks = projects[row].find_all('div', {'class' : 'tiny-info-block__wrapper'})
        
    for block in range(len(project_info_blocks)):
        # title of each detail
        title = project_info_blocks[block].find('span', {'class' : 'tiny-info-block__title'}).text
        
        # value of each detail
        value_wrapper = project_info_blocks[block].find('span', {'class' : 'tiny-info-block__value'})
        if value_wrapper.find('span'):
            if value_wrapper.find('span').find('div', {'class': 'tooltip'}): # 'Registry' detail
                # delete the container wrapped by HTML tags
                value_wrapper.find('span').find('div', {'class': 'tooltip'}).find('div').decompose()
                value = value_wrapper.find('span').find('div', {'class': 'tooltip'}).text                
            else: # 'Location' or 'Project Type' details
                value = value_wrapper.find('span').find('span').text                
        else: # 'Bezero Rating' detail
            value = value_wrapper.text
        item[title] = value
        
    # add each project to list
    results.append(item)

# save data to DataFrame
if len(results) > 0:
    with open('reforestum_projects.csv', 'w') as file:
        writer = csv.DictWriter(file, results[0].keys())
        writer.writeheader()
        writer.writerows(results)
else:
   print('Not found any project..')
