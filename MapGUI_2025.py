import tkinter as tk
from PIL import ImageTk, Image
import pygmt
import geopandas as gpd
import os
import pandas as pd # Import pandas for pd.concat

# Define default values for the input fields
default_inset_region = "95, 115, 5, 25"
default_province_size = 4

# Load the shapefile into a PyGMT dataset object
provinces_data = os.path.join("vnm_adm_gov_20201027","vnm_admbnda_adm1_gov_20201027.shp")
original_provinces: gpd.GeoDataFrame = gpd.read_file(provinces_data)

# --- Logic for merging provinces ---
# Define the old to new province mapping based on your provided list
# The key is the new province name (English, no diacritics), and the value is a list of old province names (English, no diacritics) to merge
province_merge_map = {
    "Tuyen Quang": ["Tuyen Quang", "Ha Giang"],
    "Lao Cai": ["Lao Cai", "Yen Bai"],
    "Thai Nguyen": ["Bac Kan", "Thai Nguyen"],
    "Phu Tho": ["Vinh Phuc", "Phu Tho", "Hoa Binh"],
    "Bac Ninh": ["Bac Ninh", "Bac Giang"],
    "Hung Yen": ["Hung Yen", "Thai Binh"],
    "Hai Phong city": ["Hai Duong", "Hai Phong city"], # Renamed from just "Hai Phong" for clarity if it's a city
    "Ninh Binh": ["Ha Nam", "Ninh Binh", "Nam Dinh"],
    "Quang Tri": ["Quang Binh", "Quang Tri"],
    "Hue city": ["Thua Thien Hue"],
    "Da Nang city": ["Quang Nam", "Da Nang city"], # Renamed from just "Da Nang"
    "Quang Ngai": ["Kon Tum", "Quang Ngai"],
    "Gia Lai": ["Gia Lai", "Binh Dinh"],
    "Khanh Hoa": ["Ninh Thuan", "Khanh Hoa"],
    "Lam Dong": ["Lam Dong", "Dak Nong", "Binh Thuan"],
    "Dak Lak": ["Dak Lak", "Phu Yen"],
    "Ho Chi Minh city": ["Ba Ria - Vung Tau", "Binh Duong", "Ho Chi Minh city"],
    "Dong Nai": ["Dong Nai", "Binh Phuoc"],
    "Tay Ninh": ["Tay Ninh", "Long An"],
    "Can Tho city": ["Can Tho city", "Soc Trang", "Hau Giang"], # Renamed from just "Can Tho"
    "Vinh Long": ["Ben Tre", "Vinh Long", "Tra Vinh"],
    "Dong Thap": ["Tien Giang", "Dong Thap"],
    "Ca Mau": ["Bac Lieu", "Ca Mau"],
    "An Giang": ["An Giang", "Kien Giang"]
}

# Create a copy to work with
provinces_working = original_provinces.copy()

# Add a new column for the merged province name
provinces_working['NEW_ADM1_EN'] = provinces_working['ADM1_EN']

# Apply the merges
for new_province, old_provinces_list in province_merge_map.items():
    provinces_working.loc[provinces_working['ADM1_EN'].isin(old_provinces_list), 'NEW_ADM1_EN'] = new_province

# Dissolve the provinces based on the new names
# This creates the merged geometries and retains NEW_ADM1_EN as the index
provinces_merged = provinces_working.dissolve(by='NEW_ADM1_EN')

# Reset index to make 'NEW_ADM1_EN' a regular column again
provinces_merged = provinces_merged.reset_index()

# Select only the desired columns ('NEW_ADM1_EN' and 'geometry')
provinces_merged = provinces_merged[['NEW_ADM1_EN', 'geometry']]

# Rename 'NEW_ADM1_EN' back to 'ADM1_EN' for consistency
provinces_merged.rename(columns={'NEW_ADM1_EN': 'ADM1_EN'}, inplace=True)

# Identify provinces from the original shapefile that were NOT part of any merge
all_original_province_names = set(original_provinces['ADM1_EN'].tolist())
merged_provinces_involved_old_names = set()
for old_names_list in province_merge_map.values():
    merged_provinces_involved_old_names.update(old_names_list)

non_merged_province_names = [name for name in all_original_province_names if name not in merged_provinces_involved_old_names]

# Filter original_provinces to get only the non-merged ones
non_merged_provinces_gdf = original_provinces[original_provinces['ADM1_EN'].isin(non_merged_province_names)]
# Ensure these non-merged GDF also only contain ADM1_EN and geometry for consistent concatenation
non_merged_provinces_gdf = non_merged_provinces_gdf[['ADM1_EN', 'geometry']]

