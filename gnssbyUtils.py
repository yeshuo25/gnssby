#!/usr/bin/python3 

import sys
import os
import platform
import configparser
# import for downloading from ftp/tls
from ftplib import FTP
from ftplib import FTP_TLS
# import for time conversion
import time 
import datetime
# import for downloading from http/https
import requests
# import for regular expression
import re
import logging



year_4d 	= '[YYYY]'
year_2d 	= '[YY]'
doy_3d  	= '[DDD]'
day_2d  	= '[DAY]'
month_2d    = '[MONTH]'
hour_2d     = '[HOUR]'
week_4d		= '[WEEK]'
wod_2d		= '[WOD]'
wkday_5d	= '[WD]'

FILE_TYPE	    = '[file_type]'
RENAME_PATTERN	= '[rename_pattern]'

SITE_upper   = '[SITE]'
SITE_lower   = '[site]'


# ref: https://urs.earthdata.nasa.gov/documentation/for_users/data_access/python
class SessionWithHeaderRedirection(requests.Session):
	AUTH_HOST = 'urs.earthdata.nasa.gov'
	def __init__(self, username, password):
		super().__init__()
		self.auth = (username, password)   
		#print(username + password)
	# Overrides from the library to keep headers when redirected to or from
	# the NASA auth host.
	def rebuild_auth(self, prepared_request, response):
		headers = prepared_request.headers
		url = prepared_request.url
		if 'Authorization' in headers:
			#print(headers)
			original_parsed = requests.utils.urlparse(response.request.url)
			redirect_parsed = requests.utils.urlparse(url)

			if (original_parsed.hostname != redirect_parsed.hostname) and \
					redirect_parsed.hostname != self.AUTH_HOST and \
					original_parsed.hostname != self.AUTH_HOST:
				del headers['Authorization']
		return   
        
# Time conversion, from datetime to DOY
def datetime2doy(epotime): 
	year = epotime.year
	year_origin = datetime.datetime(year,1,1,0,0,0)
	return (epotime - year_origin).days + 1

# Time conversion, from datetime to GPST
def datetime2gpst(epotime,weekday): 
	deltDays = (epotime - datetime.datetime(1980,1,6,0,0,0)).days
	weekday.append(int(deltDays / 7 )) 
	weekday.append(int(deltDays - weekday[0] * 7) )

# list all file names with extend 'ext', un-include sub-directory			
def listdirExt(path, list_name,ext): 
	lenExt = len(ext)
	for file in os.listdir(path):  
		file_path = os.path.join(path, file)  
		if os.path.isdir(file_path):  
			print('skip sub-directory '+ file_path)
		else:  
			if(file_path[0-lenExt:].lower().find(ext) != -1):
				list_name.append(file_path)

# list all file names, un-include sub-directory
def listdir_withoutSubDir(path, list_name): 
	for file in os.listdir(path):  
		file_path = os.path.join(path, file)  
		if os.path.isdir(file_path):  
			print('skip sub-directory '+ file_path)
		else:  
			list_name.append(file_path)
	
# repalce time string
def repalceTime(epotime,inputString):
	repath = inputString
	weekday = []
	datetime2gpst(epotime,weekday)
	if(repath.find(year_4d)):
		repath=repath.replace(year_4d, str(epotime.year).zfill(4))
		
	if(repath.find(year_2d)):
		repath=repath.replace(year_2d, str(epotime.year%1000).zfill(2))
		
	if(repath.find(doy_3d)):
		repath=repath.replace(doy_3d, str(datetime2doy(epotime)).zfill(3))
		
	if(repath.find(day_2d)):
		repath=repath.replace(day_2d, str(epotime.day).zfill(2))
		
	if(repath.find(month_2d)):
		repath=repath.replace(month_2d,str(epotime.month).zfill(2))
		
	if(repath.find(hour_2d)):
		repath=repath.replace(hour_2d, str(epotime.hour).zfill(2))
		
	if(repath.find(week_4d)):
		repath=repath.replace(week_4d, str(weekday[0]).zfill(4))

	if(repath.find(wod_2d)):
		repath=repath.replace(wod_2d, str(weekday[1]).zfill(2))
				
	if(repath.find(wkday_5d)):
		repath=repath.replace(wkday_5d, str(weekday[0]*10+weekday[1]).zfill(5))		
		
	repath=repath.replace('?', '.')
	return repath

