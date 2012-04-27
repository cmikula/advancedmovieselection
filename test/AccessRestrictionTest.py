'''
Created on 25.04.2012

@author: cmikula
'''

import os
from AccessRestriction import accessRestriction as restriction

path = "./tmp/"


class ServiceRef:
    def __init__(self, path):
        self.path = path
    
    def getPath(self):
        return self.path

    def getName(self):
        return self.path


def createFile(name):
    f = open(os.path.join(path, name), "wb")
    f.close()

def createTestFiles():
    createFile("access_test.mkv")

def main():
    if not os.path.exists(path):
        os.makedirs(path)

    createTestFiles()
    service_file = os.path.join(path, "access_test.ts")
    print restriction.isAccessible(("VSR-12",))
    restriction.setToService(service_file, "VSR-0")
    restriction.setToService(service_file, "VSR-12")
    restriction.setToService(service_file, "VSR-19")
    restriction.setToService(service_file, "VSR-19", True)


if __name__ == '__main__':
    main()
