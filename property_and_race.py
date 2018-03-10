"""
Python code generates geoData.js file, which needs to be copied over to the
nobleator.github.io folder for display/publication.

https://factfinder.census.gov
Selected geographies: metro and micropolitan statistical areas within the US
Selected population total
Modify table to select Hispanic or latino and race

Categories of race:
Hispanic or latino
White
Black or African American
American Indian and Alaska Native
Asian
Native Hawaiian or Other Pacific Islander
Other
Two or more races

White -> blue -> #8198ff
Hispanic -> pink -> #ff97e0
African-American -> red -> #f73b47
Asian -> green -> #00937b
"""
import pandas as pd
# import random
import json


def hex_to_rgb(value):
    """Return (red, green, blue) for the color given as #rrggbb."""
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))


def rgb_to_hex(red, green, blue):
    """Return color as #rrggbb for the given color values."""
    return '#%02x%02x%02x' % (red, green, blue)


w = hex_to_rgb('#ffffff')
h = hex_to_rgb('#00ff00')
b = hex_to_rgb('#0000ff')
"""w = hex_to_rgb('#8198ff')
h = hex_to_rgb('#ff97e0')
b = hex_to_rgb('#f73b47')
a = hex_to_rgb('#00937b')"""

features = []
race_data = 'Race_data_cleaned.xlsx'
price_data = 'City_MedianListingPrice_AllHomes.xlsx'
location_data = 'uscitiesv1.3.xlsx'
race_df = pd.read_excel(race_data, sheet_name=0)
price_df = pd.read_excel(price_data, sheet_name=0)
loc_df = pd.read_excel(location_data, sheet_name=0)

loc_lat_col = loc_df.columns.get_loc('lat')
loc_lon_col = loc_df.columns.get_loc('lng')
price_avg_col = price_df.columns.get_loc('AVERAGE')
w_p_col = race_df.columns.get_loc('Percent; White alone') + 1
h_p_col = race_df.columns.get_loc('Percent; Hispanic or Latino (of any race)') + 1
b_p_col = race_df.columns.get_loc('Percent; Black or African American alone') + 1
# a_p_col = race_df.columns.get_loc('Percent; Asian alone') + 1
race_city_col = race_df.columns.get_loc('Geography') + 1
race_state_col = race_df.columns.get_loc('State') + 1
race_type_col = race_df.columns.get_loc('Metro/Micro') + 1
# print(race_df.columns.values.tolist())

for row in race_df.itertuples():
    if row[race_type_col + 1] == 'Metro':
        continue
    city = row[race_city_col]
    state = row[race_state_col]
    w_p = 0.01 * row[w_p_col]
    h_p = 0.01 * row[h_p_col]
    b_p = 0.01 * row[b_p_col]
    # a_p = 0.01 * row[a_p_col]
    """description = '{0}% W, {1}% H, {2}% B, {3}% A'.format(round(100 * w_p, 2),
                                                          round(100 * h_p, 2),
                                                          round(100 * b_p, 2),
                                                          round(100 * a_p, 2))"""
    description = '{0}% W, {1}% H, {2}% B'.format(round(100 * w_p, 2),
                                                  round(100 * h_p, 2),
                                                  round(100 * b_p, 2))
    """red = min(int(w_p * w[0] + h_p * h[0] + b_p * b[0] + a_p * a[0]), 255)
    green = min(int(w_p * w[1] + h_p * h[1] + b_p * b[1] + a_p * a[1]), 255)
    blue = min(int(w_p * w[2] + h_p * h[2] + b_p * b[2] + a_p * a[2]), 255)"""
    red = min(int(w_p * w[0] + h_p * h[0] + b_p * b[0]), 255)
    green = min(int(w_p * w[1] + h_p * h[1] + b_p * b[1]), 255)
    blue = min(int(w_p * w[2] + h_p * h[2] + b_p * b[2]), 255)
    color = rgb_to_hex(red, green, blue)

    # DataFrame not row bc multiple matching results?
    loc_row_df = loc_df[loc_df['city'].str.contains(city) &
                        loc_df['state_id'].str.contains(state)]
    if loc_row_df.empty:
        continue
    lat = loc_row_df.iloc[0, loc_lat_col]
    lon = loc_row_df.iloc[0, loc_lon_col]

    price_row_df = price_df[price_df['RegionName'].str.contains(city) &
                            price_df['State'].str.contains(state)]
    if price_row_df.empty:
        continue
    price = price_row_df.iloc[0, price_avg_col]

    feature = {'type': 'Feature',
               "geometry": {"type": "Point",
                            "coordinates": [lon, lat]},
               "properties": {"title": '{0}, {1}'.format(city, state),
                              'description': description,
                              'price': price,
                              'color': color}}
    features.append(feature)


geo_data = {'type': 'FeatureCollection',
            'features': features}

with open('geoData.js', 'w') as fid:
    fid.write('var mapData = ')
    json.dump(geo_data, fid)
