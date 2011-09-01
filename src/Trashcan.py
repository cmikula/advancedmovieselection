#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Copyright (C) 2011 cmikula

Trashcan support for Advanced Movie Selection

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

import os, glob, shutil
from ServiceProvider import eServiceReferenceTrash

TRASH_NAME = ".trash"

class Trashcan:
    @staticmethod
    def listAllMovies(root):
        list = []
        for (path, dirs, files) in os.walk(root):
            # This path detection is only for trashed DVD structures
            if path.endswith(TRASH_NAME):
                service = eServiceReferenceTrash(path)
                list.append(service)

            for filename in files:
                if filename.endswith(TRASH_NAME):
                    service = eServiceReferenceTrash(os.path.join(path, filename))
                    list.append(service)
        return list

    @staticmethod
    def listMovies(path):
        list = []
        for filename in glob.glob(os.path.join(path, "*" + TRASH_NAME)):
            service = eServiceReferenceTrash(filename)
            list.append(service)
        return list
    
    @staticmethod
    def trash(filename):
        print "trash: ", filename
        os.rename(filename, filename + TRASH_NAME)
    
    @staticmethod
    def restore(filename):
        print "restore: ", filename
        os.rename(filename, filename.replace(TRASH_NAME, ""))
    
    @staticmethod
    def delete(filename):
        movie_ext = ["gm", "sc", "ap", "cuts"]
        print "delete: ", filename
        #path = os.path.split(filename)[0]
        original_name = filename.replace(TRASH_NAME, "")
        if os.path.isfile(filename):
            file_extension = os.path.splitext(original_name)[-1]
            eit = os.path.splitext(original_name)[0] + ".eit"
            jpg = os.path.splitext(original_name)[0] + ".jpg"
        else:
            file_extension = ""
            eit = original_name + ".eit"
            jpg = original_name + ".jpg"

        if file_extension == ".ts":
            movie_ext.append("meta")
        else:
            movie_ext.append("ts.meta")
        for ext in movie_ext:
            to_delete = original_name + "." + ext
            if os.path.exists(to_delete):
                os.remove(to_delete)
    
        if os.path.exists(jpg):
            os.remove(jpg)

        if os.path.exists(eit):
            os.remove(eit)

        if os.path.exists(filename):
            if os.path.isfile(filename):
                os.remove(filename)
            else:
                shutil.rmtree(filename)
