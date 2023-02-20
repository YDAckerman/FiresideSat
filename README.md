# FiresideSat

## About

FiresideSat is a tool to connect my (your?) garmin in-reach mini to various wildfire-related data.

## Current Goals

As I was recently reminded, fire perimeters are only part of the
problem when one is off-grid. Smoke and air-quality tracking (and
prediction) are also essential.  

## Updates

02-20-2021 - a prototype for the 'data backend' is working. Lots of different tests to run. Certainly not robust. Expected downtime this week for one of the apis - might be nice to see how the thing breaks. Next: connecting to garmin device (also via airflow?). Then user back-end and front-end. 

08-04-2022 - The current design of the project won't work because, as
far as I can tell, both twilio and the sat phone will only have
conversations if they can initiate them. Instead I'm going to take a
different approach using Garmin's MapShare feature. This won't be as
responsive, since I'll have to be checking their periodically for
updates, as opposed to running a lambda function on an sms
trigger. But that will probably be fine enough. From a cost
perspective, this might actually be better, as messages FiresideSat
sends will be billed on Garmin's end for that user. I won't get
charged for twilio messages and I'll be able to keep aws resource
usage 'fixed' per user. 

09-04-2022 - The new approach is taking shape. I'll end up using a
chron job (I think) to monitor the device's KML feed and use the feed
information to make decisions regard what information to send back to
the device. I feel like the feed should be reporting more events, but
so far, I've only seen "Tracking turned on" and "Tracking turned off"
(despite having sent messages and set waypoints during tracking). It's
minimal and not great, but that means I can just do fire monitoring
while tracking is turned on (being careful not to repeat messages) and
stop when tracking is turned off. I guess I can live with that until I
figure out how to get the messages sent to the MapShare site, which so
far has eluded me. 

testing
