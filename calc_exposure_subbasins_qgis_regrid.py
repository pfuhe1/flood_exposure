# Peter Uhe 2020/01/27
# Extract upstream and downstream points in river network for lisflood inputs.
# THis script needs to be run from the qgis console otherwise doesn't seem to work...
# Run by using this command e.g:
# exec(open('/home/pu17449/src/flood-cascade/rivernet_prep/lisflood_discharge_inputs_qgis.py').read())
#
# The output of this script is used along with the mizuRoute output to calculate bankfull Q at each point along river network.

import os,socket,subprocess
import processing # (qgis processing)

####################################################
# BASE PATH:
flood_dir = '/Users/pete/onedrivelink/data2/flood_model_tests/bangladesh_v1/recurrence_95ile'
input_pop = '/Users/pete/onedrivelink/data2/population_datasets/HRSL/population_bgd_2018-10-01_geotiff/population_bgd_2018-10-01.tif'
#input_pop = '/Users/pete/onedrivelink/data2/population_datasets/HRSL/population_bgd_2018-10-01_regrid270m.tif'
pop_dir = '/Users/pete/onedrivelink/data2/population_datasets/HRSL/processing'
outdir = '/Users/pete/onedrivelink/data2/flood_model_tests/bangladesh_v1/exposureHRSL_95ile'
clipdir = '/Users/pete/onedrivelink/data2/shapefiles/shapefile_subbasins'
if not os.path.exists(outdir):
	os.mkdir(outdir)

if not os.path.exists(pop_dir):
	os.mkdir(pop_dir)

expts = ['historical','slice20']
discharge_pts = ['Brahmaputra','Ganges','Meghna','combined']
regclip = {'Brahmaputra':'brahmaputra1','Meghna':'Meghna','Bangladesh':'','Ganges':'Ganges'}

# Population files were clipped to masks for different subregions.
# All files regridded back onto common grid (xmin,xmax,ymin,ymax):
# 87.627916667,92.737916667,21.131250000,26.681250000)
#population_regions = ['brahmaputra_regrid','ganges_regrid','meghna-clipsouth_regrid','meghna_regrid','2018-10-01_regrid','clipsouth_regrid']
#population_regions = ['2018-10-01_regrid']
for reg,fpart in regclip.items():
	if fpart !='':
		fclip = os.path.join(clipdir,fpart+'.shp')
		pop_clip = os.path.join(pop_dir,'population_bgd_'+reg+'.tif')
	else:
		pop_clip = input_pop
	pop_clip_regrid = os.path.join(pop_dir,'population_bgd_'+reg+'_regrid270m.tif')
	#gdal:cliprasterbymasklayer -> Clip raster by mask layer

	if not os.path.exists(pop_clip_regrid):

		if not os.path.exists(pop_clip):
			#gdal_cmd = ['gdalwarp','-of','GTiff','-tr','0.0024999999999999996','-0.0025000000000000005','-tap','-cutline',fclip,input_pop,pop_clip]
			#print(' '.join(gdal_cmd))
			#subprocess.call(gdal_cmd)

			cmd_dict = {'INPUT':input_pop,'MASK':fclip,'KEEP_RESOLUTION':True,'CROP_TO_CUTLINE':True,'OUTPUT':pop_clip,'OPTIONS':'COMPRESS=DEFLATE'}
			print('gdal:cliprasterbymasklayer',cmd_dict)
			out = processing.run('gdal:cliprasterbymasklayer',cmd_dict)

			#cmd_dict = {'INPUT':input_pop,'MASK':fclip,'SET_RESOLUTION':True,'X_RESOLUTION':0.0024999999999999996,'Y_RESOLUTION':-0.0025000000000000005,'CROP_TO_CUTLINE':False,'OUTPUT':pop_clip, 'OPTIONS':'COMPRESS=DEFLATE'}
			#print(cmd_dict)
			#out = processing.run('gdal:cliprasterbymasklayer',cmd_dict)

			#debug:
			raise Exception('debug, exit')

		# Then grass7:r.resamp.stats:
		regrid_cmd = {'input':pop_clip,'method':8,'output':pop_clip_regrid,'GRASS_REGION_PARAMETER':'87.627916667,92.737916667,21.131250000,26.681250000','GRASS_REGION_CELLSIZE_PARAMETER':0.0025}
		print('grass7:r.resamp.stats:',regrid_cmd)
		out = processing.run('grass7:r.resamp.stats',regrid_cmd)

	# for debugging
	continue

#for reg in population_regions:
	# Input population file
	#pop_clip = os.path.join(pop_dir,'population_bgd_'+reg+'270m.tif')
	#if not os.path.exists(pop_clip):
	#	print('Error, missing population file',pop_clip)
	#	continue
	print('\nPopulation region mask:',reg)
	population_summary = os.path.join(pop_dir,'population_bgd_'+reg+'_regrid270m_summary.html')
	# Calculating stats:
	#print('calculating summary:')
	cmd_dict = {'INPUT':pop_clip_regrid,'BAND':1,'OUTPUT_HTML_FILE':population_summary}
	out = processing.run('qgis:rasterlayerstatistics',cmd_dict)
	regpop = out['SUM']
	print(f"Total population in region (millions): {regpop/1000000:.3f}\n")
	for dischargept in discharge_pts:
		for expt in expts:
			# Input
			flood_file = os.path.join(flood_dir,'recurrence_95ile-runs_'+expt+'_'+dischargept+'.tif')
			if not os.path.exists(flood_file):
				raise Exception('Error, missing flood file: '+flood_file)
			# Output
			f_exposure = os.path.join(outdir,expt+'_'+dischargept+'_'+reg+'_1in20flood.tif')
			if not os.path.exists(f_exposure):
				print('Calculating exposed population')
				# raster calculator (see processing.algorithmHelp('gdal:rastercalculator')
				# 'where(B==100.0,A,0.0)'
				cmd_dict = {'INPUT_A':pop_clip_regrid,'BAND_A':1,'INPUT_B':flood_file,'BAND_B':1,'FORMULA':'where(B==100.0,A,0.0)','NO_DATA':0.0,'RTYPE':5,'OUTPUT':f_exposure}
				# Test dummy calculation:
				#cmd_dict = {'INPUT_A':flood_file,'BAND_A':1,'FORMULA':'A*2','NO_DATA':0.0,'OUTPUT':f_exposure}
				print(cmd_dict)
				ret = processing.run('gdal:rastercalculator',cmd_dict)
				print(ret)
				cmd = ['gdal_calc.py','-A',pop_clip_regrid,'-B',flood_file,'--calc','where(B==100.0,A,0.0)','--NoDataValue','0.0','--outfile',f_exposure,'--co','COMPRESS=DEFLATE']
				print(' '.join(cmd))
				#subprocess.call(cmd)



			exposure_summary = os.path.join(outdir,expt+'_'+dischargept+'_'+reg+'_1in20flood_summary.html')
			# Calculating stats:
			#print('calculating summary:')
			cmd_dict = {'INPUT':f_exposure,'BAND':1,'OUTPUT_HTML_FILE':exposure_summary}
			out = processing.run('qgis:rasterlayerstatistics',cmd_dict)
			#print(out)
			print(f"Exposure (millions): {dischargept} , {expt}, {out['SUM']/1000000:.3f}, {(100*out['SUM']/regpop):0.1f}%")
