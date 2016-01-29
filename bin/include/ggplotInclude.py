#!/usr/bin/python

#from ggplot import *

import os, sys

import rpy2.robjects as robjects
import pandas.rpy.common as com
from rpy2.robjects.packages import importr
from rpy2.robjects.lib import grid
from rpy2.robjects.lib import ggplot2

r = robjects.r
#rprint = robjects.globalenv.get("print")
#http://stackoverflow.com/questions/13649562/rpy2-importr-failing-with-xts-and-quantmod
rstats = importr('stats', robject_translations = {"format.perc": "format_perc2"})
grdevices = importr('grDevices')
#gtable = importr('gtable',on_conflict="warn")
#gridextra = importr('gridExtra')
rcolorbrewer = importr('RColorBrewer')
plyr = importr('plyr')
rbase = importr('base')
#round_any = plyr.round_any

class Blackhole(object):
    def write(self, string):
        pass
# END Blackhole

# Suppress output of spammy package loadings
stdout = sys.stdout
sys.stdout = Blackhole()

# Import Extra font to change plotting font families
rextrafont = importr('extrafont')
rextrafont.font_import( pattern="[C/c]omic", prompt=False )
rextrafont.font_import( pattern="[A/a]rial", prompt=False )
#print rextrafont.fonts()
sys.stdout = stdout

#head = robjects.r['head']
#summary = robjects.r['summary']

utils = importr('utils')

FONTFAM = "Arial"
#FONTFAM = "Comic Sans MS"
assert FONTFAM in rextrafont.fonts()

#ggplot2 = importr('ggplot2')

def fixRLevels( r_dataframe, column, tlevels ):
    replace = robjects.FactorVector( r_dataframe.rx2(column), 
                                    levels=robjects.StrVector(tlevels) )
    allcolumns = list(r_dataframe.colnames)
    allcolumns = [ x+"_old" if x == column else x for x in allcolumns]
    new_r_df = r_dataframe.cbind(replace)
    new_r_df.colnames = robjects.StrVector(allcolumns+[column])
    return new_r_df
# END fixRLevels 

# If you get that annoying AsIs round_any error you have to purge the data
# class of the columns that need rounding. I think this allows for on the fly
# manipulation of the values. Round any works by rounding floats to a specified
# degree. 
def fixRClasses( r_dataframe ):
    for col in r_dataframe :
        col.rclass = None
    return r_dataframe
# END fixRClasses

def makeLargePalette(ncols=12) :
    set1cols = list(rcolorbrewer.brewer_pal(9,"Set1"))
    set2cols = list(rcolorbrewer.brewer_pal(8,"Set2"))
    set3cols = list(rcolorbrewer.brewer_pal(12,"Set3"))
    allcols = set1cols+set2cols+set3cols
    return robjects.StrVector(allcols[:ncols])
# END makeLargePalette

def makeLargePalette2(ncols=12) :
    set1cols = list(rcolorbrewer.brewer_pal(3,"Set1"))
    set2cols = list(rcolorbrewer.brewer_pal(8,"Set2"))
    set3cols = list(rcolorbrewer.brewer_pal(12,"Set3"))
    allcols = set1cols+set2cols+set3cols
    return robjects.StrVector(allcols[:ncols])
# END makeLargePalette

#print robjects.r('packageVersion("ggplot2")')

#--------------------------------------------------------------------#
#                               Annotation                           #
#--------------------------------------------------------------------#
mytheme = {
        'panel.background':ggplot2.element_rect(fill='white',colour='white'),
        'axis.text':ggplot2.element_text(colour="black",size=15,
                                         family=FONTFAM),
        'axis.line':ggplot2.ggplot2.element_line(size = 1.2, colour="black"),
        'axis.title':ggplot2.element_text(colour="black",size=15,
                                          family=FONTFAM),
        'plot.title':ggplot2.element_text(face="bold", size=20,
                                          colour="black",family=FONTFAM),
        'panel.grid.minor':ggplot2.element_blank(),
        'panel.grid.major':ggplot2.element_blank(),
        'legend.key':ggplot2.element_blank(),
        'legend.text':ggplot2.element_text(colour="black",size=15,
                                           family=FONTFAM),
        'strip.text.y':ggplot2.element_text(colour="black",face="bold",
                                            size=15,family=FONTFAM),
        'strip.text.x':ggplot2.element_text(colour="black",face="bold",
                                            size=15,family=FONTFAM),
        'text':ggplot2.element_text(colour="black",family=FONTFAM)
        }
        #'panel.grid.major':ggplot2.theme_line(colour = "grey90"),