# replace site name for the configuration of [rename] 
def repalceSite(siteString,inputString):
	repath = inputString
	if(len(siteString) == 0):
		return repath
	logging.log(logging.DEBUG, 'repalceSite: ' + siteString + ' ' + inputString)
	if(repath.find('/[SITE]/')):
		repath=repath.replace(SITE_upper, str.upper(siteString))
	if(repath.find('/[site]/')):
		repath=repath.replace(SITE_lower, str.lower(siteString))
	return repath

# create logger, output to log_gnssby directory
def createLogger():
	LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
	DATE_FORMAT = "%m/%d/%Y %H:%M:%S "
	timestr = datetime.datetime.now().strftime("%Y%m%d_%H_%M_%S.txt")
	logname = 'log_gnssby'+'/'+timestr
	if not os.path.exists("log_gnssby"):
		os.mkdir("log_gnssby")
	logging.basicConfig(filename=logname, level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT)
	logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))


# get the type List for [file_type] and [rename_pattern]
def getTypeList(typeString):
	regrex = re.compile(r'[[](.*?)[]]', re.S)
	listType = re.findall(regrex, typeString)
	return listType

def repalceDirAndFile(inputString,epoch,typeString):
	timeDir = repalceTime(epoch,inputString)
	repath = timeDir
	if(len(typeString) == 0):
		return repath
	logging.log(logging.DEBUG, 'repalceDirAndFile: input - ' + inputString + ' type=' + typeString)
	if(repath.find('/[file_type]/')):
		repath=repath.replace(FILE_TYPE, typeString)

	if(repath.find('/[rename_pattern]/')):
		repath=repath.replace(RENAME_PATTERN, typeString)

	logging.log(logging.DEBUG, 'repalceDirAndFile: output - ' + repath)
	return repath

# Processing for archive files
def archiveProcess(cfg,AC,downloadFile,epoch,fileType,stationName):
	filepath,filename = os.path.split(downloadFile)
	untarFile = downloadFile
	# (1) unzip 
	if(cfg.has_option(AC,'decompression') and cfg.get(AC,'decompression') == '1'):			
		untarFile = f_unzip_file(downloadFile)
		logging.log(logging.DEBUG, 'Unzip File: from - ' + downloadFile+' to '+ untarFile)		
	# (2) crx2rnx 
	if(cfg.has_option(AC,'crx2rnx') and cfg.get(AC,'crx2rnx') == '1'):  # only for 
		if(untarFile[-1] == 'd'):
			newuntarFile = untarFile[0:-2] + 'o'
		elif(untarFile[-4:] == '.crx'):
			newuntarFile = untarFile[0:-4] + '.rnx'
		else:
			logging.log(logging.ERROR, 'crx2rnx: Unrecognized file ' + untarFile+ ', delete all file.')
			os.remove(downloadFile)	
			os.remove(untarFile)
			return	
		if(os.path.exists(newuntarFile)):
			os.remove(newuntarFile)
		p_crx2rnx(untarFile)
		untarFile = newuntarFile
		logging.log(logging.DEBUG, 'f_unzip_File: crx2rnx after ' + untarFile)			
	# (3) crx2rnx 
	if(cfg.has_option(AC,'rename')):
		rFile  = repalceDirAndFile(cfg.get(AC,'rename'),epoch,fileType)
		rFile  = repalceSite(stationName,rFile)
		renameFile(untarFile,os.path.join(filepath,rFile))

# Get the interval of two file 
def getTimeInterval(CfgAC,AC):
	step = 24                 # default: step time = 24 hour / 1 day
	if(CfgAC.has_option(AC,'step')):
		step = int(CfgAC.get(AC,'step'))
	return step

