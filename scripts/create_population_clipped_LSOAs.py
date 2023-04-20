'''THIS SCRIPT CLIPS THE LONDON LSOAs TO POPULATION EXTENT'''

from rasterio import open as rio_open
from rasterio.features import shapes
from geopandas import read_file,GeoDataFrame

#retrieve clipped (to London's extent) population raster .TIF file
pop_file = "../input_data/TQ_population_data/pop_rast_clip.TIF"

#get LSOA file for its Coordinate Reference System (CRS)
lsoa_gdf = read_file("../input_data/statistical-gis-boundaries-london/ESRI/LSOA_2011_London_gen_MHW.shp")

bin_folder ="../bin/"

'''CONVERT POPULATION RASTER FILE TO VECTOR SHAPEFILE'''

mask = None

#this loop creates a list of geometry for each cell
with rio_open(pop_file) as src:
    
    #read first band
    image = src.read(1) 
    
    #loop through and store raster values with individual geometry
    results = (
    {'properties': {'raster_val': v}, 'geometry': s}
    for i, (s, v) in enumerate(shapes(image, mask=mask, transform=src.transform)))

geoms = list(results)

#Create gdf from this geometry list. Need to define the CRS otherwise it is none
pop_shp = GeoDataFrame.from_features(geoms,crs=lsoa_gdf.crs)

#filter out empty values
pop_shp_filtered = pop_shp.loc[(pop_shp["raster_val"]>-9998)]

#overlay LSOAs over population extent
lsoa_gdf_clipped = lsoa_gdf.overlay(pop_shp_filtered,how="intersection")

#merge duplicates into respective LSOAs.
lsoa_gdf_clipped  = lsoa_gdf_clipped.dissolve(by="LSOA11CD")

#output population-clipped shapefile
lsoa_gdf_clipped.to_file(bin_folder+"lsoa_cropped.shp") 