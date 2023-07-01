from helpers.elt_funs import elt_wildfire_locations, \
    elt_wildfire_perimeters, \
    elt_mapshare_locs, \
    elt_fire_locs_aqi
from helpers.endpoint_templates import MAPSHARE_FEED_TEMPLATE, \
    AIRNOW_RADIUS_TEMPLATE, \
    WFIGS_TEST_INCIDENT_PERIMETERS_TEMPLATE, \
    WFIGS_TEST_INCIDENT_LOCATIONS_ENPOINT, \
    WFIGS_CURRENT_INCIDENT_PERIMETERS_TEMPLATE, \
    WFIGS_CURRENT_INCIDENT_LOCATIONS_TEMPLATE

MAPSHARE = {'elt_fun': elt_mapshare_locs,
            'template': MAPSHARE_FEED_TEMPLATE}

AIRNOW = {'elt_fun': elt_fire_locs_aqi,
          'template': AIRNOW_RADIUS_TEMPLATE}

TEST_PERIMS = {'elt_fun': elt_wildfire_perimeters,
               'template': WFIGS_TEST_INCIDENT_PERIMETERS_TEMPLATE}

TEST_LOCS = {'elt_fun': elt_wildfire_locations,
             'template': WFIGS_TEST_INCIDENT_LOCATIONS_ENPOINT}

CUR_PERIMS = {'elt_fun': elt_wildfire_perimeters,
              'template': WFIGS_CURRENT_INCIDENT_PERIMETERS_TEMPLATE}

CUR_LOCS = {'elt_fun': elt_wildfire_locations,
            'template': WFIGS_CURRENT_INCIDENT_LOCATIONS_TEMPLATE}

PROCESS_DICT = {
        'mapshare': MAPSHARE,
        'airnow': AIRNOW,
        'test_perimeters': TEST_PERIMS,
        'test_locations': TEST_LOCS,
        'current_perimeters': CUR_PERIMS,
        'current_locations': CUR_LOCS
}
