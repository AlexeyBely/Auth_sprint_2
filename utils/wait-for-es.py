from backoff import backoff
from elasticsearch import Elasticsearch
from waiting import waiting


@backoff()
def ping_es(host, port):
    es = Elasticsearch([f'http://{host}:{port}/'], verify_certs=True)
    es.ping()
    es.close()


if __name__ == '__main__':
    waiting('ElasticSearch', ping_es, default_host='es', default_port='9200')
