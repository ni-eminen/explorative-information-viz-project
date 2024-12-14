import copy
import json
import numpy as np
import pandas as pd
import pydeck as pdk
import pycountry
import streamlit as st
import streamlit.components.v1 as components

# Path to your GeoJSON file
# OG_DATA_URL = "./maps/all-countries.geojson"
UN_URL = './maps/un_countries.geojson'
UN_URL_LOG = './maps/un_countries_log.geojson'
# CENTROIDS = './maps/centroids.geojson'
# gdp_un = pd.read_csv("./data/gdp-per-capita-un.csv")
# migrant_workers = pd.read_csv("./data/migrant-workers-un.csv")
# migrant_workers = migrant_workers[migrant_workers['sex.label'] == 'Sex: Total']
# migrant_workers = migrant_workers[migrant_workers['classif1.label'] == 'Age (Youth, adults): 15-24']
# migrant_workers = migrant_workers[['ref_area.label', 'time', 'obs_value']]
# migrant_workers.dropna(inplace=True)
# gdp_un.dropna(inplace=True)
#
# alpha3_numeric_name = [(country.alpha_3, country.numeric, country.name) for country in pycountry.countries]
#
# migrant_workers['highest_of_the_year'] = migrant_workers.apply(lambda row: np.log(np.max(migrant_workers[migrant_workers['time'] == row['time']]['obs_value'].values.tolist())), axis=1)
#
# migrant_workers['obs_value'] = migrant_workers['obs_value'].apply(lambda x: np.log(x)) / migrant_workers['highest_of_the_year'] * 255
#
# not_exist = 0
# exist = 0
# un_countries = []
# with open(OG_DATA_URL) as f:
#     arr = json.load(f)
#
#     for i, country in enumerate(arr['features']):
#         alpha3 = country['properties']['shapeGroup']
#         if alpha3 in list(np.array(alpha3_numeric_name)[:, 0]):
#             numeric_index = list(np.array(alpha3_numeric_name)[:, 0]).index(alpha3)
#             numeric = alpha3_numeric_name[numeric_index][1]
#             name = alpha3_numeric_name[numeric_index][2]
#
#             if int(numeric) in gdp_un['Country or Area Code'].to_numpy().reshape(-1, ):
#                 d = {str(int(key)): value for key, value in
#                      gdp_un[gdp_un['Country or Area Code'] == int(numeric)][['Year', 'Value']].values.tolist()}
#                 country['properties']['gdpc'] = d
#
#                 d_m = {str(int(key)): value for key, value in
#                        migrant_workers[migrant_workers['ref_area.label'] == name][
#                            ['time', 'obs_value']].values.tolist()}
#                 country['properties']['youth_workers'] = d_m
#
#                 un_countries.append(country)
#         else:
#             not_exist += 1
#             continue
#
#     with open(UN_URL, 'w') as outfile:
#         arr_copy = copy.deepcopy(arr)
#
#         # Get top 50 countries by GDP per capita in 2020
#         top_50 = sorted(
#             un_countries,
#             key=lambda d: d['properties'].get('gdpc', {}).get('2020', 0),
#             reverse=True
#         )
#
#         # Reduce coordinates for each country
#         for i, country in enumerate(top_50):
#             geometry_type = country['geometry']['type']
#             if geometry_type == "Polygon":
#                 # Simplify single polygon
#                 for ring in country['geometry']['coordinates']:
#                     if len(ring) > 100:  # Reduce only if there are enough points
#                         ring[:] = ring[::100] + [ring[-1]]
#             elif geometry_type == "MultiPolygon":
#                 # Simplify multipolygon
#                 for polygon in country['geometry']['coordinates']:
#                     for ring in polygon:
#                         if len(ring) > 100:
#                             ring[:] = ring[::100] + [ring[-1]]
#
#         # Update the feature collection with reduced features
#         arr_copy['features'] = top_50
#
#         json.dump(arr_copy, outfile)

from pydeck.types import String
# Open and read the JSON file
with open(UN_URL, 'r') as file:
    arr_copy = json.load(file)

