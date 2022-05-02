import os
import shutil
import subprocess
import json
import np
from datetime import datetime, timedelta
import argparse




### CONSTANTS ####

BLOCK_GEN_RATE = timedelta(0,5*60) #seconds
NUMBER_OF_BLOCKS_TO_GEN = 20

class miner:
    def __init__(self, imageName):
        self.imageName = imageName
        self.blockReceivedTimings = {0:0}
        self.blockDepth = 0
    
    def getInfo(self):
        info = subprocess.run(['docker', 'exec', self.imageName,'bitcoin-cli','-getinfo'], stdout=subprocess.PIPE).stdout.decode('utf-8')
        infoJson = json.loads(info)
        return infoJson
    
    def generateBlocks(self, BLOCKS=1):
        generated = subprocess.run(['docker', 'exec', self.imageName,'bitcoin-cli','-generate', BLOCKS], stdout=subprocess.PIPE).stdout.decode('utf-8')
        generatedJson = json.loads(generated)
        return generatedJson
    
    def getPeers(self):
        info = subprocess.run(['docker', 'exec', self.imageName,'bitcoin-cli','getpeerinfo'], stdout=subprocess.PIPE).stdout.decode('utf-8')
        infoJson = json.loads(info)
        return infoJson['blocks']
        
    def getChainDepth(self):
        info = subprocess.run(['docker', 'exec', self.imageName,'bitcoin-cli','-getinfo'], stdout=subprocess.PIPE).stdout.decode('utf-8')
        infoJson = json.loads(info)
        return infoJson['blocks']
    
    def updateBlockTimings(self):
        depth = self.getChainDepth()
        if depth > self.blockDepth:
            self.blockDepth = depth
            self.blockReceivedTimings[depth] = datetime.now()


def checkChainDepth(images):
    for image in images:
        image.updateBlockTimings()

def generateBlockProportionately(probabilityTable):
    randNum = np.random.random()
    for host,probability in miningPowerRatio.items():
        if randNum >= probability:
            randNum = randNum - probability
        else:
            host.generateBlocks()
            return

def checkIfBlockGen(currentBlockGenTime, chainDepth):
    currentBlockLifespan = datetime.now() - currentBlockGenTime
    if currentBlockGenTime > BLOCK_GEN_RATE:
        generateBlockProportionately()
        return datetime.now(), chainDepth + 1
    else:
        return currentBlockGenTime, chainDepth



#mining power must add to 1 or be normalized to 1
miningPowerRatio = {
                    "1.200.10.2":.3,
                    "1.200.10.3":.3,
                    
                    "2.200.10.2":.2,
                    "2.200.10.3":.1,
                    
                    "3.200.10.2":.05,
                    "3.200.10.3":.05,
                    }

def generateHosts(miningPowerRatio):
    hosts = []
    probabilityTable = {}
    for ip, probability in miningPowerRatio.items():
        ##TODO
        pass

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--numblocks',
                    default = NUMBER_OF_BLOCKS_TO_GEN,
                    dest = 'numBlocks',
                    help = 'number of blocks to generate and test',
                    type=int)

parser.add_argument('-h','--hosts',
                    default = '',
                    dest = 'hosts',
                    help = 'location of the hostFile',
                    type=str)


if __name__=='main':
    args = parser.parse_args()
    NUMBER_OF_BLOCKS_TO_GEN = args.numBlocks
    hostFile = args.hosts
    
    hosts, probabilityTable = generateHosts(hostFile)
    
    chainTimestamps = []
    
    ## start experiment timer
    startTime = datetime.now()
    
    ## generate the first block
    generateBlockProportionately(miningPowerRatio)
    currentBlockGenTime = datetime.now()
    chainDepth = 1
    
    while (chainDepth < NUMBER_OF_BLOCKS_TO_GEN + 1):
        checkChainDepth(hosts)
        currentBlockGenTime, chainDepth = checkIfBlockGen(currentBlockGenTime, chainDepth)


