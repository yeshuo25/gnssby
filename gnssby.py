#!/usr/bin/python3 
from gnssbyUtils import *
# ftplib package is necessary for SFTP or SSH
from gnssbySSH import *


#################### configure ####################
ts = datetime.datetime(2019,1,1)
te = datetime.datetime(2019,1,1)
#AClist = ['HTTPS_RNX', 'HTTPS_AC', 'HTTPS_ACs', 'HTTPS_BRDM', 'HTTPS_CASDCB', 'HTTPS_DLRDCB', 'HTTPS_CORG', 'HTTPS_SNX', 'GFZ_Products', 'WHU_Products', 'WHU_AR', 'COD_Products', 'CNT_HTTP', 'SFTP_RNX', 'ESA_HTTP']
AClist = ['ucar_att2','ucar_clk2','ucar_RO2','ucar_clk2']
AClist = ['grace-fo']
AClist = ['GIPP']
AClist = ['swarm_RD']
#################### configure ####################


start = time.time()
# logging 
createLogger()

########## read config.ini ##########
cfg = configparser.ConfigParser()
cfgtable = configparser.ConfigParser(allow_no_value=True)

if(platform.system() == "Linux"):    
	configFile = 'config.ini'  
elif(platform.system() == "Windows"):
	configFile = 'config_win.ini'        
else:
	logging.log(logging.ERROR, "System platform have not been tested ! Please manually modify source code.")
	logging.log(logging.ERROR, platform.system())
	os._exit(1)

if(not os.path.exists(configFile)):
	logging.log(logging.ERROR, configFile + " does not exist!")
	os._exit(1)	

cfg.read(configFile)  
cfgtable.read('listTable.ini')

# print all available Ac type for next update
logging.log(logging.DEBUG, "************* available Ac Config *************")
logging.log(logging.DEBUG, cfg.sections())
logging.log(logging.DEBUG, "************* available Ac Config *************")
logging.log(logging.DEBUG, "")

########## List in AC list ##########
for ac in  AClist:
	if(len(ac) == 0):  # AC name  empty 
		continue
	logging.log(logging.DEBUG, "********* AC : "+ac+" *********")	
	if(~cfg.has_section(ac)):  # AC name must be in config.ini 
		logging.log(logging.DEBUG, " host = "+cfg.get(ac,'host'))
		logging.log(logging.DEBUG, " remote_dir = "+cfg.get(ac,'remote_dir'))
		logging.log(logging.DEBUG, " file_pattern = "+cfg.get(ac,'file_pattern'))
		logging.log(logging.DEBUG, " ftp_type = "+cfg.get(ac,'ftp_type'))

		if(cfg.get(ac,'ftp_type') == 'ftp'):
			logging.log(logging.DEBUG, " Start downloading by ftp")
			getDataFTP(ts,te,ac,cfg,cfgtable) 
		elif(cfg.get(ac,'ftp_type') == 'tls'):
			logging.log(logging.DEBUG, " Start downloading by ftp-tls")
			getDataFTP_TLS(ts,te,ac,cfg,cfgtable) 
		elif(cfg.get(ac,'ftp_type') == 'http'):
			logging.log(logging.DEBUG, " Start downloading by http")
			getDataHTTP(ts,te,ac,cfg,cfgtable) 
		elif(cfg.get(ac,'ftp_type') == 'https'):
			logging.log(logging.DEBUG, " Start downloading by https")
			getDataHTTPS(ts,te,ac,cfg,cfgtable)  
		elif(cfg.get(ac,'ftp_type') == 'sftp'):
			logging.log(logging.DEBUG, " Start downloading by SSH/SFTP")
			getDataSFTP(ts,te,ac,cfg,cfgtable) 	  


logging.log(logging.DEBUG, " All downloads are over ")

end = time.time()
print(end-start)