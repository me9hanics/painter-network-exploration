import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter
import powerlaw as pwl
from collections import Counter


def plot_deg_distr_lin(degrees, ax=None, label_turnoff = False, ticks_list = None):
    deg_distri=Counter(degrees)
    keys, values = zip(*sorted(deg_distri.items()))

    # Degree distribution
    if(ax is None): #Here we divide between if we want to just create a one plot figure, or use this plot as a part of a bigger figure
        plt.scatter(keys, values, color='blue')
        plt.plot(keys, values, color='black', linewidth=2)  # This line connects the points
        plt.xticks(ticks = ticks_list)
        #plt.yticks(fontsize=22)
        if(not label_turnoff):
            plt.xlabel('Degree', )
            plt.ylabel('Frequency', )
            plt.title('Degree Distribution', )
        return plt
    else:
        ax.scatter(keys, values, color='blue')
        ax.plot(keys, values, color='black', linewidth=2)  # This line connects the points
        if (ticks_list is not None):
            ax.set_xticks(ticks_list)
        ax.tick_params(axis='both', which='major', )
        if(not label_turnoff):
            ax.set_title('Degree Distribution', )
            ax.set_xlabel('Degree', )
            ax.set_ylabel('Frequency', )
        return ax
    
def plot_deg_distr_linandlog(degrees, ax=None):
    deg_distri=Counter(degrees)
    keys, values = zip(*sorted(deg_distri.items()))

    #This case is easier, we will use axes anyways, just a difference in whether the function creates them or not
    if ax is None:
        fig, ax = plt.subplots(1, 2, figsize=(12,6))

    if len(ax.shape)==1:
        first_ax = ax[0]
        second_ax = ax[1]
    elif len(ax.shape)==2:
        first_ax = ax[0,0]
        second_ax = ax[0,1]
    else:
        raise ValueError("Too many axes")
        return

    #Degree distribution
    first_ax.scatter(keys, values, color='blue')
    first_ax.plot(keys, values, color='black', linewidth=2)  # This line connects the points
    first_ax.set_xlabel('Degree', fontsize=22)
    first_ax.set_ylabel('Frequency', fontsize=22)
    first_ax.set_xticks([1,5,10,21])
    first_ax.tick_params(axis='both', which='major', labelsize=20)
    
    #Lin-log
    x=[]; y=[]
    for i in sorted(deg_distri):   
        x.append(i); y.append(deg_distri[i]/len(degrees))
    second_ax.set_yscale('log')
    second_ax.set_xscale('log')
    second_ax.plot(x,y,'ro')
    pwl.plot_pdf(degrees, color='black', linewidth=2, ax=second_ax)
    second_ax.tick_params(axis='both', which='major', labelsize=20)
    second_ax.set_xlabel('Degree ($k$)', fontsize=22)
    second_ax.set_ylabel('$P(k)$', fontsize=22)

    fig.suptitle('Degree Distribution', fontsize=22)
    # Show the figure
    plt.tight_layout()
    if ax is None:
        plt.show()
    return ax

def plot_deg_dist_fit_log_single(degrees, ax=None, label_ignore=False):
    deg_distri=Counter(degrees)
    fit_f = pwl.Fit(degrees)
    
    x=[]; y=[]
    for i in sorted(deg_distri):   
        x.append(i); y.append(deg_distri[i]/len(degrees))

    if ax is None:
        fig = plt.figure(figsize=(6,6))
        ax = fig.add_subplot(111)

    ax.plot(x, y, 'ro')
    pwl.plot_pdf(degrees, color='black', linewidth=2, ax=ax)
    ax.set_xscale('log')
    ax.set_yscale('log')
    if not label_ignore:
        ax.set_xlabel('Degree ($k$)')
        ax.set_ylabel('$P(k)$')
        ax.set_title("Degree distribution")
    fit_f.power_law.plot_pdf(ax=ax, color='b', linestyle='-', linewidth=1, label='fit')

def plot_deg_dist_fit_log(degrees_list, label_ignore_list=None):
    if label_ignore_list is None:
        label_ignore_list = [False] * len(degrees_list)

    n = len(degrees_list)
    if n == 1:
        plot_deg_dist_fit_log_single(degrees_list[0], label_ignore=label_ignore_list[0])
        #return something
    else:
        rows = (n + 1) // 2
        fig, axes = plt.subplots(rows, 2, figsize=(12, 6*rows))
        axes = axes.flatten()
        for i, degrees in enumerate(degrees_list):
            plot_deg_dist_fit_log_single(degrees, ax=axes[i], label_ignore=label_ignore_list[i])
        plt.tight_layout()
        #plt.show()
        return fig, axes
    
def plot_deg_dist_fit_log_single_pdf(degrees, ax=None, label_ignore=False, return_fit = False): #Added a label ignore for other cases, not just for analysis in this notebook
    deg_distri=Counter(degrees)
    fit_f = pwl.Fit(degrees)
    
    x=[]; y=[]
    for i in sorted(deg_distri):   
        x.append(i); y.append(deg_distri[i]/len(degrees))
    
    if ax is None:
        fig = plt.figure(figsize=(8,8))
        ax = fig.add_subplot(111)

    ax.plot(x, y, 'bo', markersize=5, label='Data') #Smaller size for prettiness
    pwl.plot_pdf(degrees, color='black', linewidth=2, ax=ax, label='Probability density function')
    ax.set_xscale('log')
    ax.set_yscale('log')
    if not label_ignore:
        ax.set_xlabel('Degree ($k$)', fontsize=14)
        ax.set_ylabel('$P(k)$', fontsize=14)
        ax.set_title("Degree distribution", fontsize=16)
    ax.legend(fontsize=12)
    ax.grid(True, which="major", ls="--", linewidth=0.5) #Major looks better
    ax.set_ylim([0.0001,0.1])

    if return_fit:
        return fit_f

