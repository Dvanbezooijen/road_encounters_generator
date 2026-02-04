# -*- coding: utf-8 -*-
"""
Created on Thu Dec  4 11:26:55 2025

@author: Dylan van Bezooijen

Function purpose:
    This function computes the total number of encounters road users. 
    It takes into account the number of lanes, traffic volumes, vehicle and cyclist speeds, and road types.
    The encounters are calculated using generated interaction matrices and per-hour rates.
    
    Parameters:
    aantal_rijstroken_heen : int
        Number of lanes in the "heen" direction (along the road)
    aantal_rijstroken_terug : int
        Number of lanes in the "terug" direction (towards the start)
    intensiteit_heen_pae_per_day : float
        Daily car traffic intensity in the "heen" direction
    intensiteit_terug_pae_per_dag : float
        Daily car traffic intensity in the "terug" direction
    snelheid_heen_km_per_uur : float
        Vehicle speed in the "heen" direction (km/h)
    snelheid_terug_km_per_uur : float
        Vehicle speed in the "terug" direction (km/h)
    fiets_h : float
        Daily cyclist intensity in the "heen" direction
    fiets_t : float
        Daily cyclist intensity in the "terug" direction
    fiets_h_allowed : int (0 or 1)
        Whether cyclists are allowed in the "heen" direction
    fiets_t_allowed : int (0 or 1)
        Whether cyclists are allowed in the "terug" direction
    auto_h_allowed : int (0 or 1)
        Whether cars are allowed in the "heen" direction
    auto_t_allowed : int (0 or 1)
        Whether cars are allowed in the "terug" direction
    fietsSpeedKmh : float
        Average cyclist speed (km/h)
    length_km : float
        Length of the road segment in kilometers

Returns:
    encounters : float
        Total number of encounters between all lanes and road users
"""


