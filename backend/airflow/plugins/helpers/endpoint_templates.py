
AIRNOW_RADIUS_TEMPLATE = "?format=application/json" \
    + "&latitude={lat}" \
    + "&longitude={lon}" \
    + "&distance={radius_miles}" \
    + "&API_KEY={key}"

WFIGS_CURRENT_INCIDENT_PERIMETERS_TEMPLATE = "WFIGS_Interagency_" \
    + "Perimeters_Current" \
    + "/FeatureServer/0/query?f" \
    + "=json&where=(" \
    + "attr_UniqueFireIdentifier%20IN%20(%27{}%27))" \
    + "&outFields=*"

WFIGS_CURRENT_INCIDENT_LOCATIONS_TEMPLATE = "WFIGS_Incident_" \
    + "Locations_Current" \
    + "/FeatureServer/0/" \
    + "query?f=json&" \
    + "where=(POOState%20IN%20('US-CA'%2C'US-OR'%2C'US-WA'))&outFields=*"

WFIGS_TEST_INCIDENT_LOCATIONS_ENPOINT = "WFIGS_Incident_Locations" \
    + "/FeatureServer/0/query?f=json&" \
    + "where=" \
    + "(POOState%20IN%20(%27US-CA%27))" \
    + "%20AND%20" \
    + "(IncidentName%20IN%20(%27DIXIE%27))" \
    + "%20AND%20(" \
    + "CreatedOnDateTime_dt%20%3E%3D%20DATE%20%27{data_interval_start}%27" \
    + "%20AND%20" \
    + "CreatedOnDateTime_dt%20%3C%3D%20DATE%20%27{data_interval_end}%27" \
    + ")&outFields=*"

WFIGS_TEST_INCIDENT_PERIMETERS_TEMPLATE = "WFIGS_Interagency_Perimeters" \
    + "/FeatureServer/0/query?f" \
    + "=json&where=(" \
    + "attr_UniqueFireIdentifier%20IN%20(%27{}%27))" \
    + "&outFields=*"

MAPSHARE_FEED_TEMPLATE = "{user}?imei={imei}"

SEND_MESSAGE_TEMPLATE = "{user}/Map/SendMessageToDevices"
