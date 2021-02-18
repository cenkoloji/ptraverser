# ptraverser

Python based traverser.

## Introduction

This tool is developed for people who embrace terminal, dislike graphical tools as much as me(Cenk).
It allows users to dump the tree structure of a mds tree to terminal.

## MDS Python versions

It's tested with mdsplus version in tcvdata, lacs, and current stable branch of mdsplus (7.96-17).
MDS python interface has been improved in recent years, so with the mdsplus-stable, the speed is
significantly better.

## Examples

Common examples
```shell

# Show help
./ptraverser.py -h 

./ptraverser.py -t ecrh

# Traverse measurements node of ECRH tree
./ptraverser.py -t ecrh -S MEASUREMENTS

# Traverse HARDWARE.TCPIP node of ATLAS tree, show full node paths
./ptraverser.py -t atlas -S HARDWARE.TCPIP -f

# Traverse HARDWARE.TCPIP node of ATLAS tree, maximum depth 1
./ptraverser.py -t atlas -S HARDWARE.TCPIP -f -m 1

# Traverse HARDWARE.TCPIP node of ATLAS tree, maximum depth 1, don't show ON/OFF status
./ptraverser.py -t atlas -S HARDWARE.TCPIP -f -m 1

# Traverse MEASUREMENTS node of ECRH tree for shot 65400
./ptraverser.py -t ecrh -S MEASUREMENTS -s 65400

# Traverse MEASUREMENTS node of ECRH tree, hide tag and alt-path fields, limit data field to 100 chars
./ptraverser.py -t ecrh -S MEASUREMENTS  --wtag 0 --walt 0 --wdata 100
```

Example for comparing tree structure/data from 2 shots. 
```shell
# Compare everything including ON/OFF status, data, tags...
./ptraverser.py -t ecrh -s 65400 > ecrh65400.txt
./ptraverser.py -t ecrh -s 65401 > ecrh65401.txt
vimdiff -c 'set diffopt+=iwhite' ecrh65400.txt ecrh65401.txt  # vimdiff ignoring white space changes
diff --ignore-space-change ecrh65400.txt ecrh65401.txt  # diff, ignoreing white space change

# Compare only tree structure, ignore data, tags, on-off status, alternative paths 
./ptraverser.py -t ecrh -s 65400 --hide-onoff --walt 0 --wtag 0 --wdata 0 > ecrh65400_struct.txt
./ptraverser.py -t ecrh -s 65401 --hide-onoff --walt 0 --wtag 0 --wdata 0 > ecrh65401_struct.txt
vimdiff -c 'set diffopt+=iwhite' ecrh65400_struct.txt ecrh65401_struct.txt
diff --ignore-space-change ecrh65400_struct.txt ecrh65401_struct.txt
```

Example bash loop for running all tcv trees and putting them in folder with todays date:
```shell
datstr=$(date +%Y%m%d)
mkdir -p $datstr
for tree in atlas base diagz diag_act ecrh hybrid magnetics manual power results vsystem ;
do
  ptraverser.py -t ${tree} -f > ${datstr}/${tree}.txt
done
```

## Issues
- If the tree is remote, node.getUsage() raises exception, so the usage will be set to UNKNOWN
