import tkinter as tk
from PIL import ImageTk, Image
import pygmt
import geopandas as gpd
import os

# Define default values for the input fields
default_inset_region = "95, 115, 5, 25"
default_region = "103.5, 107.5, 8, 12"
default_province_size = 4
default_district_size = 0.8

# Generate the map image using region and inset_region
# Load the shapefile into a PyGMT dataset object
provinces_data = os.path.join("vnm_adm_gov_20201027","vnm_admbnda_adm1_gov_20201027.shp")
provinces: gpd.GeoDataFrame = gpd.read_file(provinces_data)
provinces.head()

districts_data = os.path.join("vnm_adm_gov_20201027","vnm_admbnda_adm2_gov_20201027.shp")
districts: gpd.GeoDataFrame = gpd.read_file(districts_data)
districts.head()


# Define a function to generate the map
def create_map(inset_region, province,district, province_size, district_size,province_offset_x, province_offset_y, district_offset_x, district_offset_y):
    # Calculate the region based on the province dimensions
    
    # Calculate the centroid of the province
    province_shape = provinces[provinces['ADM1_EN'] == province].iloc[0]
    centroid = province_shape.geometry.centroid

    region_size = province_size

    region = [centroid.x-region_size/2+province_offset_x, centroid.x+region_size/2+province_offset_x, centroid.y-region_size/2+province_offset_y, centroid.y+region_size/2+province_offset_y]
    

    fig1 = pygmt.Figure()

    fig1.coast(
        region=region,
        projection="M15c",
        land="white",
        water="white",
        #borders="1/0.5p",
        shorelines="1/1p,black",
        frame="ag",
    )
    with pygmt.config(FONT_TITLE=12):
        fig1.basemap(rose="jTL+w2.5c+lO,E,S,N+o0.5c/3c", map_scale="jBR+w200k+o0.5c/0.5c+f")

    fig1.plot(data=provinces, color="white", pen="1p,black", xshift=0.05, yshift=-0.025, label="Province border") # Shift to match the base map, since misaligned
    
    if "city" in province.lower() or "ha noi" in province.lower():
        label_text = province
    else:
        label_text = province + " province"
    fig1.plot(data=provinces[provinces['ADM1_EN'] == province], color="steelblue", pen="1p,black", label=label_text)

    with fig1.inset(position="jBL+w3.5c+o0.2c", box="+pblack+gwhite"):
        fig1.coast(
            region=inset_region,
            projection="M3.5c",
            #land="lightgray",
            #water="lightblue",
            borders="1/0.5p,black",
            shorelines="1/0.5p,black",
            frame="a",
        )

        fig1.plot(data=districts[districts['ADM2_EN'] == "Hoang Sa"], color="white", pen="0.5p,black")
        fig1.plot(data=districts[districts['ADM2_EN'] == "Truong Sa"], color="white", pen="0.5p,black")
    
        
        rectangle = [[region[0], region[2], region[1], region[3]]]
        fig1.plot(data=rectangle, style="r+s", pen="2p,black")
        # Plot the text annotations
        fig1.text(text=["Vietnam", "Laos", "Cambodia", "Thailand"],
             x=[109.0, 103.4, 105.2, 101.5],
             y=[16.0, 20.0, 13.0, 15.5],
             font="8p,Helvetica-Bold",
             justify="CB",
             offset="0c")
        #fig1.plot(data=provinces[provinces['ADM1_EN'] == province], xshift="0.05", color = "steelblue") # Shift to match the base map, since misaligned
    # Add a legend
    # adjust font size only for legend
    with pygmt.config(FONT_ANNOT_PRIMARY="14p"):
        fig1.legend(position="JTR+jTR+o0.2c", box="+gwhite+p1p")

    fig1.savefig("map_image1.png")
    fig1.savefig("map_image1.pdf")
    # Open the image file
    img1 = Image.open("map_image1.png")
    # Display the image in a new window
    img1.show()


    # Create district window
    fig2 = pygmt.Figure()


    # Calculate the centroid of the district in case of island(s)
    far_island_districts = [
    'Phu Quoc',
    'Truong Sa',
    'Hoang Sa',
    'Con Dao']
    # Update centroid

    if district in far_island_districts:
        district_shape = districts[districts['ADM2_EN'] == district].iloc[0]
        centroid = district_shape.geometry.centroid

    region_size = district_size
    region = [centroid.x-region_size/2+district_offset_x, centroid.x+region_size/2+district_offset_x, centroid.y-region_size/2+district_offset_y, centroid.y+region_size/2++district_offset_y]
    

    fig2.plot(
        region=region,
        projection="M15c",
        data=provinces,
        color="white",
        pen="1p,black",
        frame="ag",
    )

    #fig2.plot(data=provinces, color="white", pen="1p,black")
    fig2.plot(data=provinces[provinces['ADM1_EN'] == province], color="steelblue", pen="1p,black")
    fig2.plot(data=districts[districts['ADM1_EN'] == province], pen="1p,black", label="District border")
    fig2.plot(data=districts[districts['ADM1_EN'] == province], pen="1p,white")
    fig2.plot(data=districts[districts['ADM2_EN'] == district], color = "red", pen="1p,black", label=district)
    fig2.plot(data=districts[districts['ADM2_EN'] == district], pen="1p,white")
    fig2.plot(data=provinces[provinces['ADM1_EN'] == province], pen="1p,black")
    

    #fig.plot(data=observation_area, color="green", label = "Observation area") # Too small, does not work
    #fig.plot(x=105.61, y=9.765, style="c0.5c", color="green", pen="1p,black", label = "Observation area")

    with pygmt.config(FONT_TITLE=12):
        fig2.basemap(rose="jTL+w2.5c+lO,E,S,N+o0.5c/3c", map_scale="jBR+w50k+o0.5c/0.5c+f")

    # Add a legend
    # adjust font size only for legend
    with pygmt.config(FONT_ANNOT_PRIMARY="14p"):
        fig2.legend(position="JTR+jTR+o0.2c", box="+gwhite+p1p")

    fig2.savefig("map_image2.png")
    fig2.savefig("map_image2.pdf")
    # Open the image file
    img2 = Image.open("map_image2.png")
    # Display the image in a new window
    img2.show()

