import subprocess
import json
from datetime import datetime

containerName = subprocess.check_output("hostname", shell=True)
containerName = containerName.decode("utf-8")[:-1]
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
        outPutFile.write(currentTime + '\n')
        outPutFile.flush()
        previousNumberOfBlocks = numberOfBlocks