def f_unzip_file(compressedFile):
	if(platform.system() == "Linux"): 
		if(compressedFile.endswith('.tar.gz') or compressedFile.endswith('.tar') or compressedFile.endswith('.tgz')):
			command =  'tar zxvf '
			root,ext = os.path.splitext(compressedFile)
			print(root)
			print(ext)
			if ext in ['.gz', '.bz2']:
				decompressName,tmpext = os.path.splitext(root)
		elif(compressedFile.endswith('.Z')):
			command =   'uncompress -dvf  '
			decompressName,tmpext = os.path.splitext(compressedFile)
		elif(compressedFile.endswith('.gz')):
			command =   'gunzip -dvf '
			decompressName,tmpext = os.path.splitext(compressedFile)
		elif(compressedFile.endswith('.zip') or compressedFile.endswith('.ZIP')):
			command =   'unzip  '
			decompressName,tmpext = os.path.splitext(compressedFile)
		elif(compressedFile.endswith('.rar')):
			command =   'rar x '
			decompressName,tmpext = os.path.splitext(compressedFile)
		else:
			logging.log(logging.ERROR, "f_unzip_File: Unrecognized file:"+compressedFile)
			logging.log(logging.ERROR, "f_unzip_File: Please manually modify source code.")
			decompressName = ""
	elif(platform.system() == "Windows"):
			command =   'gzip -dvf '
			decompressName,tmpext = os.path.splitext(compressedFile)
	else: 
		logging.log(logging.ERROR, "f_unzip_File: System platform have not been tested ! Please manually modify source code.")
		logging.log(logging.ERROR, "f_unzip_File: platform = "+platform.system())
		os._exit(1)

	logging.log(logging.DEBUG, "f_unzip_File: command="+command + compressedFile)
	logging.log(logging.DEBUG, "f_unzip_File: unzip file="+decompressName)
	os.system(command + compressedFile)
	return decompressName

# rename all files in AC local directory 
def renameFile(renameBefore,renameAfter):
	# the file doesn't exist
	if not os.path.exists(renameBefore):
		logging.log(logging.WARNING, 'renameFile: The renamed file does not exist= ' + renameBefore)
		return
	os.rename(os.path.join(renameBefore),os.path.join(renameAfter))
	logging.log(logging.DEBUG, 'renameFile: input= ' + renameBefore + ' out=' + renameAfter)


def p_crx2rnx(crxFile):
	logging.log(logging.DEBUG, 'p_crx2rnx: crx2rnx= ' + crxFile)
	command = './crx2rnx '
	os.system(command + crxFile)
	os.remove(crxFile)
	
def getTypeListInfo(cfgAC,AC):
	# get the list of type of file and rename type
	typeList = []
	renameList = []
	if(cfgAC.has_option(AC,'file_type')):
		typeList   = getTypeList(cfgAC.get(AC,'file_type'))
		if(cfgAC.has_option(AC,'rename_pattern')):
			renameList = getTypeList(cfgAC.get(AC,'rename_pattern'))
			if(len(typeList) != len(renameList)):
				logging.log(logging.ERROR, 'getDataFTP: number of [file_type] is not equal to [rename_pattern]')
				os._exit(1)	
		else:
			for index in range(len(typeList)):
				renameList.append('')
	else:
		typeList.append('')
		renameList.append('')
	return typeList,renameList
		
