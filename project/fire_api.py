
# __________________NOTES__________________
# state park boundaries:
# https://www.parks.ca.gov/?page_id=29682
# national park boundaries:
# https://irma.nps.gov/DataStore/Reference/Profile/2224545?lnv=True
# national park air quality monitors:
# https://www.nps.gov/subjects/air/current-data.htm
# _________________________________________


# incident point of origin
# format:
# FireDiscoveryDate: YYYY-MM-DD
# POOState: US-CA, etc.
incident_poo_url = """
https://services3.arcgis.com/
T4QMspbfLg3qTGWY/arcgis/rest/services/
Current_WildlandFire_Locations/FeatureServer
/0/query?f=json&where=
(FireDiscoveryDateTime%20%>%3D%20DATE%20%27{}%27)
%20AND%20
(POOState%20IN%20('{}')
&outFields=*
"""

# incident perimeter
# format:
# poly_IncidentName: Washburn, etc.
incident_perimeter_url = """
https://services3.arcgis.com/
T4QMspbfLg3qTGWY/arcgis/rest/services/
Current_WildlandFire_Perimeters/
FeatureServer/0/query?f=json&where=
(poly_IncidentName%20IN%20(%27{}%27))
&outFields=*
"""
