"""
This module provides functions for performing mathematical calculations and working with data.
"""

from math import radians, sin, cos, sqrt, atan2
import numpy as np
import pandas as pd
from data_model import Gaivota

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the distance between two points on the Earth's surface using the Haversine formula.
    
    Parameters
    ---------------
    lat1: float
        Latitude of the first point in degrees.
    lon1: float
        Longitude of the first point in degrees.
    lat2: float
        Latitude of the second point in degrees.
    lon2: float
        Longitude of the second point in degrees.
        
    Returns
    ---------------
    distance: float
        The distance between the two points in kilometers.
    """
    # Radius of the Earth in kilometers
    radius = 6371.0

    # Convert latitude and longitude from degrees to radians
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    # Calculate the change in coordinates
    dlon = lon2 - lon1
    dlat = lat2 - lat1

    # Apply Haversine formula
    chord_length_squared = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    angular_distance = 2 * atan2(sqrt(chord_length_squared), sqrt(1 - chord_length_squared))

    # Calculate the distance
    distance = radius * angular_distance
    return distance

def calculate_distance_between_airports(source: str, destination: str) -> float:
    """
    Calculate the distance between two airports given their IATAs.
    
    Parameters
    ---------------
    source: str
        The IATA code of the source airport.
    destination: str
        The IATA code of the destination airport.
        
    Returns
    ---------------
    distance: float
        The distance between the source and destination airports in kilometers.
    """
    # Create an instance of the Gaivota class
    gaivota = Gaivota()

    # Find latitude and longitude of source airport
    source_info = gaivota.airports[gaivota.airports['IATA'] == source]
    source_lat = source_info['Latitude'].values[0]
    source_lon = source_info['Longitude'].values[0]

    # Find latitude and longitude of destination airport
    dest_info = gaivota.airports[gaivota.airports['IATA'] == destination]
    dest_lat = dest_info['Latitude'].values[0]
    dest_lon = dest_info['Longitude'].values[0]

    # Calculate distance between the two airports
    distance = calculate_distance(source_lat, source_lon, dest_lat, dest_lon)
    return distance

def add_airports_distances(gaivota: Gaivota):
    """
    Update the airports_distances dictionary with distances between all pairs of airports.
    
    Parameters
    ---------------
    gaivota: Gaivota
        An instance of the Gaivota class containing airport data.
    """
    airports_dirty = gaivota.airports
    airport_df = airports_dirty[airports_dirty['IATA'] != "\\N"].reset_index(drop=True)

    # Calculate distances using vectorized haversine function
    distances = haversine_vectorized(airport_df['Latitude'].values[:, np.newaxis], 
                                      airport_df['Longitude'].values[:, np.newaxis], 
                                      airport_df['Latitude'].values, 
                                      airport_df['Longitude'].values)

    # Create DataFrame with distances
    distance_df = pd.DataFrame({
        'Origin': np.repeat(airport_df['IATA'], len(airport_df)),
        'Destination': np.tile(airport_df['IATA'], len(airport_df)),
        'Distance': distances.flatten()
    })

    # Filter out rows where the airports are the same
    distance_df = distance_df[distance_df['Origin'] != distance_df['Destination']]

    # Drop duplicate airport distances calculations
    unique_distances_df = distance_df.drop_duplicates(subset=['Distance'])

    # Assign DF to instance attribute
    gaivota.airports_distances = unique_distances_df

def haversine_vectorized(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points on the Earth's surface
    given their longitudes and latitudes using the Haversine formula.

    Parameters
    ---------------
    lat1 : float
        Latitude of the first point in degrees.
    lon1 : float
        Longitude of the first point in degrees.
    lat2 : float
        Latitude of the second point in degrees.
    lon2 : float
        Longitude of the second point in degrees.

    Returns
    ---------------
    distance : float
        The computed distance between the two points in kilometers.
    """
    radius = 6371.0  # Earth radius in km

    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    chord_length_squared = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
    angular_distance = 2 * np.arctan2(np.sqrt(chord_length_squared),
                                      np.sqrt(1 - chord_length_squared))

    distance = radius * angular_distance

    return distance