## main program for FTP server
def getDataFTP(tstart,tend,AC,cfgFTP,sectionTable):
	logging.log(logging.DEBUG, 'login FTP:'+cfgFTP.get(AC,'host'))
	ftp = FTP(host=cfgFTP.get(AC,'host'))
	if(cfgFTP.has_option(AC,'user') and cfgFTP.has_option(AC,'passwd')):
		logging.log(logging.DEBUG, 'login by user and password')
		if(AC.find('iGMAS') != -1 ):
			logging.log(logging.DEBUG, 'iGMAS ftp ')
			ftp.set_pasv(False)    # iGMAS ftp use port mode
		ftp.login(user=cfgFTP.get(AC,'user'), passwd=cfgFTP.get(AC,'passwd'))  
	else:
		ftp.login()  
	
	step = getTimeInterval(cfgFTP,AC)  
	typeList,renameList = getTypeListInfo(cfgFTP,AC)

	epoch = tstart
	while(epoch<=tend):
		logging.log(logging.DEBUG, 'getDataFTP: Time-> '+epoch.strftime("%Y-%m-%d %H:%M:%S"))		

		# loop remote and local directory according to [file types]
		for ifTypeDir in range(0,(1 if cfgFTP.get(AC,'remote_dir').find(FILE_TYPE) == -1  else len(typeList))):
			# get local directory
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
			ftp.cwd(cwddir)
			remoteList = ftp.nlst()

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
					
					# local file name
					localFile = localdir+matchlist[i]
					if(cfgFTP.get('global','overwrite') == '0'):	
						if os.path.exists(localdir+matchlist[i]):
							logging.log(logging.WARNING, localFile + ' already exist, no overwrite ! ')
							continue
					
					logging.log(logging.DEBUG, 'getDataFTP: download ->'+matchlist[i]+' start ! ')
					with open(localFile, 'wb') as f:
						ftp.retrbinary('RETR ' + matchlist[i], f.write)
						f.close()
						logging.log(logging.DEBUG, 'getDataFTP: download ->'+matchlist[i]+' ok ! ')

					# archieve processing
					archiveProcess(cfgFTP,AC,localFile,epoch,renameList[ifTypeFile],stationName)	
		epoch = epoch + datetime.timedelta(hours = step)
	ftp.quit()
	
## main program for FTP-TLS server
def getDataFTP_TLS(tstart,tend,AC,cfgFTP,sectionTable):
	logging.log(logging.DEBUG, 'login FTP-TLS:'+cfgFTP.get(AC,'host'))
	ftp = FTP_TLS(host=cfgFTP.get(AC,'host'))

	if(cfgFTP.has_option(AC,'user') and cfgFTP.has_option(AC,'passwd')):
		logging.log(logging.DEBUG, 'login by user and password')
		ftp.login(user=cfgFTP.get(AC,'user'), passwd=cfgFTP.get(AC,'passwd'))  
	else:
		ftp.login(user='anonymous',passwd='gnssby@gmail.com')  
	ftp.prot_p()  # secure data connection
	
	step = getTimeInterval(cfgFTP,AC)    
	typeList,renameList = getTypeListInfo(cfgFTP,AC)

	epoch = tstart
	while(epoch<=tend):
		logging.log(logging.DEBUG, 'getDataFTP_TLS: Time-> '+epoch.strftime("%Y-%m-%d %H:%M:%S"))	

		# loop remote and local directory according to [file types]
		for ifTypeDir in range(0, (1 if cfgFTP.get(AC,'remote_dir').find(FILE_TYPE) == -1  else len(typeList))):
			# local directory
			tpath = os.path.join(cfgFTP.get('global','local_dir'),cfgFTP.get(AC,'lsub_dir'))
			localdir = repalceDirAndFile(tpath,epoch,typeList[ifTypeDir])
			# if the localdir path doesn't exist, create it.
			if not os.path.exists(localdir):
				os.makedirs(localdir)
				logging.log(logging.DEBUG, 'getDataFTP_TLS: mkdir local: '+localdir)
			localdir = localdir + '/'
			logging.log(logging.DEBUG, 'getDataFTP_TLS: local directory: '+localdir)

			# remote directory
			# cwd directory with [file_type] replaced
			cwddir   = repalceDirAndFile(cfgFTP.get(AC,'remote_dir'),epoch,typeList[ifTypeDir])
			logging.log(logging.DEBUG, 'getDataFTP_TLS: cwd -'+cwddir)
			# cd remote directory and list all file 
			ftp.cwd(cwddir)
			remoteList = ftp.nlst()

			# loop remote and local files according to [file types],such as [sp3] [clk].
			for ifTypeFile in range(0,(1 if cfgFTP.get(AC,'file_pattern').find(FILE_TYPE) == -1  else len(typeList))):
				fpattern = repalceDirAndFile(cfgFTP.get(AC,'file_pattern'),epoch,typeList[ifTypeFile])
				matchlist = [name for name in remoteList if re.match(fpattern,name)]
				#logging.log(logging.DEBUG, 'getDataFTP: ftp find file: ' + matchlist)

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
						if os.path.exists(llocalFile):
							logging.log(logging.WARNING, localFile + ' already exist, no overwrite ! ')
							continue

					logging.log(logging.DEBUG, 'getDataFTP-TLS: download ->'+matchlist[i]+' start ! ')
					with open(localFile, 'wb') as f:
						ftp.retrbinary('RETR ' + matchlist[i], f.write)
						f.close()
						logging.log(logging.DEBUG, 'getDataFTP-TLS: download ->'+matchlist[i]+' ok ! ')

					# archieve processing
					archiveProcess(cfgFTP,AC,localFile,epoch,renameList[ifTypeFile],stationName)	
		# time loop
		epoch = epoch + datetime.timedelta(hours = step)
	ftp.quit()

