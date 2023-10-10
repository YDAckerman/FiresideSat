from helpers.sql_queries import SqlQueries

sql = SqlQueries()

USER_AQI_REPORT = {
    'columns': ["user_id",
                "point_id",
                "mapshare_id",
                "mapshare_pw",
                "device_id",
                "max_aqi",
                "min_aqi",
                "aqi_date"],
    'message_template': '{aqi_date}-AQI: {max_aqi}(max), {min_aqi}(min)',
    'records_sql': sql.select_active_users_latest_aqi,
    'save_sql': sql.insert_user_aqi_report
}

TRIP_STATE_REPORT = {
            'columns': ["user_id",
                        "mapshare_id",
                        "mapshare_pw",
                        "trip_id",
                        "start_date",
                        "end_date",
                        "device_id",
                        "state",
                        "date_sent"],
            'message_template': '{state} incident reports '
            + 'for trip dates {start_date} to {end_date}',
            'message_header': '',
            'records_sql': sql.select_state_change_users,
            'save_sql': sql.insert_trip_state_report
        }

INCIDENT_REPORT = {
            'columns': ["user_id", "incident_id",
                        "incident_last_update",
                        "aqi_last_update",
                        "total_acres",
                        "incident_behavior",
                        "incident_name",
                        "dist_m_to_center",
                        "centroid_lon",
                        "centroid_lat",
                        "max_aqi",
                        "aqi_obs_lon",
                        "aqi_obs_lat",
                        "mapshare_id",
                        "mapshare_pw",
                        "device_id",
                        "row_num"],
            'message_template': '{incident_name}|'
            + 'u:{incident_last_update}|'
            + 's:{total_acres}|'
            + 'c:{centroid_lat},{centroid_lon}|'
            + 'd:{dist_m_to_center}|'
            + 'aqi:{max_aqi}',
            'records_sql': sql.select_user_incidents,
            'save_sql': sql.insert_incident_report
        }

REPORTS_DICT = {
        "trip_state_report": TRIP_STATE_REPORT,
        'incident_report': INCIDENT_REPORT,
        'user_aqi_report': USER_AQI_REPORT
    }
