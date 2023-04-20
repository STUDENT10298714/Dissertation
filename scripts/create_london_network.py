'''THIS SCRIPT CREATES NETWORK LAYER FROM LONDON's ROAD/FOOTPATHS'''

'''CREATE BASE FOLDERS'''
#You cannot use relative file paths in ArcGIS, therefore base_folder must be manually set. Base folder = overall project folder
BASE_FOLDER = r""

bin_folder = BASE_FOLDER+r"\bin"

bin_gdb = bin_folder + "\dissertation_gdb.gdb"

data_folder = BASE_FOLDER+ r"\input_data"

xml_file = BASE_FOLDER+r"\input_data\XML\london_network_template.xml"

'''CREATE SHAPEFILES'''

#Retrieve London road/footpath dataset. This one needs to be "''" 
road_shp_apostrophe=r"'%s\OSM_london_roads\gis_osm_roads_free_1.shp'" %data_folder

#as above, but with no apostrophes
road_shp=r"%s\OSM_london_roads\gis_osm_roads_free_1.shp" %data_folder

#set file names for outputs
intersection_points = r"%s\road_inter_points.shp" %bin_folder

dissolved_points=r"%s\road_points_dissolved.shp" %bin_folder

road_split =  r"%s\osm_roads_split.shp" %bin_folder

network_dataset = r"%s\london_road_network" %bin_gdb

network = r"%s\london_road_network\london_road_network_dataset" %bin_gdb

'''FUNCTIONS'''

# intersect the road with itself, with output as points - these will be network's nodes
arcpy.analysis.PairwiseIntersect(road_shp_apostrophe,intersection_points, "ALL", None, "POINT")

#add xy coordinates to these points as columns
arcpy.management.AddXY(intersection_points)

#dissolve by xy coordinates, because there are lots of duplicate points
arcpy.analysis.PairwiseDissolve(intersection_points,dissolved_points, "POINT_X;POINT_Y", None, "SINGLE_PART", '')

#split road lines based at the above points - these will be network's edges. This takes a long time!
arcpy.management.SplitLineAtPoint(road_shp, dissolved_points,road_split , "0.01 Meters")

#create new dataset
arcpy.management.CreateFeatureDataset(bin_gdb, "london_road_network", 'PROJCS["British_National_Grid",GEOGCS["GCS_OSGB_1936",DATUM["D_OSGB_1936",SPHEROID["Airy_1830",6377563.396,299.3249646]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",400000.0],PARAMETER["False_Northing",-100000.0],PARAMETER["Central_Meridian",-2.0],PARAMETER["Scale_Factor",0.9996012717],PARAMETER["Latitude_Of_Origin",49.0],UNIT["Meter",1.0]];-5220400 -15524400 10000;-100000 10000;-100000 10000;0.001;0.001;0.001;IsHighPrecision')

#import points and lines to this dataset
arcpy.conversion.FeatureClassToGeodatabase(road_split+";"+dissolved_points, network_dataset)
                               
#convert above dataset to network dataset, using premade xml file as a template 
arcpy.na.CreateNetworkDatasetFromTemplate(xml_file, network_dataset)

#build ArcGIS network from network dataset
arcpy.na.BuildNetwork(network)                                      