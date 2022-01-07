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

class Connected_led(Objet):

    # class attributes
    Type = None
    PIN = None
    _condition  = None      # threading condition
    _thread     = None      # thread to handle shutter's course

    def __init__(self, unitID, MQTT_PUB_TOPIC,MQTT_SUB_TOPIC,MQTT_SERVER,MQTT_PORT,Type, PIN, io_backend=None, upOutput=None, downOutput=None, stopOutput=None, shutdown_event=None, *args, **kwargs):
       
        self.Type = Type
        self.PIN = PIN
        super().__init__(unitID,MQTT_PUB_TOPIC,MQTT_SUB_TOPIC,MQTT_SERVER,MQTT_PORT)
         
    def on_message(self, client, userdata, msg): 
        
        payload = json.loads(msg.payload)
        # the les with get the commands ON or OFF and change their state according to it
        if payload['dest'] == self.Type:
            #it is the destination
            if payload['order'] == "On":
                # turn on the LED
                GPIO.setup(self.PIN,GPIO.OUT)  
                GPIO.output(self.PIN,GPIO.HIGH)
            else:
                # turn off the LED
                GPIO.setup(self.PIN,GPIO.OUT)  
                GPIO.output(self.PIN,GPIO.LOW)
                

#
# MAIN
#

def main():
    #TODO: implement simple tests of your module
    return 


# Execution or import
if __name__ == "__main__":
    main()