# Create the GUI window
root = tk.Tk()
root.title("Map Generator")

inset_region_label = tk.Label(root, text="Inset Region:")
inset_region_label.pack()
inset_region_entry = tk.Entry(root)
inset_region_entry.pack()
inset_region_entry.insert(0, str(default_inset_region))

# Add a list of selectable provinces
provinces_label = tk.Label(root, text="Province:")
provinces_label.pack()

province_names = provinces['ADM1_EN'].tolist()
selected_province = tk.StringVar(root)
selected_province.set(province_names[0]) # Set the default value

def update_districts(*args):
    # Get the selected province
    province_name = selected_province.get()
    
    # Filter the districts based on the selected province
    selected_districts = districts[districts['ADM1_EN'] == province_name]
    
    # Update the district list
    district_names = selected_districts['ADM2_EN'].tolist()
    district_menu['menu'].delete(0, 'end')
    district_menu['menu'].add_command(label="Select a district", command=tk._setit(selected_district, ""))
    for district_name in district_names:
        district_menu['menu'].add_command(label=district_name, command=tk._setit(selected_district, district_name))

province_menu = tk.OptionMenu(root, selected_province, *province_names, command=update_districts)
province_menu.pack()

# Add province size input
province_size_label = tk.Label(root, text="Province Map Size:")
province_size_label.pack()
province_size_entry = tk.Entry(root)
province_size_entry.pack()
province_size_entry.insert(0, str(default_province_size))

# Add province map offset
province_offset_x_label = tk.Label(root, text="Offset X:")
province_offset_x_label.pack()
province_offset_x_entry = tk.Entry(root)
province_offset_x_entry.pack()
province_offset_x_entry.insert(0, str(0))

province_offset_y_label = tk.Label(root, text="Offset Y:")
province_offset_y_label.pack()
province_offset_y_entry = tk.Entry(root)
province_offset_y_entry.pack()
province_offset_y_entry.insert(0, str(0))


# Add a list of selectable districts
districts_label = tk.Label(root, text="District:")
districts_label.pack()

selected_district = tk.StringVar(root, "")
district_menu = tk.OptionMenu(root, selected_district, "")
district_menu.pack()

# Add district size input
district_size_label = tk.Label(root, text="District Map Size:")
district_size_label.pack()
district_size_entry = tk.Entry(root)
district_size_entry.pack()
district_size_entry.insert(0, str(default_district_size))


# Add district map offset
district_offset_x_label = tk.Label(root, text="Offset X:")
district_offset_x_label.pack()
district_offset_x_entry = tk.Entry(root)
district_offset_x_entry.pack()
district_offset_x_entry.insert(0, str(0))

district_offset_y_label = tk.Label(root, text="Offset Y:")
district_offset_y_label.pack()
district_offset_y_entry = tk.Entry(root)
district_offset_y_entry.pack()
district_offset_y_entry.insert(0, str(0))


# Add a button to generate the map
generate_button = tk.Button(root, text="Create Map", 
                            command=lambda: create_map(eval(inset_region_entry.get()), selected_province.get(), selected_district.get(),eval(province_size_entry.get()),eval(district_size_entry.get()),eval(province_offset_x_entry.get()),eval(province_offset_y_entry.get()),eval(district_offset_x_entry.get()),eval(district_offset_y_entry.get())))
generate_button.pack()

# Start the GUI event loop
root.mainloop()
