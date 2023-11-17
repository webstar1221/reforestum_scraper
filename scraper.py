import requests
import sys
import time
import csv
from bs4 import BeautifulSoup
from selenium import webdriver

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
    print('exporting csv file..')
    with open('reforestum_projects.csv', 'w') as file:
        writer = csv.DictWriter(file, results[0].keys())
        writer.writeheader()
        writer.writerows(results)
else:
   print('Not found any project..')
