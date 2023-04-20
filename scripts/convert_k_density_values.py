'''THIS SCRIPT CONVERTS THE KERNEL DENSITY ESTIMATE RASTER LAYER TO AN AVERAGE DENSITY VALUE FOR EACH LSOA. IT ALSO GENERATES 'CLEAN' FILES FOR MAP LAYOUTS '''

from pandas import merge
from geopandas import read_file
from rasterstats import zonal_stats

#set variables
outputs_folder = "../outputs/"
bin_folder = "../bin/"

stats_gdf = read_file(outputs_folder + "lsoa_stats_cropped.shp")
lsoa_gdf = read_file(outputs_folder+"lsoa_boundaries.shp")

#our KDE layer
k_raster = bin_folder + "charger_k_density.TIF"

'''FIND AVERAGE DENSITY VALUES FOR EACH LSOA AND PREPARE STATS FOR MGWR'''

#get mean value of charger densities within LSOA populations
summary = [s["mean"]for s in zonal_stats(stats_gdf,k_raster)]

#input these values into LSOA shapefile 
stats_gdf["charger_density"] = summary

#remove geometry column - because we dont need 2, which we will have after merging. 
stats_gdf = stats_gdf.loc[:,stats_gdf.columns!="geometry"]

#merge this charger density with LSOA file (not the clipped LSOA file)
ch_den_gdf = merge(lsoa_gdf[["LSOA11CD","geometry"]],stats_gdf ,on="LSOA11CD",how="inner")

#normalise male for our MGWR
ch_den_gdf["perc_male_norm"] = (ch_den_gdf["perc_male"]-ch_den_gdf["perc_male"].min())/(ch_den_gdf["perc_male"].max()-ch_den_gdf["perc_male"].min())

#Output this dataset as shapefile, creating a final statistics layer of all generated values
ch_den_gdf.to_file(outputs_folder+'final_stats_lyr.shp')

#remove LSOAs with charger density value of zero
ch_den_gdf_no_zero = ch_den_gdf.loc[(ch_den_gdf["charger_density"]!=0)]

#from above we output as a shapefile - this layer will be used for running our MGWR analysis
ch_den_gdf_no_zero.to_file(outputs_folder+"lsoa_for_mgwr.shp")

'''MAKE LAYOUTS FILE'''
#the above outputted shapefile is for analysis. Next we make a shapefile that is for better visualisation, with renamed columns and rounded values

decimal_col = [
'over_65',
'under_15',
'mid_age',
'drive_%',
'ev_%',
'onstreet_p',
'bme_perc',
'imd_score',
'perc_fem',
'perc_male',
'mjr_dis',
'Total_Leng',
'white_p',
'Point_Coun',
'charger_density']

#round columns to 2 d.p.
for col in ch_den_gdf[decimal_col].columns:
    ch_den_gdf[col]= ch_den_gdf[col].round(decimals=2)

#rename columns to make them more understandable. Has to be within 10 characters due to shapefile limits
layout=ch_den_gdf.rename(columns={
'LSOA11CD': 'LSOA',
'over_65': '% Elderly',
'avhholdsz': 'Av HholdSz',
'under_15': '% Children',
'mid_age': '% Mid-age',
'car_dpndnt':'% Car-dep',
'drive_%': '% Drive',
'ev_%': '% EV',
'white_p':'% White',
'onstreet_p': '% Onstreet' ,
'bme_perc': '% BME',
'av_income': 'Av Income',
'imd_score':'IMD Score',
'perc_fem':'% Female',
'perc_male': '% Male',
'mjr_dis': '% Disabled',
'Total_Leng':' Min dist',
'Point_Coun': 'Coverage',
'charger_density': 'OSC dnsty'})

#Output
layout.to_file(outputs_folder+'layouts_shp.shp')
