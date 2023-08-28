# FiresideSat

## About

FiresideSat is a tool to send wildfire and AQI data your (garmin)
satellite phone. 

The program's tasks are divided into directed acyclic graphs
(DAGs) that are managed by Apache Airflow. The main tasks involve
adding and managing data in a postgreSQL database and sending reports
based on those data to the end user's phone. 

As of now, everything works, but only runs locally. Before going into
the backcountry, I run docker-compose up -d, turn on the 'production'
DAGs in the airflow web gui, and then leave my computer running for
the duration of the trip. To get it running on your own,
however, will take a bit of setup, including setting an airnow.gov api
key and doing some data entry via SQL. If that is something you'd like
to do, feel free to reach out to me via email and I will be more than
happy to assist.

I am currently working on a browser-based frontend for the service
to allow adding/modifying users and trips. 

## Installation

Coming soon

## Usage

Coming soon

