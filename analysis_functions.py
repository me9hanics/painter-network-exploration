import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
import pandas as pd
import ast

### Network creation functions (for similarities between artists)
def years_fixer(years): #Birth, first active year, last active year, death
    if np.isnan(years[0]) and np.isnan(years[1]):
        return np.nan
    if np.isnan(years[2]) and np.isnan(years[3]):
        return np.nan
    
    if np.isnan(years[0]):
        years[0] = years[1]-20
    if np.isnan(years[1]):
        years[1] = years[0]+20
    if np.isnan(years[2]):
        years[2] = years[3]
    if np.isnan(years[3]):
        years[3] = years[2]

    #Sort just in case
    return sorted(years)


def index_simple(places1, places2, years1, years2, birthplace1, birthplace2, nationality1, nationality2, citizenship1, citizenship2, active_years_only = False):
    p = 0
 
    if (type(places1) != float and type(places2) != float):
        #Assuming not np.nan, but list
        for place1 in places1:
            for place2 in places2:
                if place1 == place2:
                    p += 1

    if not type(birthplace1) == float and not type(birthplace2) == float:
        if birthplace1 == birthplace2:
            p += 1
    if not type(citizenship1) == float and not type(citizenship2) == float:
        if citizenship1 == citizenship2:
            p += 0.3
        elif (not type(nationality1) == float) and (not type(nationality2) == float):
            for nat1 in nationality1:
                for nat2 in nationality2:
                    if nat1 == nat2:
                        p += 0.3/(len(nationality1)*len(nationality2))

    #Years: Birthyear, first year, last year, death year. Assumed all four are given
    common_years = 0
    common_active_years = 0
    if years1[1] > years2[1]:
        years_min, years_max = years2, years1
    else:
        years_min, years_max = years1, years2

    for i in range(int(years_min[1]), int(years_min[2])+1):
        if i >= years_max[1] and i <= years_max[2]:
            common_active_years += 1
    
    if years1[0]>years2[0]:
        years_min, years_max = years2, years1
    else:
        years_min, years_max = years1, years2

    for i in range(int(years_min[0]), int(years_min[3])+1):
        if i >= years_max[0] and i <= years_max[3]:
            common_years += 1


    #Formula: average_common_years / places  *  common_places  -> Dimension: time (which is good, because more time means more connections)
    if active_years_only:
        average_common_years_per_place1 = common_active_years/(len(places1)) if len(places1) > 0 else 0
        average_common_years_per_place2 = common_active_years/(len(places2)) if len(places2) > 0 else 0
    else:
        average_common_years_per_place1 = common_years/(len(places1)) if len(places1) > 0 else 0
        average_common_years_per_place2 = common_years/(len(places2)) if len(places2) > 0 else 0
    
    return (average_common_years_per_place1 + average_common_years_per_place2)/2 * p

########## Network analysis functions

def get_column_counts(artists_df, column):
    return (artists_df[column]).value_counts()

def get_column_counts_adjusted(artists_df, column):
    return (artists_df[column]).value_counts(normalize=True)

def get_column_average(artists_df, column):
    return (artists_df[column]).mean()

def get_column_std(artists_df, column):
    return (artists_df[column]).std()

def get_locations_average(artists_df):
    all_people_locations = []
    for index, row in artists_df.iterrows():
        locations = ast.literal_eval(row['locations'])
        all_people_locations.extend(locations)

    return pd.Series(all_people_locations).value_counts(normalize=True)

def get_female_percentage(artists_df):
    values = (artists_df['gender'].value_counts(normalize=True))
    try:
        values_known = values['male'] + values['female']
    except KeyError:
        try:
            values_known = values['male']
            if values_known == 0:
                return None
            else :
                return 0
        except KeyError:
            try:
                values_known = values['female']
                if values_known == 0:
                    return None
                else:
                    return 100
            except KeyError:
                return None
    return 100*values['female'] / values_known

def plot_deg_distr_lin(degrees, ax=None, label_turnoff = False, ticks_list = None):
    import powerlaw as pwl

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
    import powerlaw as pwl
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
        print("Too many dimensions") #Added this for the future
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
    import powerlaw as pwl
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
    
def plot_deg_dist_fit_log_single_no_fit(degrees, ax=None, label_ignore=False): #Added a label ignore for other cases, not just for analysis in this notebook
    import powerlaw as pwl
    from collections import Counter
    deg_distri=Counter(degrees)
    fit_f = pwl.Fit(degrees)
    
    x=[]; y=[]
    for i in sorted(deg_distri):   
        x.append(i); y.append(deg_distri[i]/len(degrees))
    
    if ax is None:
        fig = plt.figure(figsize=(10,10))
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
