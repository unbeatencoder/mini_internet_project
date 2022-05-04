import os
import shutil
import subprocess
import json
import numpy as np
import pandas
import re
from datetime import datetime, timedelta
import argparse




### CONSTANTS ####

BLOCK_GEN_RATE = timedelta(0,0.2*60) #seconds
NUMBER_OF_BLOCKS_TO_GEN = 20

class miner:
    def __init__(self, imageName):
        self.imageName = imageName
        self.blockReceivedTimings = {0:0}
        self.blockDepth = 0
        info = subprocess.run(['docker', 'exec', self.imageName,'ifconfig'], stdout=subprocess.PIPE).stdout.decode('utf-8')

    def getIP(self):
        eth = subprocess.run(['docker', 'exec', self.imageName, 'ifconfig'], stdout=subprocess.PIPE).stdout.decode('utf-8')
        self.ip = re.findall('inet ([\d\.]*) ',eth)[0]
        return self.ip

    def connectToNeighbors(self, hosts):
        for host in hosts:
            subprocess.run(['docker', 'exec', self.imageName, 'bitcoin-cli', 'addnode', host.ip, 'add'])

    def getInfo(self):
        info = subprocess.run(['docker', 'exec', self.imageName,'bitcoin-cli','-getinfo'], stdout=subprocess.PIPE).stdout.decode('utf-8')
        infoJson = json.loads(info)
        return infoJson
    
    def generateBlocks(self, BLOCKS=1):
        generated = subprocess.run(['docker', 'exec', self.imageName,'bitcoin-cli','-generate', str(BLOCKS)], stdout=subprocess.PIPE).stdout.decode('utf-8')
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
    
    def printBlockTimings(self, blockSpawnTimes):
        print(self.imageName)
        for depth, time in self.blockReceivedTimings.items():
            # print(depth)
            # blockSpawn = blockSpawnTimes[depth]
            # print("blockspawn")
            # print(blockSpawn)
            # print(type(blockSpawn))
            # print("time")
            # print(time)
            # print(type(time))
            # latency = time - blockSpawn
            # print("block: ",depth,", latency: ",latency.total_seconds(),'s')
            print("block: ",depth,", time: ", time)


def checkChainDepth(images):
    for image in images:
        image.updateBlockTimings()

def generateBlockProportionately(hosts,probabilityTable, blockSpawnTimes):
    print('creating new block')
    randNum = np.random.random()
    for hostname,probability in probabilityTable.items():
        if randNum >= probability:
            randNum = randNum - probability
        else:
            host = getHostByName(hosts,hostname)
            host.generateBlocks()
            blockSpawnTimes.append(datetime.now())
            return blockSpawnTimes

def checkIfBlockGen(currentBlockGenTime, chainDepth,hosts,probabilityTable, blockSpawnTimes):
    currentBlockLifespan = datetime.now() - currentBlockGenTime
    if currentBlockLifespan > BLOCK_GEN_RATE:
        blockSpawnTimes = generateBlockProportionately(hosts,probabilityTable, blockSpawnTimes)
        return datetime.now(), chainDepth + 1, blockSpawnTimes
    else:
        return currentBlockGenTime, chainDepth, blockSpawnTimes


def generateHosts(hostFile):
    hosts = []
    probabilityTable = {}
    hostsfileDF = pandas.read_csv(hostFile,sep='\s+')
    for i, row in hostsfileDF.iterrows():
        hostName = row['NAMES']
        if re.search('miner',hostName):
            print('found host ', hostName)
            newMiner = miner(hostName)
            netMiner.getIP()
            hosts.append(newMiner)
            probabilityTable[hostName] = np.random.random() #TODO shouldn't be random
    return hosts, probabilityTable

def getHostByName(hosts,hostname):
    for host in hosts:
        if host.imageName == hostname:
            return host

def normalizeProbs(probabilityTable):
    #cumulatively sum probabilities
    cumsum = 0
    for host,prob in probabilityTable.items():
        cumsum = cumsum + prob
    
    for host,prob in probabilityTable.items():
        prob = prob / cumsum
    
    return probabilityTable



parser = argparse.ArgumentParser()
parser.add_argument('-n', '--numblocks',
                    default = NUMBER_OF_BLOCKS_TO_GEN,
                    dest = 'numBlocks',
                    help = 'number of blocks to generate and test',
                    type=int)

parser.add_argument('-A','--hosts',
                    default = '',
                    dest = 'hosts',
                    help = 'location of the hostFile',
                    type=str)


def main():
    print('starting in main')
    args = parser.parse_args()
    NUMBER_OF_BLOCKS_TO_GEN = args.numBlocks
    print(args.numBlocks)
    hostFile = args.hosts
    print(hostFile)
    hosts, probabilityTable = generateHosts(hostFile)
    probabilityTable = normalizeProbs(probabilityTable)
    blockSpawnTimes = []

    print('connecting hosts together')
    for host in hosts:
        host.connectToNeighbors(hosts)
    
    
    print('stating experiment')
    ## start experiment timer
    startTime = datetime.now()
    
    ## generate the first block
    blockSpawnTimes = generateBlockProportionately(hosts,probabilityTable,blockSpawnTimes)
    currentBlockGenTime = datetime.now()
    chainDepth = 1
    
    while (chainDepth < NUMBER_OF_BLOCKS_TO_GEN + 1):
        checkChainDepth(hosts)
        currentBlockGenTime, chainDepth, blockSpawnTimes = checkIfBlockGen(currentBlockGenTime, chainDepth,hosts,probabilityTable, blockSpawnTimes)

    for host in hosts:
        host.printBlockTimings(blockSpawnTimes)
        print()

if __name__=="__main__":
    print('calling main')
    main()