def measure_measure_scatter(values1, values2, ax=None, xlabel=None, ylabel=None, title=None):
    if ax is None:
        fig, ax = plt.subplots(figsize=(6,6))
    ax.scatter(values1, values2, color='blue')
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    return ax

def plot_fraction(thresholds, fractions, title, xlabel, ylabel, vspan_intervals=None, yticks=None, xticks=None):

    plt.scatter(thresholds, fractions, color='blue')
    plt.yscale('log')
    plt.xscale('log')
    
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    
    if yticks is not None:
        plt.yticks(yticks)
    if xticks is not None:
        plt.xticks(xticks)
    
    if vspan_intervals is not None:
        for interval0, interval1, color, label in vspan_intervals:
            plt.axvspan(interval0, interval1, color=color, alpha=0.3, label=label)
        plt.legend()


def plot_threshold_sizes_regions(
    thresholds,
    more_than_threshold,
    largest_component_sizes,
    threshold_vlines=(5, 20),
    supercritical_range=(0.01, 5),
    subcritical_range=(20, 147),
    best_region_range=(5, 20),
    edge_threshold=100000,
    component_size_threshold=2000,
    edge_yticks=np.array([1, 10, 100, 1000, 10000, 100000, 200000]),
    component_yticks=np.array([1, 10, 100, 1000, 4000]),
    figsize=(14, 6),
):
    """
    Draws a figure, with two plots on edge weight threshold and size connections:
    1. Number of edges above threshold
    2. Largest connected component size
    """
    
    def format_yticks(tick_val, pos):
        return int(tick_val)
    
    fig, ax = plt.subplots(1, 2, figsize=figsize)

    ax[0].scatter(thresholds, more_than_threshold, color='blue')
    ax[0].set_yscale('log')
    ax[0].set_xscale('log')
    ax[0].axvline(x=threshold_vlines[0], color='red', linestyle='--', label=f'Selected threshold {threshold_vlines[0]}')
    ax[0].axvspan(*supercritical_range, color='grey', alpha=0.3, label='Supercritical regime')
    ax[0].axvspan(*subcritical_range, color='red', alpha=0.3, label='Subcritical regime')
    ax[0].axvspan(*best_region_range, color='gold', alpha=0.3, label='Assumed best region for threshold')
    ax[0].set_title('Number of edges above threshold')
    ax[0].set_xlabel('Threshold')
    ax[0].set_ylabel('No. of edges')
    ax[0].set_yticks(edge_yticks)
    ax[0].axhline(y=edge_threshold, xmin=0.0001, xmax=1, color='green', linestyle='--')
    ax[0].yaxis.set_major_formatter(FuncFormatter(format_yticks))
    ax[0].legend()

    ax[1].scatter(thresholds, largest_component_sizes, color='orange')
    ax[1].set_yscale('log')
    ax[1].set_xscale('log')
    ax[1].axvline(x=threshold_vlines[1], color='red', linestyle='--', label=f'Selected threshold {threshold_vlines[1]}')
    ax[1].axvspan(*supercritical_range, color='grey', alpha=0.3, label='Supercritical regime')
    ax[1].axvspan(*subcritical_range, color='red', alpha=0.3, label='Subcritical regime')
    ax[1].axvspan(*best_region_range, color='gold', alpha=0.3, label='Assumed best region for threshold')
    ax[1].set_title('Largest connected component size')
    ax[1].set_xlabel('Threshold')
    ax[1].set_ylabel('Component size')
    ax[1].set_yticks(component_yticks)
    ax[1].axhline(y=component_size_threshold, xmin=0.0001, xmax=1, color='green', linestyle='--')
    ax[1].yaxis.set_major_formatter(FuncFormatter(format_yticks))
    ax[1].legend()

    plt.tight_layout()
    #plt.show()

def plot_CC_distribution_hist(clustering_coefficients, ax):
    ax.hist(clustering_coefficients, bins=np.linspace(0, 1, 21), density=True, alpha=0.75)
    ax.set_xlabel("Clustering coefficient")
    ax.set_ylabel("Fraction of nodes")
    ax.set_title("Clustering coefficient distribution")
    ax.set_xlim(0, 1)

def plot_values_per_k(k_nn_values_per_k, ax=None, xscale="log", yscale="log",
                      title="Average neighbor's neighbour degree per node degree",
                      ylabel="Average neighbor's neighbour degree"):
    """Intended to use with a dictionary, for these purposes:
       - either {k: average_knn_for_k(k_nn_dict, k)}
       - or nx.rich_club_coefficient(G)
       """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))
    else:
        fig = None

    ax.plot(list(k_nn_values_per_k.keys()), list(k_nn_values_per_k.values()), 'o')
    ax.set_xlabel("Node degree ($k$)")
    ax.set_ylabel(ylabel)
    ax.set_xscale(xscale)
    ax.set_yscale(yscale)
    ax.set_title(title)
    
    if fig is not None:
        plt.show()
