import sys
import pwd
import grp
import os
from subprocess import call
import optparse
import httplib2
import urllib, logging
import string
import NewtHelper
from time import time, sleep
import json
import shutil
import sqlite3 as lite
import fileinput

#mpirun ... powerspec.out ngrid inputfile nfiles outputfile boxsize [line of sight w omega_m]

def create_pbs_file(nodes, procs, exeQueue, exetime, toolsDir, workingDir, workingName, ngrid, inputfile, nfiles, outfile, boxsize):
    numnodes = int(nodes)
    numprocs = int(procs)
    exeTime = int(exetime)
    np = numnodes*numprocs
    pbsText = """
#PBS -q %(exeQueue)s
#PBS -A hacc
#PBS -l nodes=%(numnodes)d:ppn=%(numprocs)d
#PBS -l walltime=00:%(exeTime)d:00
#PBS -N pow
#PBS -e pow.$PBS_JOBID.err
#PBS -o pow.$PBS_JOBID.out
#PBS -V
    
module unload pgi
module load gcc
module load fftw
module load gsl   
module load sqlite
 
cd %(workingDir)s

mpirun -n %(np)d %(toolsDir)s/powerspec.out %(ngrid)s %(inputfile)s %(nfiles)s %(outfile)s %(boxsize)s
chmod 777 %(outfile)s
chgrp hacc %(outfile)s
""" % {"exeQueue":exeQueue, "numnodes":numnodes, "numprocs":numprocs, "exeTime":exeTime, "workingDir":workingDir, "np":numnodes*numprocs, "toolsDir":toolsDir,"ngrid":ngrid, "inputfile":inputfile, "nfiles":nfiles, "outfile":outfile, "boxsize":boxsize, "outfile":outfile, "outfile":outfile}
    pbsPath = workingDir +"/" + "pow." + workingName + ".pbs"
    pbsFile = open(pbsPath, 'w')
    pbsFile.write(pbsText)
    pbsFile.close()
   # print outfile
    print 'Created PBS file.'
    return pbsPath
    

def run():    
    parser = optparse.OptionParser()
    parser.add_option('--inputfile', action="store", dest="inputfile")
    parser.add_option('--ngrid', action="store", dest="ngrid")
#    parser.add_option('--nfiles', action="store", dest="nfiles")
    parser.add_option('--outfile', action="store", dest="outfile")
#   parser.add_option('--boxsize', action="store", dest="boxsize")
    parser.add_option('--numNodes', action="store", dest="numNodes")
    parser.add_option('--numProcs', action="store", dest="numProcs")    
    parser.add_option('--exeTime', action="store", dest="exeTime")    
    parser.add_option('--exeQueue', action="store", dest="exeQueue")    

    (options, args) = parser.parse_args()
    
    nodes = options.numNodes
    procs = options.numProcs

    toolsDir = "/project/projectdirs/hacc/PDACS/JK_Tools"
    workingDir = "/project/projectdirs/hacc/PDACS/working/"

    #workingDir = os.getcwd()

    #get the name of the file - used to make the temp output files.
    workingName = options.outfile.split("/")
    workingName = workingName[len(workingName)-1]
   # print workingName

    #set the path to create files
    if not os.path.exists(workingDir):
        os.makedirs(workingDir)

    outFile = workingDir + workingName + ".out"
  
    con = lite.connect(options.inputfile)
    cur = con.cursor()
    cur.execute("select value from metadata where name='box_size [Mpc/h]'")
    row = cur.fetchone()
    boxsize = float(row[0])
    cur.execute("select value from metadata where name='numFiles'")
    row = cur.fetchone()
    nfiles = float(row[0])
    cur.execute("select value from metadata where name='Snapshot'")
    con.commit()
    row = cur.fetchone()
    snapshotname = row[0]
    
    #print options.outfile
    inFile = "/project/projectdirs/hacc/PDACS/Coyote/Grid/" + snapshotname
   # print inFile

    #write the pbs file to execute on Carver
    pbsPath = create_pbs_file(nodes, procs, options.exeQueue, options.exeTime, toolsDir, workingDir, workingName, options.ngrid, inFile, nfiles, outFile, boxsize)
   # print pbsPath
  #  os.chmod(pbsPath, S_IRUSR|S_IWUSR|S_IRGRP|S_IWGRP|S_IROTH|S_IWOTH) 

    #authenticate with NEWT
    res, con = NewtHelper.authenticate()
    cookieStr = res['set-cookie']
    print 'Authenticated'    
    res, con = NewtHelper.execute_job(pbsPath, cookieStr)
    print 'Submitted job: ' + NewtHelper.getJobID(con)
    jobid = NewtHelper.getJobID(con)
    print "Job queued successfully."
    status = NewtHelper.getJobStatus(jobid, cookieStr)
    status = NewtHelper.waitToFinish(jobid, cookieStr)
    
    if status == "C":
        print "Job completed."
    #print outFile 
    cmd = "sed 's/^[ \t]*//' %s | tr -s ' ' '\t' > %s" %(outFile, options.outfile)
    os.system(cmd)
    headers = 'k pk'.split()
    for line in fileinput.input([options.outfile], inplace=True):
      if fileinput.isfirstline():
        print '\t'.join(headers)
      print line

    os.remove(outFile)
    os.remove(pbsPath)
if __name__ == '__main__':
    run()
