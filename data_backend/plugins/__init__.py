from __future__ import division, absolute_import, print_function

from airflow.plugins_manager import AirflowPlugin

import operators
import helpers


# Defining the plugin class
class FirePlugin(AirflowPlugin):
    name = "fire_plugin"
    operators = [
        operators.LoadWildfireData
    ]
    helpers = [
        helpers.SqlQueries,
        helpers.ApiCalls,
        helpers.DataExtractors,
    ]
