#!/usr/bin/python

# Data source
# 1. DNA extraction ("sample_type" and sample "barcode" recorded)
# 2. DNA fragmentation
#     - in-process QC metric: average fragment size ("frag_size")
#     - in-process QC metric: DNA concentration ("pre_quant")
# 3. library preparation
#     a. blunt-end
#     b. A-tailing
#     c. adapter ligation
# 4. PCR
#     - in-process QC metric: DNA concentration ("post_quant")
# 5. target enrichment
# 6. sequencing
#     - sequencing QC flag: sequencing coverage ("coverage")
#     - sequencing QC flag: reliable CNV calling ("CNV_calling")
#     - Sample quality is assessed during calling review using QC metrics and
#       manual inspection of the data to make a final call ("passing_well")

import os
import inspect
import sys
from pandas import *

# Custom inclusions
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                             'include'))
#sys.path.append(os.path.join(os.path.curdir, 'include'))

# housekeeping has simple functions for working with files and directories
import housekeeping as hk
# ggplotInclude pulls in necessary rpy imports for generating ggplot2 plots
from ggplotInclude import *


def sample_type_proportions(samptypedf):
    # For target dataframe, generate a proportions column
    # For each sample type, calculate the proportion of each QC flag
    tmp = []
    for sample_type, subdata in samptypedf.groupby("sample_type"):
        subdata["proportion"] = (subdata["Count"]
                                 .apply(lambda x: x /
                                        float(subdata.Count.sum())))
        tmp.append(subdata)

    samptypedf = concat(tmp)
    return samptypedf
# END sample_type_proportions


def plot_qc_proportions(sampleqccnts, figdir):
    # plot_qc_proportions
    # Generate a bar plot showing the propotions of samples with different QC
    # statuses Across sample types
    # Plot relationship between QC flags
    r_dataframe = com.convert_to_r_dataframe(sampleqccnts)

    p = (ggplot2.ggplot(r_dataframe) +
         ggplot2.aes_string(x="qcstatus", y="proportion",
                            fill="factor(sample_type)") +
         #ggplot2.ggtitle("Part B: Relationship of QC metrics") +
         ggplot2.geom_bar(stat="identity", position="dodge") +
         ggplot2.scale_y_continuous("Proportion",
                                    expand=robjects.IntVector((0, 0)),
                                    limits=robjects.IntVector((0, 1.))) +
         ggplot2.scale_x_discrete("Coverage: CNV Calling") +
         ggplot2.scale_fill_brewer("Sample Type", palette="Set1") +
         ggplot2.theme(**sitefreqtheme) +
         ggplot2.theme(**{'legend.position': "right"}))

    figname = os.path.join(figdir, "qc_bars.pdf")
    print "Writing file:", figname
    grdevices.pdf(figname, width=5.8, height=6.2)
    p.plot()
    grdevices.dev_off()
# END plot_qc_proportions


def plot_metrics(metricsdf, figdir):
    # plot_metrics
    # Generate a box plot to show distributions of sample values across
    # different QC metrics and comparing sample types
    r_dataframe = com.convert_to_r_dataframe(metricsdf)

    p = (ggplot2.ggplot(r_dataframe) +
         ggplot2.aes_string(x="sample_type", y="value",
                            fill="factor(qcstatus)") +
         #ggplot2.ggtitle("Part C: Metrics associated with failing QC") +
         ggplot2.geom_boxplot(notch=True) +
         ggplot2.scale_y_continuous("QC Metric Value") +
         ggplot2.scale_x_discrete("Sample Type") +
         ggplot2.scale_fill_brewer("Coverage: CNV Calling", palette="Set1") +
         ggplot2.theme(**sitefreqtheme) +
         ggplot2.theme(**{'legend.position': "right"}) +
         ggplot2.facet_grid(robjects.Formula('variable ~ .'), scale="free"))
    #ggplot2.theme(**{'axis.text.x': ggplot2.element_text(angle = 45)}) +

    figname = os.path.join(figdir, "metrics_boxs.pdf")
    print "Writing file:", figname
    grdevices.pdf(figname, width=7, height=6)
    p.plot()
    grdevices.dev_off()
# END plot_metrics


