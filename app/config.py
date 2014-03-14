import json, os
from os.path import join

dir = os.path.realpath(join( os.path.dirname(os.path.realpath(__file__)), ".."))

with open( join(dir, "config.json"), 'r' ) as f:
	config = json.load( f )
	f.close()


if config["mysqldump"]:
	mysqldump = config["mysqldump"]
else:
	mysqldump = "mysqldump"

if config["mysql"]:
	mysql = config["mysql"]
else:
	mysql = "mysql"

if not config["zipType"] or config["zipType"] == "zip":
	zipType = "zip"
	sevenZip = False
else:
	zipType = "7zip"
	if config["sevenZip"]:
		sevenZip = config["sevenZip"]
	else:
		sevenZip = "7z.exe"


staticbackup = config["staticbackup"]

libFiles = join(dir, "lib")
logFiles = join(dir, "log")

wikis = config["wikis"]