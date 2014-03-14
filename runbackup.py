# This file backs up a MediaWiki installation from a server on a Windows
# network onto a local installation of MediaWiki. It also backs up a compressed
# file onto another server.
#
#
#
#
import os # for many reasons...
from os.path import join # to do join() instead of os.path.join()
import shutil # for erase directory contents
import distutils.core # to allow copying contents of dir into another dir
import subprocess

#
#	Exit script if user doesn't type "yes"
#
print "You are about to start the wiki backup process"
askContinue = raw_input("Are you sure you want to continue (type \"yes\" or \"debug\")?: ")
if askContinue.lower() == "debug":
	debug = True
	print "Proceeding with script in DEBUG mode\n"
elif askContinue.lower() != "yes":
	print "Exiting script"
	exit()
else:
	debug = False
	print "Proceeding with script\n"


dir = os.path.dirname(os.path.realpath(__file__))


##### ENVIRONMENT VARIABLES #####
import app.config

print "Which wiki would you like to backup?"
for (i, wiki) in enumerate( app.config.wikis ):
	print "    %d: %s" % (i, wiki["wikiname"])
wikinum = raw_input("Enter the wiki number above: ")


try:
	wikinum = int(wikinum)
	wikiname = app.config.wikis[wikinum]["wikiname"]
except IndexError:
	print "There is no wiki number %d. Goodbye." % wikinum
	exit()

# wikinum = 1 # temporary until I've enabled looping through wikis

wikiname = app.config.wikis[wikinum]["wikiname"]

print "Set to Wiki #%d %s" % (wikinum, wikiname)

sourcepath = app.config.wikis[wikinum]["sourcepath"]
sourcehost = app.config.wikis[wikinum]["sourcehost"]
sourceuser = app.config.wikis[wikinum]["sourceuser"]
sourcepass = app.config.wikis[wikinum]["sourcepass"]
sourcedb   = app.config.wikis[wikinum]["sourcedb"]

localpath = app.config.wikis[wikinum]["localpath"]
localhost = app.config.wikis[wikinum]["localhost"]
localuser = app.config.wikis[wikinum]["localuser"]
localpass = app.config.wikis[wikinum]["localpass"]
localdb   = app.config.wikis[wikinum]["localdb"]


# FIXME: don't rely on JSCMOD extension
# Path to wgReadOnly.php on wiki to be locked
wgReadOnlyPath = join(sourcepath,'extensions','JSCMOD','wgReadOnly.php')

wikiSqlFile = join(localpath,"wiki-db.sql")


staticbackup = app.config.staticbackup
libFiles = app.config.libFiles
logFiles = app.config.logFiles
zipType = app.config.zipType
mysql = app.config.mysql
mysqldump = app.config.mysqldump
sevenZip = app.config.sevenZip # if used





# STDOUT and STDERR (from subprocess) write to these, to be written to a file later
output = "" # STDOUT
errors = "" # STDERR

previousStep = False
stepNumber = 0

def eraseDirectoryContents ( dirpath ):
	for filename in os.listdir(dirpath):
		filepath = os.path.join(dirpath, filename)
		try:
			if debug:
				print "Deleting file:    " + filepath
			if os.path.isfile(filepath):
				os.unlink(filepath)
			elif os.path.isdir(filepath):
				shutil.rmtree(filepath)
		except Exception, e:
			print e

def recordSubprocessOutput(title, comm):
	out, err = comm
	global output
	global errors
	if out:
		output = output + "\n\n##" + title + "\n\n" + out
	if err:
		errors = errors + "\n\n##" + title + "\n\n" + err

def writeOutputFiles():
	global backupTimestamp
	global output
	logprefix = sourcedb + "_" + backupTimestamp
	if len(output) > 0:
		outputTitle = "Py Wiki Backup Standard Output File"
		output = outputTitle + "\n" + ("="*len(outputTitle)) + "\n\n" + output
		outputFile = open(join(logFiles,logprefix + '_stdout.txt'),'w+')
		outputFile.write(output)
		outputFile.close()
	global errors
	if len(errors) > 0:
		errorsTitle = "Py Wiki Backup Errors File"
		errors = errorsTitle + "\n" ("="*len(errorsTitle)) + "\n\n" + errors
		errorsFile = open(join(logFiles,logprefix + '_stderr.txt'),'w+')
		errorsFile.write(errors)
		errorsFile.close()

def printSteps(stepText):
	global previousStep
	global stepNumber
	global wikiname
	global wikinum

	if previousStep:
		print "Complete: %s\n\n" % previousStep
	previousStep = stepText
	stepNumber = stepNumber + 1
	stepText = "Wiki %d (%s) Step %d:\n    %s" % (wikinum, wikiname, stepNumber, stepText)
	if debug:
		debugAsk = raw_input("%s...continue? (yes/no): " % stepText)
		if debugAsk.lower() != "yes":
			print "Debug...breaking out of script"
			exit()
	else:
		print stepText + "\n"

