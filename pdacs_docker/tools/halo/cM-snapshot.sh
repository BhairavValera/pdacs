#!/bin/bash -l

omega_m=$(sqlite3 $1 "select value from metadata where name='Omega_m';")

omega_b=$(sqlite3 $1 "select value from metadata where name='Omega_bar';")

n_s=$(sqlite3 $1 "select value from metadata where name='n_s';")

w=$(sqlite3 $1 "select value from metadata where name='w_de';")

sigma_8=$(sqlite3 $1 "select value from metadata where name='Sigma_8';")

a=$(sqlite3 $1 "select value from metadata where name='a_val';")

hubble=$(sqlite3 $1 "select value from metadata where name='hubble';")

echo "a is $a"
z=`echo "scale=6;(1/$a)-(1)" | bc`
echo "red shift is $z"

hsqr=`echo "scale=6;($hubble)*($hubble)" | bc`
#echo "hsqr: $hsqr"
newomega=`echo "scale=6;($hsqr) * ($omega_m)" | bc`
#echo "Omega_m: $newomega"

tmp=`python -c "print float('$omega_b')"`
newomegab=`echo "scale=6;($hubble)*($hubble)*($tmp)" | bc`

echo $a $newomega $newomegab $n_s $w $sigma_8 $z | tr ' ' \\n > cm.local.param.ini

echo "0.1539 0.0231 0.9468 0.816 0.8161
0.1460 0.0227 0.8952 0.758 0.8548
0.1324 0.0235 0.9984 0.874 0.8484
0.1381 0.0227 0.9339 1.087 0.7000
0.1358 0.0216 0.9726 1.242 0.8226
0.1516 0.0229 0.9145 1.223 0.6705
0.1268 0.0223 0.9210 0.700 0.7474
0.1448 0.0223 0.9855 1.203 0.8090
0.1392 0.0234 0.9790 0.739 0.6692
0.1403 0.0218 0.8565 0.990 0.7556
0.1437 0.0234 0.8823 1.126 0.7276
0.1223 0.0225 1.0048 0.971 0.6271
0.1482 0.0221 0.9597 0.855 0.6508
0.1471 0.0233 1.0306 1.010 0.7075
0.1415 0.0230 1.0177 1.281 0.7692
0.1245 0.0218 0.9403 1.145 0.7437
0.1426 0.0215 0.9274 0.893 0.6865
0.1313 0.0216 0.8887 1.029 0.6440
0.1279 0.0232 0.8629 1.184 0.6159
0.1290 0.0220 1.0242 0.797 0.7972
0.1335 0.0221 1.0371 1.165 0.6563
0.1505 0.0225 1.0500 1.107 0.7678
0.1211 0.0220 0.9016 1.261 0.6664
0.1302 0.0226 0.9532 1.300 0.6644
0.1494 0.0217 1.0113 0.719 0.7398
0.1347 0.0232 0.9081 0.952 0.7995
0.1369 0.0224 0.8500 0.836 0.7111
0.1527 0.0222 0.8694 0.932 0.8068
0.1256 0.0228 1.0435 0.913 0.7087
0.1234 0.0230 0.8758 0.777 0.6739
0.1550 0.0219 0.9919 1.068 0.7041
0.1200 0.0229 0.9661 1.048 0.7556
0.1399 0.0225 1.0407 1.147 0.8645
0.1497 0.0227 0.9239 1.000 0.8734
0.1485 0.0221 0.9604 0.853 0.8822
0.1216 0.0233 0.9387 0.706 0.8911
0.1495 0.0228 1.0233 1.294 0.9000" > design.dat

#echo initial.output
#echo $6
# Run the actual program.
echo /global/project/projectdirs/hacc/PDACS/cm/cM cm.local.param.ini cm.initial.output
/global/project/projectdirs/hacc/PDACS/cm/cM cm.local.param.ini cm.initial.output

#grep -v '^#' initial.output > stripped.output
( echo "#logmass conc" ; cat cm.initial.output ) > initial.output && rm cm.initial.output
sed '/^#/ d' initial.output | tr ' ' '\t' >$2
