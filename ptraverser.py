#!/usr/bin/python
# -*- coding: utf-8 -*-

# Python program to traverse through tree and print information about nodes/tags/data

from __future__ import print_function  # For python3 compatibility

import sys
import traceback
import MDSplus

class IgnoreData(Exception): # Thrown if getdata=False in traverseTree
    pass

class IgnoreUsage(Exception): # Thrown if getusage=False in traverseTree
    pass

# NodeOutput object simply stores information about node, including some
# metadata used for output formatting (depth, islast, ischild). But the
# global output formatting parameters are kept out of this class, as they
# will be same for all instances
class NodeOutput(object):
    """MDSPlus node properties required for displaying information"""
    def __init__(self, name, fullpath, usage, tag, alt, data, depth, last, child, off):
        super(NodeOutput, self).__init__()
        self.name = name   # Node name without the path
        self.fullpath= fullpath  # Full path of the node
        self.usage=usage  # Node type (SIGNAL, STRUCTURE, ...)
        self.tag = tag
        self.alt = alt
        self.data = data
        self.depth = depth
        self.islast = last     # see lastnode argument of traverseTree
        self.ischild = child   # used for printing ":" or "." as delimiter
        self.off = off

    def node_str(self,printfullpath=False):
        """
            Return node portion of output

            Arguments:
            printfullpath -- Print full path instead of tree style
        """
        if printfullpath:
            return self.fullpath

        delimiter = ":"
        if self.ischild:
            delimiter = "."
        # Output for tree style display. prechars is the characters to print before node name
        # While printing last child, it should be a different character for prettier display
        prechars = "├─ "
        #prechars = "+- "
        if self.islast:
            prechars = "└─ "
            #prechars = "'- "
        result = "    "*self.depth + prechars + delimiter + self.name
        return result

def traverseTree(rootNode,
                 depth = 0,
                 parentFullPath = "",
                 parentpaths = [],
                 getdata = True,
                 getusage = True,
                 gettags = True,
                 output = [],
                 maxdepth = -1,
                 notraverseoff=False,
                 lastnode = False):
    """ Recursive function to traverse through a tree and print information about nodes

        Arguments:
        rootNode -- Name of this node
        depth -- Depth/level in tree, can be used to indent child nodes, and enforce maximum depth
        parentFullPath -- Path of parent, it's used to prevent costly getLocalPath calls
        parentpaths -- Other possible paths to parent node, including tags
        getdata -- If false, data will be set to "-". Used to prevent costly getData and replace calls
        getusage -- If false, usage will be set to UNKNOWN. Used to prevent costly getUsage calls
        gettags -- If false, tags and alt paths won't be calculated
        output -- List of NodeOutput objects, this is the main object that will be used by top level caller
        notraverseoff -- If true, It won't traverse deeper into nodes that are OFF
        lastnode -- true if it's last child/member of a node. internally used for output formatting
    """
    if depth > maxdepth and maxdepth > 0:
        return 0

    rootName = str(rootNode.getNodeName())

    tagstr = []

    if gettags:
        tags = rootNode.getTags()

        try:
            tags = list(tags)
        except TypeError:
            tags = []
        tagstr = [str(t) for t in tags]

    try:
        if not getdata:
            raise IgnoreData

        data = rootNode.getData().decompile()

        # Prevent data from being a multi line string by replacing EOL with \n
        # On different platforms, there was some issues with different EOL characters
        # Following covers all cases
        data = data.replace("\r\n","\\n")
        data = data.replace("\n\r","\\n")
        data = data.replace("\n","\\n")
        data = data.replace("\r","\\n")
    except:
        data = "-"



    delimiter = ":"
    ischild = rootNode.isChild()
    if ischild:
        delimiter = "."

    if parentFullPath=="":
        rootLocalPath = str(rootNode.getLocalPath())
    else:
        rootLocalPath = parentFullPath + delimiter + rootName

    # Dump path in error stream, this allows following progress of program and see where it is stuck.
    sys.stderr.flush()
    sys.stderr.write("\r" + rootLocalPath + " "*30)

    try:
        if not getusage:
            raise IgnoreUsage
        usage = rootNode.getUsage()
        usagestr = str(usage)
    except:
        usagestr = "UNKNOWN"

    altpaths = []
    if gettags:
        altpaths = [path + delimiter + rootName for path in parentpaths]

    isoff = not rootNode.isOn()

    # minpath = MDSplus.TdiExecute('GETNCI(' + rootLocalPath + ' ,"MINPATH")')  # Doesn't work on some mdsplus versions, throws mdsExceptions.TreeNOT_OPEN
    n = NodeOutput(name = rootName, fullpath=rootLocalPath , usage=usagestr, tag=str(tagstr), alt=str(altpaths), data=data, depth=depth, last = lastnode, child = ischild, off = isoff)

    output.append(n)

    if notraverseoff and isoff:
        return

    # This is where the recursion starts
    try:
        subnodes = rootNode.getDescendants()  # Includes both children and members

        if subnodes is None:  # Needed on some versions of mdsplus-python
            return

        for i in range(len(subnodes)):
            last = False
            if i == len(subnodes)-1:
                last = True
            nextnode = subnodes[i]

            traverseTree(rootNode=nextnode, depth=depth+1, getdata=getdata, getusage=getusage, gettags=gettags, parentFullPath=rootLocalPath, parentpaths=tagstr+altpaths, output=output, maxdepth=maxdepth, lastnode=last, notraverseoff=notraverseoff)
    except:
       traceback_string = traceback.format_exc()
       print(traceback_string,file=sys.stderr)