def setReadOnly ( setReadOnly ):
	wgReadOnly = open( wgReadOnlyPath, 'w' )

	if setReadOnly is True:
		sourceFilename = "setReadOnlyContent.txt"
	else:
		sourceFilename = "unsetReadOnlyContent.txt"

	sourceFile = open( join(libFiles, sourceFilename ), 'r' )
	wgReadOnly.write( sourceFile.read() )
	sourceFile.close()
	wgReadOnly.close()


##### (1) DELETE images directory on local computer #####
printSteps("Delete local images folder")
eraseDirectoryContents( join(localpath,"images") )


##### (2) LOCK source wiki; make read-only #####
printSteps("Lock source wiki")
setReadOnly( True )


##### (3) copy files from source to local #####
printSteps("Copy source files to local")
distutils.dir_util.copy_tree( join(sourcepath,"images"), join(localpath,"images"))

# This happens here because it's the latest possible before the database dump #
# Though the wiki is locked for edits the database is still updated with user #
# views and other statistics, so this step should happen just before the dump #
import time, datetime
backupTimestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H%M%S')


##### (4) MYSQLDUMP source sql to localhost/wiki, called wiki-db.sql #####
printSteps("mysqldump source wiki onto local")
proc = subprocess.Popen(
	[mysqldump,'--host='+sourcehost,'--user='+sourceuser,
		'--password='+sourcepass,sourcedb,'--result-file='+wikiSqlFile],
		stdin=subprocess.PIPE, stdout=subprocess.PIPE )
recordSubprocessOutput( "MySQL Dump Source DB", proc.communicate() )


##### (5) UNLOCK source; make wiki editable #####
printSteps("Unlock source wiki")
setReadOnly( False )


##### (6) Delete and re-create local database #####
printSteps("Drop local database")
proc = subprocess.Popen(
	["mysql", "--host=%s" % localhost, "--user=%s" % localuser,
		"--password=%s" % localpass, "-e", "DROP DATABASE %s" % localdb],
		stdin=subprocess.PIPE, stdout=subprocess.PIPE)
recordSubprocessOutput(
	"MySQL Drop Local DB",
	proc.communicate() )


##### (7) Re-create local database #####
printSteps("Re-create local database")
proc = subprocess.Popen(
	["mysql", "--host=%s" % localhost, "--user=%s" % localuser,
		"--password=%s" % localpass, "-e", "CREATE DATABASE %s" % localdb],
		stdin=subprocess.PIPE, stdout=subprocess.PIPE)
recordSubprocessOutput(
	"MySQL Recreate Local DB",
	proc.communicate() )


##### (8) PUSH SQL to local
printSteps("Push SQL to local wiki")
proc = subprocess.Popen(
	["mysql", "--host=%s" % localhost, "--user=%s" % localuser,
		"--password=%s" % localpass, localdb],
		stdin=subprocess.PIPE, stdout=subprocess.PIPE)
recordSubprocessOutput(
	"MySQL Import to Local DB",
	proc.communicate(file(wikiSqlFile).read()) )


##### (9) COMPRESS images folder, push to static backup #####
printSteps("Zip /images into backup location")

zipFilePath = join(staticbackup,sourcedb+"_"+backupTimestamp+".zip")

if zipType == "7zip":
	proc = subprocess.Popen(
		[sevenZip, "a", zipFilePath, join(localpath, "images", "*"), "-r", "-tzip"],
		stdin=subprocess.PIPE, stdout=subprocess.PIPE)
	recordSubprocessOutput("7-Zip Compression", proc.communicate())

else:
	proc = subprocess.Popen(
		["zip", "-r", zipFilePath, join(localpath, "images")],
		stdin=subprocess.PIPE, stdout=subprocess.PIPE)
	recordSubprocessOutput("Zip Utility Compression", proc.communicate())


##### (10) Update static backup folder with SQL file #####
printSteps("Add SQL file to compressed backup")
if zipType == "7zip":
	proc = subprocess.Popen(
		[sevenZip, "u", zipFilePath, wikiSqlFile],
		stdin=subprocess.PIPE, stdout=subprocess.PIPE)
	recordSubprocessOutput("7-Zip Update with SQL", proc.communicate())

else:
	print zipFilePath
	proc = subprocess.Popen(
		["zip", "-r", zipFilePath, wikiSqlFile],
		stdin=subprocess.PIPE, stdout=subprocess.PIPE)
	recordSubprocessOutput("Zip Update with SQL", proc.communicate())



##### (11) Write output files #####
printSteps("Write output and errors files")
writeOutputFiles()


print "\n\nWiki Backup Complete"