pointtheme = {
        'panel.background':ggplot2.element_rect(fill='white',colour='black',size=2),
        'axis.text':ggplot2.element_text(colour="black",size=15,family=FONTFAM),
        'axis.text.x': ggplot2.element_text(angle = 45, hjust=1, vjust=1,
                                            size=15,family=FONTFAM),
        'axis.title':ggplot2.element_text(face="bold",colour="black",
                                          size=15,family=FONTFAM),
        'plot.title':ggplot2.element_text(face="bold", size=20,
                                          colour="black",family=FONTFAM),
        'panel.grid.major':ggplot2.element_blank(),
        'panel.grid.minor':ggplot2.element_blank(),
        'legend.background':ggplot2.element_blank(),
        'legend.key':ggplot2.element_blank(),
        'legend.position':'top',
        'legend.title':ggplot2.element_text(face="bold",colour="black",
                                            size=15,family=FONTFAM),
        'legend.text':ggplot2.element_text(colour="black",size=15,family=FONTFAM),
        'plot.margin':grid.unit(robjects.IntVector([0,0,0,0]), "lines"),
        'axis.ticks':ggplot2.ggplot2.element_line(colour="black"),
        'strip.text.y':ggplot2.element_text(colour="black",face="bold",size=15,
                                            angle=-90,family=FONTFAM),
        'strip.text.x':ggplot2.element_text(colour="black",face="bold",
                                            size=15,family=FONTFAM),
        'text':ggplot2.element_text(colour="black",family=FONTFAM)
        }

sitefreqtheme = {
        'panel.background':ggplot2.element_rect(fill='white',colour='white'),
        'axis.text':ggplot2.element_text(colour="black",size=15,family=FONTFAM),
        'axis.text.x': ggplot2.element_text(angle = 45, hjust=1, vjust=1,
                                            size=15,family=FONTFAM),
        'axis.line':ggplot2.ggplot2.element_line(size = 1.2, colour="black"),
        'axis.title':ggplot2.element_text(face="bold",colour="black",
                                          size=15,family=FONTFAM),
        'plot.title':ggplot2.element_text(face="bold", size=20,
                                          colour="black",family=FONTFAM),
        'panel.grid.minor':ggplot2.element_blank(),
        'panel.grid.major':ggplot2.element_blank(),
        'legend.key':ggplot2.element_blank(),
        'legend.position':'top',
        'legend.title':ggplot2.element_text(face="bold",colour="black",
                                            size=15,family=FONTFAM),
        'legend.text':ggplot2.element_text(colour="black",size=15,family=FONTFAM),
        'strip.text.y':ggplot2.element_text(colour="black",face="bold",size=15,
                                            angle=-90,family=FONTFAM),
        'strip.text.x':ggplot2.element_text(colour="black",face="bold",
                                            size=15,family=FONTFAM),
        'text':ggplot2.element_text(colour="black",family=FONTFAM)
        }
        #'strip.text.y':ggplot2.element_text(colour="black",face="bold",size=15),

################################################################################
fsttheme = {
        'panel.background':ggplot2.element_rect(fill='white',colour='white'),
        'axis.text':ggplot2.element_text(size=15,family=FONTFAM),
        'axis.text.x': ggplot2.element_text(angle=-90, hjust=0, size=15,
                                            family=FONTFAM), # vjust=1, 
        'axis.text.y': ggplot2.element_text(angle=0, hjust=1, size=15,
                                            family=FONTFAM), # vjust=1, 
        'axis.line':ggplot2.ggplot2.element_blank(),
        'axis.title':ggplot2.element_blank(),
        'plot.title':ggplot2.element_text(face="bold", size=20,colour="black",
                                          family=FONTFAM),
        'panel.grid.minor':ggplot2.element_blank(),
        'panel.grid.major':ggplot2.element_blank(),
        'legend.key':ggplot2.element_blank(),
        'legend.position':'right',
        'legend.title':ggplot2.element_text(size=15,family=FONTFAM),
        'legend.text':ggplot2.element_text(size=15, family=FONTFAM),
        'text':ggplot2.element_text(family=FONTFAM)
        }# END fsttheme
        #'axis.line':ggplot2.ggplot2.element_line(size = 1.2, colour="black"),
        #'strip.text.y':ggplot2.element_text(colour="black",face="bold",size=15,angle=-90),
        #'strip.text.x':ggplot2.element_text(colour="black",face="bold",size=15)

admixtheme = {
        'panel.background':ggplot2.element_rect(fill='white',colour='white'),
        'axis.text.x': ggplot2.element_blank(),
        'axis.text.y': ggplot2.element_blank(),
        'axis.title.x':ggplot2.element_blank(),
        'axis.title.y':ggplot2.element_blank(),
        'panel.grid.major':ggplot2.element_blank(),
        'panel.grid.minor':ggplot2.element_blank(),
        'legend.position':"none",
        'strip.text.x':ggplot2.element_text(size=10, face="bold", colour="black",
                                            angle=0,family=FONTFAM),
        'strip.text.y':ggplot2.element_text(size=12, face="bold", colour="black",
                                            family=FONTFAM),
        'strip.background':ggplot2.element_rect(colour="white", fill="white"),
        'axis.ticks':ggplot2.element_blank(),
        'text':ggplot2.element_text(colour="black",family=FONTFAM)
        }
        #'strip.text':ggplot2.element_text(size=8, colour="blue",angle=90),

