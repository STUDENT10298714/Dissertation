'''THIS SCRIPT RETRIEVES LONDON ON-STREET CHARGERS FROM THE NATIONAL CHARGEPOINT REGISTRY API'''

from geopandas import read_file,points_from_xy,GeoDataFrame,clip
import requests
import pandas as pd

#NCR API Link
API = "http://chargepoints.dft.gov.uk/api/retrieve/registry/format/xml/post-town/"

#XSL style sheet- for processing the XML data
xsl = "../input_data/XML/XSLT.xsl"

#retrieve boundary of London - this will be used to crop the NCR data
london_boundary = read_file(r"..\input_data\statistical-gis-boundaries-london\ESRI\London_Borough_Excluding_MHW.shp")

#output folder
out_path = "../outputs/"

#set Coordinate Reference System of boundary
london_boundary = london_boundary.to_crs('epsg:27700')

#access API 
response = requests.get(API)

#encode and clean retrieved XML data, getting the longitude and latitude into seperate columns
NCR_XML = pd.read_xml(response.text, stylesheet=xsl,encoding="utf-8") 
NCR_XML["ChargeDeviceLocation"],NCR_XML["address"] = NCR_XML['ChargeDeviceLocation'].str.split(',,', expand=True)[0],NCR_XML['ChargeDeviceLocation'].str.split(',,', expand=True)[1]
NCR_XML["longitude"],NCR_XML["latitude"] = NCR_XML['ChargeDeviceLocation'].str.split(',', expand=True)[0],NCR_XML['ChargeDeviceLocation'].str.split(',', expand=True)[1]
NCR_gdf = GeoDataFrame(NCR_XML, geometry=points_from_xy(x=NCR_XML.latitude, y=NCR_XML.longitude)).set_crs('epsg:4326').to_crs('epsg:27700')

#select only on-street chargers
NCR_gdf = NCR_gdf.loc[(NCR_gdf["LocationType"]=='On-street')]

#clip NCR chargers to London boundary
NCR_London = clip(NCR_gdf,london_boundary)

#export these chargers to a shapefile
NCR_London.to_file(out_path+"NCR_chargers.shp")

#we export another copy- this will be edited later during accessibillity calculations
NCR_London.to_file(out_path+"NCR_chargers_snap.shp")