def main():

    import argparse
    parser = argparse.ArgumentParser(description='Traverse through a mdsplus tree and print information',
                                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-t','--tree', help="experiment tree to traverse", required=True)
    parser.add_argument('-S','--startnode', help="Top node to start traversing from", default='')
    parser.add_argument('-s','--shot', help="Shot number", type=int, default=-1)

    parser.add_argument('-m','--maxdepth', help="Maximum depth to traverse, default is infinite", type=int, default=-1)

    parser.add_argument('--dont-traverse-off-nodes', help="Do not traverse into a node if it's OFF", action="store_true")

    formatargs = parser.add_argument_group('Output formatting options. By default optimal width of each field will be dynamically calculated.'
                                           'Setting any width to 0 will remove the field from output')

    formatargs.add_argument('-f','--fullpaths', action='store_true',
                        help='print fullpaths of each node')

    formatargs.add_argument('--wnode', help="Width of node field", type=int, default=-1)
    formatargs.add_argument('--wusage', help="Width of usage field", type=int, default=-1)
    formatargs.add_argument('--wtag', help="Width of tag field", type=int, default=-1)
    formatargs.add_argument('--walt', help="Width of alternate path field", type=int, default=-1)
    formatargs.add_argument('--wdata', help="Width of data field", type=int, default=-1)
    formatargs.add_argument('--hide-onoff', help="Don't show on-off status", action='store_true')

    args = parser.parse_args()
    #print(args)

    experiment = args.tree
    shot = args.shot

    node = "\\TOP"

    if args.startnode != "":
        node = "\\TOP." + args.startnode

    try:
        tree = MDSplus.Tree(experiment, shot)
    except:
        print("Cannot open tree: {}, shot: {}, node: {}".format(experiment, shot, node))
        traceback_string = traceback.format_exc()
        print(traceback_string,file=sys.stderr)
        sys.exit(0);

    startNode = tree.getNode(node)

    getdata = False if args.wdata==0 else True
    getusage = False if args.wusage==0 else True
    gettags = False if args.wtag==0 and args.walt==0 else True

    results = []
    traverseTree(rootNode=startNode, getdata=getdata, getusage=getusage, gettags=gettags, output=results, maxdepth=args.maxdepth, notraverseoff=args.dont_traverse_off_nodes);

    # Calculate maximum possible lengths in each field
    wmaxnode = max([len(x.node_str(args.fullpaths)) for x in results])
    wmaxusage = max([len(x.usage) for x in results])
    wmaxtag = max([len(x.tag) for x in results])
    wmaxalt = max([len(x.alt) for x in results])
    wmaxdata = max([len(x.data) for x in results])

    wnode = args.wnode
    if wnode != 0:
        wnode = max([wmaxnode + 5,wnode,len("Node")+2])

    wusage = args.wusage
    if wusage != 0:
        wusage = max([wmaxusage + 5,wusage,len("Tags")+2])

    wtag = args.wtag
    if wtag != 0:
        wtag = max([wmaxtag + 5,wtag,len("Tags")+2])

    walt = args.walt
    if walt != 0:
        walt = max([wmaxalt + 5,walt,len("Alternative Paths")+2])

    wdata = args.wdata
    if wdata != 0:
        wdata = wmaxdata if wdata == -1 else wdata

    onoffformat = "" if args.hide_onoff else "{off:4s}"
    nodeformat= "" if wnode==0 else "{node:{lnode}s}"
    usageformat= "" if wusage==0 else "{usage:{lusage}s}"
    tagformat=  "" if wtag==0 else"{tag:{ltag}s}"
    altformat= "" if walt==0 else "{alt:{lalt}s}"
    dataformat= "" if wdata==0 else "{data}"

    formatstr= onoffformat + nodeformat + usageformat + tagformat + altformat + dataformat

    sys.stderr.write("\n\n")

    print(formatstr.format(off="OFF",node="Node", usage="Usage", tag="Tags", alt="Alternative Paths", data="Data", lnode=wnode, lusage=wusage, ltag=wtag , lalt=walt))
    print(formatstr.format(off="===",node="="*(wnode-2), usage="="*(wusage-2), tag="="*(wtag-2), alt="="*(walt-2), data="="*(wdata-2), lnode=wnode, lusage=wusage, ltag=wtag, lalt=walt))

    # This is a hack
    # There are unicode characters in tree style formatting, and they seem to take less character space
    # Thus we need to add extra spaces
    if not args.fullpaths:
        wnode += 4

    for i in range(len(results)):
        n = results[i]
        nodestr = n.node_str(printfullpath=args.fullpaths)
        if len(n.data)> wdata:
            data = n.data[0:wdata] + "..."
        else:
            data = n.data
        offstr = "OFF" if n.off  else ""
        print(formatstr.format(off=offstr, node=nodestr, usage=n.usage, tag=n.tag, alt=n.alt, data=data, lnode=wnode, lusage=wusage, ltag=wtag, lalt=walt))

if __name__ == "__main__":
    main()