# Concatenate the dissolved (merged) provinces with the non-merged provinces
# Use .drop_duplicates() to handle any accidental duplicates that might arise from edge cases in name handling
provinces = gpd.GeoDataFrame(pd.concat([provinces_merged, non_merged_provinces_gdf], ignore_index=True), crs=original_provinces.crs)
provinces.drop_duplicates(subset=['ADM1_EN'], inplace=True) # Explicitly drop duplicates based on ADM1_EN

districts_data = os.path.join("vnm_adm_gov_20201027","vnm_admbnda_adm2_gov_20201027.shp")
districts: gpd.GeoDataFrame = gpd.read_file(districts_data)
districts.head()
# --- End of logic for merging provinces ---


# Define a function to generate the map
def create_map(inset_region, province, province_size, province_offset_x, province_offset_y):
    # Calculate the centroid of the selected province
    province_shape = provinces[provinces['ADM1_EN'] == province]
    if province_shape.empty:
        print(f"Error: Province '{province}' not found after merging. Available: {provinces['ADM1_EN'].tolist()}")
        return

    centroid = province_shape.iloc[0].geometry.centroid

    region_size = province_size
    region = [
        centroid.x - region_size / 2 + province_offset_x,
        centroid.x + region_size / 2 + province_offset_x,
        centroid.y - region_size / 2 + province_offset_y,
        centroid.y + region_size / 2 + province_offset_y
    ]

    fig1 = pygmt.Figure()

    fig1.coast(
        region=region,
        projection="M15c",
        land="white",
        water="white",
        shorelines="1/1p,black",
        frame="ag",
    )
    with pygmt.config(FONT_TITLE=12):
        fig1.basemap(rose="jTL+w2.5c+lO,E,S,N+o0.5c/3c", map_scale="jBR+w200k+o0.5c/0.5c+f")

    # Plot all provinces, then highlight the selected one
    fig1.plot(data=provinces, color="white", pen="1p,black", xshift=0.05, yshift=-0.025, label="Province border")
    
    # Use English names for comparison in label logic
    if "city" in province.lower() or "ha noi" in province.lower():
        label_text = province
    else:
        label_text = province + " Province"
    fig1.plot(data=province_shape, color="steelblue", pen="1p,black", label=label_text)

    with fig1.inset(position="jBL+w3.5c+o0.2c", box="+pblack+gwhite"):
        fig1.coast(
            region=inset_region,
            projection="M3.5c",
            borders="1/0.5p,black",
            shorelines="1/0.5p,black",
            frame="a",
        )

        fig1.plot(data=districts[districts['ADM2_EN'] == "Hoang Sa"], color="white", pen="0.5p,black")
        fig1.plot(data=districts[districts['ADM2_EN'] == "Truong Sa"], color="white", pen="0.5p,black")
    
        
        rectangle = [[region[0], region[2], region[1], region[3]]]
        fig1.plot(data=rectangle, style="r+s", pen="2p,black")
        # Plot the text annotations for surrounding countries
        fig1.text(text=["Vietnam", "Laos", "Cambodia", "Thailand"],
             x=[109.0, 103.4, 105.2, 101.5],
             y=[16.0, 20.0, 13.0, 15.5],
             font="8p,Helvetica-Bold",
             justify="CB",
             offset="0c")
    with pygmt.config(FONT_ANNOT_PRIMARY="14p"):
        fig1.legend(position="JTR+jTR+o0.2c", box="+gwhite+p1p")

    fig1.savefig("map_image1.png")
    fig1.savefig("map_image1.pdf")
    img1 = Image.open("map_image1.png")
    img1.show()


# Create the GUI window
root = tk.Tk()
root.title("Province Map Generator")

inset_region_label = tk.Label(root, text="Inset Region:")
inset_region_label.pack()
inset_region_entry = tk.Entry(root)
inset_region_entry.pack()
inset_region_entry.insert(0, str(default_inset_region))

provinces_label = tk.Label(root, text="Province:")
provinces_label.pack()

# Get the list of new province names
province_names = provinces['ADM1_EN'].tolist()
selected_province = tk.StringVar(root)
selected_province.set(province_names[0] if province_names else "")

province_menu = tk.OptionMenu(root, selected_province, *province_names)
province_menu.pack()

province_size_label = tk.Label(root, text="Province Map Size:")
province_size_label.pack()
province_size_entry = tk.Entry(root)
province_size_entry.pack()
province_size_entry.insert(0, str(default_province_size))

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

generate_button = tk.Button(root, text="Create Map", 
                            command=lambda: create_map(eval(inset_region_entry.get()), selected_province.get(), eval(province_size_entry.get()),eval(province_offset_x_entry.get()),eval(province_offset_y_entry.get())))
generate_button.pack()

root.mainloop()