import time
import json
import threading
import paho.mqtt.client as mqtt_client
import os
import sys
from connection import Objet
import RPi.GPIO as GPIO
import smbus

class Presence_sensor(Objet):

    # class attributes
    subID            = None  # id of the object instance
    PIN              = None  # a default value
    # attributes
    _status = None
    courseTime  = 30;       # (seconds) max. time for resend the data

    _curCmd     = None
    _thread     = None      # thread to handle shutter's course

    def __init__(self, PIN, unitID, subID, MQTT_PUB_TOPIC, MQTT_SERVER, MQTT_PORT,MQTT_SUB_TOPIC=None, *args, **kwargs):
       
        ''' Initialize object '''
        self.subID = subID
        GPIO.setmode(GPIO.BCM)
        self.PIN = PIN
        GPIO.setup(self.PIN,GPIO.IN,pull_up_down=GPIO.PUD_UP)
        super().__init__(unitID,MQTT_PUB_TOPIC,MQTT_SUB_TOPIC,MQTT_SERVER,MQTT_PORT)
        
        
      
    def presence_detected(self, pin):     
        print("a presence detection found")
        #publish the detected value
        data = {
                "unitID": self.unitID,
                "subID": self.subID,
                "value": not GPIO.input(pin)
         }
        data_out = json.dumps(data)
        # send current data
        self.connection.publish(self.mqtt_pub_topic, data_out)
        print("data sent")
       

    def on_connect(self, client, userdata, flags, rc):
        if rc==0:
            self.connection.connected_flag = True
            print("Connection returned code: "+ str(rc))
            # make a thread that waits for presence detection
            GPIO.add_event_detect(self.PIN, GPIO.BOTH, bouncetime=50)
            GPIO.add_event_callback(self.PIN, self.presence_detected)
                         
        else:
             print("Bad connection Returned code= "+str(rc))
    
    def on_message(self, client, userdata, msg):
        
        print("received data")
        payload = json.loads(msg.payload)

#
# MAIN
#

def main():

    #TODO: implement simple tests of your module
    return 


# Execution or import
if __name__ == "__main__":
    # Start executing
    main()




