from datetime import datetime
import requests
from bs4 import BeautifulSoup
from time import sleep
import csv
import argparse
import nltk
import RAKE
import operator
import logging
from elasticsearch import Elasticsearch
import re #for the regex wildcards (word replacement)

stop_dir = nltk.corpus.stopwords.words('english') + ['arggis', 'others', 'us', 'plus', 'like']
rakeObj = RAKE.Rake(stop_dir)

# Connect to elastic search server.
# Ping pings the server and returns true if gets connected.
def connect_elasticsearch():
    _es = None
    _es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    if _es.ping():
        print('Yay Connect')
    else:
        print('Awww it could not connect!')
    return _es

# if __name__ == '__main__':
#   logging.basicConfig(level=logging.ERROR)

# Creates Index in elastic search.
# Can be checked after running this programm in Kibana: Stack Management/Index Management
def create_index(es_object, index_name):
    created = False
    # index settings
    settings = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        },
        "mappings": {
            "properties": {
                "job_title": {
                    "type": "text"
                },
                "job_location": {
                    "type": "keyword"
                },
                "company_name": {
                    "type": "text"
                },
                "job_salary": {
                    "type": "integer"
                },
                "description_text": {
                    "type": "text"
                },
                "keywords": {
                    "type": "text"
                }
            }
        }
    }

    try:
        if not es_object.indices.exists(index_name):
            # Ignore 400 means to ignore "Index Already Exist" error.
            #Creates an index with particular name with a template above.
            es_object.indices.create(index=index_name, ignore=400, body=settings)
            print('Created Index')
        created = True
    except Exception as ex:
        print(str(ex))
    finally:
        return created

# Adds the record (job offer) to the ES index.
def store_record(elastic_object, index_name, record):
    try:
        outcome = elastic_object.index(index=index_name, body=record)
    except Exception as ex:
        print('Error in indexing data')
        print(str(ex.info))

def Sort_Tuple(tup) :
    tup.sort(key = lambda x: x[1])
    return tup

def get_url(position, location):
    #TODO: More than just the US Version of Indeed (e.g UK,Germany...)

    #the template is the link of indeed, in which you fill out job title & location
    #job title is the first {} & job location is the second {}
    template = 'http://www.indeed.com/jobs?q={}&l={}'
    url = template.format(position, location)
    return url


def get_record(card):
    start_date = datetime.today().strftime('%Y-%m-%d')
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
    description_text = soup2.find('div', 'jobsearch-jobDescriptionText').get_text().replace("\n", ' ')
    description_text = re.sub(" \S+.com\S+", '', description_text)  #replaces every url that ends with .com (including backslashes with additional info, such as .com/info/details)
    description_text = re.sub(" \S+.org\S+", '', description_text)  #replaces every url that ends with .org (same as above)
    description_text = re.sub(" \S+@\S+", '', description_text)     #replaces every e-mail address
    description_text = re.sub(" https\S+", '', description_text)    #replaces any url that starts with https and the whitespace beforehand
    description_text = re.sub(" www.\S+", '', description_text)     #replaces any url that starts with www. and the whitespace beforehand
    description_text = re.sub("[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]", '', description_text)   #replaces all dates y-m-d
    description_text = re.sub("[0-9][0-9]/[0-9][0-9]/[0-9][0-9][0-9][0-9]", '', description_text)   #replaces all dates d/m/y
    description_text = re.sub("[0-9][0-9][0-9][0-9]+", '', description_text)    #replaces all numbers with 4 or more digits (years etc.)

    '''
    TODO:
        description_text is what needs to be cleaned. 
        'description_text.replace("\n", '. ') is the only cleaning that's been done so far (see above).
        we need to look at the results to decide what some of the common clutter looks like.
        DONE so far - (months, dots, addresses?)
    '''
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
    #If connected to ES, it sends the data (job offer) one by one to the created index.
    #After running this file with command for location, position, size, everything will be stored in your kibana.
    #Look up the Index Management. There the index "job offer" is created. 
    if es is not None:
        if create_index(es, 'job_offers'):
            for record in records:
                entry = { 'job_title': record[0], 'job_location' : record[1], 'company_name': record[2], 'job_salary': record[3], 'description_text': record[4], 'keywords': record[5]}
                out = store_record(es, 'job_offers', entry)
            print('Data indexed successfully')


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
    maxCards = [3, 3, 3 ]
    firstEntry = [True, False, False]
    
    es = connect_elasticsearch()
    i = 0
    for entry in position:
        main(position=position[i], location=location[i], maxCards=maxCards[i], firstEntry=firstEntry[i])
        i += 1