with open(UN_URL_LOG, 'r') as file:
    arr_copy_log = json.load(file)

# Initial view state (global view)
INITIAL_VIEW_STATE = pdk.ViewState(
    latitude=0,  # Centered globally
    longitude=0,
    zoom=1,  # Global zoom to see all centroids
    pitch=0,
    bearing=0
)

selected_year = st.sidebar.slider("Select a Year", 2000, 2021, 2021)
# Add toggles and sidebar inputs
log_scale_toggle = st.sidebar.checkbox("Use Log Scale for Heights", value=False)
# st.sidebar.markdown("### Legend:")
# st.sidebar.markdown("""
# - **Green**: No youth worker data
# - **Gradient Red**: Youth worker percentage for selected year (darker = higher)
# """)

# Adjust height calculation based on toggle
# height_expression = (
#     f"Math.log(properties.gdpc['{selected_year}']) * 3" if log_scale_toggle
#     else f"properties.gdpc['{selected_year}'] * 3"
# )

if log_scale_toggle:
    data = arr_copy_log
else:
    data = arr_copy

# Define the GeoJSON layer with the adjusted height logic
geojson_layer = pdk.Layer(
    "GeoJsonLayer",
    data,
    opacity=.5,
    stroked=True,  # Enable borders
    filled=True,   # Fill polygons
    extruded=True,  # Enable extrusion
    wireframe=True,  # Show wireframe
    get_elevation=f'properties.gdpc["{selected_year}"] * {10000 if log_scale_toggle else 3}',
    get_fill_color=f"""
        properties.youth_workers['{selected_year}'] 
        ? [255 - properties.youth_workers['{selected_year}'], 0, properties.youth_workers['{selected_year}']] 
        : [100, 100, 100]
    """,
    get_line_color=[0, 0, 0],  # Black borders
    line_width_min_pixels=1,  # Minimum border thickness,
)

# Render the Pydeck visualization
r = pdk.Deck(
    layers=[geojson_layer],
    initial_view_state=INITIAL_VIEW_STATE,
)

# Save as an HTML file and display in Streamlit
html_path = "countries_with_borders.html"
r.to_html(html_path)

st.pydeck_chart(r, use_container_width=True, width=1000, height=850)

# Sidebar Legend
st.sidebar.markdown("### Legend:")
st.sidebar.markdown("""
<div style="display: flex; align-items: center; margin-bottom: 5px;">
    <div style="width: 20px; height: 20px; background-color: grey; margin-right: 10px; border: 1px solid black;"></div>
    <span>No youth worker data</span>
</div>
<div style="display: flex; align-items: center; margin-bottom: 5px;">
    <div style="width: 20px; height: 20px; background: linear-gradient(to right, rgb(128, 0, 0), rgb(255, 0, 0)); margin-right: 10px; border: 1px solid black;"></div>
    <span>Low employment of 15-24-year-old migrants</span>
</div>
<div style="display: flex; align-items: center; margin-bottom: 5px;">
    <div style="width: 20px; height: 20px; background: linear-gradient(to right, rgb(100, 0, 140), rgb(127, 0, 170)); margin-right: 10px; border: 1px solid black;"></div>
    <span>Medium employment of 15-24-year-old migrants</span>
</div>
<div style="display: flex; align-items: center; margin-bottom: 5px;">
    <div style="width: 20px; height: 20px; background: linear-gradient(to right, rgb(0, 0, 220), rgb(0, 0, 255)); margin-right: 10px; border: 1px solid black;"></div>
    <span>High employment of 15-24-year-old migrants</span>
</div>
<div style="margin-top: 10px;">
    <strong>Country platform height:</strong> GDP per capita (log scale if toggled)
</div>

<h3>Data</h3>
<ul>
  <li><strong>Data from UN member states:</strong> Employment data from the International Labour Organization (ILO), Department of Economic and Social Affairs, and the World Bank. This includes historical data on employment rates of young migrants (15-24-year-olds) and GDP per capita.</li>
</ul>
""", unsafe_allow_html=True)

