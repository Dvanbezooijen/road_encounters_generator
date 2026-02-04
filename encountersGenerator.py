# -*- coding: utf-8 -*-
"""
@author: Dylan van Bezooijen
"""

import numpy as np
import time

def computeEncounters(rateHourA:float,
                      rateHourB:float,
                      speedKmhA:float,
                      speedKmhB:float,
                      roadLengthKm:float,
                      confidenceTreshold:float,
                      groupWindow: float,
                      ):
    """
    Compute expected encounter rates between two traffic streams on a road segment.
    
    The road is split into analysis pieces until the probability of observing
    more than one vehicle per lane falls within the user-specified confidence
    interval. Probabilities of encounters along and towards each other are
    calculated based on Poisson arrival rates, vehicle speeds, and lane lengths.
    Monte Carlo simulation is used if both streams have identical speeds.
    
    Parameters
    ----------
    rateHourA : float
        Arrival rate of stream A [vehicles per hour]
    rateHourB : float
        Arrival rate of stream B [vehicles per hour]
    speedKmhA : float
        Speed of stream A [km/h]
    speedKmhB : float
        Speed of stream B [km/h]
    roadLengthKm : float
        Total road segment length [km]
    confidenceTreshold : float
        Minimum confidence threshold for splitting road into analysis pieces
    groupWindow : float
        Time window in seconds for group-thinning of arrivals (0 for no thinning)
    
    Returns
    -------
    results : dict
        Dictionary containing:
            - 'Encounters (towards)': expected encounters toward each other per hour
            - 'Encounters (along)': expected encounters along each other per hour
    """
    
    # Initialize variable for while loop
    roadPieces = 1
    # Input paramters for range of observable vehicles on the road, limited to known state space (max 1 veh per side)
    vehObsA = [0,1]
    vehObsB = vehObsA #Must be symetric
    speedKmh = np.minimum(speedKmhA,speedKmhB) #slowest moving vehicle decided temporal state
    
    #introduce group thinning rates (if groupWindow = 0, no group thinning)
    rateHourA = rateHourA * np.exp(-(groupWindow/3600)*rateHourA)
    rateHourB = rateHourB * np.exp(-(groupWindow/3600)*rateHourB)
    
    while True:
        # Calculate neccesary input parameters
        analysisLengthKm = roadLengthKm / roadPieces #analysis length of a piece of road [km]
    
        #The maximum dwell time in a state (slowest vehicle)
        dwellTimeStateHour = analysisLengthKm/speedKmh
        
        # Set state space (output [0,1])
        vehObsA = np.arange(0,2)
        vehObsB = np.arange(0,2)
        
        #Calculate probability of N(1,1) vector wize
        pA = ((rateHourA*dwellTimeStateHour) ** vehObsA) * np.exp(-rateHourA*dwellTimeStateHour)
        pB = ((rateHourB*dwellTimeStateHour) ** vehObsB) * np.exp(-rateHourB*dwellTimeStateHour)
        
        #Calculate the pairwise probabilities
        probGrid = np.outer(pA, pB)
        
        #Calculate state confidence (state treshold)
        confidence = np.sum(probGrid)
        
        # Check if confidence falls within treshold
        if confidence >= confidenceTreshold:
            break
        
        #Otherswise advance loop
        roadPieces += 1
    
    """
    When the road is split into its analysis length pieces, the number of encounters for each piece
    can be calculated depending if the two streams A and B are heading towards one another, or passing/overtaking
    """
    # Encounters towards for the state space is known deterministacally as:
    encProbTowards = 1
        
    # When the streams are directed along/past each other
    if speedKmhA != speedKmhB:
        timeWindowA = max(0, analysisLengthKm*(1/speedKmhA - 1/speedKmhB))
        timeWindowB = max(0, analysisLengthKm*(1/speedKmhB - 1/speedKmhA))
    
        if rateHourA + rateHourB > 0:  # only calculate if rates are non-zero
            probAB = (rateHourA/(rateHourA+rateHourB)) * (timeWindowA*rateHourB)*np.exp(-timeWindowA*rateHourB)
            probBA = (rateHourB/(rateHourA+rateHourB)) * (timeWindowB*rateHourA)*np.exp(-timeWindowB*rateHourA)
            encProbAlong = probAB + probBA
        else:
            encProbAlong = 0.0
    
    elif speedKmhA == speedKmhB:
        if rateHourA + rateHourB > 0:  # Monte Carlo simulation only if non-zero rates
            nSamples = 10_000
            stdSpeeds = 0.10
            speedsKmhDrawnA = np.random.normal(speedKmhA, speedKmhA*stdSpeeds, nSamples)
            speedsKmhDrawnA = np.clip(speedsKmhDrawnA, 1, None)
            timeWindowsA = analysisLengthKm*(1/speedsKmhDrawnA - 1/speedKmhB)
            timeWindowsB = analysisLengthKm*(1/speedKmhB - 1/speedsKmhDrawnA)
            timeWindowsA = np.clip(timeWindowsA, 0, None)
            timeWindowsB = np.clip(timeWindowsB, 0, None)
    
            probsAB = (rateHourA/(rateHourA+rateHourB)) * (timeWindowsA*rateHourB) * np.exp(-timeWindowsA*rateHourB)
            probsBA = (rateHourB/(rateHourA+rateHourB)) * (timeWindowsB*rateHourA) * np.exp(-timeWindowsB*rateHourA)
            probs = probsAB + probsBA
            encProbAlong = np.mean(probs)
        else:
            encProbAlong = 0.0


    """
    Now that the number of encounters for each analysis road is computed. They must be converted
    to a total encounter rate for the road. 
    """
    
    #Occurances per dwellTimeState
    occurrences = roadPieces * probGrid[1][1]
    #Encounters per occurance
    encountersTowards = occurrences * encProbTowards
    encountersAlong = occurrences * encProbAlong
    #The number of encounters for each state is given by
    encountersTowardsRate = encountersTowards /dwellTimeStateHour
    encountersAlongRate = encountersAlong /dwellTimeStateHour
    
    # Give results
    results = {
        'Encounters (towards)': encountersTowardsRate,
        'Encounters (along)': encountersAlongRate,
        }
    
    return results

#------------
#Example usage
#-----------
if __name__ == "__main__":
    rateHourA = 190
    rateHourB = 190
    speedKmhA = 50
    speedKmhB = 50
    roadLengthKm = 0.083412195401082009
    confidenceTreshold= 0.84
    groupWindow = 0
    
    startTime = time.time()
    results = computeEncounters(rateHourA, rateHourB, speedKmhA, speedKmhB, roadLengthKm, confidenceTreshold, groupWindow)
    endTime = time.time()
    elapsedTime = endTime - startTime
    print(f'it took {elapsedTime} to run')