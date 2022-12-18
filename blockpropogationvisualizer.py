import argparse
import os
from datetime import datetime
import matplotlib.pyplot as plt
from numpy import array
import seaborn as sns
def read_data(folder_name):
    scanned = sorted([f for f in os.scandir(folder_name)], key=lambda f: f.name)
    data = { }
    for n, image_file in enumerate(scanned):
        f = open(folder_name + image_file.name, "r")
        Lines = f.readlines()
        nodeName = ""
        for line in Lines:
            if(line == Lines[0]):
                nodeName = line
                continue
            stringsOfLine = line.split()
            if stringsOfLine[8] in data:
                data[stringsOfLine[8]].append([datetime.strptime(stringsOfLine[5] +' '+stringsOfLine[6], '%m/%d/%Y, %H:%M:%S:%f'), nodeName[:-1]])
            else : 
                data[stringsOfLine[8]] = [[datetime.strptime(stringsOfLine[5] +' '+stringsOfLine[6], '%m/%d/%Y, %H:%M:%S:%f'), nodeName[:-1]]]
    return data

def plot_data(data):
    timeDifferences = { }
    minimumTimeNode = ""
    for block in data:
        minimumTime = data[block][0][0]
        minimumTimeNode = data[block][0][1]
        for node in data[block]:
            if(node[0] < minimumTime):
                minimumTime = node[0]
                minimumTimeNode = node[1]
        for node in data[block]:
            timeDifference =  node[0] - minimumTime
            timeDifferenceInSeconds = timeDifference.total_seconds()
            if block in timeDifferences :
                timeDifferences[block].append(timeDifferenceInSeconds*1000)
            else :
                timeDifferences[block] = [timeDifferenceInSeconds*1000]
        print(block + minimumTimeNode)
    for block in timeDifferences : 
        xaxis = array(range(len(timeDifferences[block])))
        yaxis = timeDifferences[block]
        fig = plt.figure()
        plt.hist(yaxis,  cumulative=True, label='CDF',
         histtype='step', alpha=0.8, color='k')
        plt.xlabel("Delay in propogation(milli-seconds)")
        plt.ylabel("No. of nodes with the latest block information")
        plt.savefig(block[:10] + "cdf")

        fig = plt.figure()
        # seaborn histogram
        fig.add_axes([0.15,0.15,0.75,0.75])
        sns.distplot(yaxis, hist=False, kde=True, rug = True,
                    bins=len(yaxis), color = 'blue',
                    hist_kws={'edgecolor':'black'})
        # Add labels
        plt.title('Density plot with rug plot for block arrival')
        plt.xlabel('Delay in propogation(milli-seconds)')
        plt.ylabel('Density')
        plt.savefig(block[:10] + "cdfandrug")



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("data_folder", help="The GPL file to turn into topology")
    args = parser.parse_args()
    data = read_data(args.data_folder)
    plot_data(data)
