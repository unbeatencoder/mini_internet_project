from ctypes import sizeof
import os
import shutil
import subprocess
import json
import numpy as np
import pandas
import re
from datetime import datetime, timedelta
import argparse
import random

from tomlkit import boolean



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

    def connectToNeighbors(self, hosts, quickConnect = False):
        print('connecting neighbors for ',self.imageName)
        if quickConnect:
            for host in random.sample(hosts, 40):
                subprocess.run(['docker', 'exec', self.imageName, 'bitcoin-cli', 'addnode', host.ip+":8333", 'add'])
        else:
            for host in hosts:
                subprocess.run(['docker', 'exec', self.imageName, 'bitcoin-cli', 'addnode', host.ip+":8333", 'add'])

    def getInfo(self):
        info = subprocess.run(['docker', 'exec', self.imageName,'bitcoin-cli','-getinfo'], stdout=subprocess.PIPE).stdout.decode('utf-8')
        infoJson = json.loads(info)
        return infoJson
    
    def generateBlocks(self, BLOCKS=1):
        print(self.imageName + 'generating block')
        generated = subprocess.run(['docker', 'exec', self.imageName,'bitcoin-cli','-generate', str(BLOCKS)], stdout=subprocess.PIPE).stdout.decode('utf-8')
        generatedJson = json.loads(generated)
        return generatedJson
    
    def getPeers(self):
        info = subprocess.run(['docker', 'exec', self.imageName,'bitcoin-cli','getpeerinfo'], stdout=subprocess.PIPE).stdout.decode('utf-8')
        infoJson = json.loads(info)
        return infoJson['blocks']

def generateBlockProportionately(hosts):
    print('creating new block')
    randNum = np.random.randint(0,len(hosts)-1)
    host = getHostByName(hosts,hosts[randNum].imageName)
    host.generateBlocks()
    print(len(hosts))

def generateHosts(hostFile):
    hosts = []
    hostsfileDF = pandas.read_csv(hostFile,sep='\s+')
    for i, row in hostsfileDF.iterrows():
        hostName = row['NAMES']
        print(hostName)
        print('found host ', hostName)
        newMiner = miner(hostName)
        newMiner.getIP()
        hosts.append(newMiner)
    return hosts

def getHostByName(hosts,hostname):
    print(hostname)
    for host in hosts:
        print(host.imageName)
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
                    type = int)

parser.add_argument('-A','--hosts',
                    default = '',
                    dest = 'hosts',
                    help = 'location of the hostFile',
                    type = str)

parser.add_argument('-q', '--quickconnect',
                    action = 'store_const',
                    const = True,
                    default = False,
                    dest = 'quickConnect',
                    help = 'connect to only 40 random other hosts durring connection false')



def main():
    # print('starting in main')
    args = parser.parse_args()
    NUMBER_OF_BLOCKS_TO_GEN = args.numBlocks
    print(args.numBlocks)
    hostFile = args.hosts
    print(hostFile)
    hosts = generateHosts(hostFile)
    ## generate the first block
    for i in range(NUMBER_OF_BLOCKS_TO_GEN):
        generateBlockProportionately(hosts)
    

if __name__=="__main__":
    print('calling main')
    main()