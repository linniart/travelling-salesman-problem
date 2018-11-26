import pandas as pd
import itertools
import numpy as np
import math
import random
import googlemaps
from datetime import datetime
from collections import namedtuple

gmaps = googlemaps.Client(key='[Your Google Maps API code]')

#create a named tuple for the routes
Route=namedtuple('Route',['start','end','distance'])

def make_route(start,end,distance):
    return Route(start,end,distance)

#get the distance from origin to destination using Google Maps Directions API
def get_distance(origin,dest):
    directions_result = gmaps.directions(origin,
                                     dest,
                                     mode="driving",
                                     departure_time=datetime.now())
    return directions_result[0]['legs'][0]['distance']['value']

class Graph:
    def __init__(self,address):
        #add 'Singapore' to the postal code
        self.address=['Singapore '+a for a in address]
        
        #find all the possible route combinations
        combination=list(itertools.permutations(self.address,2))
        
        #make routes that consist of start, end, distance
        self.routes=[make_route(i[0],i[1],get_distance(i[0],i[1])) for i in combination]
    
    #function to add new routes and append them to self.routes
    def add_route(self,address):
        self.address=['Singapore '+a for a in address]
        combination=list(itertools.permutations(self.address,2))
        for new_route in combination:
            if new_route in [(route.start,route.end) for route in self.routes]:
                pass
            else:
                self.routes.append(Route(new_route[0],new_route[1],get_distance(new_route[1],new_route[0])))
    
    #find the total distance for specific tour
    def totaldistancetour(self,tour):
        d=0
        for i in range(1,len(tour)):
            origin=self.test_address[tour[i-1]]
            dest=self.test_address[tour[i]]
            distance=[route.distance for route in self.routes if (route.start==origin and route.end==dest)][0]
            d=d+distance
        origin=self.test_address[tour[len(tour)-1]]
        dest=self.test_address[tour[0]]
        distance=[route.distance for route in self.routes if (route.start==origin and route.end==dest)][0]
        d=d+distance
        return d
    
    #brute force method to find the shortest tour
    def tsp_brute_force_gmaps(self,test_address):
        #to add the tested routes to self.routes if they do not exist
        self.add_route(test_address)
        self.test_address=['Singapore '+a for a in test_address]
        n=len(self.test_address)
        tour=random.sample(range(n),n)

        allpossibletour=list(itertools.permutations(tour))
        lbest=1000000
        ibest=tour
        
        #find the total distance for each possible tour and get the shortest one
        for i in range(len(allpossibletour)):
            l=self.totaldistancetour(allpossibletour[i])
            if l < lbest:
                lbest=l
                ibest=i                
        return allpossibletour[ibest],lbest
    
    #using simulated annealing 
    def tsp_anneal_gmaps(self,test_address):
        self.test_address=['Singapore '+ a for a in test_address]
        n=len(self.test_address)
        tour=random.sample(range(n),n)
        for temperature in np.logspace(0,5,num=10000)[::-1]:
            oldDistance=self.totaldistancetour(tour)
            [i,j]=sorted(random.sample(range(n),2))
            newTour=tour[:i]+tour[j:j+1]+tour[i+1:j]+tour[i:i+1] + tour[j+1:]
            newDistance=self.totaldistancetour(newTour)
            if math.exp((oldDistance-newDistance)/temperature)>random.random():
                tour=newTour.copy()
            return tour,self.totaldistancetour(tour)