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
if host == 'mac':
	outdir = '/Users/pete/onedrivelink/data2/flood_model_tests/bangladesh_v1/exposureHRSL_95ile'
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

expts = ['historical','slice20']
discharge_pts = ['combined','Brahmaputra','Ganges','Meghna',]
regclip = {'Bangladesh':None,'Brahmaputra':'brahmaputra1','Meghna':'Meghna','Ganges':'ganges_subset'}

#plt.figure()

fig, (axlist) = plt.subplots(1, len(regclip),figsize=(7,4))
plt.suptitle('Population exposed (millions)')
lines = {}
for i,reg in enumerate(regclip.keys()):
	ax = axlist[i]
	if i==0:
		ax.set_ylabel('Population exposed to 1 in 20 year flood (millions')
	ax.set_title(reg)
	for d in discharge_pts:
		if d==reg or d=='combined':
			lines[d] = ax.scatter([1,2],exposure[reg][d].values(),label=d,color=cols[d])
			ax.set_xticklabels(['','Present','2$^\circ$C'])

plt.legend(lines.values(),lines.keys(),loc='best',title='Discharge event')
plt.savefig('figs/exposure_absolute_'+plotname+'.png')

fig, (axlist) = plt.subplots(1, len(regclip),sharey=True,figsize=(7,4))
plt.suptitle('Percentage of population exposed')
lines = {}
for i,reg in enumerate(regclip.keys()):
	ax = axlist[i]
	if i==0:
		ax.set_ylabel('Population exposed to 1 in 20 year flood (percent)')
	ax.set_title(reg)
	for d in discharge_pts:
		data = np.array(list(exposure[reg][d].values()))
		print(data)
		if d==reg or d=='combined':
			lines[d] = ax.scatter([1,2],100*data/total_pop[reg],label=d,color=cols[d])
			ax.set_xticklabels(['','Present','2$^\circ$C'])
			ax.set_ylim([15,35])

plt.legend(lines.values(),lines.keys(),loc='best',title='Discharge event')
plt.savefig('figs/exposure_percent_'+plotname+'.png')

