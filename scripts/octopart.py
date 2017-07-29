import urllib
import json
import urllib.parse
import urllib.request
import time


from forex_python.converter import CurrencyRates
c = CurrencyRates()


MY_API_KEY = 'ac2f2e4c'
ERROR_MSG = 'N/A'

def __request(query_params, other_params=False):
    #limit to less than 3 HTTP request / sec
    time.sleep(0.35)
    base_url = 'http://octopart.com/api/v3/parts/match?apikey=%s' % MY_API_KEY
    query_string = "&queries=%s" % urllib.parse.quote(json.dumps(query_params))
    if other_params:
        query_string = query_string + other_params
    # print base_url + query_string
    data = json.loads(urllib.request.urlopen(base_url + query_string).read().decode('utf-8'))
    if (data['results'][0]['hits'] == 0) or \
       (data['request']['queries'][0]['mpn_or_sku'] == "") or \
       (data['request']['queries'][0]['mpn_or_sku'] == 0.0):
        return False
    return data


# Fetches the Octopart URL for the part
def octopart_url(mpn_or_sku, manufacturer=False):

    query_params = [{ 'mpn_or_sku' : mpn_or_sku }]

    if manufacturer:
        query_params[0]['brand'] = manufacturer

    results = __request(query_params)
    if results:
        return results['results'][0]['items'][0]['octopart_url']
    return ERROR_MSG




# Fetches the datasheet URL for the part
def datasheet_url(mpn_or_sku, manufacturer=False):
    query_params = [{ 'mpn_or_sku' : mpn_or_sku }]

    if manufacturer:
        query_params[0]['brand'] = manufacturer

    results = __request(query_params, "&include[]=datasheets")
    if results and results['results'][0]['items'][0]['datasheets']:
        return results['results'][0]['items'][0]['datasheets'][0]['url']
    return ERROR_MSG
    


# Fetches the stock for the part, given a distributor
def disty_stock(distributor, mpn_or_sku, manufacturer=False):
    query_params = [
        { 'seller' : distributor,
          'mpn_or_sku' : mpn_or_sku }
        ]

    if manufacturer:
        query_params[0]['brand'] = manufacturer

    response = __request(query_params)

    if response and response['results'][0]['items']:
        for offer in response['results'][0]['items'][0]['offers']:
            if offer['seller']['name'] == distributor:
                return offer['in_stock_quantity']

    return ERROR_MSG


# Fetches the price for the part, given a distributor
def disty_price(distributor, mpn_or_sku, manufacturer=False):
    query_params = [
        { 'seller' : distributor,
          'mpn_or_sku' : mpn_or_sku }
        ]

    if manufacturer:
        query_params[0]['brand'] = manufacturer

    response = __request(query_params)

    if response and response['results'][0]['items']:
        for offer in response['results'][0]['items'][0]['offers']:
            if offer['seller']['name'] == distributor:
                if "EUR" in offer['prices']:
                    return offer['prices']['EUR'][0][1]
                elif "USD" in offer['prices']:
                    return c.convert('USD', 'EUR', float(offer['prices']['USD'][0][1]))

    return ERROR_MSG
    

# Fetches minimun order quantity, given a distributor
def disty_moq(distributor, mpn_or_sku, manufacturer=False):
    query_params = [
        { 'seller' : distributor,
          'mpn_or_sku' : mpn_or_sku }
        ]

    if manufacturer:
        query_params[0]['brand'] = manufacturer

    response = __request(query_params)

    if response and response['results'][0]['items']:
        for offer in response['results'][0]['items'][0]['offers']:
            if offer['seller']['name'] == distributor:
                return offer['moq']


    return ERROR_MSG



# Fetches the distributor's Buy Now link
def disty_url(distributor, mpn_or_sku, manufacturer=False):
    query_params = [
        { 'seller' : distributor,
          'mpn_or_sku' : mpn_or_sku }
        ]

    if manufacturer:
        query_params[0]['brand'] = manufacturer

    response = __request(query_params)

    if response and response['results'][0]['items']:
        for offer in response['results'][0]['items'][0]['offers']:
            if offer['seller']['name'] == distributor:
                return offer['product_url']

    return ERROR_MSG
