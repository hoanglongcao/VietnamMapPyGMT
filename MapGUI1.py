import tkinter as tk
from PIL import ImageTk, Image
import pygmt
import geopandas as gpd
import os

import faulthandler
faulthandler.enable()

# Define default values for the input fields
default_inset_region = "95, 115, 5, 25"
default_region = "103.5, 107.5, 8, 12"
default_province_size = 4
default_district_size = 0.8

# Generate the map image using region and inset_region
# Load the shapefile into a PyGMT dataset object
provinces_data = os.path.join("vnm_adm_gov_20201027","vnm_admbnda_adm0_gov_20200103.shp")
provinces = gpd.read_file(provinces_data)
