#!/bin/bash -l

if [ $# -ne 3 ]
then
  echo "Wrong number of arguments in $0: got $#, require 3"
  exit 1
fi

#rankinfo=$1
infile=$1
outfile=$2
galaxy_dir=$3
tools_dir=`dirname ${galaxy_dir}`

fbname=$(basename "$infile" .dat)
fname=$(basename "$infile")
dname=$(dirname $infile)
new_name=$dname"/"$fbname"_files/"$fname

module unload pgi
module load gcc
${tools_dir}/Frontend_reader/GenericIOPrint $new_name > $outfile
