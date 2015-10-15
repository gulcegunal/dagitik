import sys
from Airline import *

def canRedeem(current, goal, pathForMiles, airlinesVisited, network):
    if(current == goal):
        pathForMiles.append(current)
        return True
    elif(airlinesVisited.count(current)!=0):
        return False
    else:
        airlinesVisited.append(current)
        pathForMiles.append(current)
        pos = -1
        index = 0
        while (pos == -1 and index < len(network)):
              if(network[index].getName() == current):
                  pos = index
              index += 1
        if(pos == -1):
              return False
        index = 0
        partners = network[pos].getPartners()
        foundPath = False
        while (not foundPath  and index < len(partners)):
              foundPath = canRedeem(partners[index], goal, pathForMiles, airlinesVisited, network)
              index += 1
        if( not foundPath ):
              pathForMiles.remove(pathForMiles[len(pathForMiles)-1])
        return foundPath


try:
    scannerToReadAirlines = open("airlines.txt","r")
except:
    print ("Could not connect to file airlines.txt")
    sys.exit(0)
if (scannerToReadAirlines != None):
              airlinesPartnersNetwork = [] 
              airlinesPartnersNetworkpr = []
              for line in scannerToReadAirlines:
                  lineFromFile = line.strip("\n")
                  airlineNames = lineFromFile.split(",")
                  newAirline = Airline(airlineNames)
                  airlinesPartnersNetwork.append(newAirline)
                  airlinesPartnersNetworkpr.append(newAirline.toString())
              
              print(airlinesPartnersNetworkpr)
              start = input("Enter airline miles are on: ")
              goal = input("Enter goal airline: ")
              pathForMiles = []
              airlinesVisited = []
              if( canRedeem(start, goal, pathForMiles, airlinesVisited, airlinesPartnersNetwork)):
                  print("Path to redeem miles: ", pathForMiles)
              else:
                  print("Cannot convert miles from ", start, " to ", goal, ".");

scannerToReadAirlines.close()    
