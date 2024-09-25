from collections import defaultdict
import json
import requests
from dotenv import load_dotenv
import os
import logging.config
from logging import getLogger
from art import tprint, DEFAULT_FONT
from send_to_openserarch_decorator import sent_data_to_opensearch

load_dotenv()

with open("./logging.conf") as log_file:
    config = json.load(log_file)

logging.config.dictConfig(config=config)
logger = getLogger()

@sent_data_to_opensearch
def get_data_from_opensearch():
    """This func gets data from Opensearch server, analyzes and returns filtered data for Opensearch-dashboard"""
    
    cpu_metrics = defaultdict(list)
    mem_metrics = defaultdict(set)

    query = {
        "_source": ["@timestamp", "cpu_p", "system_p", "user_p",
            "Mem.used", "Mem.free", "Mem.total",
        ],
        "size": 10,
        "from": 0,
        "sort": [
            {"@timestamp": {"order": "desc"}}
        ]
    }

    try:
        response = requests.get(url=os.getenv("URL"), headers=os.getenv("HEADERS"), data=json.dumps(query), verify=False)
        response.raise_for_status()

        if response.status_code == 200:
            data = response.json()

            for metric in data['hits']['hits']:
                for k, v in metric['_source'].items():
                    cpu_starts = ('cpu', 'user_p', 'system_p')
                    cpu_metrics[k].append(v) if k.startswith(cpu_starts) else mem_metrics[k].add(v) if k != "@timestamp" else None
            for k, v in cpu_metrics.items():
                cpu_metrics[k] = sum(v)

            return cpu_metrics, mem_metrics
        else:
            print(f"Error: {response.status_code}")
    except requests.exceptions.RequestException as error:
        logger.error("[-] Error %s", error)
        return f"{error}. Do something, bro"
    

def main():
    tprint("ALG_INNOVATIONS", font=DEFAULT_FONT)
    get_data_from_opensearch()


if __name__ == "__main__":
    logger.info("[+] Starting the data transfer to OpenSearch")
    print("[+] Starting the data transfer to OpenSearch")
    main()
    print("[+] Transfer data to OpenSearch completed")
    logger.info("[+] Transfer data to OpenSearch completed")