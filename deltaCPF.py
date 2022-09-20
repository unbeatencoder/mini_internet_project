import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
import sys
from datetime import datetime, timedelta
import numpy as np

if len(sys.argv)>1:
    fileLoc = sys.argv[1]
else:
    fileLoc = 'outputwithoutdelay.txt'
print(fileLoc)
with open(fileLoc,'r') as file:
    hosts = re.findall(r'found host\s*(\S*)',file.read())
    file.seek(0)
    blockGens = re.findall('new block\n([\S]*)\n([\S]+ [\S]+)\n', file.read())
    blockGens = pd.DataFrame(blockGens)
    blockGens.columns = ['blockGenerator','time']
    file.seek(0)
    blockReceptions = re.findall(r"block:\s*(\d*) , received time:\s*([\S]+ [\S]+)\n", file.read())
    blockReceptions = pd.DataFrame(blockReceptions)
    blockReceptions.columns = ['blockNum','time']

#process blockGens
blockGens['time'] = pd.to_datetime(blockGens['time'])
print(len(blockGens))
print(len(blockReceptions))
minBlock = int(blockReceptions['blockNum'][0])
maxBlock = int(blockReceptions['blockNum'][0])
for i in range(len(blockReceptions)):
	if(minBlock > int(blockReceptions['blockNum'][i])):
		minBlock = int(blockReceptions['blockNum'][i])
	if(maxBlock < int(blockReceptions['blockNum'][i])):
		maxBlock = int(blockReceptions['blockNum'][i])
print(minBlock)
print(maxBlock)
#process block receptions
#minBlock = int(blockReceptions['blockNum'].min())
print("minblock")
print(minBlock)
#maxBlock = int(blockReceptions['blockNum'].max())
print("maxblock")
print(maxBlock)
numBlocks = maxBlock - minBlock

blockReceptions['blockNum'] = blockReceptions['blockNum'].astype(int) - minBlock
blockReceptions['time'] = pd.to_datetime(blockReceptions['time'])

deltas = []
for i in range(len(blockReceptions)):
    block = blockReceptions['blockNum'][i]
    #print(block)
    spawnTime = blockGens['time'][block]
    deltas.append(blockReceptions['time'][i] - spawnTime)

orderedHosts = []
for host in hosts:
    orderedHosts = orderedHosts + [host]* (numBlocks+1)

blockReceptions['hosts'] = orderedHosts
blockReceptions['delta'] = deltas


output = fileLoc[:-4] + "_ordered.csv"
blockGens.to_csv(output, index=False, header=True)
blockReceptions.to_csv(output, index=False, header=True, mode='a')


kwargs = {'cumulative': True}
sns.distplot(blockReceptions['delta'], hist_kws=kwargs, kde_kws=kwargs)
plt.show()
plt.savefig(output[:-4])

print("testing!!")
print(blockReceptions['delta'].mean())
