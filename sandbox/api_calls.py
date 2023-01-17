
current_wildfire_incidents_url = "https://services3.arcgis.com/T4QMspbfLg3qTGWY/" + \
    "arcgis/rest/services/Current_WildlandFire_Perimeters/" + \
    "FeatureServer/0/query?f=json&where=" + \
    "(irwin_POOState%20IN%20(%27US-CA%27))&outFields=*"

historic_wildfire_incidents_url = "https://services3.arcgis.com/T4QMspbfLg3qTGWY/" + \
    "arcgis/rest/services/Fire_History_Perimeters_Public/" + \
    "FeatureServer/0/query?f=json&where=" + \
    "(poly_CreateDate%20%3E%3D%20DATE%20'2022-04-01'%20" + \
    "AND" + \
    "%20poly_CreateDate%20%3C%3D%20DATE%20'2022-09-28')%20" + \
    "AND" + \
    "%20(irwin_POOState%20IN%20('US-CA'))&outFields=*"
