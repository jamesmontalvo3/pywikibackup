import json, os
from os.path import join

dir = os.path.realpath(join( os.path.dirname(os.path.realpath(__file__)), ".."))

with open( join(dir, "config.json"), 'r' ) as f:
	config = json.load( f )
	f.close()


if "mysqldump" in config.keys():
	mysqldump = config["mysqldump"]
else:
	mysqldump = "mysqldump"

if "mysql" in config.keys():
	mysql = config["mysql"]
else:
	mysql = "mysql"

if "zipType" not in config.keys() or config["zipType"] == "zip":
	zipType = "zip"
	sevenZip = False
else:
	zipType = "7zip"
	if "sevenZip" in config.keys():
		sevenZip = config["sevenZip"]
	else:
		sevenZip = "7z.exe"


staticbackup = config["staticbackup"]

libFiles = join(dir, "lib")
logFiles = join(dir, "log")

wikis = config["wikis"]