# gnssby
Python script for downloading of gnss data 

#      Note     
#
|  File   | Explanation  |
|  ----  | ----  |
| ***config.ini***  | FTP configure for Linux |
| ***config_win.ini***  | FTP configure for Windows |
| ***listTable.ini***  | The type or prefix of file name |
                  

#

Manual configuration changes are necessary for the downloading configure in gnssby.py.

|  Variable   | Explanation  |
|  ----  | ----  |
| ***ts***  | start  time |
| ***te***  | ending time |
| ***AClist***  | remote and local configure. |


#

The multi-thread processing of python is not recommended to achieve, but 
running multiple scripts with different configurations at the same time can improve the speed of downloading.
#
*******************************      Note      *******************************

# Command
## Windows
python gnssby.py

## Linux
python3 gnssby.py