## main program for HTTP server
def getDataHTTP(tstart,tend,AC,cfgFTP,sectionTable):
	logging.log(logging.DEBUG, 'Download by HTTP:'+cfgFTP.get(AC,'host'))
	host = cfgFTP.get(AC,'host')
	step = getTimeInterval(cfgFTP,AC)    
	typeList,renameList = getTypeListInfo(cfgFTP,AC)

	epoch = tstart
	while(epoch<=tend):
		logging.log(logging.DEBUG, 'getDataHTTP: Time-> '+epoch.strftime("%Y-%m-%d %H:%M:%S"))	

		# loop remote and local directory according to [file types]
		for ifTypeDir in range(0,(1 if cfgFTP.get(AC,'remote_dir').find(FILE_TYPE) == -1  else len(typeList))):
			# local directory
			tpath = os.path.join(cfgFTP.get('global','local_dir'),cfgFTP.get(AC,'lsub_dir'))
			localdir = repalceDirAndFile(tpath,epoch,typeList[ifTypeDir])
			# if the localdir path doesn't exist, create it.
			if not os.path.exists(localdir):
				os.makedirs(localdir)
				logging.log(logging.DEBUG, 'getDataHTTP: mkdir local: '+localdir)
			localdir = localdir + '/'
			logging.log(logging.DEBUG, 'getDataHTTP: local directory: '+localdir)

			# remote directory
			# cwd directory with [file_type] replaced
			cwddir   = repalceDirAndFile(host+cfgFTP.get(AC,'remote_dir'),epoch,typeList[ifTypeDir])
			logging.log(logging.DEBUG, 'getDataHTTP: cwd - '+cwddir)
			htmlText = requests.get(cwddir).text
			subUrls = re.findall(r'<a.*?href="(.*?)">', htmlText)
			remoteList = list(set(subUrls))

			# loop remote and local files according to [file types],such as [sp3] [clk].
			for ifTypeFile in range(0,(1 if cfgFTP.get(AC,'file_pattern').find(FILE_TYPE) == -1  else len(typeList))):
				fpattern = repalceDirAndFile(cfgFTP.get(AC,'file_pattern'),epoch,typeList[ifTypeFile])
				matchlist = [name for name in remoteList if re.match(fpattern,name)]

				# loop the matching file list in remote server
				for i in range(0,len(matchlist)):
					# table section  
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
						if os.path.exists(localFile):
							logging.log(logging.WARNING, localFile + ' already exist, no overwrite ! ')
							continue
					

					logging.log(logging.DEBUG, 'getDataHTTP: download ->'+matchlist[i]+' start ! ')
					r = requests.get(cwddir+matchlist[i])
					with open(localFile, 'wb') as fd:
						for chunk in r.iter_content(chunk_size=1000):
							fd.write(chunk)
					fd.close()
					logging.log(logging.DEBUG, 'getDataHTTP: download ->'+matchlist[i]+' ok ! ')
					# archieve processing
					archiveProcess(cfgFTP,AC,localFile,epoch,renameList[ifTypeFile],stationName)	

		epoch = epoch + datetime.timedelta(hours = step)

