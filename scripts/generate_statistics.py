'''THIS SCRIPT GENERATES DESCRIPTIVE STATISTICS AND CORRELATION STATISTICS OF THE DATA/RESULTS'''

from geopandas import read_file
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import shapiro
from scipy import stats
import seaborn as sns
from matplotlib.patches import Patch 

def significance(p_val):
    '''This simple function returns true or false if a test statistic is below/above the significance level respectively'''
    if p_val <SIG_LEVEL:
        return "True"
    else:
        return "False"
    
def grab(data, rank):
    '''This simple function grabs a list from a tuple of lists'''
    data_list = []
    
    for v in data:
        data_list.append(v[rank])
    return data_list   

def make_graph(title,data,borough,method,signif):
    '''This function produces graphs for spearman ranks for london boroughs'''
    fig,ax = plt.subplots(figsize=(14,11))
    
    #set title
    font = {'family':'cursive','size':19}
    ax.set_title(title,fontdict=font)
    
    #change colour of bars depending on whether values are significant or not
    colors = ["red" if i != "True" else "gray" for i in data[signif]]
    
    #plot graph with boroughs on x axis and rank values on y axis
    graph=ax.bar(data[borough] ,data[method],color=colors,width=0.5,align="center")
    
    #create legend
    fig.canvas.draw()
    renderer = fig.canvas.renderer
    ax.draw(renderer)
    ax.legend(handles=[
            Patch(facecolor='red', label="Not significant"),
            Patch(facecolor='grey', label="Significant"),
        ],loc='upper right')
    
    #create y axis label and limits
    ax.set_ylabel("Spearman's Rank Statistic")
    ax.axhline(linewidth=0.5, color='black')
    ax.set_ylim([-1, 1])
    
    labels_y = ax.get_yticklabels()
    
    for label in labels_y:
        label.set_fontsize(13)
    
    labels_x = ax.get_xticklabels()

    # change x axis labels depending on whether borough is inner, outer or other
    for label in labels_x:

        if label.get_text() in inner_london:
            label.set_color('darkgreen')
            label.set_fontsize(13)
            label.set_rotation('vertical')

        elif label.get_text() in outer_london:
            label.set_color('blue')
            label.set_fontsize(13)
            label.set_rotation('vertical')
        else:
            label.set_rotation('vertical')
            label.set_fontsize(13)
            
    #add values on top of graph
    ax.bar_label(graph,fmt='%.2f',padding=7, fontsize=8.5)        
    ax.plot()

#define variables    
csv_path = "../layouts/"

mgwr_layer = read_file("../outputs/lsoa_for_mgwr.shp")
input_stats_gdf = read_file("../outputs/layouts_shp.shp")

'''CREATE CORRELATION MATRIX'''

#variables we will be correlating
mgwr_layer = mgwr_layer.rename(columns={
'ev_%':'% EV',
'onstreet_p':'% Onstreet',
'imd_score':'IMD Score',
'white_p':'% White',
'drive_%':'% Drive',
'mid_age':'% Mid-age',
'perc_male':'% Male'    
})

corr_matrix_variables = [
'% EV',
'% Onstreet',
'IMD Score',
'% White',
'% Drive',
'% Mid-age',
'% Male'   
]

# set figure size
plt.figure(figsize=(10,7))

# Generate a mask to onlyshow the bottom triangle
mask = np.triu(np.ones_like(mgwr_layer[corr_matrix_variables].corr(), dtype=bool))

# generate matrix
sns.heatmap(mgwr_layer[corr_matrix_variables].corr(), annot=True, mask=mask, vmin=-1, vmax=1)
r"$\bf{OSC\ Count\ by\ Borough}$"
plt.title(r"$\bf{Correlation\ Coefficient\ of\ Predictors}$",font = {'family':'cursive','size':14})
plt.show()


'''SPEARMANS - ACCESSIBILITY'''

#set significance level
SIG_LEVEL = 0.05

#normalise values
input_stats_gdf['% Female_norm']= (input_stats_gdf['% Female'] - input_stats_gdf['% Female'].min())/(input_stats_gdf['% Female'].max()-input_stats_gdf['% Female'].min())
input_stats_gdf['% Elderly_norm']= (input_stats_gdf['% Elderly'] - input_stats_gdf['% Elderly'].min())/(input_stats_gdf['% Elderly'].max()-input_stats_gdf['% Elderly'].min())
input_stats_gdf['% Children_norm']= (input_stats_gdf['% Children'] - input_stats_gdf['% Children'].min())/(input_stats_gdf['% Children'].max()-input_stats_gdf['% Children'].min())
input_stats_gdf['% Disabled_norm']= (input_stats_gdf['% Disabled'] - input_stats_gdf['% Disabled'].min())/(input_stats_gdf['% Disabled'].max()-input_stats_gdf['% Disabled'].min())

