import time
import json
import threading
import paho.mqtt.client as mqtt_client
import os
import sys
from connection import Objet
import RPi.GPIO as GPIO
from time import sleep
from datetime import datetime

class Heater_actuator(Objet):

    # class attributes
    min_threshold = 19
    max_threshold = 23
    heater_topic = None
    _condition  = None      # threading condition
    _thread     = None      # thread to handle shutter's course

    def __init__(self, unitID, MQTT_PUB_TOPIC,MQTT_SUB_TOPIC,MQTT_SERVER,MQTT_PORT,min_threshold,max_threshold,heater_topic, io_backend=None, upOutput=None, downOutput=None, stopOutput=None, shutdown_event=None, *args, **kwargs):
       
        self.min_threshold = min_threshold
        self.max_threshold = max_threshold
        self.heater_topic = heater_topic
        super().__init__(unitID,MQTT_PUB_TOPIC,MQTT_SUB_TOPIC,MQTT_SERVER,MQTT_PORT)
         
         
    def get_date_time(self):
        
        weekdays= ("Lundi","Mardi","Mercredi","Jeudi","Vendredi","Samedi","Dimanche")
        # detect time and the day
        time = datetime.now().strftime("%H")
        date = datetime.today().weekday()
        return (weekdays[date],time)

    def on_message(self, client, userdata, msg): 
        #check that the presence respects the times that authorise access
       
        (day, hour) = self.get_date_time()
        hour = int(hour)
        payload = json.loads(msg.payload)
        
        if (day == "Samedi" and hour >= 8 and hour <= 15) or (day != "Samedi" and day != "Vendredi" and hour>=8 and hour <=20):
            if payload['value'] < self.min_threshold :
                # send a on command to heater
                data = {
                    "dest": "heater",
                    "order": "On"
                }
                data_out = json.dumps(data)
                # send current data 
                self.connection.publish(self.heater_topic, data_out)
            elif payload['value'] > self.max_threshold:
                # send a off command to heater
                data = {
                    "dest": "heater",
                    "order": "Off"
                }
                data_out = json.dumps(data)
                # send current data 
                self.connection.publish(self.heater_topic, data_out)
            
        # at the end of the day turn off the heater
        if (day == "Samedi" and hour > 15) or (day != "Samedi" and day != "Vendredi" and hour > 20):
            # send a off command to heater
            data = {
                "dest": "heater",
                "order": "Off"
            }
            data_out = json.dumps(data)
            # send current data 
            self.connection.publish(self.heater_topic, data_out)    

#
# MAIN
#

def main():
    #TODO: implement simple tests of your module
    return 


# Execution or import
if __name__ == "__main__":
    main()




