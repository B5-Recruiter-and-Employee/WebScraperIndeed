#import libraries we need for webscraping:
import csv
from datetime import datetime
import requests
from bs4 import BeautifulSoup



def get_url(position, location):
   
    template = 'https://www.indeed.com/q-WP{}-l-{}'
    #fill in the two curly brackets with the two variables used for the function call
    url = template.format(position, location)
    return url

url = get_url('senior accountant', 'charlotte nc') #creates an url looking for a senior accountant in charlotte nc

response = requests.get(url)

soup = BeautifulSoup(response.text, 'html.parser')

#will create a list of all the elements that will meet the search criteria
cards = soup.find_all('div', 'jobsearch-SerpJobCard')

card = cards[0]



def get_record(card):
    """Extract job data from a single record"""
    atag = card.h2.a 
    job_title = atag.get('title') 
    company_name = card.find('span', 'company').text.strip() 
    job_location = card.find('div', 'recJobLoc').get('data-rc-loc')
    try:
        job_salary = card.find('span', 'salaryText').text.strip()   #not all cards have a salary attached to them
    except AttributeError:
        job_salary = ''

    record = (job_title, company_name, job_location)