#create social need values
input_stats_gdf["Social nd"] =((input_stats_gdf['% Female_norm']+input_stats_gdf["% Elderly_norm"]+input_stats_gdf["% Children_norm"]+input_stats_gdf["% Disabled_norm"])/4)*10

#create overall need by adding social need to minimum between drive % and onstreet % 
input_stats_gdf["Ch Need"] = np.minimum(input_stats_gdf["% Car-dep"],input_stats_gdf["% Onstreet"]) + input_stats_gdf["Social nd"]

#output this need as a shp file for map layout
input_stats_gdf[["Ch Need","LSOA","geometry"]].to_file("../layouts/map_lsoas/Ch Need.shp")

#rank values, and also subtract them to form disparity values
input_stats_gdf["Need_rank"] = input_stats_gdf['Ch Need'].rank(ascending=False,method = 'first')

input_stats_gdf["Length_r"] =input_stats_gdf[' Min dist'].rank(ascending=False,method = 'first')

input_stats_gdf["disparity"] = input_stats_gdf["Need_rank"] - (input_stats_gdf["Length_r"].max()-input_stats_gdf["Length_r"] )

#output this disparity to a shapefile which we use for disparity map
input_stats_gdf.to_file("../layouts/map_lsoas/Ch disparity.shp")

#because spearman function overlooks zeros, we want to include them
input_stats_gdf['Coverage'].replace(0, 0.0001,inplace=True)

#rank coverage values
input_stats_gdf["Cover_r"] = input_stats_gdf['Coverage'].rank(ascending=False,method = 'first')

#define London Boroughs
boroughs = ['City of London','Barking and Dagenham','Barnet','Bexley','Brent','Bromley','Camden','Croydon','Ealing','Enfield','Greenwich','Hackney','Hammersmith and Fulham','Haringey','Harrow','Havering','Hillingdon','Hounslow','Islington','Kensington and Chelsea','Kingston upon Thames','Lambeth','Lewisham','Merton','Newham','Redbridge','Richmond upon Thames','Southwark','Sutton','Tower Hamlets','Waltham Forest','Wandsworth','Westminster']
inner_london = ['Lambeth','Southwark','Lewisham','Wandsworth','Hammersmith and Fulham','Kensington and Chelsea','Westminster','Camden','Tower Hamlets','Islington','Hackney','Haringey','Newham','City of London']
outer_london = ['Kingston upon Thames','Croydon','Bromley','Hounslow','Ealing','Havering','Hillingdon','Harrow','Brent','Barnet','Greenwich','Bexley','Enfield','Waltham Forest','Redbridge','Sutton','Richmond upon Thames','Merton','Barking and Dagenham']

#initialise empty lists
spear_rho_len = []
spear_rho_cov = []
spear_p_len = []
spear_p_cov = []
sig_min = []
sig_cov = []
borough_l = []
all_dist = []
all_cov= []

#find spearmans r between across all of london
borough_l.append("All")
rho_dist_all,p_dist_all = stats.spearmanr(input_stats_gdf["Need_rank"],input_stats_gdf["Length_r"],nan_policy = "omit")
rho_cover_all,p_cover_all = stats.spearmanr(input_stats_gdf["Cover_r"],input_stats_gdf["Need_rank"],nan_policy = "omit")

#append these values as 1 tuple to empty list
all_dist.append(("All",rho_dist_all,p_dist_all,significance(p_dist_all)))
all_cov.append(("All",rho_cover_all,p_cover_all,significance(p_cover_all)))

#find spearmans r just within Inner London
inner_l = input_stats_gdf.loc[(input_stats_gdf["LAD11NM"].isin(inner_london))]
borough_l.append("Inner London")
rho_dist_inner,p_dist_inner = stats.spearmanr(inner_l["Need_rank"],inner_l["Length_r"],nan_policy = "omit")
rho_cover_inner,p_cover_inner = stats.spearmanr(inner_l["Cover_r"],inner_l["Need_rank"],nan_policy = "omit")
all_dist.append(("Inner London",rho_dist_inner,p_dist_inner,significance(p_dist_inner)))
all_cov.append(("Inner London",rho_cover_inner,p_cover_inner,significance(p_cover_inner)))

#find spearmans r just within Outer London
borough_l.append("Outer London")
outer_l = input_stats_gdf.loc[(input_stats_gdf["LAD11NM"].isin(outer_london))]
rho_dist_outer,p_dist_outer = stats.spearmanr(outer_l["Need_rank"],outer_l["Length_r"],nan_policy = "omit")
rho_cov_outer,p_cov_outer = stats.spearmanr(outer_l["Cover_r"],outer_l["Need_rank"],nan_policy = "omit")
all_dist.append(("Outer London",rho_dist_outer,p_dist_outer,significance(p_dist_outer)))
all_cov.append(("Outer London",rho_cov_outer,p_cov_outer,significance(p_cov_outer)))

