import numpy as np
from numpy.random import randn
import pandas as pd
from scipy import stats
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns

import time

"""
This file is responsible for graphing the various statistics we've been
keeping through this simulation
"""

def init_graph_style():
    sns.set_palette("pastel", desat=.6)
    np.random.seed(9221999)

def graph_time_to_guard(times_list, layer_num, experiment_descr, text_info):
    """Graph time to guard discovery"""
    init_graph_style()

    fig = plt.figure()
    # Make the figure bigger than default
    fig.set_size_inches(18.5, 10.5)
    ax = fig.add_subplot(1,1,1)
    fig.subplots_adjust(top=0.72)

    ax.set_title("Time to compromise G%d" % layer_num)

    ax.set_xlabel("Hours to compromise G%d" % layer_num)
    ax.set_ylabel("Probability to compromise G%d" % layer_num)

    ax.hist(times_list, bins=100, cumulative=True, normed=1)
    sns.rugplot(times_list)

    ax.text(0.05, 0.78, text_info, bbox=dict(facecolor='red', alpha=0.2),
            transform=fig.transFigure, fontsize=12)

#    plt.show()

    # e.g. time_to_g1_2-4-8_hard_APT_20180330-120958.jpg
    timestr = time.strftime("%Y%m%d-%H%M%S")
    graph_filename = "time_to_g%s_%s_%s.jpg" % (layer_num, experiment_descr, timestr)
    plt.savefig(graph_filename, dpi=100)
    plt.close()

def graph_remaining_g2_times(times_list, experiment_descr, text_info):
    """Graph remaining G2 lifetimes when G3 gets sybiled"""
    init_graph_style()

    fig = plt.figure()
    # Make the figure bigger than default
    fig.set_size_inches(18.5, 10.5)
    ax = fig.add_subplot(1,1,1)
    fig.subplots_adjust(top=0.72)

    ax.set_title("Remaining g2 lifetimes when g3 gets sybiled")

    ax.set_xlabel("Remaining g2 lifetime in hours ")
    ax.set_ylabel("Probability of remaining lifetime")

    ax.set_xticks(np.arange(min(times_list), max(times_list)+1, 10.0))

    ax.hist(times_list, bins=100, cumulative=True, normed=1)
    sns.rugplot(times_list)

    ax.text(0.05, 0.78, text_info, bbox=dict(facecolor='red', alpha=0.2),
            transform=fig.transFigure, fontsize=12)

#    plt.show()

    timestr = time.strftime("%Y%m%d-%H%M%S")
    graph_filename = "remaining_g2_lifetime_%s_%s.jpg" % (experiment_descr, timestr)
    plt.savefig(graph_filename, dpi=100)
    plt.close()

