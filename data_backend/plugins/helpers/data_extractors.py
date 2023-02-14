
class DataExtractors():

    def extract_wildfire_incident_values(attributes):
        """
        """
        attribute_keys = [
            'poly_GlobalID',
            'poly_IncidentName',
            'irwin_FireBehaviorGeneral',
            'irwin_CalculatedAcres',
            'irwin_PercentContained',
            'poly_DateCurrent',
            'poly_CreateDate'
        ]

        # None holds the lat/lon centroid values that
        # will come as part of the transform step
        return ([attributes[x] for x in attribute_keys] + [None])

    def extract_wildfire_perimeter_values(incident_id, rings):
        """
        """
        return ([(incident_id, i, x[0], x[1])
                 for i in range(len(rings))
                 for x in rings[i]
                 ])
