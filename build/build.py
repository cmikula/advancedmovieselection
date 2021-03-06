#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 17.04.2012

@author: cmikula

Compiling python plugin and create ipk.

The source code will exported from svn server to plugin path.

Required Packages for building with dreambox:
* subversion_1.7.1_mipsel.ipk
* python-compile_2.6.7-ml8.3_mipsel.ipk
* python-compiler_2.6.7-ml8.3_mipsel.ipk

To build the code always use the same python version as the device has installed.
* Currently used version is 2.6.7 but 2.6.6 can be used

usage:

start building the installer package use command line

> python build.py

this command exports the trunk from svn server and builds the package in the current python script location.

use command line parameters to export other svn locations
-s or --svn       # specifies the subversion repository path
-d or --deploy    # specifies the output path for the ipk file
-b or --build     # specifies the build path for the ipk file
-t or --package   # specifies the package type (ipk - deb - ipk,deb - all)

for example: export the tag version 2.6.1 and the ipk should stored to location /media/net/hdd1/enigma/deploy/ams/

> python build.py -s tags/v2.6.1 -d /media/net/hdd1/enigma/deploy/ams

'''

import py_compile
import os, shutil, subprocess, time
from tarfile import TarFile
from arfile import ArFile
import sys, platform 
from datetime import date

print "sys.version:\t", sys.version
print "sys.platform:\t", sys.platform
print "platform:\t", platform.platform()

def path_join(path, *paths):
    p = os.path.join(path, *paths).replace('\\', '/')
    return p

py_version = 0 
# checking python version
if (sys.version_info < (2, 6, 99) and sys.version_info > (2, 6, 0)):
    # sys.stderr.write("You need python 2.6.6 to 2.6.8 to build package compiled for dream multimedia devices\n") 
    ARCH = "mipsel"
    py_version = 2.6

if (sys.version_info < (2, 7, 99) and sys.version_info > (2, 7, 0)):
    # sys.stderr.write("You need python 2.7 to build package compiled for opendreambox-2.0.0\n") 
    ARCH = "mips32el"
    py_version = 2.7

PACKAGE_TYPE = "ipk"
BUILD_PATH = "deploy/build"
DEPLOY_PATH = "deploy"
CURRENT_PATH = os.getcwd()

PLUGIN_NAME = "AdvancedMovieSelection"
PLUGIN_PATH = "/usr/lib/enigma2/python/Plugins/Extensions/"
COMPONENTS_PATH = "/usr/lib/enigma2/python/Components"

PLUGIN = path_join(PLUGIN_PATH, PLUGIN_NAME)

PLUGIN_VERSION_FILE = path_join(PLUGIN, "Version.py") 
PLUGIN_HASH_FILE = path_join(PLUGIN, "md5sums") 

PACKAGE_PREFIX = "enigma2-plugin-extensions"
PACKAGE = "%s-%s" % (PACKAGE_PREFIX, PLUGIN_NAME.lower())
PACKAGE_DESCRIPTION = "Advanced Movie Selection for Enigma2"  # "Erweiterte Filmauswahl"
PACKAGE_ARCHITECTURE = ARCH
PACKAGE_SECTION = "extra"
PACKAGE_PRIORITY = "optional"
PACKAGE_MAINTAINER = "JackDaniel, cmikula"
PACKAGE_HOMEPAGE = "http://www.i-have-a-dreambox.com"
PACKAGE_DEPENDS = "kernel-module-isofs, kernel-module-udf, python-json"  # TODO: check working enigma version
PACKAGE_SOURCE = "https://svn.code.sf.net/p/advancedmovieselection/code"

SVN_REPOSITORY_EXPORT = "svn://svn.code.sf.net/p/advancedmovieselection/code/trunk/src"

# recommended packages
PACKAGE_RECOMENDS = None

CONTROL_CONFFILES = ()

LIBRARY_SOURCES = ()#("Source/ServiceProvider.py", "Source/CueSheetSupport.py", "Source/ServiceUtils.py", "Source/EventInformationTable.py", "Source/EpgListExtension.py", "Source/ISOInfo.py")

POSTINST = "#!/bin/sh\n\
echo \"* plugin installed successfully *\"\n\
echo \"* for questions visit: *\"\n\
echo \"* www.i-have-a-dreambox.com *\"\n\
echo \"* ATTENTION *\"\n\
echo \"* E2 restart is required *\"\n\
\n\
exit 0\n"

PREINST = "#!/bin/sh\n\
#created by mod ipkg-build from Erim\n\
\tFREEsize=`df -k /usr/ | grep [0-9]% | tr -s \" \" | cut -d \" \" -f 4`\n\
if [ \"2040\" -gt \"$FREEsize\" ]; then\n\
\techo Paketsize 2040kb tis to big for your Flashsize \"$FREEsize\"kb\n\
\techo Abort Installation\n\
\tkillall -9 ipkg install 2> /dev/null\n\
\tkillall -9 opkg install 2> /dev/null\n\
\t#rm -r /tmp/opkg* 2> /dev/null\n\
\t#rm -r /tmp/ipkg* 2> /dev/null\n\
fi\n\
exit 0\n"

POSTRM = "#!/bin/sh\n\
\n\
if [ $1 = \"remove\" ]; then\n\
    echo \"* POSTRM: deleting AdvancedMovieSelection\"\n\
    rm -rf /usr/lib/enigma2/python/Plugins/Extensions/AdvancedMovieSelection/\n\
    rm -f /usr/lib/enigma2/python/Components/Renderer/AdvancedMovieSelectionImageRenderer.py*\n\
fi\n\
\n\
exit 0\n"

# create dictionary of branding strings
branding_info = {}

def genBrandingInfo(package_revision=None):
    svn_info = ["svn", "info", SVN_REPOSITORY_EXPORT]
    proc = subprocess.Popen(svn_info, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc.wait()
    out = proc.stdout.read()
    err = proc.stderr.read().replace("\r\n", "")
    proc.stdout.close()
    proc.stderr.close()
    if err:
        raise Exception(err)
    for line in out.split("\r\n"):
        if line.startswith("Last Changed Rev:") or line.startswith("Letzte geänderte Rev:"):
            print line
            branding_info['svn_revision'] = line.strip().split(' ')[-1]
            break
    # checking svn revision, we can not update the version file without this info
    if not branding_info.has_key('svn_revision'):
        raise Exception("error getting last changed revision from svn server")

    # read back currently control revision
    control_path = path_join(BUILD_PATH, "CONTROL", "control")
    current_date = date.today().strftime("%Y%m%d")
    
    if os.path.exists(control_path) and package_revision is None:
        control = open(control_path, 'rb')
        for line in control.readlines():
            if line.startswith("Version:"):
                revs = line.strip().rsplit('-')
                if revs and revs[-1]:
                    if current_date == revs[-2]:
                        package_revision = int(revs[-1][1:])
                        package_revision += 1
                    break
    
    if package_revision is None:
        package_revision = 0

def updateVersionFile():
    version_file = open(PLUGIN_VERSION_FILE, 'rb')
    version = version_file.readlines()
    version_file.close()
    new_version = []
    for index, item in enumerate(version):
        new_version.append(item)
        line = item.strip()
        if len(line) == 0:
            continue
        if line[0:1] in ['#']:
            continue
        key, value = [s.strip() for s in line.split('=', 1)]
        branding_info[key] = value.replace("\"", "")
        if line.startswith("__version__") and branding_info.has_key('svn_revision'):
            oe_version = branding_info.get("__oe__")
            if oe_version:
                branding_info["__version__"] = branding_info["__version__"] + "-" + branding_info["__oe__"]
            print "write new version file, for revision", branding_info['svn_revision']
            new_version.append("__date__ = \"" + date.today().strftime("%Y.%m.%d") + "\"\r\n")
            new_version.append("__branch__ = \"" + branding_info["__branch__"] + "\"\r\n")
            new_version.append("__revision__ = \"" + branding_info['svn_revision'] + "\"\r\n")
            new_version.append("__build_version__ = \"%s\"\r\n" % sys.version)
            new_version.append("__build_platform__ = \"%s\"\r\n" % sys.platform)
            version_file = open(PLUGIN_VERSION_FILE, 'wb')
            version_file.writelines(new_version)
            version_file.close()
            break

    current_date = date.today().strftime("%Y%m%d")
    branding_info['version'] = "%s-%s" % (branding_info["__version__"], branding_info['svn_revision'])
    branding_info['file_version'] = "%s-%s-r%s" % (branding_info["__version__"], current_date, branding_info['svn_revision'])
    branding_info['ipkg_name'] = "%s_%s_%s.%s" % (PACKAGE, branding_info['file_version'], PACKAGE_ARCHITECTURE, PACKAGE_TYPE)

def makeTarGz(folder_name, tar_name):
    import tarfile
    tar = tarfile.open(tar_name, 'w:gz')
    tar.add(folder_name)
    tar.close()

def clearPluginPath():
    print "clear plugin path", PLUGIN
    if os.path.exists(PLUGIN):
        shutil.rmtree(PLUGIN)
        # prevent win 8 io error
        time.sleep(0)

    print "clear path:", COMPONENTS_PATH
    if os.path.exists(COMPONENTS_PATH):
        shutil.rmtree(COMPONENTS_PATH)
        # prevent win 8 io error
        time.sleep(0)

def createControl(control_path="."):
    data = []
    data.append("Package: %s" % (PACKAGE))
    data.append("Version: %s" % (branding_info['version']))
    data.append("Description: %s" % (PACKAGE_DESCRIPTION))
    data.append("Section: %s" % (PACKAGE_SECTION))
    data.append("Priority: %s" % (PACKAGE_PRIORITY))
    data.append("Maintainer: %s" % (PACKAGE_MAINTAINER)) 
    data.append("Architecture: %s" % (PACKAGE_ARCHITECTURE))
    data.append("Homepage: %s" % (PACKAGE_HOMEPAGE))
    data.append("Depends: %s" % (PACKAGE_DEPENDS))
    data.append("Source: %s" % (PACKAGE_SOURCE))
    if PACKAGE_RECOMENDS:
        data.append("Recommends: %s" % (PACKAGE_RECOMENDS))
    size = getDirSize(PLUGIN)
    data.append("Installed-Size: " + str(int(size / 1024.0)))

    data[-1] += "\n" # finally append newline
    file_name = path_join(control_path, "control")
    f = open(file_name, 'wb')
    f.write("\n".join(data))
    f.close()

def createConfFiles(control_path="."):
    file_name = path_join(control_path, "conffiles")
    if len(CONTROL_CONFFILES) > 0:
        f = open(file_name, 'wb')
        f.write("\n".join(CONTROL_CONFFILES))
        f.close()

def createPreInst(control_path="."):
    file_name = path_join(control_path, "preinst")
    f = open(file_name, 'wb')
    f.write(PREINST)
    f.close()

def createPostInst(control_path="."):
    file_name = path_join(control_path, "postinst")
    f = open(file_name, 'wb')
    f.write(POSTINST)
    f.close()

def createPreRM(control_path="."):
    file_name = path_join(control_path, "prerm")
    # f = open(file_name, 'wb')
    # f.close()

def createPostRM(control_path="."):
    file_name = path_join(control_path, "postrm")
    f = open(file_name, 'wb')
    f.write(POSTRM)
    f.close()

def createDebianBinary():
    file_name = "debian-binary"
    f = open(file_name, 'wb')
    f.write("2.0\n")  # 
    f.close()

def tar_filter(tarinfo):
    tarinfo.uid = tarinfo.gid = 0
    tarinfo.uname = tarinfo.gname = "root"
    if not tarinfo.isdir():
        tarinfo.mode = int('755', 8) 
    else: 
        tarinfo.mode = int('755', 8)
    return tarinfo

def getDirSize(path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.exists(fp):
                total_size += os.path.getsize(fp)

    return total_size   # in megabytes

def createPluginStructure():
    global BUILD_PATH
    if os.path.exists(BUILD_PATH):
        shutil.rmtree(BUILD_PATH)
        # prevent win 8 io error
        time.sleep(1)
    
    if not os.path.exists(BUILD_PATH):
        os.makedirs(BUILD_PATH)
    os.chdir(BUILD_PATH)

    BUILD_PATH = os.getcwd()
    
    control_path = path_join(BUILD_PATH, "CONTROL")
    os.mkdir(control_path)
    shutil.move(PLUGIN_HASH_FILE, path_join(BUILD_PATH, "CONTROL"))
    createControl(control_path)
    #createConfFiles(control_path)
    #createPreInst(control_path)
    #createPostInst(control_path)
    #createPreRM(control_path)
    createPostRM(control_path)
    createDebianBinary()

    native_tar = False    

    if not native_tar:
        tar = TarFile.open("control.tar.gz", "w:gz")
        tar.add("CONTROL", ".", filter=tar_filter)
        tar.close()
        
        tar = TarFile.open("data.tar.gz", "w:gz")
        tar.add(PLUGIN)
        tar.add(COMPONENTS_PATH)
        tar.close()

    # tar_name = path_join(BUILD_PATH, "control.tar.gz")
    # os.chdir(path_join(BUILD_PATH, "CONTROL"))
    # os.system("chmod 755 *")
    # makeTarGz(".", tar_name)
    # os.chdir(BUILD_PATH)

    # tar_name = path_join(BUILD_PATH, "data.tar.gz")
    # makeTarGz(PLUGIN, tar_name)
    
    if native_tar:
        os.system("chmod 755 CONTROL/*")
        cmd = "tar -C CONTROL -czf control.tar.gz ."
        os.system("chmod 755 CONTROL/*")
        os.system(cmd)
    
        cmd = "tar -C . -czf data.tar.gz %s" % (PLUGIN)
        os.system(cmd)

def createIPKG():
    archiveFile = ArFile()
    debian_tar = path_join(BUILD_PATH, "debian-binary")
    archiveFile.files.append(debian_tar)
    control_tar = path_join(BUILD_PATH, "control.tar.gz")
    archiveFile.files.append(control_tar)
    data_tar = path_join(BUILD_PATH, "data.tar.gz")
    archiveFile.files.append(data_tar)
    
    native_ar = False
    
    if not native_ar:
        f = open(branding_info['ipkg_name'], 'wb')
        f.write(archiveFile.packed())
        f.close()
    
    if native_ar:
        cmd = "../ar -r %s %s %s %s" % (branding_info['ipkg_name'] + "a", "debian-binary", "data.tar.gz", "control.tar.gz")
        os.system(cmd)

def moveToDeploy():
    os.chdir(CURRENT_PATH)
    if not os.path.exists(DEPLOY_PATH):
        os.makedirs(DEPLOY_PATH)
    src = path_join(BUILD_PATH, branding_info['ipkg_name'])
    dst = path_join(DEPLOY_PATH, branding_info['ipkg_name'])
    shutil.move(src, dst)
    return dst

def cleanup():
    if os.path.exists(BUILD_PATH):
        shutil.rmtree(BUILD_PATH)

    clean = path_join(BUILD_PATH, "control.tar.gz")
    if os.path.exists(clean):
        os.remove(clean)

    clean = path_join(BUILD_PATH, "data.tar.gz")
    if os.path.exists(clean):
        os.remove(clean)
    
    clean = path_join(BUILD_PATH, "debian-binary")
    if os.path.exists(clean):
        os.remove(clean)

def exportSVNRepository():
    cmd = "svn export %s %s" % (SVN_REPOSITORY_EXPORT.replace("src", "Components"), COMPONENTS_PATH)
    exit_code = os.system(cmd)
    if exit_code != 0:
        raise Exception("error exporting sources from svn server")

    cmd = "svn export %s %s" % (SVN_REPOSITORY_EXPORT, PLUGIN)
    exit_code = os.system(cmd)
    if exit_code != 0:
        raise Exception("error exporting sources from svn server")

def compilePlugin():
    # compileall.compile_dir(PLUGIN, force=1)
    for lib in LIBRARY_SOURCES:
        # Not supported in python26
        # compileall.compile_file(path_join(PLUGIN, lib), force=1)
        py_compile.compile(path_join(PLUGIN, lib), None, None, True)

def removeLibrarySources():
    for lib in LIBRARY_SOURCES:
        library = path_join(PLUGIN, lib)
        if os.path.exists(library):
            print "removing library", library
            os.remove(library)
        else:
            print "library not exists", library

def applyUserSettings():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-p", "--deploy", dest="deploypath", help="path to deploy")
    parser.add_option("-s", "--svn", dest="repository", help="repository location")  # , default="trunk")
    parser.add_option("-b", "--build", dest="build_path", help="build location")
    parser.add_option("-a", "--arch", dest="architecture", help="pakage architecture")
    parser.add_option("-t", "--package_type", dest="package_type", help="package type")
    parser.add_option("-d", "--depends", dest="depends", help="depends")
    
    global PACKAGE_DEPENDS
    global PACKAGE_ARCHITECTURE
    (options, args) = parser.parse_args()
    if options.deploypath:
        global DEPLOY_PATH
        DEPLOY_PATH = options.deploypath
        print "set deploy path to:", DEPLOY_PATH
    if options.repository:
        global SVN_REPOSITORY_EXPORT
        branding_info["__branch__"] = options.repository
        SVN_REPOSITORY_EXPORT = SVN_REPOSITORY_EXPORT.replace("trunk", options.repository)
        print "set repository export to:", SVN_REPOSITORY_EXPORT
    else:
        branding_info["__branch__"] = "trunk"
    if options.build_path:
        global BUILD_PATH
        BUILD_PATH = options.build_path
        print "set build path to", BUILD_PATH
    if options.architecture:
        PACKAGE_ARCHITECTURE = options.architecture
        print "set package architecture to", PACKAGE_ARCHITECTURE
    if options.depends:
        if PACKAGE_DEPENDS:
            PACKAGE_DEPENDS = PACKAGE_DEPENDS + ", " + options.depends
        else:
            PACKAGE_DEPENDS = options.depends
        print "set depends to", PACKAGE_DEPENDS
    if options.package_type:
        global PACKAGE_TYPE
        if options.package_type == 'deb':
            PACKAGE_TYPE = options.package_type
            PACKAGE_ARCHITECTURE = "all"
            print "set package type to", PACKAGE_TYPE

def checkingBuildOptions():
    sys.stdout.write("checking build options...")
    if py_version == 0:
        raise Exception("unrecognized python version!")
    
#    if py_version == 2.6:
#        if PACKAGE_ARCHITECTURE != "mipsel": 
#            raise Exception("python version with package version is not compatibel!")
#    if py_version == 2.7:
#        if PACKAGE_ARCHITECTURE != "mips32el": 
#            raise Exception("python version with package version is not compatibel!")
    
    if __debug__:
        raise Exception("Optimization is currently disabled! Start build file with python -O and try again...\n")
    
    print " pass!"

def listSourceFiles():
    l = []
    for (path, dirs, files) in os.walk(PLUGIN):
        for filename in files:
            if filename.endswith('.py'):
                f = path_join(path, filename)
                l.append(f)
    return l

def md5sum(filename):
    import hashlib
    md5 = hashlib.md5()
    with open(filename, 'rb') as f: 
        for chunk in iter(lambda: f.read(128 * md5.block_size), b''): 
            md5.update(chunk)
    return md5.hexdigest()

def createMD5Hashes():
    hash_file = open(PLUGIN_HASH_FILE, 'wb')
    sources = listSourceFiles()
    for filename in sources:
        hash_file.write(md5sum(filename) + '  ' + filename + '\r')
    for lib in LIBRARY_SOURCES:
        filename = path_join(PLUGIN, lib + 'o')
        hash_file.write(md5sum(filename) + '  ' + filename + '\r')
    hash_file.close()

def hashFromFile(filename):
    print "create hash for:", filename
    hash_file = open(filename + '.md5', 'wb')
    hash_file.write(md5sum(filename))
    hash_file.close()

def main():
    applyUserSettings()
    print "--- start building enigma2.%s package ---" % (PACKAGE_ARCHITECTURE)
    checkingBuildOptions()
    clearPluginPath()
    cleanup()
    genBrandingInfo()
    exportSVNRepository()
    updateVersionFile()
    compilePlugin()
    removeLibrarySources()
    createMD5Hashes()
    print "build package:", PLUGIN_NAME, branding_info['version']
    
    createPluginStructure()
    createIPKG()
    ipkg = moveToDeploy()
    hashFromFile(ipkg)
    print "build success:", branding_info['ipkg_name']
    print "stored in:", DEPLOY_PATH

if __name__ == '__main__':
    main()
