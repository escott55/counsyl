#!/usr/bin/python

import os, sys
import subprocess
import glob

######################################################################
# filesInDir
######################################################################
def filesInDir( path, filetype, prefix=None ):
    filelist = []
    if prefix is not None :
        filelist = glob.glob( os.path.join( path, "%s*%s" %(prefix, filetype)))
    else :
        filelist = glob.glob( os.path.join( path, "*"+filetype ) )
    if filetype[-5:] == "fastq" :
        prefixdict = {}
        for file in sorted(filelist) :
            prefix = getBasename( file )
            if not prefixdict.has_key(prefix[:-3]) :
                prefixdict[prefix[:-3]] = []
            prefixdict[prefix[:-3]].append( file )
        return prefixdict.values()
    return filelist
# End filesInDir

######################################################################
# getBasename
######################################################################
def getBasename( originalfilename ) :
    filepath, filename = os.path.split( originalfilename )
    #print "path",filepath,"name", filename
    if originalfilename[-3:] == ".gz" :
        basename, suffix = os.path.splitext( filename[:-3] )
        #print "Base:", basename, "Suff:",suffix
    else :
        basename, suffix = os.path.splitext( filename )
    return filepath, basename, suffix
# End getBasename

