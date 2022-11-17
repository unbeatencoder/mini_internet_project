import argparse
from ctypes import sizeof
from venv import create
import networkx as nx
import pandas as pd
import numpy as np
import random
import json
import os
from pathlib import Path

def generate_topology(input_file):
    print(input_file)
    G = nx.read_gml(input_file)
    edges = {}
    nodeNameToIdMapping = {}
    nodeId = 1
    for u, v, weight in G.edges.data("weight"):
        edges[(u,v)] = weight
        if u in nodeNameToIdMapping:
            continue
        else:
            nodeNameToIdMapping[u] =  nodeId
            nodeId = nodeId + 1
        if v in nodeNameToIdMapping:
            continue
        else:
            nodeNameToIdMapping[v] =  nodeId
            nodeId = nodeId + 1

    print(nodeNameToIdMapping)
    check_if_frr_daemons_file_exists()
    check_if_subnet_config_file_exists()
    check_if_welcome_message_file_exists()
    create_external_links_config(nodeNameToIdMapping, edges)
    create_AS_config(nodeNameToIdMapping)
    create_router_config_files_for_all_AS(nodeNameToIdMapping)
    create_internal_link_config_files_for_all_AS(nodeNameToIdMapping)
    create_layer2_switches_config_files_for_all_AS(nodeNameToIdMapping)
    create_layer2_hosts_config_files_for_all_AS(nodeNameToIdMapping)
    create_layer2_links_config_files_for_all_AS(nodeNameToIdMapping)

def check_if_frr_daemons_file_exists():
    my_file = Path("/daemons")
    if my_file.is_file():
        print("free_daemons_file missing!")
        exit
    return 

def check_if_subnet_config_file_exists():
    my_file = Path("/subnet_config.sh")
    if my_file.is_file():
        print("free_daemons_file missing!")
        exit
    return 

def check_if_welcome_message_file_exists():
    my_file = Path("/welcoming_message.txt")
    if my_file.is_file():
        print("free_daemons_file missing!")
        exit
    return  

#1 AMZN02 Peer 2 AMZAES Peer 10000 1000 179.0.1.0/24
def create_external_links_config(nodeNameToIdMapping, edges):
    f = open("external_links_config.txt", "w")
    externalIPsubnet = 1
    count = 0 
    for edge in edges:
        f.write(str(nodeNameToIdMapping[edge[0]]))
        f.write(" ")
        f.write(str(edge[0]))
        f.write(" ")
        f.write("Peer")
        f.write(" ")
        f.write(str(nodeNameToIdMapping[edge[1]]))
        f.write(" ") 
        f.write(edge[1])
        f.write(" ") 
        f.write("Peer")
        f.write(" ")
        f.write("10000")
        f.write(" ")
        f.write("1000")
        f.write(" ")
        f.write("179.0." + str(externalIPsubnet) + ".0/24")
        externalIPsubnet = externalIPsubnet + 1
        count = count + 1
        if count != len(edges):
            f.write("\n")
    f.close()
    return

def getRouterConfigFileName(ASName):
    return "router_config_"+ASName+".txt"

def getInternalLinksConfigFileName(ASName):
    return "internal_links_config_"+ASName+".txt"

def getLayer2SwitchesConfigFileName(ASName):
    return "layer2_switches_config_"+ASName+".txt"

def getLayer2HostsConfigFileName(ASName):
    return "layer2_hosts_config_"+ASName+".txt"

def getLayer2LinksConfigFileName(ASName):
    return "layer2_links_config_"+ASName+".txt"

def create_AS_config(nodeNameToIdMapping):
    f = open("AS_config.txt", "w")
    count = 0
    numberOfAS = len(nodeNameToIdMapping)
    for ASName in nodeNameToIdMapping:
        f.write(str(nodeNameToIdMapping[ASName]))
        f.write("\t")
        f.write(ASName)
        f.write("\t")
        f.write("Config")
        f.write("\t")
        f.write(getRouterConfigFileName(ASName))
        f.write("\t")
        f.write(getInternalLinksConfigFileName(ASName))
        f.write("\t")
        f.write(getLayer2SwitchesConfigFileName(ASName))
        f.write("\t")
        f.write(getLayer2HostsConfigFileName(ASName))
        f.write("\t")
        f.write(getLayer2LinksConfigFileName(ASName))
        count = count + 1
        if count != numberOfAS:
            f.write("\n")
    f.close()
    return 

def create_router_config_files_for_all_AS(nodeNameToIdMapping):
    for ASName in nodeNameToIdMapping:
            create_router_config(ASName, nodeNameToIdMapping[ASName])
    return

def create_router_config(ASName, ASId):
    print(ASName)
    print(ASId)
    f = open(getRouterConfigFileName(ASName), "w")
    f.write(ASName) 
    f.write("\tN/A\tL2-AS" +str(ASId)+":\tvtysh")
    f.close()
    return 

def create_internal_link_config_files_for_all_AS(nodeNameToIdMapping):
    for ASName in nodeNameToIdMapping:
            create_internal_link_config(ASName, nodeNameToIdMapping[ASName])
    return

def create_internal_link_config(ASName, ASId):
    f = open(getInternalLinksConfigFileName(ASName), "w")
    f.close()
    return 

def create_layer2_switches_config_files_for_all_AS(nodeNameToIdMapping):
    for ASName in nodeNameToIdMapping:
            create_layer2_switches_config(ASName, nodeNameToIdMapping[ASName])
    return

def create_layer2_switches_config(ASName, ASId):
    f = open(getLayer2SwitchesConfigFileName(ASName), "w")
    f.write("AS"+str(ASId))
    f.write("\t")
    f.write("SwitchAS"+str(ASId))
    f.write("\t")
    f.write(ASName)
    f.write("\t")
    f.write(rand_mac())
    f.write("\t")
    f.write("1")
    f.close()
    return

def rand_mac():
    return "%02x:%02x:%02x:%02x:%02x:%02x" % (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255)
        )

def create_layer2_hosts_config_files_for_all_AS(nodeNameToIdMapping):
    for ASName in nodeNameToIdMapping:
            create_layer2_hosts_config(ASName, nodeNameToIdMapping[ASName])
    return

def create_layer2_hosts_config(ASName, ASId):
    f = open(getLayer2HostsConfigFileName(ASName), "w")
    f.write("node0"+str(ASId))
    f.write("\t")
    f.write("unbeatencoder/miniinternet")
    f.write("\t")
    f.write("AS"+str(ASId))
    f.write("\t")
    f.write("SwitchAS"+str(ASId))
    f.write("\t")
    f.write("10000")
    f.write("\t")
    f.write("1000")
    f.write("\t")
    f.write("10")
    f.close()
    return  

def create_layer2_links_config_files_for_all_AS(nodeNameToIdMapping):
    for ASName in nodeNameToIdMapping:
            create_layer2_links_config(ASName, nodeNameToIdMapping[ASName])
    return

def create_layer2_links_config(ASName, ASId):
    f = open(getLayer2LinksConfigFileName(ASName), "w")
    f.close()
    return   


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("gpl_file", help="The GPL file to turn into topology")
    args = parser.parse_args()
    generate_topology(args.gpl_file)