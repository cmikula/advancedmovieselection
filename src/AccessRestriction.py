#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Copyright (C) 2012 cmikula

In case of reuse of this source code please do not remove this copyright.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    For more information on the GNU General Public License see:
    <http://www.gnu.org/licenses/>.

For example, if you distribute copies of such a program, whether gratis or for a fee, you 
must pass on to the recipients the same freedoms that you received. You must make sure 
that they, too, receive or can get the source code. And you must show them these terms so they know their rights.
'''
import os

FSK = ["FSK-0", "FSK-6", "FSK-12", "FSK-16", "FSK-18"]

class AccessRestriction:
    def __init__(self):
        self.access = 18
    
    def setAccess(self, access):
        print "set FSK:", access
        self.access = int(access)

    def getAccess(self):
        return self.access
    
    def isAccessible(self, tags):
        if not tags:
            return True
        for tag in tags:
            if tag.startswith("FSK-"):
                fsk = int(tag[4:])
                if fsk > self.access:
                    return False
        return True

    def setToService(self, file_name, access, clear_access=False):
        try:
            meta_file = file_name.endswith(".ts") and file_name + ".meta" or file_name + ".ts.meta"  
            if not clear_access:
                print "Set %s to %s"%(access, meta_file)
            else:
                print "Clear FSK to", meta_file
            if os.path.exists(meta_file):
                metafile = open(meta_file, "r")
                sid = metafile.readline().rstrip()
                title = metafile.readline().rstrip()
                descr = metafile.readline().rstrip()
                time = metafile.readline().rstrip()
                tags = metafile.readline().rstrip()
                rest = metafile.read()
                metafile.close()
            else:
                sid = ""
                title = os.path.basename(os.path.splitext(file_name)[0])
                descr = ""
                time = ""
                tags = ""
                rest = ""
    
            tag_list = tags.split()
            new_tags = []
            for t in tag_list:
                if not t.startswith("FSK"):
                    new_tags.append(t)
            
            if not clear_access:
                new_tags.insert(0, access)
            tags = " ".join(new_tags)
                    
            metafile = open(meta_file, "w")
            metafile.write("%s\n%s\n%s\n%s\n%s\n%s" % (sid, title, descr, time, tags, rest))
            metafile.close()
        except Exception, e:
            print e

accessRestriction = AccessRestriction();
