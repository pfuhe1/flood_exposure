# Peter Uhe 2020/01/27
# Extract upstream and downstream points in river network for lisflood inputs.
# THis script needs to be run from the qgis console otherwise doesn't seem to work...
# Run by using this command e.g:
# exec(open('/home/pu17449/src/flood-cascade/rivernet_prep/lisflood_discharge_inputs_qgis.py').read())
#
# The output of this script is used along with the mizuRoute output to calculate bankfull Q at each point along river network.

import os,socket,subprocess


####################################################
# PATHS:
#input_pop = '/Users/pete/onedrivelink/data2/population_datasets/HRSL/population_bgd_2018-10-01_regrid270m.tif'
#pop_dir = '/Users/pete/onedrivelink/data2/population_datasets/HRSL/processing'
#clipdir = '/Users/pete/onedrivelink/data2/shapefiles/shapefile_subbasins'

input_pop = '/home/pu17449/data2/population_datasets/worldpop2020/bgd_ppp_2020_constrained_regrid270m.tif'
pop_dir = '/home/pu17449/data2/population_datasets/worldpop2020/processing'
clipdir = '/home/pu17449/data2/shapefiles/shapefile_subbasins'

if not os.path.exists(pop_dir):
	os.mkdir(pop_dir)

regclip = {'Brahmaputra':'brahmaputra1','Meghna':'Meghna','Ganges':'ganges_subset','Bangladesh':''}

# Population files were clipped to masks for different subregions.
# All files regridded back onto common grid (xmin,xmax,ymin,ymax):
# 87.627916667,92.737916667,21.131250000,26.681250000)
#population_regions = ['brahmaputra_regrid','ganges_regrid','meghna-clipsouth_regrid','meghna_regrid','2018-10-01_regrid','clipsouth_regrid']
#population_regions = ['2018-10-01_regrid']
for reg,fpart in regclip.items():
	pop_clip = os.path.join(pop_dir,'population_bgd_'+reg+'_regrid270m.tif')
	if not os.path.exists(pop_clip):
		if fpart != '':
			fclip = os.path.join(clipdir,fpart+'.shp')
			#gdal_cmd = ['gdalwarp','-of','GTiff','-tr','0.0024999999999999996','-0.0025000000000000005','-tap','-te','87.627916667','21.131250000','92.737916667','26.681250000','-cutline',fclip,input_pop,pop_clip]
			gdal_cmd = ['gdalwarp','-of','GTiff','-tr','0.0025','-0.0025','-te','87.627916667','21.131250000','92.737916667','26.681250000','-cutline',fclip,input_pop,pop_clip]
			print(' '.join(gdal_cmd))
			subprocess.call(gdal_cmd)
		else:
			os.symlink(input_pop,pop_clip)