## main program for HTTPS server
## only for CDDIS
def getDataHTTPS(tstart,tend,AC,cfgFTP,sectionTable):
	logging.log(logging.DEBUG, 'Download by HTTPS:'+cfgFTP.get(AC,'host'))
	
	host = cfgFTP.get(AC,'host')
	username = "SHAODownload"  # acccount of Chao Yu 
	password = "Download1234"
	# make the request to the web site to get filenames
	session = SessionWithHeaderRedirection(username, password) 

	# get the list of type of file and rename type
	step = getTimeInterval(cfgFTP,AC)   
	typeList,renameList = getTypeListInfo(cfgFTP,AC)

	epoch = tstart
	while(epoch<=tend):
		logging.log(logging.DEBUG, 'getDataHTTPS: Time-> '+epoch.strftime("%Y-%m-%d %H:%M:%S"))		
		# loop remote and local directory according to [file types]
		for ifTypeDir in range(0,(1 if cfgFTP.get(AC,'remote_dir').find(FILE_TYPE) == -1  else len(typeList))):
			# local directory
			tpath = os.path.join(cfgFTP.get('global','local_dir'),cfgFTP.get(AC,'lsub_dir'))
			# print(ifTypeDir)
			localdir = repalceDirAndFile(tpath,epoch,typeList[ifTypeDir])
			# if the localdir path doesn't exist, create it.
			if not os.path.exists(localdir):
				os.makedirs(localdir)
				logging.log(logging.DEBUG, 'getDataHTTPS: mkdir local: '+localdir)
			localdir = localdir + '/'
			logging.log(logging.DEBUG, 'getDataHTTPS: local directory: '+localdir)

			# remote directory
			# cwd directory with [file_type] replaced
			cwddir   = repalceDirAndFile(host+cfgFTP.get(AC,'remote_dir'),epoch,typeList[ifTypeDir])
			logging.log(logging.DEBUG, 'getDataHTTPS: cwd - '+cwddir)
			response = session.get(cwddir + "*?list", stream=True)
			if response.status_code is not requests.codes.ok:
				logging.log(logging.ERROR, 'getDataHTTPS:  '+"Could not connect to cddis server. HTML code: %d" % (response.status_code))
				return False   
			
			# parse the response and make list of filenames
			lines = response.text.split('\n')
			remoteList =[]
			for line in lines:
					if line.startswith("#"):    # comment lines
						continue
					if line.strip() == "":      # empty lines
						continue
					filename, size = line.split()
					remoteList.append(filename) 
				
			# loop remote and local files according to [file types],such as [sp3] [clk].
			for ifTypeFile in range(0,(1 if cfgFTP.get(AC,'file_pattern').find(FILE_TYPE) == -1  else len(typeList))):
				fpattern = repalceDirAndFile(cfgFTP.get(AC,'file_pattern'),epoch,typeList[ifTypeFile])
				matchlist = [name for name in remoteList if re.match(fpattern,name)]
				excl_list = ["MD5SUMS", "SHA512SUMS", "index.html"]
			
				for i in range(0,len(matchlist)):
					if matchlist[i] in excl_list:
						continue

					# table section  
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
						if os.path.exists(localFile):
							logging.log(logging.WARNING, localFile + ' already exist, no overwrite ! ')
							continue

					logging.log(logging.DEBUG, 'getDataHTTPS: download ->'+matchlist[i]+' start ! ')
					response = session.get(cwddir+matchlist[i])
					# download each file and save it
					with open(localFile, 'wb') as fd:
						for chunk in response.iter_content(chunk_size=1024*1024):
							fd.write(chunk)
					fd.close()
					logging.log(logging.DEBUG, 'getDataHTTPS: download ->'+matchlist[i]+' ok ! ')
					# archieve processing
					archiveProcess(cfgFTP,AC,localFile,epoch,renameList[ifTypeFile],stationName)	

		epoch = epoch + datetime.timedelta(hours = step)

