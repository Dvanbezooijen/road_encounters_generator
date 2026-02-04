# -*- coding: utf-8 -*-
"""
Created on Wed Feb  4 11:20:17 2026

@author: dvbezooijen
"""

import streamlit as st
from roadEncountersGenerator import computeEncountersRoad  # adjust import

st.title("Road User Encounters Calculator")

st.header("Road configuration")

aantal_rijstroken_heen = st.number_input(
    "Motorvoertuig rijstroken (heen)", min_value=0, value=1, step=1
)

aantal_rijstroken_terug = st.number_input(
    "Motorvoertuig rijstroken (terug)", min_value=0, value=0, step=1
)

intensiteit_heen = st.number_input(
    "Motorvoertuig intensiteit heen (per etmaal)", min_value=0.0, value=1000.0
)

intensiteit_terug = st.number_input(
    "Motorvoertuig intensiteit terug (per etmaal)", min_value=0.0, value=0.0
)

snelheid_heen = st.number_input(
    "Snelheid motorvoertuigen heen (km/h)", min_value=0.0, value=60.0
)

snelheid_terug = st.number_input(
    "Snelheid motorvoertuigen terug (km/h)", min_value=0.0, value=60.0
)

fiets_h = st.number_input(
    "Fiets intensiteit heen (per etmaal)", min_value=0.0, value=20.0
)

fiets_t = st.number_input(
    "Fiets intensiteit terug (per etmaal)", min_value=0.0, value=20.0
)

fietsSpeedKmh = st.number_input(
    "Fiets snelheid (km/h)", min_value=0.0, value=18.0
)

length_km = st.number_input(
    "Weg lengte (km)", min_value=0.0, value=0.1
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

    st.subheader("Results (per hour)")
    st.metric(
        "Total encounters",
        f"{results['totalEncountersHour']:.2f}"
    )

    st.write("Breakdown:")
    st.write(f"🚗🚗 Car–Car: {results['ccEncountersHour']:.2f}")
    st.write(f"🚲🚗 Bike–Car: {results['bcEncountersHour']:.2f}")
    st.write(f"🚲🚲 Bike–Bike: {results['bbEncountersHour']:.2f}")
