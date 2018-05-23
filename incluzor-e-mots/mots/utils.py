import requests
import json
from bs4 import BeautifulSoup


BASE_API_URL = "http://api.incluzor.fr:5005/"


def api_call(api_url, payload):
    response = requests.get(BASE_API_URL+"mots/"+api_url, params=payload)

    if response.status_code == 200:
        return json.loads(response.content.decode('utf-8'))
    else:
        return None


def get_fréquence(flexion_string):
    # Get ngrams counts
    res = api_call("fréquence", {"q": flexion_string})
    return res

