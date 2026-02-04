# -*- coding: utf-8 -*-
"""
@author: Dylan van Bezooijen
"""

import numpy as np

def generateInteractionMatrices(aantal_rijstroken_heen: int,
                                aantal_rijstroken_terug: int,
                                fiets_h_allowed: int,
                                fiets_t_allowed: int,
                                auto_h_allowed: int,
                                auto_t_allowed: int):
    """
    Generate lane interaction matrices for a road segment.
    
    Parameters: 
    aantal_rijstroken_heen : Number of lanes in the "heen" direction (outbound)
    aantal_rijstroken_terug : Number of lanes in the "terug" direction (inbound)
    fiets_h_allowed : Number of cycling lanes in "heen" direction (0 or 1)
    fiets_t_allowed : Number of cycling lanes in "terug" direction (0 or 1)
    intensiteit_heen_pae_per_dag : car volume per day in 'heen' direction
    intensiteit_terug_pae_per_dag : car volume per day in 'terug' direction
    
    Returns:
    interactionAlong : NxN matrix of lane interactions along the lane
    interactionToward  NxN matrix of lane interactions toward opposing lanes
    """
    
    # Create additonal bool parameter because sometimes traffic is allowed but not present
    boolAutoHeen = int((aantal_rijstroken_heen * auto_h_allowed) > 0)
    boolAutoTerug = int((aantal_rijstroken_terug * auto_t_allowed) > 0)

    # Total lanes
    nLanes = aantal_rijstroken_heen * boolAutoHeen + aantal_rijstroken_terug *boolAutoTerug + fiets_h_allowed + fiets_t_allowed
    interactionAlong = np.zeros((nLanes, nLanes), dtype=int)
    interactionToward = np.zeros((nLanes, nLanes), dtype=int)

    # Determine the index separating directions
    edgeIndex = fiets_t_allowed + (aantal_rijstroken_terug* auto_t_allowed) - 1  # last lane of terug direction
          
    # Build along matrix
    for a in range(nLanes):
        interactionAlong[a, a] = 1  # self-interaction always for along
        for b in range(nLanes):
            if abs(a - b) == 1:  # lanes next to each other 
                interactionAlong[a, b] = 1 #these interact 
                
    # Remove interactions for along between opposing car lanes if opposing traffic exists
    if boolAutoTerug == 1 and boolAutoHeen == 1: #when there is both to and from car traffic
        #For the lanes touching each other but travelling in opposite direction there is no along encounter
        interactionAlong[edgeIndex, edgeIndex + 1] = 0 
        interactionAlong[edgeIndex + 1, edgeIndex] = 0
    
    #Build toward matrix
    if boolAutoTerug == 1 and boolAutoHeen == 1: #When there is both to and from car traffic
        #If they are touching each other on edge, toward encounter happens
        interactionToward[edgeIndex, edgeIndex + 1] = 1 
        interactionToward[edgeIndex + 1, edgeIndex] = 1
    
    # Additional toward encounters for roads with cyclists
    if fiets_t_allowed == 1: #When cyclists are allowed on the from direction
        if boolAutoHeen == 1: #and there is a from direction for cars    
            # They interact with opposing motor lanes
            interactionToward[0, edgeIndex + 1] = 1
            interactionToward[edgeIndex + 1, 0] = 1
    if fiets_h_allowed == 1: #When cyclist are allowed on the to direction
        if boolAutoTerug == 1: #and there is a to direction for cars
            #They interact with the opposing motor lane
            interactionToward[-1, edgeIndex] = 1
            interactionToward[edgeIndex, -1] = 1
           
    return interactionAlong, interactionToward

# -----------------------
# Example usage
# -----------------------
if __name__ == "__main__":
    # Example: Hengelosestraat
    interactionAlong, interactionToward = generateInteractionMatrices(
        aantal_rijstroken_heen=1,
        aantal_rijstroken_terug=0,
        fiets_h_allowed = 0,
        fiets_t_allowed = 0,
        auto_h_allowed= 1,
        auto_t_allowed= 0,
            )

    print("Interaction Along Matrix:\n", interactionAlong)
    print("\nInteraction Toward Matrix:\n", interactionToward)
            
    

