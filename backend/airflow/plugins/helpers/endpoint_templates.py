AIRNOW_RADIUS_ENDPOINT = "?format=application/json" \
    + "&latitude={lat}" \
    + "&longitude={lon}" \
    + "&distance={radius_miles}" \
    + "&API_KEY={key}"

WFIGS_CURRENT_INCIDENT_PERIMETERS_ENDPOINT = "WFIGS_Interagency_" \
    + "Perimeters_Current/" \
    + "FeatureServer/0/query?f=json&where=" \
    + "(attr_POOState%20IN%20('US-CA'))&outFields=*"

WFIGS_CURRENT_INCIDENT_LOCATIONS_ENDPOINT = "WFIGS_Incident_" \
    + "Locations_Current" \
    + "/FeatureServer/0/" \
    + "query?f=json&" \
    + "where=(POOState%20IN%20('US-CA'))&outFields=*"

WFIGS_TEST_INCIDENT_LOCATIONS_ENPOINT = "WFIGS_Incident_Locations" \
    + "/FeatureServer/0/" \
    + "query?f=json&where=" \
    + "(FireDiscoveryDateTime%20%3E%3D%20DATE%20'{data_interval_start}'%20" \
    + "AND" \
    + "%20FireDiscoveryDateTime%20%3C%3D%20DATE%20'{data_interval_start}')%20" \
    + "AND" \
    + "%20(POOState%20IN%20('US-CA'))" \
    + "&outFields=*"

WFIGS_TEST_INCIDENT_PERIMETERS_ENDPOINT = "WFIGS"\
    + "_Interagency_Perimeters/" \
    + "FeatureServer" \
    + "/0/query?f=json&where=" \
    + "(poly_CreateDate%20%3E%3D%" \
    + "20DATE%20'{data_interval_start}'%20" \
    + "AND" \
    + "%20poly_CreateDate%20%3C%3D%" \
    + "20DATE%20'{data_interval_start}')%20" \
    + "AND" \
    + "%20(attr_POOState" \
    + "%20IN%20('US-CA'))&outFields=*"

MAPSHARE_FEED_ENDPOINT = "{user}?imei={imei}"

SEND_MESSAGE_ENDPOINT = "{user}/Map/SendMessageToDevices"