#next, loop through all london boroughs and find spearmans r within them
for borough in boroughs:
    borough_l.append(borough)
    
    filt = input_stats_gdf.loc[input_stats_gdf['LAD11NM']==borough] 
    rho_dist,p_dist = stats.spearmanr(filt["Need_rank"],filt["Length_r"],nan_policy = "omit")
    rho_cover,p_cover = stats.spearmanr(filt["Cover_r"],filt["Need_rank"],nan_policy = "omit")

    all_dist.append((borough,rho_dist,p_dist,significance(p_dist)))
    all_cov.append((borough,rho_cover,p_cover,significance(p_cover)))

# we have a list of tuples with all the above spearmans r calculations. we sort this list by ranking the spearmans r, in order to produce a clearer graph
all_dist.sort(key=lambda a: a[1])

#we do the same for the coverage method but reverse the ranking to match the orders
all_cov.sort(key=lambda a: a[1],reverse=True)

#from these sorted lists of tuples, we grab the individual components from each tuple and make it their own list    
cov_name = grab(all_cov,0)
dist_name = grab(all_dist,0)

cov_sp = grab(all_cov,1)
dist_sp = grab(all_dist,1)

cov_p =grab(all_cov,2)
dist_p =grab(all_dist,2)

cov_sig =grab(all_cov,3)
dist_sig =grab(all_dist,3)

#we initialise a dictionary with the columns our data will have
data_dic_sp = {"borough dist":dist_name,"spearmans rank len":dist_sp,"spearmans p len":dist_p,"len signif":dist_sig,
               "borough cov":cov_name,"spearmans rank cov":cov_sp,"spearmans p cov":cov_p,"signif coverage":cov_sig}

#we then create a dataframe from this dictionary, and export it as a csv file
data_frame_sp = pd.DataFrame(data = data_dic_sp)
data_frame_sp.to_csv(path_or_buf=csv_path+"spearmans.csv")

'''CREATE SPEARMAN GRAPHS'''

#"Spearman's Rank Statistics per London Borough: Minimum Distance"
title_dist = r"$\bf{Spearman's\ Rank\ Statistics:\ Minimum-Distance}$"
make_graph(title_dist,data_dic_sp,"borough dist","spearmans rank len","len signif")

title_cov = r"$\bf{Spearman's\ Rank\ Statistics:\ Coverage\ Method}$"
make_graph(title_cov,data_dic_sp,"borough cov","spearmans rank cov","signif coverage")

'''GENERATE DESCRIPTIVE STATISTICS FOR ALL VARIABLES'''

#variables we will be getting descriptive stats from
keep = [
 '% Elderly', 
 '% Children',
 '% Mid-age',
 'PT Access', 
 '% Drive', 
 '% EV', 
 '% Onstreet', 
 'IMD Score', 
 '% Female', 
 '% Male', 
 '% Disabled',
 '% White'
 ]

#initialise empty lists
overview = []
name = []
normals = []
means = []
maxis = []
medians = []
mins = []
stds = []
inner_mean_l = []
outer_mean_l = []

#loop through every variable and get descriptive statistics of them
for col in input_stats_gdf[keep].columns:
    
    #get stats
    outer_mean = outer_l[col].mean()
    inner_mean = inner_l[col].mean()
    mean = input_stats_gdf[col].mean()
    median = input_stats_gdf[col].median()
    std = input_stats_gdf[col].std()

    #find normality
    normal = False
    norm=shapiro(input_stats_gdf[col])
    
    if norm[1] > SIG_LEVEL and norm[1] !=1:
        normal = True
    else:
        normal = False
        
    #append values to lists
    name.append(col)
    normals.append(normal)
    stds.append(std)
    medians.append(median)
    means.append(mean)
    maxis.append(input_stats_gdf[col].max())
    mins.append(input_stats_gdf[col].min())
    inner_mean_l.append(inner_mean)
    outer_mean_l.append(outer_mean)

#initialise pandas dataframe of these values in lists    
data_dic = {
"Name":name,
"Mean":means,
"Std":stds,
"Median":medians,
"Min":mins,
"Max":maxis,
"Inner London Mean":inner_mean_l,
"Outer London Mean":outer_mean_l,
"Normal?":normals,
}

#export dataframe to CSV file
data_frame = pd.DataFrame(data = data_dic)
data_frame.to_csv(path_or_buf=csv_path+"stats.csv")



