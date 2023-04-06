#!/usr/bin/python3 

from gnssbyUtils import *



########## configure ##########
ts = datetime.datetime(2021,3,31)
te = datetime.datetime(2021,4,5)

AClist = ['CDDIS_TEST','swarm_A','swarm_B','swarm_C','swarm_A_RD','swarm_B_RD','swarm_C_RD']
# AClist = ['swarm_A']
AClist = ['CDDIS_PRODUCT','CDDIS_TEST','swarm_A','swarm_A_RD']

AClist = ['CDDIS_LW']
AClist = ['GFZ_PREM']
AClist = ['swarm_A','swarm_B','swarm_C','swarm_A_RD','swarm_B_RD','swarm_C_RD']

AClist = ['CDDISHTTPS_M']

AClist = ['swarm']



AClist = ['ESA']
AClist = ['CDDIS_PRODUCT_HTTPS']




AClist = ['swarm','swarm_RD']
AClist = ['CDDIS_HTTPS']

AClist = ['CDDIS_POD']

# ['grace', 'grace-fo''swarm_A',
# ['GOP', 'GOP_M', 'GOP_BRDC', 
# ['CDDIS', 'CDDIS_N', 'CDDIS_M', 'CDDIS_P', 'CDDIS_SNX', 'cddis_PRE', 'cddis_PREM','cddis_ION','cddis_DCB',
# ['ESA_PRE', 'GFZ_PRE', 'WUH_PRE']

########## read config.ini ##########
cfg = configparser.ConfigParser()
cfgtable = configparser.ConfigParser(allow_no_value=True)

if(platform.system() == "Linux"):    
	configFile = 'config.ini'  
elif(platform.system() == "Windows"):
	configFile = 'config_win.ini'        
else:
	print("System platform have not been tested ! Please modify source code manually.")
	print(platform.system())
	os._exit(1)

if(not os.path.exists(configFile)):
	print(configFile + " is not exists!") 
	os._exit(1)	

cfg.read(configFile)  
cfgtable.read('listTable.ini')

# print all available Ac type for next update
print('************* available Ac Config *************')
print(cfg.sections())  		
print('************* available Ac Config *************')

########## List in AC list ##########
for ac in  AClist:
	if(len(ac) == 0):  # empty AC name 
		continue
	print('********* AC : '+ac+' *********')	
	if(~cfg.has_section(ac)):  # AC name must be in config.ini 

		print(' host = '+cfg.get(ac,'host'))
		print(' remote_dir = '+cfg.get(ac,'remote_dir'))
		print(' file_pattern = '+cfg.get(ac,'file_pattern'))
		print(' ftp_type = '+cfg.get(ac,'ftp_type'))

		if(cfg.get(ac,'ftp_type') == 'ftp'):
			print(' ')
			getDataFTP(ts,te,ac,cfg,cfgtable) 
		elif(cfg.get(ac,'ftp_type') == 'tls'):
			print(' ')
			getDataFTP_TLS(ts,te,ac,cfg,cfgtable) 
		elif(cfg.get(ac,'ftp_type') == 'http'):
			print(' ')
			getDataHTTP(ts,te,ac,cfg,cfgtable) 
		elif(cfg.get(ac,'ftp_type') == 'https'):
			print(' ')
			getDataHTTPS(ts,te,ac,cfg,cfgtable)    
		