from encountersGenerator import computeEncounters
from interactionGenerator import generateInteractionMatrices
import numpy as np
def computeEncountersRoad(
    aantal_rijstroken_heen,
    aantal_rijstroken_terug,
    intensiteit_heen_pae_per_dag,
    intensiteit_terug_pae_per_dag,
    snelheid_heen_km_per_uur,
    snelheid_terug_km_per_uur,
    fiets_h,
    fiets_t,
    fietsSpeedKmh,
    length_km
):
    
    auto_h_allowed = 0 if not intensiteit_heen_pae_per_dag else 1
    auto_t_allowed = 0 if not intensiteit_terug_pae_per_dag else 1
    fiets_h_allowed =  0 if not fiets_h else 1
    fiets_t_allowed = 0 if not fiets_t else 1
    
    #Generate interaction matrices
    interactionAlong, interactionTowards = generateInteractionMatrices(
        aantal_rijstroken_heen, aantal_rijstroken_terug, 
        fiets_h_allowed, 
        fiets_t_allowed, 
        auto_h_allowed, 
        auto_t_allowed
    )
    
    #Check if interaction matrices are same size
    assert len(interactionAlong) == len(interactionTowards)
    nLanes = len(interactionAlong)

    #Initialize encounter matrices
    encountersTowards = np.zeros((nLanes,nLanes))
    encountersAlong = encountersTowards
    #Iniatialize rates and speeds lists
    ratesHour = []
    speedsKmh = []
    

    #Generate lists of variables for computing number of encounters
    if fiets_t_allowed:
        ratesHour.append(fiets_t / 24) #Convert daily rate to per hour rate     
        speedsKmh.append(fietsSpeedKmh)     

    if auto_t_allowed:
        for _ in range(aantal_rijstroken_terug):  # "terug" = towards
            ratesHour.append(intensiteit_terug_pae_per_dag / 24 / aantal_rijstroken_terug)  # divide by lanes
            speedsKmh.append(snelheid_terug_km_per_uur)
            
    if auto_h_allowed:
        for _ in range(aantal_rijstroken_heen):  # "heen" = along
            ratesHour.append(intensiteit_heen_pae_per_dag / 24 / aantal_rijstroken_heen)  # divide by lanes
            speedsKmh.append(snelheid_heen_km_per_uur)
    
    if fiets_h_allowed:
        ratesHour.append(fiets_h / 24) #Convert daily rate to per hour rate
        speedsKmh.append(fietsSpeedKmh)
    
    #Compute encounters for each number of lanes
    for laneA in range(nLanes):
        # only upper triangle so that encounters are not double ocunters (j>i)
        for laneB in range(laneA,nLanes):
            rateA, rateB = ratesHour[laneA], ratesHour[laneB]
            speedA, speedB = speedsKmh[laneA], speedsKmh[laneB]
            enc = computeEncounters(rateA, rateB, speedA, speedB, length_km, 0.84,groupWindow=2)
            encountersAlong[laneA, laneB] = enc['Encounters (along)']
            encountersTowards[laneA, laneB] = enc['Encounters (towards)']

    #Multiply encounter matrix by interaction matrix
    encountersAlong = np.multiply(encountersAlong,interactionAlong)
    encountersTowards = np.multiply(encountersTowards,interactionTowards)
    
    #Total amount of encounters
    totalEncountersHour = np.sum(encountersAlong) + np.sum(encountersTowards)
    
    
    #Set lane types for differntiating between encounter types
    laneTypes = []
    if fiets_t_allowed:
        laneTypes.append('bike')  # fiets_t
    if auto_t_allowed:
        laneTypes.extend(['car'] * aantal_rijstroken_terug)  # car_t
    if auto_h_allowed:
        laneTypes.extend(['car'] * aantal_rijstroken_heen)  # car_h
    if fiets_h_allowed:
        laneTypes.append('bike')  # fiets_h
        
    # Initialize encounter type counters
    ccEncounters = 0  # car-car
    bcEncounters = 0  # bike-car or car-bike
    bbEncounters = 0  # bike-bike
    
    # Compute encounters per lane pair and classify by type
    nLanes = len(laneTypes)
    for laneA in range(nLanes):
        for laneB in range(laneA, nLanes):  # upper triangle to avoid double counting
            # Total encounters for this lane pair
            totalPairEnc = encountersAlong[laneA, laneB] + encountersTowards[laneA, laneB]
            
            typeA = laneTypes[laneA]
            typeB = laneTypes[laneB]
            
            if typeA == 'car' and typeB == 'car':
                ccEncounters += totalPairEnc
            elif typeA == 'bike' and typeB == 'bike':
                bbEncounters += totalPairEnc
            else:  # one car, one bike
                bcEncounters += totalPairEnc
    
    results = {
        'totalEncountersHour': totalEncountersHour,
        'ccEncountersHour': ccEncounters,
        'bcEncountersHour': bcEncounters,
        'bbEncountersHour': bbEncounters}
        
    # Return results
    return results
#----------------
#Example usage
#---------------

if __name__ == "__main__":
    # Example road segment attributes
    aantal_rijstroken_heen = 1
    aantal_rijstroken_terug = 0
    intensiteit_heen_pae_per_dag = 1000
    intensiteit_terug_pae_per_dag = 0
    snelheid_heen_km_per_uur = 60
    snelheid_terug_km_per_uur= 60
    fiets_h = 20
    fiets_t = 20
    fietsSpeedKmh = 18  # default average cyclist speed
    length_km = 0.1

    # Compute encounters for this road segment
    results = computeEncountersRoad(
        aantal_rijstroken_heen,
        aantal_rijstroken_terug,
        intensiteit_heen_pae_per_dag,
        intensiteit_terug_pae_per_dag,
        snelheid_heen_km_per_uur,
        snelheid_terug_km_per_uur,
        fiets_h,
        fiets_t,
        fietsSpeedKmh,
        length_km
    )


    
    
    
    
    