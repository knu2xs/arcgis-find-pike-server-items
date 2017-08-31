# import modules
import re
import arcgis
import pandas as pd

# where to get the organizations and credentials
web_gis_file = '.\\resources\\web_gis_list.csv'  # this file has to be created - it is not part of the repo

# load the web gis list into a pandas data frame, and drop any org's without all information
df_web_gis = pd.read_csv(web_gis_file, index_col='name')
df_web_gis.dropna(inplace=True)

# pike can be referenced by the DNS pike, and by the amazon url, so we have to account for both
server_01 = 'pike'
server_02 = 'ec2-54-210-26-63.compute-1.amazonaws.com'
server_list = [server_01, server_02]
regex_list = [re.compile('((\.|//){}([.:]))'.format(server)) for server in server_list]


def server_in_url(server_url):
    """
    Helper function for determining if the server pattern is in the layer url.
    :param server_url:
    :return: Boolean True or false
    """
    # try both server names
    for server_name in server_list:

        # if the server name is in the provided server url
        if server_name in server_url:

            # now try against the possible regular expressions, slightly slower, but more accurate
            for regex in regex_list:
                if len(regex.findall(server_url)):

                    # return true - this layer is an offender
                    return True

    # if nothing found by now, must be false - not an offender
    return False


def get_offendeing_maps_data_frame_for_organization(web_gis, gis):
    """
    Get a Pandas DataFrame of offending maps and layers.
    :param web_gis: Pandas Series with relevant information collected from the web gis file.
    :param gis: Esri Python API authenticated Web GIS.
    :return: Pandas Data Frame with relevant metrics.
    """
    # get all the web map items - really just piles of JSON
    webmap_item_list = gis.content.search(
        query='',
        max_items=10000,
        item_type='Web Map'
    )

    # this is our empty data frame to populate with the offending data
    df_maps = pd.DataFrame(columns=['organization', 'map_name', 'map_link', 'layer_name', 'layer_item_link',
                                    'layer_url'])

    # iterate the web map items
    for webmap_item in webmap_item_list:

        try:

            # create a web map object instance for this web map item
            webmap = arcgis.mapping.WebMap(webmap_item)

            # for every layer being used in the web map
            for item_layer in webmap['operationalLayers']:

                # save a list of the JSON keys to test against
                key_list = list(item_layer.keys())

                # if the layer item has both a url and itemId key
                if 'visibleLayers' not in key_list and 'featureCollection' not in key_list and 'url' in key_list:

                    # test for the url as one of our blacklisted url's
                    if server_in_url(item_layer['url']):

                        # if a blacklisted url, add relevant information to the list
                        layer_series = pd.Series({
                            'organization': web_gis.name,
                            'map_name': webmap_item.title,
                            'map_link': '{}/home/item.html?aid={}'.format(gis._con._parsed_org_url,
                                                                         webmap_item.id),
                            'layer_name': item_layer['title'],
                            'service_url': item_layer['url']
                        })

                        # if the layer also happens to be an item in the org itself
                        if 'itemId' in key_list:

                            # save a link to the item in the org
                            layer_series['layer_item_url'] = '{}/home/item.html?id={}'.format(
                                gis._con._parsed_org_url, item_layer['itemId'])

                        else:
                            layer_series['layer_item_url'] = None

                        # add the offender to the list...
                        df_maps.append(layer_series, ignore_index=True)

        except Exception as e:
            print(e)
            print('{}/home/item.html?id={}'.format(gis._con._parsed_org_url, webmap_item.id))

    # return the data frame
    return df_maps


def get_offfending_maps():
    """
    Iterate the organizations to find maps containing offending data frames.
    :return: Pandas DataFrame with offender information.
    """
    # create a template data frame to populate
    df_maps = pd.DataFrame(columns=['organization', 'map_name', 'map_link', 'layer_name', 'layer_item_link',
                                    'layer_url'])

    # iterate the rows in teh data frame.
    for web_gis in df_web_gis.iterrows():

        # get the series out of the returned tuple
        web_gis = web_gis[1]

        # create a gis object instance for this organization
        gis = arcgis.gis.GIS(
            url=web_gis.url,
            username=web_gis.username,
            password=web_gis.password
        )

        # get a data frame of this organization's offending maps
        df_maps = df_maps.append(get_offendeing_maps_data_frame_for_organization(web_gis, gis), ignore_index=True)

    # return the master data frame
    return df_maps
