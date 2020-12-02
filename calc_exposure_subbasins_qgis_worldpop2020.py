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
flood_dir = '/home/pu17449/data2/flood_model_tests/bangladesh_v1/recurrence_95ile'
pop_dir = '/home/pu17449/data2/population_datasets/worldpop2020/processing'
outdir = '/home/pu17449/data2/flood_model_tests/bangladesh_v1/exposureWorldpop2020_95ile'
pickle_out = os.path.join(outdir,'exposure_dict.pkl')
if not os.path.exists(outdir):
	os.mkdir(outdir)

if not os.path.exists(pop_dir):
	os.mkdir(pop_dir)


exposure_dict = {}
total_pop     = {}
expts = ['historical','slice20']
discharge_pts = ['Brahmaputra','Ganges','Meghna','combined']
regclip = {'Brahmaputra':'brahmaputra1','Meghna':'Meghna','Bangladesh':None,'Ganges':'ganges_subset'}

# Population files were clipped to masks for different subregions.
# All files regridded back onto common grid (xmin,xmax,ymin,ymax):
# 87.627916667,92.737916667,21.131250000,26.681250000)
#population_regions = ['brahmaputra_regrid','ganges_regrid','meghna-clipsouth_regrid','meghna_regrid','2018-10-01_regrid','clipsouth_regrid']
#population_regions = ['2018-10-01_regrid']
for reg in regclip.keys():
	exposure_dict[reg]={}
	#fclip = os.path.join(clipdir,fpart+'.shp')
	pop_clip = os.path.join(pop_dir,'population_bgd_'+reg+'_regrid270m.tif')
	#gdal:cliprasterbymasklayer -> Clip raster by mask layer


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
	cmd_dict = {'INPUT':pop_clip,'BAND':1,'OUTPUT_HTML_FILE':population_summary}
	out = processing.run('qgis:rasterlayerstatistics',cmd_dict)
	regpop = out['SUM']
	total_pop[reg] = regpop/1000000.
	#print(f"Total population in region (millions): {regpop/1000000:.3f}\n")
	print('total pop:',regpop/1000000)
	for dischargept in discharge_pts:
		exposure_dict[reg][dischargept]={}
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
				cmd_dict = {'INPUT_A':pop_clip,'BAND_A':1,'INPUT_B':flood_file,'BAND_B':1,'FORMULA':'where(B==100.0,A,0.0)','NO_DATA':0.0,'RTYPE':5,'OUTPUT':f_exposure}
				# Test dummy calculation:
				#cmd_dict = {'INPUT_A':flood_file,'BAND_A':1,'FORMULA':'A*2','NO_DATA':0.0,'OUTPUT':f_exposure}
				print(cmd_dict)
				ret = processing.run('gdal:rastercalculator',cmd_dict)
				print(ret)
				cmd = ['gdal_calc.py','-A',pop_clip,'-B',flood_file,'--calc','where(B==100.0,A,0.0)','--NoDataValue','0.0','--outfile',f_exposure,'--co','COMPRESS=DEFLATE']
				print(' '.join(cmd))
				#subprocess.call(cmd)


			exposure_summary = os.path.join(outdir,expt+'_'+dischargept+'_'+reg+'_1in20flood_summary.html')
			# Calculating stats:
			#print('calculating summary:')
			cmd_dict = {'INPUT':f_exposure,'BAND':1,'OUTPUT_HTML_FILE':exposure_summary}
			out = processing.run('qgis:rasterlayerstatistics',cmd_dict)
			#print(out)
			#print(f"Exposure (millions): {dischargept} , {expt}, {out['SUM']/1000000:.3f}, {(100*out['SUM']/regpop):0.1f}%")
			print("Exposure (millions):",dischargept, expt, out['SUM']/1000000, 100*out['SUM']/regpop)
			exposure_dict[reg][dischargept][expt] = out['SUM']/1000000.

with open(pickle_out,'wb') as f:
	pickle.dump(exposure_dict,f)
	pickle.dump(total_pop,f)
