import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
import pandas as pd
import ast

########## Network creation (Network based on similarities between artists)
def fix_years(years, override_active_years = True, return_all_nan=False): #Birth, first active year, last active year, death
    if np.isnan(years[0]) and np.isnan(years[1]):
        if return_all_nan:
            return [np.nan, np.nan, np.nan, np.nan]
        return np.nan
    if np.isnan(years[2]) and np.isnan(years[3]):
        if return_all_nan:
            return [np.nan, np.nan, np.nan, np.nan]
        return np.nan
    
    if np.isnan(years[0]):
        years[0] = years[1]-20
    if np.isnan(years[1]):
        years[1] = years[0]+20
    if np.isnan(years[2]):
        years[2] = years[3]
    if np.isnan(years[3]):
        years[3] = years[2]

    if override_active_years:
        if years[2]>years[3]:
            years[2] = years[3]
        if years[1]>years[0]:
            years[1] = years[0]

    #Sort just in case
    return sorted(years)


def get_loc_similarity(places1, places2, years1, years2, birthplace1, birthplace2, nationality1, nationality2, citizenship1, citizenship2, active_years_only = False):
    """
    Calculate similarity index between two artists based on their places and years."""
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

 