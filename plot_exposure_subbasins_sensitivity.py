# Peter Uhe 2020/01/27
# Extract upstream and downstream points in river network for lisflood inputs.
# THis script needs to be run from the qgis console otherwise doesn't seem to work...
# Run by using this command e.g:
# exec(open('/home/pu17449/src/flood-cascade/rivernet_prep/lisflood_discharge_inputs_qgis.py').read())
#
# The output of this script is used along with the mizuRoute output to calculate bankfull Q at each point along river network.

import os,socket,subprocess,socket,pickle
import numpy as np
import matplotlib.pyplot as plt

####################################################
# BASE PATH:
host = socket.gethostname()
if host == 'Peters-MacBook-Pro.local':
	plotname = 'facebookHRSL_v2'
	outdir = '/Users/pete/onedrivelink/data2/flood_model_tests/bangladesh_v1/exposureHRSL_95ile_v2'
	pickle_out = os.path.join(outdir,'exposure_dict_fill0.pkl')
else:
	plotname = 'facebookHRSL'
	outdir = '/home/pu17449/data2/flood_model_tests/bangladesh_v1/exposureHRSL_95ile'
	#plotname = 'worldpop2020'
	#outdir = '/home/pu17449/data2/flood_model_tests/bangladesh_v1/exposureWorldpop2020_95ile'
	pickle_out = os.path.join(outdir,'exposure_dict.pkl')

cols = {'combined':'Black','Brahmaputra':'blue','Meghna':'green','Ganges':'orange'}

if os.path.exists(pickle_out):
	with open(pickle_out,'rb') as f:
		exposure = pickle.load(f)
		total_pop = pickle.load(f)
else:
	raise Exception('Error, missing pickle file:',pickle_out)
sensitivity_expts = ['skip-r1i1p1','skip-r2i1p1','skip-r3i1p1','skip-r4i1p1','skip-r5i1p1','skip-r6i1p1','skip-r7i1p1']
expts = ['historical','slice20']
discharge_pts = ['combined','Brahmaputra','Ganges','Meghna',]
#regclip = {'Bangladesh':None,'Brahmaputra':'brahmaputra1','Meghna':'Meghna','Ganges':'ganges_subset','Bangladesh-north':'BangladeshBox-clipsouth','Meghna-north':'Meghna-clipsouth'}

regclip = {'Bangladesh-north':'BangladeshBox-clipsouth','Meghna-north':'Meghna-clipsouth','Brahmaputra':'brahmaputra1','Ganges':'ganges_subset'}

################################################################################

fig, (axlist) = plt.subplots(1, len(regclip),figsize=(7,4))
plt.suptitle('Population exposed (millions)')
lines = {}
for i,reg in enumerate(regclip.keys()):
	ax = axlist[i]
	if i==0:
		ax.set_ylabel('Population exposed to 1 in 20 year flood (millions')
	ax.set_title(reg.split('-')[0])
	for d in discharge_pts:
		if d==reg.split('-')[0] or d=='combined':
			for s in sensitivity_expts:
				data = [exposure[reg][d][s+'_historical'],exposure[reg][d][s+'_slice20']]
				ax.scatter([1.25,2.25],data,label=d,color=cols[d],marker='x',linewidths=0.5)

			data = [exposure[reg][d]['historical'],exposure[reg][d]['slice20']]
			lines[d] = ax.scatter([1,2],data,label=d,color=cols[d])
			ax.set_xticklabels(['','Present','2$^\circ$C'])
			#ax.set_ylim([0,50])

plt.legend(lines.values(),lines.keys(),loc='best',title='Discharge event')
plt.savefig('figs/exposure_absolute_'+plotname+'_sensitivity.png')

################################################################################

fig, (axlist) = plt.subplots(1, len(regclip),figsize=(7,4))
plt.suptitle('Change in population exposed (millions)')
lines = {}
for i,reg in enumerate(regclip.keys()):
	ax = axlist[i]
	if i==0:
		ax.set_ylabel('Change in population exposed (2$^\circ$C - Present')
	ax.set_title(reg)
	plotdata = []
	shift=0
	for d in discharge_pts:
		sdata = []
		if d==reg.split('-')[0] or d=='combined':
			for s in sensitivity_expts:
				data = [exposure[reg][d][s+'_slice20']-exposure[reg][d][s+'_historical']]
				plotdata.append(data[0])
				sdata.append(data[0])
				ax.scatter([1.25],data,label=d,color=cols[d],marker='x',linewidths=1)
			ax.boxplot(sdata,medianprops={'color':cols[d]},flierprops={'marker':'x','color':cols[d]})
			data = [exposure[reg][d]['slice20']-exposure[reg][d]['historical']]
			plotdata.append(data[0])
			lines[d] = ax.scatter([1],data,label=d,color=cols[d])
			ax.set_xticklabels(['',''])
			#ax.set_ylim([-5,8])
			yrange = [np.floor(np.min(plotdata))-0.5,np.ceil(np.max(plotdata))+0.5]
			print(plotdata)
			print(yrange)
			ax.set_ylim(yrange)

plt.legend(lines.values(),lines.keys(),loc='best',title='Discharge event')
plt.savefig('figs/exposure_change_'+plotname+'_sensitivity.png')

################################################################################

fig, (axlist) = plt.subplots(1, len(regclip),sharey=True,figsize=(7,4))
plt.suptitle('Percentage of population exposed')
lines = {}
for i,reg in enumerate(regclip.keys()):
	ax = axlist[i]
	if i==0:
		ax.set_ylabel('Population exposed to 1 in 20 year flood (percent)')
	ax.set_title(reg)
	for d in discharge_pts:
		#data = np.array(list(exposure[reg][d].values()))
		if d==reg.split('-')[0] or d=='combined':
			for s in sensitivity_expts:
				data = np.array([exposure[reg][d][s+'_historical'],exposure[reg][d][s+'_slice20']])
				ax.scatter([1.25,2.25],100*data/total_pop[reg],label=d,color=cols[d],marker='x',linewidths=1)
			data = np.array([exposure[reg][d]['historical'],exposure[reg][d]['slice20']])
			print(data)
			lines[d] = ax.scatter([1,2],100*data/total_pop[reg],label=d,color=cols[d])
			ax.set_xticklabels(['','Present','2$^\circ$C'])
			ax.set_ylim([15,38])

plt.legend(lines.values(),lines.keys(),loc='best',title='Discharge event')
plt.savefig('figs/exposure_percent_'+plotname+'_sensitivity.png')
