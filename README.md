# FiresideSat

## About

FiresideSat is a tool to send wildfire and AQI data your (garmin)
satellite phone. 

The program's tasks are broken down into directed acyclic graphs
(DAGs) that are managed by Apache Airflow. The main tasks involve
adding and managing data in a postgreSQL database and sending reports
based on those data to the end user's phone. 

As of now, everything runs locally. When I go on (backpacking) trips,
I run docker-compose up -d, turn on the 'production' DAGs in the
airflow web gui, and then leave my computer running for the duration
of the trip.

In the near future, I'd like to add a frontend to support
adding/removing trips and users; and a way to easily deploy the
program to run in the cloud. 

## Installation

Coming soon

## Usage

Coming soon

