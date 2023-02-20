

class ApiCalls():

    airnow_bbox_url = "https://airnowapi.org/aq/data/" \
        + "?startDate={year}-{month}-{day}T{hour_start}" \
        + "&endDate={year}-{month}-{day}T{hour_end}" \
        + "&parameters=PM25" \
        + "&BBOX={bbox}" \
        + "&datatype=A" \
        + "&format=application/json" \
        + "&monitorType=2" \
        + "&verbose=0" \
        + "&includeconcentrations=0" \
        + "&api_key={api_key}"

    # https://www.airnowapi.org/aq/observation/latLong/current/
    airnow_radius_url = "?format=application/json" \
        + "&latitude={lat}" \
        + "&longitude={lon}" \
        + "&distance=150" \
        + "&API_KEY={key}"

    active_wildfire_incidents_url = "https://services3.arcgis.com/" \
        + "T4QMspbfLg3qTGWY/arcgis/rest/services/" \
        + "Current_WildlandFire_Perimeters/" \
        + "FeatureServer/0/query?f=json&where=" \
        + "(irwin_POOState%20IN%20(%27US-CA%27))&outFields=*"

    wildfire_incidents_test_url = "https://services3.arcgis.com/" \
        + "T4QMspbfLg3qTGWY/arcgis" \
        + "/rest/services/" \
        + "Fire_History_Perimeters_Public/" \
        + "FeatureServer" \
        + "/0/query?f=json&where=" \
        + "(poly_CreateDate%20%3E%3D%" \
        + "20DATE%20'{}'%20" \
        + "AND" \
        + "%20poly_CreateDate%20%3C%3D%" \
        + "20DATE%20'{}')%20" \
        + "AND" \
        + "%20(irwin_POOState" \
        + "%20IN%20('US-CA'))&ouFields=*"

    wildfire_incidents_test_endpoint = "Fire_History_Perimeters_Public/" \
        + "FeatureServer" \
        + "/0/query?f=json&where=" \
        + "(poly_CreateDate%20%3E%3D%" \
        + "20DATE%20'{}'%20" \
        + "AND" \
        + "%20poly_CreateDate%20%3C%3D%" \
        + "20DATE%20'{}')%20" \
        + "AND" \
        + "%20(irwin_POOState" \
        + "%20IN%20('US-CA'))&outFields=*"
