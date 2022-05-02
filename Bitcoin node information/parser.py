from re import A
import requests
from requests.exceptions import HTTPError
import csv
from datetime import datetime

try:
    response = requests.get('https://bitnodes.io/api/v1/snapshots/latest/')
    response.raise_for_status()
    # access JSOn content
    jsonResponse = response.json()
    availableNodes = jsonResponse["nodes"]
    totalNodes = jsonResponse["total_nodes"]
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print("Current Time =", current_time)
    print("Total Nodes " + str(totalNodes))
    nononioncount = 0
    countedNodes = 0
    ASList = dict()
    for key, value in availableNodes.items():
        countedNodes = countedNodes + 1
        if("onion" not in key):
            nononioncount = nononioncount + 1
            ASno = value[11]
            if ASno in ASList:
                ASList[ASno] = ASList[ASno] + 1
            else:
                ASList[ASno] = 1
    with open('data.csv', 'w') as f:
        for key in ASList.keys():
            f.write("%s, %s\n" % (key, ASList[key]))
    print("Length of AS list " + str(len(ASList)))
    print("Non onion nodes " +  str(nononioncount))
    print("Onion nodes" + str((countedNodes - nononioncount)))
    print("Counted nodes " + str(countedNodes))

except HTTPError as http_err:
    print(f'HTTP error occurred: {http_err}')
except Exception as err:
    print(f'Other error occurred: {err}')