ribbontheme = {
        'panel.background':ggplot2.element_rect(fill='white',colour='white'),
        'axis.text.y': ggplot2.element_text(colour="black",size=15,family=FONTFAM),
        'axis.text.x': ggplot2.element_blank(),
        'axis.title':ggplot2.element_text(colour="black",size=15,family=FONTFAM),
        #'axis.title.x':ggplot2.element_blank(),
        #'axis.title.y':ggplot2.element_blank(),
        'panel.grid.major':ggplot2.element_blank(),
        'panel.grid.minor':ggplot2.element_blank(),
        'panel.margin':grid.unit(.0, "lines"), # cant find unit....
        'strip.text.x':ggplot2.element_text(size=6, colour="black",angle=90,
                                            hjust=0,vjust=.75,family=FONTFAM),
        'strip.text.y':ggplot2.element_text(size=12, face="bold", colour="black",
                                            family=FONTFAM),
        'strip.background':ggplot2.element_blank(),
        'axis.ticks':ggplot2.element_blank(),
        'text':ggplot2.element_text(colour="black",family=FONTFAM)
        #'strip.background':ggplot2.element_rect(colour="white", fill="white"),
        #'axis.ticks':ggplot2.ggplot2.element_line(colour="black")
        }

pointtheme_nolegend = {
        'panel.background':ggplot2.element_blank(),
        'axis.text':ggplot2.element_text(colour="black",size=15,family=FONTFAM),
        'axis.title':ggplot2.element_text(colour="black",size=15,family=FONTFAM),
        'plot.title':ggplot2.element_text(face="bold", size=20,
                                          colour="black",family=FONTFAM),
        'panel.grid.minor':ggplot2.element_blank(),
        'panel.grid.major':ggplot2.element_blank(),
        'legend.position':"none",
        'axis.text.x': ggplot2.element_text(angle = 45, hjust=1, vjust=1,
                                            family=FONTFAM),
        'strip.text.y':ggplot2.element_text(colour="black",face="bold",
                                            size=15,angle=-90,family=FONTFAM),
        'strip.text.x':ggplot2.element_text(colour="black",face="bold",
                                            size=15,family=FONTFAM),
        'text':ggplot2.element_text(colour="black",family=FONTFAM)
        }

pcatheme = {
        #'panel.background':ggplot2.element_blank(),
        'panel.background':ggplot2.element_rect(colour="black", fill="white"),
        'axis.text':ggplot2.element_blank(),
        'axis.title':ggplot2.element_text(colour="black",size=15,family=FONTFAM),
        'plot.title':ggplot2.element_text(face="bold", size=20,
                                          colour="black",family=FONTFAM),
        'panel.grid.minor':ggplot2.element_blank(),
        'panel.grid.major':ggplot2.element_blank(),
        'legend.background':ggplot2.element_blank(),
        'legend.key':ggplot2.element_blank(),
        'plot.margin':grid.unit(robjects.IntVector([0,0,0,0]), "lines"),
        'axis.ticks':ggplot2.element_blank(),
        'text':ggplot2.element_text(colour="black",family=FONTFAM)
        }

pcathemesmall = {
        #'panel.background':ggplot2.element_blank(),
        'panel.background':ggplot2.element_rect(colour="black", fill="white"),
        'axis.text':ggplot2.element_blank(),
        'axis.title':ggplot2.element_text(colour="black",size=10,family=FONTFAM),
        'plot.title':ggplot2.element_text(face="bold", size=20,colour="black",family=FONTFAM),
        'panel.grid.minor':ggplot2.element_blank(),
        'panel.grid.major':ggplot2.element_blank(),
        'legend.background':ggplot2.element_blank(),
        'legend.key':ggplot2.element_blank(),
        'plot.margin':grid.unit(robjects.IntVector([0,0,0,0]), "lines"),
        'axis.ticks':ggplot2.element_blank(),
        'text':ggplot2.element_text(colour="black",family=FONTFAM)
        }

        #'axis.text.x': ggplot2.element_text(angle = 45, hjust=1, vjust=1),
        #'strip.text.y':ggplot2.element_text(colour="black",face="bold",size=10,angle=-90),
        #'strip.text.x':ggplot2.element_text(colour="black",face="bold",size=10),
        #'legend.position':"none",

        #'strip.background':ggplot2.element_rect(colour="white", fill="white")
        #'axis.title':ggplot2.element_blank(),

#'panel.background':ggplot2.element_rect(colour = "black"),
        #'panel.grid.minor':ggplot2.element_blank(),



