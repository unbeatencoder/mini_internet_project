import subprocess
import json
from datetime import datetime

#Check the name of the container to identify the data.
containerName = subprocess.check_output("hostname", shell=True)
containerName = containerName.decode("utf-8")[:-1]
#Create a file in the /etc/containerData volume which is the shared directory between containers and our machine.
#Change first path of the folder to your own path in : platform/setup/container_setup.sh
#Replace : home/kirtan/mini_internet_project/containerData with your own folder where you want data to be collated.
fileName = '/etc/containerData/'+'{}.txt'.format("outputOf" + containerName)
outPutFile = open(fileName, "w")
outPutFile.write(containerName + '\n')
outPutFile.flush()
previousNumberOfBlocks = 0
while(1):
    currentTime = datetime.now().strftime("%m/%d/%Y, %H:%M:%S:%f")
    output = subprocess.check_output("bitcoin-cli getblockchaininfo", shell=True)
    jsonoutput = json.loads(output)
    numberOfBlocks = jsonoutput["blocks"]
    if(numberOfBlocks > previousNumberOfBlocks):
        #Also add hash of the block that was received 
        outPutFile.write('block no. ' + str(numberOfBlocks) + ' currentTime : ' + currentTime + ' blockhash: ' + jsonoutput["bestblockhash"] + '\n')
        outPutFile.flush()
        previousNumberOfBlocks = numberOfBlocks
