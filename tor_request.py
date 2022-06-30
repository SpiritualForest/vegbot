import requests

def torRequest(url):
    session = requests.session()
    session.proxies = {'http':  'socks5://127.0.0.1:9050',
                       'https': 'socks5://127.0.0.1:9050'}
    try:
        response = session.get(url)
    except requests.exceptions.ConnectionError:
        print("torRequest() Connection error")
        response = None
    return response
