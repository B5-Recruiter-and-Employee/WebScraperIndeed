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

if __name__ == '__main__':
  logging.basicConfig(level=logging.ERROR)

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
                "location": {
                    "type": "keyword"
                    },
                "company_name": {
                    "type": "text"
                    },
                "salary": {
                    "type": "integer"
                },
                "description": {
                    "type": "text"
                    },
                "start_date": {
                    "type": "date",
                    "format": "yyyy-mm-dd"
                    },
                "job_keywords": {
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

# def Extract_Keywords(job_descrip): 
#     filtered_data = job_descrip.replace("\n", " ")
#     keywords = Sort_Tuple(rakeObj.run(filtered_data))[-10:]

def get_url(position, location):
    # TODO: More than just the US Version of Indeed (e.g UK,Germany...)
    template = 'http://www.indeed.com/jobs?q={}&l={}'
    url = template.format(position, location)
    return url


def get_record(card):
    # start data was not scrapped that is why default start date is always today.
    start_date = datetime.today().strftime('%Y-%m-%d')
    a_tag_from_card = card.h2.a
    job_title = a_tag_from_card.get('title')
    job_url = 'http://www.indeed.com' + a_tag_from_card.get('href')
    location = card.find('div', 'recJobLoc').get('data-rc-loc')
    try:
        company_name = card.find('span', 'company').text.strip()
    except AttributeError:
        company_name = ''
    job_summary = card.find('div', 'summary').text.strip()
    post_date = card.find('span', 'date').text
    today = datetime.today().strftime('%Y-%m-%d')
    try:
        salary = card.find('span', 'salaryText').text.strip()
    except AttributeError:
        salary = ''
    sleep(1)
    response_job_descr_website = requests.get(job_url)

    soup2 = BeautifulSoup(response_job_descr_website.text, 'html.parser')
    description = soup2.find('div', 'jobsearch-jobDescriptionText').get_text().replace("\n", '. ')
    keys = Sort_Tuple(rakeObj.run(description))[-10:]
    keywords = []
    # extract keywords from list of tuples w/o scores
    for a_tuple in keys:
        keywords.append(a_tuple[0])
    record_for_ES = {
        'job_title': job_title, 'location' : location, 'company_name': company_name, 'salary':salary, 'description': description, 'start_date':start_date, 'keywords':keywords
    }
    #record = (job_title, location, company_name, salary, description, start_date, keywords)
    return record_for_ES


def main(position, location,maxSize):
    records = []
    url = get_url(position, location)
    filename = position + " " + location + " " + datetime.today().strftime('%Y-%m-%d')
    size = 0
    flag = True
    while flag == True:
        sleep(1)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        cards = soup.find_all('div', 'jobsearch-SerpJobCard')
        for card in cards:
            if maxSize > size:
                record = get_record(card)
                records.append(record)
                size = size + 1
                print(size,maxSize)
            else:
                flag = False
                break
        try:
            url = 'http://www.indeed.com' + soup.find('a', {'aria-label': 'Next'}).get('href')
        except AttributeError:
            break
    # Connects to elastic search and send the data (job offer) one by one to the created index.
    #After running this file with command for location, position, size, everything will be stored in your kibana.
    #Look up the Index Management. There the index "job offer" is created. 
    es = connect_elasticsearch()
    if es is not None:
        if create_index(es, 'job_offers'):
            for record in records:
                out = store_record(es, 'job_offers', record)
            print('Data indexed successfully')

    #Csv file generation is commented out for now.
    # with open('%s.csv' % filename, 'w', newline='', encoding='utf-8') as f:
    #     writer = csv.writer(f)
    #     writer.writerow(
    #         ['job_title', 'location', 'company_name',  'salary', 'description', 'start_date', 'keywords'])
    #     writer.writerows(records)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Crawling Indeed Job Data')
    parser.add_argument('--position', type=str, required=True,
                        help='Position for Job Search')
    parser.add_argument('--location', type=str, required=True,
                        help='Location for Job Search')
    parser.add_argument('--maxSize', type=int, required=True,
                        help='sets the maxSize of the csv file')
    args = parser.parse_args()
    main(position=args.position, location=args.location, maxSize=args.maxSize)
