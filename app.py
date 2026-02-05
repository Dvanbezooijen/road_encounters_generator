# -*- coding: utf-8 -*-
"""
Created on Wed Feb  4 11:20:17 2026

@author: dvbezooijen
"""

import streamlit as st
from roadEncountersGenerator import computeEncountersRoad  # adjust import

st.title("Road user encounter model")

st.header("Road data")
st.write("Input the road data. Click the 'Compute encounters' button below to run the model. Notes: ""\n"" There are two directions on the road 'to' and 'from' \n A maximum of 1 cycling lane per direction is available \n If no cyclist lane or cyclists are present, enter a rate of 0")
   
aantal_rijstroken_heen = st.number_input(
    "Number of motor vehicle lanes (to)", min_value=0, value=1, step=1
)

aantal_rijstroken_terug = st.number_input(
    "Number of motor vehicle lanes (from)", min_value=0, value=0, step=1
)

intensiteit_heen = st.number_input(
    "Motor vehicle rate to (per day)", min_value=0, value=1000
)

intensiteit_terug = st.number_input(
    "Motor vehicle rate from (per day)", min_value=0, value=0
)

snelheid_heen = st.number_input(
    "Motor vehicle speed to (km/h)", min_value=0, value=60
)

snelheid_terug = st.number_input(
    "Motor vehicle speed from (km/h)", min_value=0, value=60
)

fiets_h = st.number_input(
    "Cycling rate to (per day)", min_value=0, value=20
)

fiets_t = st.number_input(
    "Cycling rate from (per day)", min_value=0, value=20
)

fietsSpeedKmh = st.number_input(
    "Cyclists speed (km/h)", min_value=0, value=18
)

length_km = st.number_input(
    "Road length (km)", min_value=0.0, value=1.0
)

if st.button("Compute encounters"):
    results = computeEncountersRoad(
        aantal_rijstroken_heen,
        aantal_rijstroken_terug,
        intensiteit_heen,
        intensiteit_terug,
        snelheid_heen,
        snelheid_terug,
        fiets_h,
        fiets_t,
        fietsSpeedKmh,
        length_km
    )

    st.subheader("Results (per day)")
    st.metric(
        "Total number of encounters",
        f"{results['totalEncountersHour']*24:.0f}"
    )

    st.write("Breakdown:")
    st.write(f"🚗🚗 MV–MV: {results['ccEncountersHour']*24:.0f}")
    st.write(f"🚲🚗 Bike–MV: {results['bcEncountersHour']*24:.0f}")
    st.write(f"🚲🚲 Bike–Bike: {results['bbEncountersHour']*24:.0f}")
    st.write("Since the model outputs float point numbers, rounding errors may apply the the above results")
