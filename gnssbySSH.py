#!/usr/bin/python3 

# import for SSH/SFTP protocol
import paramiko    

from gnssbyUtils import *

## main program for SSH/SFTP server
def getDataSFTP(tstart,tend,AC,cfgFTP,sectionTable):
	logging.log(logging.DEBUG, 'login SFTP:'+cfgFTP.get(AC,'host'))

	transport = paramiko.Transport(cfgFTP.get(AC,'host'),int(cfgFTP.get(AC,'port')))
	if(cfgFTP.has_option(AC,'user') and cfgFTP.has_option(AC,'passwd')):
		logging.log(logging.DEBUG, 'login by user and password')
		transport.connect(username = cfgFTP.get(AC,'user'),password = cfgFTP.get(AC,'passwd'))
	else:
		transport.connect(username = 'anonymous',password = 'gnssby@gmail.com')
	sftp = paramiko.SFTPClient.from_transport(transport)

	step = getTimeInterval(cfgFTP,AC) 
	typeList,renameList = getTypeListInfo(cfgFTP,AC)

	epoch = tstart
	while(epoch<=tend):
		logging.log(logging.DEBUG, 'getDataFTP: Time-> '+epoch.strftime("%Y-%m-%d %H:%M:%S"))		
		# loop remote and local directory according to [file types]
		for ifTypeDir in range(0,(1 if cfgFTP.get(AC,'remote_dir').find(FILE_TYPE) == -1  else len(typeList))):

			# local directory
			tpath = os.path.join(cfgFTP.get('global','local_dir'),cfgFTP.get(AC,'lsub_dir'))
			localdir = repalceDirAndFile(tpath,epoch,typeList[ifTypeDir])
			# if the localdir path doesn't exist, create it.
			if not os.path.exists(localdir):
				os.makedirs(localdir)
				logging.log(logging.DEBUG, 'getDataFTP: mkdir local: '+localdir)
			localdir = localdir + '/'
			logging.log(logging.DEBUG, 'getDataFTP: local directory: '+localdir)

			# remote directory
			# cwd directory with [file_type] replaced
			cwddir   = repalceDirAndFile(cfgFTP.get(AC,'remote_dir'),epoch,typeList[ifTypeDir])
			logging.log(logging.DEBUG, 'getDataFTP: cwd - '+cwddir)
			# cd remote directory and list all file 
			sftp.chdir(cwddir)
			remoteList = sftp.listdir()

			# loop remote and local files according to [file types],such as [sp3] [clk].
			for ifTypeFile in range(0,(1 if cfgFTP.get(AC,'file_pattern').find(FILE_TYPE) == -1  else len(typeList))):
				fpattern = repalceDirAndFile(cfgFTP.get(AC,'file_pattern'),epoch,typeList[ifTypeFile])
				matchlist = [name for name in remoteList if re.match(fpattern,name)]
				
                # loop the matching file list in remote server
				for i in range(0,len(matchlist)):
					# table section, get station name if the file needs to be renamed.
					stationName = []
					if(sectionTable.has_section(AC) and len(sectionTable.options(AC)) != 0):
						length = len(sectionTable.options(AC)[0])
						stationName = matchlist[i][0:length]
						if(not sectionTable.has_option(AC,str.upper(matchlist[i][0:length])) and not sectionTable.has_option(AC,str.lower(matchlist[i][0:length])) ):
							continue
					else:
						stationName = matchlist[i][0:4]  # default: char 4
						logging.log(logging.DEBUG, 'Download mode: All files will be downloaded !')

					localFile = localdir+matchlist[i]
					if(cfgFTP.get('global','overwrite') == '0'):	
						if os.path.exists(localdir+matchlist[i]):
							logging.log(logging.WARNING, localFile + ' already exist, no overwrite ! ')
							continue

					logging.log(logging.DEBUG, 'getDataFTP: download ->'+matchlist[i]+' start ! ')
					sftp.get(matchlist[i],localFile)
					logging.log(logging.DEBUG, 'getDataFTP: download ->'+matchlist[i]+' ok ! ')

					# archieve processing
					archiveProcess(cfgFTP,AC,localFile,epoch,renameList[ifTypeFile],stationName)	
		
		epoch = epoch + datetime.timedelta(hours = step)
	sftp.close()
	


