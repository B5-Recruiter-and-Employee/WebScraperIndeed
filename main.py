from datetime import datetime
import requests
from requests.exceptions import Timeout
from requests.exceptions import ConnectionError
from bs4 import BeautifulSoup
from time import sleep
import json
import argparse
import nltk
import RAKE
import operator
import logging
from elasticsearch import Elasticsearch
import re #for the regex wildcards (word replacement)

stop_dir = nltk.corpus.stopwords.words('english') + ['arggis', 'others', 'us', 'plus', 'like']
rakeObj = RAKE.Rake(stop_dir)

def Sort_Tuple(tup) :
    tup.sort(key = lambda x: x[1])
    return tup

def get_url(position, location):
    #the template is the link of stackoverflow, in which you fill out job title & location
    #job title is the first {} & job location is the second {}
    template = 'https://stackoverflow.com/jobs?q={}&l={}&d=10&u=Km'
    url = template.format(position, location)
    return url


def get_record(card):
    atag = card.h2.a
    job_title = atag.get('title')
    print(job_title, end=' @ ')
    job_url = 'https://stackoverflow.com' + atag.get('href')
    info = card.h3.find_all('span')
    
    try:
        if len(info[0].contents) > 1:
            company_name = info[0].contents[0].string.strip()
        else:
            company_name = info[0].text.strip()
        print(company_name)
    except AttributeError as e:
        company_name = ''
        print("[COMPANY NAME]: ", str(e))

    try:
        job_location = info[1].text.strip()
    except AttributeError as e:
        job_location = ''
        print("[JOB LOCATION]: ", str(e))

    hard_skills = []
    try:
        tags = card.find_all('a', 'post-tag')
        for tag in tags:
            hard_skills.append(tag.text.strip())
    except AttributeError as e:
        print("[HARD SKILLS]: ", str(e))

    sleep(1)
    try:
        response_job_descr_website = requests.get(job_url, timeout=10)
    except (Timeout, ConnectionError):
        print("JOB DETAILS: REQUEST TIMEOUT.")
        return None
    else:
        #accesses the reloaded page in which the description can be seen
        soup2 = BeautifulSoup(response_job_descr_website.text, 'html.parser')

        try:
            job_salary = soup2.find('span', '-salary').get('title')
        except AttributeError as e:
            job_salary = ''
        
        item = soup2.find('h2', string='Job description')
        try:
            description = item.find_parent('section').find_all('p')
            if not description:
                description = item.find_parent('section').find_all('div')
        except AttributeError as e:
            print("[DESCRIPTION + KEYWORDS]: ", str(e))
            return None
        else:
            text = ""
            for d in description:
                text = text + " " + d.text
            description_text = " ".join(text.split()).replace('*', '')
            clean = re.compile('<.*?>')
            description_text = re.sub(clean, '', description_text)          #replaces every HTML tag
            description_text = re.sub(clean, '', description_text)          #replaces every nested HTML tag
            description_text = re.sub(" \S+.com\S+", '', description_text)  #replaces every url that ends with .com (including backslashes with additional info, such as .com/info/details)
            description_text = re.sub(" \S+.org\S+", '', description_text)  #replaces every url that ends with .org (same as above)
            description_text = re.sub(" \S+@\S+", '', description_text)     #replaces every e-mail address
            description_text = re.sub(" https\S+", '', description_text)    #replaces any url that starts with https and the whitespace beforehand
            description_text = re.sub(" www.\S+", '', description_text)     #replaces any url that starts with www. and the whitespace beforehand
            description_text = re.sub("[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]", '', description_text)   #replaces all dates y-m-d
            description_text = re.sub("[0-9][0-9]/[0-9][0-9]/[0-9][0-9][0-9][0-9]", '', description_text)   #replaces all dates d/m/y
            description_text = re.sub("[0-9][0-9][0-9][0-9]+", '', description_text)    #replaces all numbers with 4 or more digits (years etc.)

            keys = Sort_Tuple(rakeObj.run(description_text))[-20:]
            keywords = []
            #extract keywords from list of tuples w/o scores
            for a_tuple in keys:
                keywords.append(a_tuple[0])
   
        record = {
            'job_title': job_title, 
            'location': job_location, 
            'company_name': company_name, 
            'salary': job_salary, 
            'description': description_text, 
            'work_culture_keywords': keywords,
            'hard_skills': hard_skills
            }
        return record


def main(search_request, maxCards):
    records = {}
    records['job_offers'] = []
    for search in search_request:
        position = search[0]
        location = search[1]
        url = get_url(position, location)
        print("\nJobs for %s in %s:" % (position, location))

        current_card = 0
        flag = True
        while flag == True:
            sleep(1)
            try:
                response = requests.get(url, timeout=10) #will send a request to the site & the response will be sent back (200 if successful)
            except (Timeout, ConnectionError):
                print("JOB POSITION: REQUEST TIMEOUT. RETRYING")
            else:
                soup = BeautifulSoup(response.text, 'html.parser') #soup is used to navigate the html tree structure of the web page
                cards = soup.find_all('div', '-job') #find all job cards
                for card in cards:
                    if maxCards > current_card:
                        print("%s / %s:" % (current_card+1,maxCards), end=' ')
                        record = get_record(card)
                        if record is not None:
                            records['job_offers'].append(record)
                            current_card = current_card + 1
                    else:
                        flag = False
                        break

    with open('collected_data.json', 'w', encoding='utf-8') as f:
        json.dump(records, f)
        f.close()


if __name__ == '__main__':
    max_cards_per_job_title = 10
    search_request = [
        ('web developer', 'new york'),
        ('software developer', 'chicago'),
        ('data scientist', 'atlanta'),
        ('devops', 'new york'),
        ('machine learning engineer', 'chicago'),
        ('android developer', 'atlanta'),
        ('ios developer', 'new york'),
        ('qa tester', 'chicago'),
        ('python developer', 'atlanta'),
        ('java developer', 'new york'),
        ('software architect', 'chicago'),
        ('frontend engineer', 'atlanta'),
        ('full-stack engineer', 'new york'),
        ('mobile developer', 'chicago'),
        ('backend engineer', 'atlanta'),
        ('web developer', 'san francisco'),
        ('software developer', 'denver'),
        ('data scientist', 'seattle'),
        ('devops', 'san francisco'),
        ('machine learning engineer', 'denver'),
        ('android developer', 'seattle'),
        ('ios developer', 'san francisco'),
        ('qa tester', 'denver'),
        ('python developer', 'seattle'),
        ('java developer', 'san francisco'),
        ('software architect', 'denver'),
        ('frontend engineer', 'seattle'),
        ('full-stack engineer', 'san francisco'),
        ('mobile developer', 'denver'),
        ('backend engineer', 'seattle')
    ]

    main(search_request, max_cards_per_job_title)