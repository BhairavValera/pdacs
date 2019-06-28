import sys
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

def create_pbs_file(nodes, procs, exeQueue, exetime, toolsDir, workingDir, workingName, ngrid, inputfile, nfiles, outfile, boxsize, line, w, omega_m):
    numnodes = int(nodes)
    numprocs = int(procs)
    exeTime= int(exetime)
    np = numnodes*numprocs
    pbsText = """
#PBS -q %(exeQueue)s
#PBS -A hacc
#PBS -l nodes=%(numnodes)d:ppn=%(numprocs)d
#PBS -l walltime=00:%(exeTime)d:00
#PBS -N rs_pow
#PBS -e rs_pow.$PBS_JOBID.err
#PBS -o rs_pow.$PBS_JOBID.out
#PBS -V
    
module unload pgi
module load gcc
module load fftw
module load gsl   
module load sqlite

cd %(workingDir)s
mpirun -n %(np)d %(toolsDir)s/powerspec.out %(ngrid)s %(inputfile)s %(nfiles)s %(outfile)s %(boxsize)s %(line)s %(w)s %(omega_m)s
chmod 777 %(outfile)s.*
chgrp hacc %(outfile)s.*
""" % {"exeQueue":exeQueue, "numnodes":numnodes, "numprocs":numprocs, "exeTime":exeTime, "workingDir":workingDir, "np":numnodes*numprocs, "toolsDir":toolsDir,"ngrid":ngrid, "inputfile":inputfile, "nfiles":nfiles, "outfile":outfile, "boxsize":boxsize, "line":line, "w":w, "omega_m":omega_m, "outfile":outfile, "outfile":outfile} 
    pbsPath = workingDir +"/" + "rs_pow." + workingName + ".pbs"
    pbsFile = open(pbsPath, 'w')
    pbsFile.write(pbsText)
    pbsFile.close()
    print 'Created PBS file.'
    return pbsPath
    

def run():    
    parser = optparse.OptionParser()
    parser.add_option('--inputfile', action="store", dest="inputfile")
    parser.add_option('--ngrid', action="store", dest="ngrid")
    parser.add_option('--exeTime', action="store", dest="exeTime")
    parser.add_option('--exeQueue', action="store", dest="exeQueue")
    parser.add_option('--outfile_2d', action="store", dest="outfile_2d")
    parser.add_option('--outfile_multipole', action="store", dest="outfile_multipole")
#    parser.add_option('--boxsize', action="store", dest="boxsize")
    parser.add_option('--line', action="store", dest="line")
#    parser.add_option('--w', action="store", dest="w")
#    parser.add_option('--omega_m', action="store", dest="omega_m")
    parser.add_option('--numNodes', action="store", dest="numNodes")
    parser.add_option('--numProcs', action="store", dest="numProcs")    

    (options, args) = parser.parse_args()
    
    nodes = options.numNodes
    procs = options.numProcs

    toolsDir = "/project/projectdirs/hacc/PDACS/JK_Tools/"
    workingDir = "/project/projectdirs/hacc/PDACS/working/"

   # inputArg = options.inputfile
   # split = os.path.splitext(options.inputfile)

    #get the name of the file - used to make the temp output files.
    workingName = options.outfile_2d.split("/")
    workingName = workingName[len(workingName)-1]
    #outFile = "rs_pow.out"
    #workingDir + workingName
    #set the path to create files
    if not os.path.exists(workingDir):
        os.makedirs(workingDir)

    outFile = workingDir + workingName + ".out"
    #write the pbs file to execute on Carver
    #os.chmod(outFile,S_IRUSR|S_IWUSR|S_IRGRP|S_IWGRP|S_IROTH|S_IWOTH)

    con = lite.connect(options.inputfile)
    cur = con.cursor()
    cur.execute("select value from metadata where name='box_size [Mpc/h]'")
    row = cur.fetchone()
    boxsize = float(row[0])
    cur.execute("select value from metadata where name='numFiles'")
    row = cur.fetchone()
    nfiles = float(row[0])
    cur.execute("select value from metadata where name='Omega_m'")
    row = cur.fetchone()
    omega_m = float(row[0])
    cur.execute("select value from metadata where name='w_de'")
    row = cur.fetchone()
    w = float(row[0])
    cur.execute("select value from metadata where name='Snapshot'")
    con.commit()
    row = cur.fetchone()
    snapshotname = row[0]

#    print options.outfile
    infile = "/project/projectdirs/hacc/PDACS/Coyote/Grid/" + snapshotname
#    print infile
    
    pbsPath = create_pbs_file(nodes, procs, options.exeQueue, options.exeTime, toolsDir, workingDir, workingName, options.ngrid, infile, nfiles, outFile, boxsize, options.line, w, omega_m)
    
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
    
    #output the files

    #shutil.copyfile(outFile, options.outputfile)
#    cmd = "tr ' ' '\t' <%s >%s" %(outputFile, options.outFile)
    cmd = "sed -e 's/^[ \t]*//;s/[ \t]*$//' %s | tr -s ' ' '\t' > %s" %(outFile+".2D", options.outfile_2d)
    os.system(cmd)
    headers = 'k mu P_k_mu'.split()
    for line in fileinput.input([options.outfile_2d], inplace=True):
      if fileinput.isfirstline():
        print '\t'.join(headers)
      print line
    cmd = "sed -e 's/^[ \t]*//;s/[ \t]*$//' %s | tr -s ' ' '\t' > %s" %(outFile+".multipole", options.outfile_multipole)
    os.system(cmd)
    headers = 'k monopole quadrupole'.split()
    for line in fileinput.input([options.outfile_multipole], inplace=True):
      if fileinput.isfirstline():
        print '\t'.join(headers)
      print line
    os.remove(outFile+".2D")
    os.remove(outFile+".multipole")
    os.remove(pbsPath)

if __name__ == '__main__':
    run()
