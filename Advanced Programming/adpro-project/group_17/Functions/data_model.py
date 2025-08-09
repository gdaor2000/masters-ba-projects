""" This module contains one class with the purpose of analyzing flight data."""

import os
import zipfile
from typing import List, Any
import pandas as pd
import requests
from pydantic import BaseModel, HttpUrl, Field
from shapely.geometry import Point, LineString
from fuzzywuzzy import process
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
from langchain_openai import OpenAI
from langchain.chat_models import ChatOpenAI
from IPython.display import Markdown
from openai import OpenAI
from dotenv import load_dotenv

class Gaivota(BaseModel):
    """
    Class to explain and analyze Commercial Airflight data.

    Attributes
    ----------
    project_dir : str
        Root directory of the project. The default value is the current working directory.
    downloads_dir : str
        Directory where downloaded files are stored. By default,
        it is a 'downloads' folder in the current working directory.
    data_files : List[dict]
        A list of dictionaries, each containing a URL to a CSV file and its corresponding filename.
        These files are essential data sources for the class.
    airlines : Any
        A dictionary or DataFrame that holds data about airlines.
        Initially empty.
    airports : Any
        A dictionary or DataFrame that holds data about airports.
        Initially empty.
    airplanes : Any
        A dictionary or DataFrame that holds data about airplanes.
        Initially empty.
    routes : Any
        A dictionary or DataFrame that holds data about flight routes.
        Initially empty.
    airports_distances : Any
        A dictionary or DataFrame that holds data about distances between airports.
        Initially empty.

    """
    project_dir: str = Field(default=os.getcwd(),
                             description="Root directory of the project.")
    downloads_dir: str = Field(default=os.path.join(os.getcwd(), 'downloads'))
    data_files: List[dict] = Field(default=[
        {'url':
         'https://gitlab.com/adpro1/adpro2024/-/raw/main/Files/airlines.csv',
         'filename': 'airlines.csv'},
        {'url':
         'https://gitlab.com/adpro1/adpro2024/-/raw/main/Files/airplanes.csv',
         'filename': 'airplanes.csv'},
        {'url':
         'https://gitlab.com/adpro1/adpro2024/-/raw/main/Files/airports.csv',
         'filename': 'airports.csv'},
        {'url':
         'https://gitlab.com/adpro1/adpro2024/-/raw/main/Files/routes.csv',
         'filename': 'routes.csv'}])

    airlines: Any = {}
    airports: Any = {}
    airplanes: Any = {}
    routes: Any = {}
    airports_distances: Any = {}

    def __init__(self):
        super().__init__()

        # Create downloads directory if it does not exist
        if not os.path.exists(self.downloads_dir):
            os.makedirs(self.downloads_dir)

        # Download and read datasets into corresponding DataFrames
        for file_info in self.data_files:
            file_path = os.path.join(self.downloads_dir, file_info['filename'])

            # Check if the file already exists
            if not os.path.exists(file_path):
                print(f"Downloading {file_info['filename']}...")
                self.download_file(file_info['url'], file_path)
            else:
                print(f"{file_info['filename']} already exists.")

            # Read the dataset into a DataFrame
            df_f = pd.read_csv(file_path)

            # Set the modified DataFrame as an attribute of the class
            setattr(self, os.path.splitext(file_info['filename'])[0], df_f)

            self.remove_columns()

    def download_file(self, url: HttpUrl, file_path: str) -> None:
        """Funtion to download the files online"""
        response = requests.get(url)
        if response.status_code == 200:
            with open(file_path, 'wb') as file_d:
                file_d.write(response.content)
            print(f"{file_path} downloaded successfully.")
        else:
            print(
                f"Failed to download {file_path}. Status code: {response.status_code}")

        # Check if the file was downloaded successfully
        if not os.path.exists(file_path):
            print(
                f"Trying to download {os.path.basename(file_path)} from ZIP archive...")
            zip_url = 'https://gitlab.com/adpro1/adpro2024/-/raw/main/Files/flight_data.zip?inline=false'
            zip_file_path = os.path.join(self.downloads_dir, 'flight_data.zip')
            self.download_file(zip_url, zip_file_path)

            # Extract the ZIP archive
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(self.downloads_dir)

            # Check if the required file exists after extraction
            extracted_file_path = os.path.join(
                self.downloads_dir, os.path.basename(file_path))
            if os.path.exists(extracted_file_path):
                print(
                    f"{os.path.basename(file_path)} extracted from ZIP archive successfully.")
            else:
                print(
                    f"Failed to extract {os.path.basename(file_path)} from ZIP archive.")

    def remove_columns(self):
        """Funtion to download the files online"""
        if isinstance(self.airlines, pd.DataFrame) and not self.airlines.empty:
            self.airlines = self.airlines.drop(
                columns=['Alias', 'Active'], errors='ignore')
        if isinstance(self.airports, pd.DataFrame) and not self.airports.empty:
            self.airports = self.airports.drop(
                columns=['Source', 'DST', 'Timezone'], errors='ignore')

    def plot_airports_by_country(self, country_name: str):
        """
        Plot all airports in a given country.

        This method receives a string (a country name) and
        plots a map of the country and all it's airports.

        Parameters
        ----------
        country_name : string
            A string that will indicate which country to plot

        Returns
        -------
        None
            This method does not return any value but shows a plot.
        """
        airports = getattr(self, 'airports', None)
        if airports is None:
            print("Airports data is not available.")
            return

        country_airports = airports[airports['Country'].str.contains(
            country_name, case=False, na=False)]
        if country_airports.empty:
            print(f"No airports found in {country_name}.")
            return

        gdf_airports = gpd.GeoDataFrame(
            country_airports,
            geometry=gpd.points_from_xy(
                country_airports.Longitude, country_airports.Latitude
            )
        )

        world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

        fig, axes = plt.subplots(1, figsize=(15, 10))
        world[world.name.str.contains(country_name, case=False)].plot(
            axes=axes, color='white', edgecolor='black'
        )
        gdf_airports.plot(
            axes=axes,
            marker='o',
            color='blue',
            markersize=25,
            label='-Airport')
        axes.legend(loc='upper left')
        plt.title(f"Airports in {country_name}")
        plt.show()

    def distance_analysis(self):
        """
        Plots the distribution of flight distances for all flights.
        Args:
            None.
        Returns:
            None. Displays a plot of the distribution of distances for all flights.
        """
        from real_distances import calculate_distance

        # Ensure the airports DataFrame is loaded with the necessary columns
        if 'Latitude' not in self.airports.columns or 'Longitude' not in self.airports.columns:
            print("Airports data does not contain Latitude and Longitude information.")
            return

        # Initialize a list to store distances
        distances = []

        # Iterate over the rows in the routes DataFrame
        for _, row in self.routes.iterrows():
            # Get the source and destination airports' IATA codes
            source_iata = row['Source airport']
            destination_iata = row['Destination airport']

            # Find the latitude and longitude for both the source and
            # destination airports
            source_info = self.airports.loc[self.airports['IATA']
                                            == source_iata]
            destination_info = self.airports.loc[self.airports['IATA']
                                                 == destination_iata]

            # Check if we found the airport information
            if not source_info.empty and not destination_info.empty:
                source_lat = source_info['Latitude'].values[0]
                source_lon = source_info['Longitude'].values[0]
                dest_lat = destination_info['Latitude'].values[0]
                dest_lon = destination_info['Longitude'].values[0]

                # Calculate the distance between the two airports
                distance = calculate_distance(
                    source_lat, source_lon, dest_lat, dest_lon)
                distances.append(distance)

        # Plot the distribution of distances
        plt.figure(figsize=(10, 6))
        sns.histplot(distances, bins=50, kde=True)
        plt.title("Distribution of Flight Distances")
        plt.xlabel("Distance (km)")
        plt.ylabel("Frequency")
        plt.show()

    def internal_airport(self, airport, show_internal=True):
        """
        Plots internal and/or external flights involving a specified airport.

        Args:
            airport (str): IATA code of the airport.
            show_internal (bool, optional):
            If True, show only internal flights;
            otherwise, show all flights. Default is True.

        Returns:
            None. Displays a matplotlib plot of the flights on a world map.
        """
        airports = getattr(self, 'airports', None)
        routes = getattr(self, 'routes', None)
        # Create GeoDataFrame
        source = routes[["index", "Airline", "Airline ID",
                         "Source airport",
                         "Source airport ID", "Codeshare",
                         "Stops", "Equipment"]]
        destination = routes[["index", "Airline", "Airline ID",
                              "Destination airport", "Destination airport ID",
                              "Codeshare", "Stops", "Equipment"]]
        source_country = source.merge(airports,
                                      left_on="Source airport",
                                      right_on="IATA", how="left")
        destination_country = destination.merge(airports,
                                                left_on="Destination airport",
                                                right_on="IATA", how="left")
        source_country = source_country.iloc[:, [0, 3, 12, 15, 16]]
        source_country.rename(
            columns={
                "index_x": "index",
                "Country": "Source Country",
                "Latitude": "Source Latitude",
                "Longitude": "Source Longitude"},
            inplace=True)
        destination_country = destination_country.iloc[:, [0, 3, 12, 15, 16]]
        destination_country.rename(
            columns={
                "index_x": "index",
                "Country": "Destination Country",
                "Latitude": "Destination Latitude",
                "Longitude": "Destination Longitude"},
            inplace=True)
        internaldf = source_country.merge(destination_country,
                                          left_on="index",
                                          right_on="index",
                                          how="left")
        internaldf.dropna(inplace=True)
        internaldf["internal"] = internaldf["Source Country"] == internaldf["Destination Country"]
        internaldf = internaldf[(internaldf["Source airport"] == airport) | (
            internaldf["Destination airport"] == airport)]

        if not internaldf.empty:
            if show_internal:
                # Filter only internal flights
                internaldf = internaldf[internaldf["internal"]]

                # Create LineString geometry for the flights
                internaldf['flight_geometry'] = internaldf.apply(
                    lambda row: LineString([(row['Source Longitude'], row['Source Latitude']),
                                            (row['Destination Longitude'], row['Destination Latitude'])]),
                    axis=1
                )

                buffer_factor = 20  # You can adjust this factor based on your preference

                bbox = (
                    internaldf[['Source Longitude', 'Destination Longitude']].min().min() - buffer_factor,
                    internaldf[['Source Latitude', 'Destination Latitude']].min().min() - buffer_factor,
                    internaldf[['Source Longitude', 'Destination Longitude']].max().max() + buffer_factor,
                    internaldf[['Source Latitude', 'Destination Latitude']].max().max() + buffer_factor
                )

                # Plot world map with zoom
                world = gpd.read_file(
                    gpd.datasets.get_path('naturalearth_lowres'))
                axes = world.plot(figsize=(10, 6), edgecolor='black')

                # Plot airports
                gdf_airports_source = gpd.GeoDataFrame(
                    internaldf, geometry=[
                        Point(
                            lon, lat) for lon, lat in zip(
                            internaldf['Source Longitude'], internaldf['Source Latitude'])])
                gdf_airports_source.plot(
                    axes=axes,
                    marker='o',
                    color='red',
                    markersize=50,
                    label='Source Airports')

                gdf_airports_dest = gpd.GeoDataFrame(
                    internaldf, geometry=[
                        Point(
                            lon, lat) for lon, lat in zip(
                            internaldf['Destination Longitude'], internaldf['Destination Latitude'])])
                gdf_airports_dest.plot(
                    axes=axes,
                    marker='o',
                    color='blue',
                    markersize=50,
                    label='Destination Airports')

                # Plot flights
                gdf_flights = gpd.GeoDataFrame(
                    internaldf, geometry=internaldf['flight_geometry'])
                gdf_flights.plot(
                    axes=axes,
                    color='green',
                    linewidth=2,
                    linestyle='dashed',
                    label='Flights')

                # Set plot limits based on the bounding box
                axes.set_xlim([bbox[0], bbox[2]])
                axes.set_ylim([bbox[1], bbox[3]])

                plt.title(f'Flights Between Airports in {airport}')
                plt.legend()
                plt.show()
            else:
                buffer_factor = 0  # You can adjust this factor based on your preference
                bbox = (
                    internaldf[['Source Longitude', 'Destination Longitude']].min().min() - buffer_factor,
                    internaldf[['Source Latitude', 'Destination Latitude']].min().min() - buffer_factor,
                    internaldf[['Source Longitude', 'Destination Longitude']].max().max() + buffer_factor,
                    internaldf[['Source Latitude', 'Destination Latitude']].max().max() + buffer_factor
                )

                # Create LineString geometry for the flights
                internaldf['flight_geometry'] = internaldf.apply(
                    lambda row: LineString([(row['Source Longitude'], row['Source Latitude']),
                                            (row['Destination Longitude'], row['Destination Latitude'])]),
                    axis=1
                )

                # Plot world map without zoom
                world = gpd.read_file(
                    gpd.datasets.get_path('naturalearth_lowres'))
                axes = world.plot(figsize=(10, 6), edgecolor='black')

                # Plot airports
                gdf_airports_source = gpd.GeoDataFrame(
                    internaldf, geometry=[
                        Point(
                            lon, lat) for lon, lat in zip(
                            internaldf['Source Longitude'], internaldf['Source Latitude'])])
                gdf_airports_source.plot(
                    axes=axes,
                    marker='o',
                    color='red',
                    markersize=50,
                    label='Source Airports')

                gdf_airports_dest = gpd.GeoDataFrame(
                    internaldf, geometry=[
                        Point(
                            lon, lat) for lon, lat in zip(
                            internaldf['Destination Longitude'], internaldf['Destination Latitude'])])
                gdf_airports_dest.plot(
                    axes=axes,
                    marker='o',
                    color='blue',
                    markersize=50,
                    label='Destination Airports')

                # Plot flights
                gdf_flights = gpd.GeoDataFrame(
                    internaldf, geometry=internaldf['flight_geometry'])
                gdf_flights.plot(
                    axes=axes,
                    color='green',
                    linewidth=2,
                    linestyle='dashed',
                    label='Flights')

                # Set plot limits based on the bounding box
                axes.set_xlim([bbox[0], bbox[2]])
                axes.set_ylim

    def plot_most_used_airplane_models(self, countries=None, top_n=None):
        """
        Plots the most used airplane models based on the number of routes they operate on.

        This method filters the routes based on the countries provided and then counts the occurrences
        of each airplane model to find the most used ones. It then plots the top N most used models.

        Parameters
        ----------
        countries : list, optional
            A list of country names to filter the airports. If None, no country filter is applied.
        top_n : int, optional
            The number of top airplane models to display in the plot. If None, all models are displayed.

        Returns
        -------
        None
            This method does not return any value but shows a bar plot.
        """
        # Attempt to convert 'Source airport ID' and 'Destination airport ID' to integers
        # Use errors='coerce' to set any problematic values to NaN, which can
        # then be handled appropriately
        self.routes['Source airport ID'] = pd.to_numeric(
            self.routes['Source airport ID'],
            errors='coerce').fillna(0).astype(int)
        self.routes['Destination airport ID'] = pd.to_numeric(
            self.routes['Destination airport ID'],
            errors='coerce').fillna(0).astype(int)

        if countries is not None:
            if not isinstance(countries, list):
                countries = [countries]

            # Filter airports within the specified countries
            country_airports = self.airports[self.airports['Country'].isin(
                countries)]['Airport ID'].unique()

            # Filter routes where either the source or destination airport ID
            # is in the specified countries
            filtered_routes = self.routes[(self.routes['Source airport ID'].isin(
                country_airports)) | (self.routes['Destination airport ID'].isin(country_airports))]
        else:
            filtered_routes = self.routes

        # Modify this line to handle None value for top_n
        equipment_counts = filtered_routes['Equipment'].str.split(
            expand=True).stack().value_counts()
        if top_n is not None:
            equipment_counts = equipment_counts.head(top_n)

        # Check if there are any airplane models to plot
        if equipment_counts.empty:
            print("No data found for the specified criteria.")
            return

        # Plotting the results
        plt.figure(figsize=(10, 6))
        sns.barplot(
            x=equipment_counts.values,
            y=equipment_counts.index,
            palette='viridis')
        plt.title(f'Top {top_n} Most Used Airplane Models')
        plt.xlabel('Number of Routes')
        plt.ylabel('Equipment (Airplane Model)')
        plt.show()

    def internal_country2(
            self,
            country,
            show_internal=True,
            short_haul_cutoff=None):
        """
        Plots internal flights within a specified country.

        Args:
            country (str): The country for which to plot internal flights.
            show_internal (bool): If True, show only internal flights; otherwise, show all flights.
            short_haul_cutoff (float, optional): The cutoff distance in kilometers to define short-haul flights.

        Returns:
            None. Displays a matplotlib plot of the flights.
        """

        from real_distances import calculate_distance

        source = self.routes[["index",
                              "Airline",
                              "Airline ID",
                              "Source airport",
                              "Source airport ID",
                              "Codeshare",
                              "Stops",
                              "Equipment"]]
        destination = self.routes[["index",
                                   "Airline",
                                   "Airline ID",
                                   "Destination airport",
                                   "Destination airport ID",
                                   "Codeshare",
                                   "Stops",
                                   "Equipment"]]

        source_country = source.merge(
            self.airports,
            left_on="Source airport",
            right_on="IATA",
            how="left")
        destination_country = destination.merge(
            self.airports,
            left_on="Destination airport",
            right_on="IATA",
            how="left")

        source_country = source_country.iloc[:, [0, 3, 12, 15, 16]]
        source_country.rename(
            columns={
                "index_x": "index",
                "Country": "Source Country",
                "Latitude": "Source Latitude",
                "Longitude": "Source Longitude"},
            inplace=True)

        destination_country = destination_country.iloc[:, [0, 3, 12, 15, 16]]
        destination_country.rename(
            columns={
                "index_x": "index",
                "Country": "Destination Country",
                "Latitude": "Destination Latitude",
                "Longitude": "Destination Longitude"},
            inplace=True)

        internal_df = source_country.merge(
            destination_country, on="index", how="left")
        internal_df.dropna(inplace=True)
        internal_df["internal"] = internal_df["Source Country"] == internal_df["Destination Country"]
        internal_df = internal_df[internal_df["Source Country"] == country]

        # Apply the calculate_distance function row-wise
        internal_df['Distance'] = internal_df.apply(
            lambda row: calculate_distance(
                row['Source Latitude'],
                row['Source Longitude'],
                row['Destination Latitude'],
                row['Destination Longitude']),
            axis=1)
        if short_haul_cutoff is None:
            short_haul_cutoff = 1000
            # Now you can filter short-haul flights and sum up their distances
            # as before
        internal_df['flight_type'] = internal_df['Distance'].apply(
            lambda x: 'short-haul' if x < short_haul_cutoff else 'long-haul')

        short_haul_distances = internal_df[internal_df['Distance']
                                           < short_haul_cutoff]['Distance'].sum()

        # Assume a standard emissions factor for aviation and for rail, and
        # calculate potential savings
        avg_emission_factor_flight = 0.115  # CO2 kg per km per passenger, example value
        # CO2 kg per km per passenger, example value, significantly lower than
        # flights
        avg_emission_factor_rail = 0.025
        total_emissions_flight = short_haul_distances * avg_emission_factor_flight
        potential_emissions_rail = short_haul_distances * avg_emission_factor_rail
        emissions_savings = total_emissions_flight - potential_emissions_rail

        if not internal_df.empty:
            if show_internal:
                # Filter only internal flights
                internal_df = internal_df[internal_df["internal"]]

                # Create LineString geometry for the flights
                internal_df['flight_geometry'] = internal_df.apply(
                    lambda row: LineString([(row['Source Longitude'], row['Source Latitude']),
                                            (row['Destination Longitude'], row['Destination Latitude'])]),
                    axis=1
                )

                buffer_factor = 3  # You can adjust this factor based on your preference
                bbox = (
                    internal_df['Source Longitude'].min() - buffer_factor,
                    internal_df['Source Latitude'].min() - buffer_factor,
                    internal_df['Source Longitude'].max() + buffer_factor,
                    internal_df['Source Latitude'].max() + buffer_factor
                )

                # Plot world map with zoom
                world = gpd.read_file(
                    gpd.datasets.get_path('naturalearth_lowres'))
                axes = world.plot(figsize=(10, 6), edgecolor='black')

                # Plot airports
                gdf_airports = gpd.GeoDataFrame(
                    internal_df, geometry=[
                        Point(
                            lon, lat) for lon, lat in zip(
                            internal_df['Source Longitude'], internal_df['Source Latitude'])])
                gdf_airports.plot(
                    axes=axes,
                    marker='o',
                    color='red',
                    markersize=50,
                    label='Airports')

                # Plot flights
                # Differentiate flights by type
                gdf_flights_short = gpd.GeoDataFrame(
                    internal_df[internal_df['flight_type'] == 'short-haul'], geometry='flight_geometry')
                gdf_flights_long = gpd.GeoDataFrame(
                    internal_df[internal_df['flight_type'] == 'long-haul'], geometry='flight_geometry')

                gdf_flights_short.plot(
                    axes=axes,
                    color='green',
                    linewidth=2,
                    linestyle='-',
                    label='Short-haul Flights')
                gdf_flights_long.plot(
                    axes=axes,
                    color='blue',
                    linewidth=2,
                    linestyle='-',
                    label='Long-haul Flights')

                # Set plot limits based on the bounding box
                axes.set_xlim([bbox[0], bbox[2]])
                axes.set_ylim([bbox[1], bbox[3]])

                annotation_text = f'Potential CO2 Savings: {emissions_savings:.2f} kg CO2 by replacing short-haul flights with rail'
                plt.annotate(
                    annotation_text, xy=(
                        0.5, 0), xycoords='axes fraction', xytext=(
                        0, -40), textcoords='offset points', ha='center', fontsize=10, bbox=dict(
                        boxstyle="round", alpha=0.5))

                plt.title(f'Flights Between Airports in {country}')
                plt.legend()
                plt.show()
            else:
                # Create LineString geometry for the flights
                internal_df['flight_geometry'] = internal_df.apply(
                    lambda row: LineString([(row['Source Longitude'], row['Source Latitude']),
                                            (row['Destination Longitude'], row['Destination Latitude'])]),
                    axis=1
                )

                # Plot world map without zoom
                world = gpd.read_file(
                    gpd.datasets.get_path('naturalearth_lowres'))
                axes = world.plot(figsize=(10, 6), edgecolor='black')

                # Plot airports
                gdf_airports = gpd.GeoDataFrame(
                    internal_df, geometry=[
                        Point(
                            lon, lat) for lon, lat in zip(
                            internal_df['Source Longitude'], internal_df['Source Latitude'])])
                gdf_airports.plot(
                    axes=axes,
                    marker='o',
                    color='red',
                    markersize=50,
                    label='Airports')

                # Plot flights
                gdf_flights = gpd.GeoDataFrame(
                    internal_df, geometry=internal_df['flight_geometry'])
                gdf_flights.plot(
                    axes=axes,
                    color='blue',
                    linewidth=2,
                    linestyle='dashed',
                    label='Flights')

                # Correct and improve annotation for potential emissions
                # reduction
                annotation_text = f'Potential CO2 Savings: {emissions_savings:.2f} kg CO2 by replacing short-haul flights with rail'
                plt.annotate(
                    annotation_text, xy=(
                        0.5, 0), xycoords='axes fraction', xytext=(
                        0, -40), textcoords='offset points', ha='center', fontsize=10, bbox=dict(
                        boxstyle="round", alpha=0.5))

                # Adjust subplot to make space for the annotation
                plt.subplots_adjust(bottom=0.15)

                annotation_text = f'Potential CO2 Savings: {emissions_savings:.2f} kg CO2 by replacing short-haul flights with rail'
                plt.annotate(
                    annotation_text, xy=(
                        0.5, 0), xycoords='axes fraction', xytext=(
                        0, -40), textcoords='offset points', ha='center', fontsize=10, bbox=dict(
                        boxstyle="round", alpha=0.5))

                plt.title(f'Flights with source in {country}')
                plt.legend()
                plt.show()
        else:
            print(f"No flights found for {country}")

    def aircrafts(self):
        """
        Prints the list of aircraft models.
        """
        airplanes = getattr(self, 'airplanes', None)
        if airplanes is None:
            print("Aircraft data is not available.")
            return

        aircraft_models = airplanes['Name'].unique()
        if len(aircraft_models) == 0:
            print("No aircraft models found.")
            return

        print("List of Aircraft Models:")
        for model in aircraft_models:
            print(model)

    def aircraft_info(self, aircraft_name: str):
        """
        Get information about a specific aircraft model.

        Parameters
        ----------
        aircraft_name : str
            The name of the aircraft model to retrieve information about.

        Returns
        -------
        pd.Series
        A pandas Series containing information about the specified aircraft model.
        """
        airplanes = getattr(self, 'airplanes', None)
        if airplanes is None:
            print("Aircraft data is not available.")
            return

        try:
            aircraft_info = airplanes[airplanes['Name'] == aircraft_name]
            if aircraft_info.empty:
                available_aircrafts = airplanes['Name'].unique()
                print(
                    f"Aircraft model '{aircraft_name}' not found in the data.")

                # Fuzzy string matching to find similar aircraft names
                similar_names = process.extract(
                    aircraft_name, available_aircrafts, limit=5)
                similar_names = [(name, score)
                                 for name, score in similar_names if score > 50]

                if not similar_names:
                    print(
                        "No similar aircraft models found. Here is the list of all available aircraft models:")
                    for name in available_aircrafts:
                        print(name)
                else:
                    print("Similar aircraft models:")
                    for name, score in similar_names:
                        print(f"{name}")

                    print("Please choose a valid aircraft name from the list above.")
                return None

            # Load environment variables from .env file
            load_dotenv()

            # Access the OpenAI API key
            openai_api_key = os.getenv("OPENAI_API_KEY")

            llm = ChatOpenAI(temperature=0.1)
            result = llm.invoke(
                f'What can you tell us about this aircraft model (in a table of specifications): {aircraft_name}')
            display(Markdown(result.content))
            return aircraft_info.squeeze()
        except ValueError as v_error:
            print(v_error)
            return None

    def airport_info(self, airport_name: str):
        """
        Get information about a specific airport.

        Parameters
        ----------
        airport_name : str
            The name of the airport to retrieve information about.

        Returns
        -------
        pd.Series
            A pandas Series containing information about the specified airport.
        """
        airports = getattr(self, 'airports', None)
        if airports is None:
            print("Airport data is not available.")
            return

        try:
            airport_info = airports[airports['Name'] == airport_name]
            if airport_info.empty:
                available_airports = airports['Name'].unique()
                print(f"Airport '{airport_name}' not found in the data.")

                # Fuzzy string matching to find similar airport names
                similar_names = process.extract(
                    airport_name, available_airports, limit=5)
                similar_names = [(name, score)
                                 for name, score in similar_names if score > 50]

                if not similar_names:
                    print(
                        "No similar airports found. Here is the list of all available airports:")
                    for name in available_airports:
                        print(name)
                else:
                    print("Similar airports:")
                    for name, score in similar_names:
                        print(f"{name}")

                    print("Please choose a valid airport name from the list above.")
                return None

            # Load environment variables from .env file
            load_dotenv()

            # Access the OpenAI API key
            openai_api_key = os.getenv("OPENAI_API_KEY")

            llm = ChatOpenAI(temperature=0.1)
            result = llm.invoke(
                f'What can you tell us about this airport  (in a table of specifications): {airport_name}')
            display(Markdown(result.content))
            return airport_info.squeeze()
        except ValueError as v_eror:
            return v_eror
