import numpy as np

########## Network creation (Network based on similarities between artists)
def years_validity(years):
    if np.isnan(years[0]) and np.isnan(years[1]):
        return False
    if np.isnan(years[2]) and np.isnan(years[3]):
        return False
    if not np.isnan(years[0]) and not np.isnan(years[3]):
        if years[0]>years[3]:
            return False
        if years[0] + 130 < years[3]:
            return False
    return True
    

def fix_years(years, override_active_years = True, check_years = True, return_all_nan=False): #Birth, first active year, last active year, death
    if check_years:
        if years_validity(years):
            if return_all_nan:
                return [np.nan, np.nan, np.nan, np.nan]
            else:
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
        if years[1]<years[0]:
            years[1] = years[0]

    #Sort just in case
    return sorted(years)


def get_loc_similarity(places1=None, places2=None, years1=None, years2=None,
                       birthplace1=None, birthplace2=None, nationality1=None,
                       nationality2=None, citizenship1=None, citizenship2=None,
                       active_years_only = False, full_data_1 = None, full_data_2 = None):
    """
    Calculate similarity index between two artists based on their places and years.
    """
    p = 0
    if full_data_1 is not None:
        pass
    if full_data_2 is not None:
        pass
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
