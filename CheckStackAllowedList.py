# Display IP list from Splunk Cloud (splunksupport) or direct
# Needs Python 3

import requests
import json
import sys


session = requests.Session()
targetStack = ""
# Set color options


class color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


# Create known options
knownOptions = {"search-api": ["Search head API access", "8089", "Grants access for customer subnets to Splunk search head api (applies to automated interfaces)"],
                "hec": ["HEC access for ingestion", "443", "Allows customer's environment to send HTTP data to Splunk indexers."],
                "s2s": ["Indexer ingestion", "9997", "Allows subnets that include UF or HF to send data to Splunk indexers."],
                "search-ui": ["SH UI access", "80/443", "Grant explicit access to search head UI in regulated customer environments."],
                "idm-ui": ["IDM UI access", "443", "Grant explicit access to IDM UI in regulated customer environments."],
                "idm-api": ["IDM API", "8089", "Grant access for add-ons that require an API. (Allows add-ons to send data to Splunk Cloud.)"]
                }

# Stack

#
# Need to give menu choice of using stack creds or token add
#


def getTokenAuth():
    login_token = "<enter token created in SH>"

    # Add token to header for auth
    session.headers.update({'Authorization': 'Bearer '+login_token})


targetStack = "<enter stack name>"


responseList = []

getTokenAuth()

try:
    # Get list of IP allowed list from the openAPI

    response_openAPI = requests.get(
        'https://admin.splunk.com/service/info/specs/v1/openapi.json', timeout=5)
    response_openAPI.raise_for_status()

    # convert to text and load into dictionary
    API_dump = json.loads(json.dumps(response_openAPI.json()))

    # grab from api list of available config
    API_dump_allowedOptions = (
        API_dump['components']['parameters']['feature']['schema']['enum'])

    for numberItemInAllowed in API_dump_allowedOptions:
        response = session.get(
            'https://admin.splunk.com/'+targetStack+'/adminconfig/v1/access/'+numberItemInAllowed+'/ipallowlists', timeout=5)
        responseList.append(json.loads(json.dumps(response.json())))
        response.raise_for_status()

    print("======================================")
    print("=     Listing of IP allowed list     =")
    print("====================================== \n")
    # reset counter
    section_counter = 0
    for numberItemInAllowed in API_dump_allowedOptions:
        try:
            knownOptionsItems = knownOptions[numberItemInAllowed]
            print(
                "----------------------------------------------------------------------------------------------")
            print("- "+color.BOLD+color.GREEN+knownOptionsItems[0]+color.END)
            print("- Port: "+knownOptionsItems[1])
            print("- Info: "+knownOptionsItems[2])
            print(
                "----------------------------------------------------------------------------------------------")

        except KeyError:
            print(
                "----------------------------------------------------------------------------------------------")
            print("- "+numberItemInAllowed)
            print("----------------------------------------------------------------------------------------------\n")

        # get array of ip address
        allowed_ip = responseList[section_counter].get('subnets')

        if not allowed_ip:
            print("< None Set >\n ")
        section_counter += 1
        # for number, letter in enumerate(allowed_ip):
        #    print(str(number+1)+")", letter)
        # print("\n")

        print(*allowed_ip, sep="\n")
        print("\n")
        
except requests.exceptions.HTTPError as errh:
    print(errh)
except requests.exceptions.ConnectionError as errc:
    print(errc)
except requests.exceptions.Timeout as errt:
    print(errt)
except requests.exceptions.RequestException as err:
    print(err)
