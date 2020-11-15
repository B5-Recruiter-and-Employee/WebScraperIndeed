from datetime import datetime
import requests
from bs4 import BeautifulSoup
from time import sleep
import csv
import argparse
import nltk
import RAKE
import operator

stop_dir = nltk.corpus.stopwords.words('english') + ['arggis', 'others', 'us', 'plus', 'like']
rakeObj = RAKE.Rake(stop_dir)

def Sort_Tuple(tup) :
    tup.sort(key = lambda x: x[1])
    return tup

def Extract_Keywords(job_descrip): 
    filtered_data = job_descrip.replace("\n", " ")
    keywords = Sort_Tuple(rakeObj.run(filtered_data))[-10:]

def get_url(position, location):
    #TODO: More than just the US Version of Indeed (e.g UK,Germany...)

    #the template is the link of indeed, in which you fill out job title & location
    #job title is the first {} & job location is the second {}
    template = 'http://www.indeed.com/jobs?q={}&l={}'
    url = template.format(position, location)
    return url


def get_record(card):
    atag = card.h2.a
    job_title = atag.get('title')
    job_url = 'http://www.indeed.com' + atag.get('href')
    job_location = card.find('div', 'recJobLoc').get('data-rc-loc')
    try:
        company_name = card.find('span', 'company').text.strip()
    except AttributeError:
        company_name = ''
    try:
        job_salary = card.find('span', 'salaryText').text.strip()
    except AttributeError:
        job_salary = ''
    sleep(1)
    response_job_descr_website = requests.get(job_url)

    #accesses the reloaded page in which the description can be seen
    soup2 = BeautifulSoup(response_job_descr_website.text, 'html.parser')
    description_text = soup2.find('div', 'jobsearch-jobDescriptionText').get_text().replace("\n", '. ')

    '''
    TODO:
        description_text is what needs to be cleaned. 
        'description_text.replace("\n", '. ') is the only cleaning that's been done so far (see above).
        we need to look at the results to decide what some of the common clutter looks like.
    '''
   # filtered_data  = description_text.replace("\n", '\n')
    keys = Sort_Tuple(rakeObj.run(description_text))[-10:]
    keywords = []
    #extract keywords from list of tuples w/o scores
    for a_tuple in keys:
        keywords.append(a_tuple[0])

    record = (
        job_title, job_location, company_name, job_salary, description_text, keywords)
    return record


def main(position, location, maxCards, firstEntry):
    records = []
    url = get_url(position, location)
    #filename = position + " " + location + " " + datetime.today().strftime('%Y-%m-%d') #original filename
    filename = 'collected_data'
    current_card = 0
    flag = True
    while flag == True:
        sleep(1)
        response = requests.get(url) #will send a request to the site & the response will be sent back (200 if successful)
        soup = BeautifulSoup(response.text, 'html.parser') #soup is used to navigate the html tree structure of the web page
        cards = soup.find_all('div', 'jobsearch-SerpJobCard') #find all cards with a div with the class 'jobsearch-SerpJobCard'
        for card in cards:
            if maxCards > current_card:
                record = get_record(card)
                records.append(record)
                current_card = current_card + 1
                print(current_card,maxCards)
            else:
                flag = False
                break
        try:
            url = 'http://www.indeed.com' + soup.find('a', {'aria-label': 'Next'}).get('href')
        except AttributeError:
            break

    with open('%s.csv' % filename, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if firstEntry == True:
            writer.writerow(
                ['job_title', 'job_location', 'company_name', 'job_salary','description_text','keywords'])
        writer.writerows(records)


if __name__ == '__main__':
    '''
    TODO:
        create a list with positions, corresponding locations, the max number of cards for each position
        and whether it's the first entry (except the first time always False)
    '''
    position = ['web developer', 'chemist', 'data scientist']
    location = ['new york', 'new york', 'san francisco']
    maxCards = [3, 3, 2]
    firstEntry = [True, False, False]
    
    i = 0
    for entry in position:
        main(position=position[i], location=location[i], maxCards=maxCards[i], firstEntry=firstEntry[i])
        i += 1
