from elasticsearch import Elasticsearch
import json

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
                "job_title" : {"type": "text"},
                "location" : {"type": "keyword"},
                "company_name" : {"type": "text"},
                "salary" : { "type": "text" },
                "description" :{"type": "text"},
                "job_type" : {"type": "text"},

                "work_culture_keywords": {"type": "text"},

                "soft_skills" : {"type": "text"},
                "hard_skills" : {"type": "text"},
                "other_aspects" : {"type": "text"}
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
        elastic_object.index(index=index_name, body=record)
    except Exception as ex:
        print('Error in indexing data')
        print(str(ex))

if __name__ == "__main__":
    es = connect_elasticsearch()

    with open('collected_data.json', 'r') as f:
        data = json.load(f)

        #If connected to ES, it sends the data (job offer) one by one to the created index.
        #After running this file, everything will be stored in your kibana.
        #Look up the Index Management. There the index "job offer" is created. 
        if es is not None:
            if create_index(es, 'job_offers'):
                for d in data['job_offers']:
                    store_record(es, 'job_offers', d)
                print('Data indexed successfully')