def plot_batch_stats(batchstats, figdir):
    # plot_batch_stats
    # Generate a candlestick like plot showing the mean and standard devations
    # for QC metrics over subsequent batches
    r_dataframe = com.convert_to_r_dataframe(batchstats)
    p = (ggplot2.ggplot(r_dataframe) +
         ggplot2.aes_string(x="nbatch", y="mean") +
         #ggplot2.ggtitle("Part D: QC metrics across batches") +
         ggplot2.geom_point(stat="identity") +
         ggplot2.geom_errorbar(ggplot2.aes_string(ymin="sd_low",
                                                  ymax="sd_high"),
                               size=1, width=.1) +
         ggplot2.scale_y_continuous("QC Metric Value") +
         ggplot2.scale_x_continuous("Batch ID") +
         ggplot2.theme(**sitefreqtheme) +
         ggplot2.theme(**{'legend.position': "top"}) +
         ggplot2.facet_grid(robjects.Formula('metric ~ .'), scale="free"))
    #ggplot2.theme(**{'axis.text.x': ggplot2.element_text(angle = 45)}) +
    #ggplot2.scale_fill_brewer("QC Metric", palette="Set1") +

    figname = os.path.join(figdir, "batch_candlesticks.pdf")
    print "Writing file:", figname
    grdevices.pdf(figname, width=6, height=6)
    p.plot()
    grdevices.dev_off()
# END plot_batch_stats


def main():
    file_path = (os.path.
                 dirname(os.path.
                         abspath(inspect.getfile(inspect.currentframe()))))
    rawdata_dir = os.path.abspath(os.path.join(file_path, "../rawdata"))
    figure_dir = os.path.abspath(os.path.join(file_path, "../figures"))
    assert os.path.exists(rawdata_dir), "Error: raw data not found"
    assert os.path.exists(figure_dir), \
        "Error: defined target directory not found"

    sampledf = []
    for batchfile in hk.filesInDir(rawdata_dir, "txt"):
        fpath, batchid, suffix = hk.getBasename(batchfile)
        platedata = read_csv(batchfile, sep="\t")
        platedata["Batch"] = batchid
        sampledf.append(platedata)

    assert len(sampledf) > 0, "Error: no files found"
    sampledf = concat(sampledf)

    print sampledf.head()

    print "Percentage of samples that passed sequencing QC:"
    print "%.2f%%" % (sum(sampledf["passed_well"] == "passed") /
                      float(len(sampledf)) * 100)
    print "Percentage failed due to low sequencing coverage:"
    print "%.2f%%" % (sum(sampledf["coverage"] == "failed") /
                      float(len(sampledf)) * 100)

    print ("Percentage of samples that passed sequencing coverage but" +
           "failed due to CNV calling:")
    print "%.2f%%" % (sum((sampledf["coverage"] == "passed") &
                          (sampledf["CNV_calling"] == "failed")) /
                      float(len(sampledf)) * 100)

    print "Does Sample type relate to failing sequencing coverage QC?"
    sampleqccnts = DataFrame({"Count": sampledf.groupby(["sample_type",
                                                         "coverage"]).size()
                              }).reset_index()
    sampleqccnts = sample_type_proportions(sampleqccnts)
    print sampleqccnts

    print ("Does Sample type relate to passing coverage but failing"
           "CNV calling?")
    sampleqccnts = (DataFrame({"Count":
                              sampledf.groupby(["sample_type", "coverage",
                                                "CNV_calling"]).size()})
                    .reset_index())
    sampleqccnts = sample_type_proportions(sampleqccnts)
    sampleqccnts["qcstatus"] = (sampleqccnts["coverage"] + ":" +
                                sampleqccnts["CNV_calling"])
    print sampleqccnts

    # Generate a bar plot showing the differences in distribution between
    # QC statuses
    plot_qc_proportions(sampleqccnts, figure_dir)

    # Merge the QC status columns into a single attribute
    sampledf["qcstatus"] = sampledf["coverage"] + ":" + sampledf["CNV_calling"]
    metricsdf = (melt(sampledf, id_vars=["Batch", "sample_type", "qcstatus"],
                      value_vars=["frag_size", "post_quant", "pre_quant"])
                 .reset_index(drop=True))

    # Generate a box plot diagramming the distributions of QC metrics
    plot_metrics(metricsdf, figure_dir)

    # For each batch and QC metric, calculate the mean and standard deviation
    batchstats = []
    for grp, subdata in metricsdf.groupby(["Batch", "variable"]):
        batchstats.append(list(grp)+[subdata["value"].mean(),
                                     subdata["value"].std()])

    batchstats = DataFrame(batchstats, columns=["Batch", "metric", "mean",
                                                "std"])
    batchstats["sd_high"] = batchstats["mean"] + batchstats["std"]
    batchstats["sd_low"] = batchstats["mean"] - batchstats["std"]

    # Rename the batches by the integer value
    batchstats["nbatch"] = batchstats["Batch"].apply(lambda x:
                                                     int(x[x.find("_")+1:]))

    # Plot the batch statistics using a candlestick like plot
    plot_batch_stats(batchstats, figure_dir)
# END main

if __name__ == "__main__":
    main()
# END MAIN
