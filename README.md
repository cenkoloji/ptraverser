# ptraverser

Python based traverser.

## Introduction

This tool is developed for people who embrace terminal, dislike graphical tools as much as me(Cenk).
It allows users to dump the tree structure of a mds tree to terminal.

## MDS Python versions

It's tested with mdsplus version in tcvdata, lacs, and current stable branch of mdsplus (7.96-17).
MDS python interface has been improved in recent years, so with the mdsplus-stable, the speed is
significantly better.

## Capabilities and Limitations

* The ptraverser shows the "RECORD", and not the "DATA" of nodes. It basically shows what you'd see
  in traverser/jTraverser or what is returned by `getnci("PATH","RECORD")`.
* The tree nodes has many extra attributes, ptraverser only shows some of them.
* If a tree contains raw data, it may use a lot of memory, and output may be too large. For
  instance, don't use it to show data in a raw tree. If you want to see only the structure of such
  a tree, you can use `--wdata 0` (which will make it not even read the data for the nodes)
* It can show tags for each node, and something called "Alternative path". This is useful if there
  is multiple ways to access a node, due to tags set at different levels.
* If you want to traverse a tree progressively, use `--maxdepth,-m` option (`-m 1`), then at
  next run, you can traverse only in the node you want to see using `--startnode,-S` option
  (See examples)
* There is support for wildcards and regular expressions. Wildcards are very efficient as they are
  natively supported by mdsplus. For details on wildcard examples,
  see: https://mdsplus.org/index.php/Documentation:Users:Tree_syntax

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
./ptraverser.py -t atlas -S HARDWARE.TCPIP -f -m 1 --hide-onoff

# Traverse HARDWARE.TCPIP node of ATLAS tree, don't traverse in the nodes that are OFF
./ptraverser.py -t atlas -S HARDWARE.TCPIP --dont-traverse-off-nodes

# Traverse MEASUREMENTS node of ECRH tree for shot 65400
./ptraverser.py -t ecrh -S MEASUREMENTS -s 65400

# Traverse MEASUREMENTS node of ECRH tree, hide tag and alt-path fields, limit data field to 100 chars
./ptraverser.py -t ecrh -S MEASUREMENTS  --wtag 0 --walt 0 --wdata 100

# Traverse ATLAS tree, for wildcard pattern HARDWARE.TCPIP:DT_ECE_00*
./ptraverser.py -t atlas -w HARDWARE.TCPIP:DT_ECE_00*
./ptraverser.py -t atlas -S HARDWARE.TCPIP -w DT_ECE_00*  # Same result
./ptraverser.py -t atlas -w \\DT4G_ECE_00*                # Same result

# Show all nodes under atlas tree that has tag \DT196_*
ptraverser.py -t atlas -w \\DT196* -m 0

# Regex matching, experimental feature: It's much slower then wildcards
# Traverse MIX dtacqs and show nodes that match DECIM_* or I_START
ptraverser.py -t atlas -w HARDWARE.TCPIP:DT_MIX*:CHANNEL_*:* -m 0 -r "DECIM.*|I_START" -f 
ptraverser.py -t atlas -w HARDWARE.TCPIP:DT_MIX* -r "DECIM.*|I_START" -f
```

Example for progressive traversing into a tree using `--maxdepth,-m`
```shell
# Traverser atlas HARDWARE.TCPIP node only 1 level. This will reveal all dtacq nodes
./ptraverser.py -t atlas -S HARDWARE.TCPIP -m 1 -f --wusage 0 --wdata 0 --walt 0 --wtag 0

# Get the name from output of last command and traverse into specific dtacq node
./ptraverser.py -t atlas -S HARDWARE.TCPIP.DT_MIX_001
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
