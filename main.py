from datetime import datetime
import requests
from bs4 import BeautifulSoup
from time import sleep
import csv
import argparse


def get_url(position, location):
    #TODO: More than just the US Version of Indeed (e.g UK,Germany...)
    template = 'http://www.indeed.com/jobs?q={}&l={}'
    url = template.format(position, location)
    return url


def get_record(card):
    a_tag_from_card = card.h2.a
    job_title = a_tag_from_card.get('title')
    job_url = 'http://www.indeed.com' + a_tag_from_card.get('href')
    job_location = card.find('div', 'recJobLoc').get('data-rc-loc')
    try:
        company_name = card.find('span', 'company').text.strip()
    except AttributeError:
        company_name = ''
    job_summary = card.find('div', 'summary').text.strip()
    post_date = card.find('span', 'date').text
    today = datetime.today().strftime('%Y-%m-%d')
    try:
        job_salary = card.find('span', 'salaryText').text.strip()
    except AttributeError:
        job_salary = ''
    sleep(1)
    response_job_descr_website = requests.get(job_url)

    soup2 = BeautifulSoup(response_job_descr_website.text, 'html.parser')
    description_text = soup2.find('div', 'jobsearch-jobDescriptionText').get_text()
    record = (
        job_title, job_location, company_name, job_summary, post_date, today, job_salary, job_url, description_text)
    return record


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

    with open('%s.csv' % filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(
            ['job_title', 'job_location', 'company_name', 'job_summary', 'post_date', 'extract_date', 'job_salary', 'posting_url',
             'description_text'])
        writer.writerows(records)


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
