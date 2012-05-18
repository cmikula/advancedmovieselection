"""Tools for AdvancedMoovieSelection

This tool copy or clear the short description from movie to tag location

Usage:

First parameter: cp copy or cl clear
Second parameter: directory path
"""


'''
Created on 20.02.2012

@author: cmikula
'''

META_TAGS = "/etc/enigma2/movietags"

import getopt
import os
import sys

def listAllMeta(root):
    list = []
    for (path, dirs, files) in os.walk(root):
        for filename in files:
            if filename.endswith('.ts.meta'):
                f = os.path.join(path, filename)
                list.append(f)
    return list


def copyTag(file):
    if os.path.exists(file):
        metafile = open(file, "r")
        sid = metafile.readline()
        title = metafile.readline()
        descr = metafile.readline()
        time = metafile.readline()
        oldtags = metafile.readline().rstrip()
        rest = metafile.read()
        metafile.close()
        tags = descr
        if tags != oldtags:
            metafile = open(file, "w")
            metafile.write("%s%s%s%s%s%s" %(sid, title, descr, time, tags, rest))
            metafile.close()
        return tags.rstrip("\r\n") 

def clearTag(file):
    if os.path.exists(file):
        metafile = open(file, "r")
        sid = metafile.readline()
        title = metafile.readline()
        descr = metafile.readline()
        time = metafile.readline()
        oldtags = metafile.readline().rstrip()
        rest = metafile.read()
        metafile.close()
        # clear tags
        tags = "\n"
        metafile = open(file, "w")
        metafile.write("%s%s%s%s%s%s" %(sid, title, descr, time, tags, rest))
        metafile.close()
        return oldtags.rstrip("\r\n") 

def loadTagsFile():
    try:
        file = open(META_TAGS)
        tags = [x.rstrip() for x in file]
        while "" in tags:
            tags.remove("")
        file.close()
    except Exception, e:
        print e
        tags = []
    return tags

def saveTagsFile(tags):
    file = open(META_TAGS, "w")
    file.write("\n".join(tags) + "\n")
    file.close()

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", ["help"])
    except getopt.error, msg:
        print msg
        print "for help use --help"
        sys.exit(2)
        
    for o, a in opts:
        if o in ("-h", "--help"):
            print __doc__
            sys.exit(0)

    if len(args) != 2:
        print __doc__
        sys.exit(0)
    
    do_copy = False
    do_clear = False
    tags = loadTagsFile()
    if args[0] in ("cp", "copy"):
        do_copy = True
    elif args[0] in ("cl", "clear"):
        do_clear = True
    else:
        print __doc__
        sys.exit(0)

    if not os.path.exists(args[1]):
        print __doc__
        sys.exit(0)
        
    meta_list = listAllMeta(args[1])
    for meta in meta_list:
        print meta 
        if do_copy:
            tag = copyTag(meta)
            if len(tag) > 4 and not tag in tags:
                tags.append(tag)
        elif do_clear:
            tag = clearTag(meta)
            if tag in tags:
                tags.remove(tag)

    saveTagsFile(tags)
    
if __name__ == '__main__':
    main()
