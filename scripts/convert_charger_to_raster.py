'''THIS SCRIPT CONVERTS THE CHARGER POINTS TO A RASTER LAYER BASED ON OVERLAPPING 500m SERVICE AREAS'''

from rasterio import open as rio_open
from geopandas import read_file
from rasterio.features import rasterize
from numpy import zeros
from rasterio.mask import mask

#define variables
population_raster = "../input_data/TQ_population_data/pop_rast_clip.TIF"
london = read_file("../input_data/statistical-gis-boundaries-london/ESRI/london_area.shp")

#a 500m network-based buffer around each OSC, created earlier
buffer="../input_data/other/Charger_shed_buffer.shp"
buffer_shp=read_file(buffer)

#add column with value of 1 - this will be used to add overlapping buffers
buffer_shp["add_val"] = 1

#open the raster dataset of population- this will be our template
with rio_open(population_raster) as d:
    
    #we extract the actual values from the raster layer into a numpy array using .read(1) (i.e. read the first band of our raster)
    dem_data = d.read(1)
    
    #create blank template of raster layer
    out_img = zeros(dem_data.shape)
    
    #loop through the inputted buffers and add overlying ones
    for index,buff in buffer_shp.iterrows():
        
        #create tuple of buffer value and its geometry
        pairs = (buff.geometry,buff["add_val"])
        
        #create raster out of this buffer
        buffer_raster=rasterize(pairs, out_shape=d.shape, transform=d.transform )
        
        #add this created raster to overall raster - overlying cells will be added
        out_img += buffer_raster
    
    #create new raster .tif file which we write data to
    with rio_open("../outputs/charger_heatmap_full.tif",'w+',driver="GTiff",count=1,height=d.height,width=d.width,crs=d.crs,dtype="float32",transform=d.transform,nodata="nan") as dissag:

        #writing our spatial dissaggregation numpy array to our new raster layer. With 1 index.
        dissag.write(out_img,indexes = 1)
        
        #mask our new raster layer to the shape of our Manchester districts. This creates an Affine Transformation Matrix to map the raster layer to these districts, which is the same as our original population raster's matrix. So we can ignore it with [0]. All_touched is set to true to include pixels that are on the district border which makes the map neater
        result = mask(dissag, london.geometry, all_touched=True,indexes = 1)[0]
        
        #add this mask to raster dataset
        dissag.write(result,indexes=1)
