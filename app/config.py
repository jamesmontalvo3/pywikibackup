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


def getFromWikiOrDie(wikinum, field):
	global wikis
	if field in wikis[wikinum]:
		return wikis[wikinum][field]
	else:
		print "Wiki %d does not have a %s. This must be set for all wikis." % (wikinum, field)
		exit()

def getFromWikiOrDefault(wikinum, field):
	global wikis, config
	
	if field in wikis[wikinum].keys():
		return wikis[wikinum][field]
	elif field in config["defaults"].keys():
		return config["defaults"][field]
	else:
		print "%s was not found in wiki %d or in default settings" % (field, wikinum)
		exit()


# The following four parameters must be set for each wiki
def getSourcePath(wikinum):
	return getFromWikiOrDie(wikinum, "sourcepath")

def getSourceDB(wikinum):
	return getFromWikiOrDie(wikinum, "sourcedb")

def getLocalPath(wikinum):
	return getFromWikiOrDie(wikinum, "localpath")

def getLocalDB(wikinum):
	return getFromWikiOrDie(wikinum, "localdb")



# If the following parameters are not set in a wiki, the default will be used
def getSourceHost(wikinum):
	return getFromWikiOrDefault(wikinum, "sourcehost")

def getSourceUser(wikinum):
	return getFromWikiOrDefault(wikinum, "sourceuser")

def getSourcePass(wikinum):
	return getFromWikiOrDefault(wikinum, "sourcepass")
	
def getLocalHost(wikinum):
	return getFromWikiOrDefault(wikinum, "localhost")

def getLocalUser(wikinum):
	return getFromWikiOrDefault(wikinum, "localuser")

def getLocalPass(wikinum):
	return getFromWikiOrDefault(wikinum, "localpass")
	