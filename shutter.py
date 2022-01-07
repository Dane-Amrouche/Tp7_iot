#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Shutter module
#
# Thiebolt  aug.19  updated
# Francois  apr.16  initial release
#

import time
import json
import threading
import paho.mqtt.client as mqtt_client
import os
import sys
from connection import Objet
import RPi.GPIO as GPIO

#GREEN/UP LED
PIN_UP = 6
#RED/DOWN LED
PIN_DOWN = 12
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_UP,GPIO.OUT) 
GPIO.output(PIN_UP,GPIO.LOW)
GPIO.setup(PIN_DOWN,GPIO.OUT)  
GPIO.output(PIN_DOWN,GPIO.LOW)


class Shutter(Objet):

    # class attributes
    SHUTTER_POS_CLOSED  = 0
    SHUTTER_POS_OPEN    = 1
    SHUTTER_POS_BETWEEN = 2

    SHUTTER_ACTION_CLOSE    = 0
    SHUTTER_ACTION_OPEN     = 1
    SHUTTER_ACTION_STOP     = 2
    SHUTTER_ACTION_IDLE     = 3
    SHUTTER_ACTION_UNKNOWN  = 4

    SHUTTER_TYPE_WIRED = 0
    SHUTTER_TYPE_WIRELESS = 1

    MQTT_TYPE_TOPIC = "shutter"

    # Min. and max. values for shutter course time
    MIN_COURSE_TIME         = 5
    MAX_COURSE_TIME         = 60

    # attributes
    _status = None
    shutterType = SHUTTER_TYPE_WIRED
    courseTime  = 30;       # (seconds) max. time for shutter to get fully open / close

    _backend    = None      # current backends
    _upOutput   = None
    _downOutput = None
    _stopOutput = None

    _curCmd     = None
    _condition  = None      # threading condition
    _thread     = None      # thread to handle shutter's course

    def __init__(self, unitID, MQTT_PUB_TOPIC,MQTT_SUB_TOPIC,MQTT_SERVER,MQTT_PORT, shutterType="wired", courseTime=30, io_backend=None, upOutput=None, downOutput=None, stopOutput=None, shutdown_event=None, *args, **kwargs):
       
        ''' Initialize object '''
        self._status = self.SHUTTER_POS_CLOSED
        self._curCmd = self.SHUTTER_ACTION_IDLE
        self.courseTime = courseTime
        super().__init__(unitID,MQTT_PUB_TOPIC,MQTT_SUB_TOPIC,MQTT_SERVER,MQTT_PORT)
       

    def set_status(self):
        # end of command execution
        self._status = self.SHUTTER_POS_OPEN if self._curCmd == self.SHUTTER_ACTION_OPEN else self.SHUTTER_POS_CLOSED
        self.curCmd = self.SHUTTER_ACTION_IDLE
        GPIO.output(PIN_UP,GPIO.LOW)
        GPIO.output(PIN_DOWN,GPIO.LOW)
        # on completion send status
        data = {
                    "unitID": self.unitID,   
                    "status": self._status,   
                    "order": "UP" if self._curCmd == self.SHUTTER_ACTION_OPEN else "DOWN"
                }
        data_out = json.dumps(data)
        self.connection.publish(self.mqtt_pub_topic, data_out)

    def on_message(self, client, userdata, msg):
       
        payload = json.loads(msg.payload)
        if( self.unitID is not None and ( payload['dest'] == "all" or payload['dest'] == str(self.unitID) )):
            data = {
                    "unitID": self.unitID,   
                    "status": self._status,   
                    "order": payload['order']
                }
            print(data)
            data_out = json.dumps(data)
            
            # send current status 
            self.connection.publish(self.mqtt_pub_topic, data_out)
            
            #execute the commande
            if payload['order'] == "UP":
               if(self._curCmd != self.SHUTTER_ACTION_OPEN and self._status != self.SHUTTER_POS_OPEN):
                   self._curCmd = self.SHUTTER_ACTION_OPEN
                   # turn on the up led and set new status to between 
                   GPIO.output(PIN_UP,GPIO.HIGH)
                   GPIO.output(PIN_DOWN,GPIO.LOW)
                   self._status = self.SHUTTER_POS_BETWEEN
                   # start a timer to courseTime seconds 
                   self._thread = threading.Timer( self.courseTime, self.set_status)
                   self._thread.start()
                   print("timer started")
                   
            elif payload['order'] =="DOWN":
                # change the current cmd and execute close order
                if(self._curCmd != self.SHUTTER_ACTION_CLOSE and self._status != self.SHUTTER_POS_CLOSED):
                   self._curCmd = self.SHUTTER_ACTION_CLOSE
                   # turn on the up led and set new status to between 
                   GPIO.output(PIN_UP,GPIO.LOW)
                   GPIO.output(PIN_DOWN,GPIO.HIGH)
                   self._status = self.SHUTTER_POS_BETWEEN
                   # start a timer to courseTime seconds 
                   self._thread = threading.Timer( self.courseTime, self.set_status)
                   self._thread.start()
                   print("timer started")

            elif payload['order'] =="STOP":
                # cancel the current command end set the status to between if not on idle status
                if (self._curCmd != self.SHUTTER_ACTION_IDLE):
                    self._thread.cancel()
                    self._status = self.SHUTTER_POS_BETWEEN
                    self.curCmd = self.SHUTTER_ACTION_IDLE
                    GPIO.output(PIN_UP,GPIO.LOW)
                    GPIO.output(PIN_DOWN,GPIO.LOW)
                    # on completion send status
                    data = {
                                "unitID": self.unitID,   
                                "status": self._status,   
                                "order": payload['order']
                            }
                    data_out = json.dumps(data)
                    self.connection.publish(self.mqtt_pub_topic, data_out)  
                      
            elif payload['order'] =="STATUS":
                # already sent the status 
                return
            
            else:
                print("invalid command")
            
#
# MAIN
#

def main():

    #TODO: implement simple tests of your module
    return 


# Execution or import
if __name__ == "__main__":

    # Logging setup
    '''logging.basicConfig(format="[%(asctime)s][%(module)s:%(funcName)s:%(lineno)d][%(levelname)s] %(message)s", stream=sys.stdout)
    log = logging.getLogger()

    print("\n[DBG] DEBUG mode activated ... ")
    log.setLevel(logging.DEBUG)'''
    #log.setLevel(logging.INFO)

    # Start executing
    main()


# The END - Jim Morrison 1943 - 1971
#sys.exit(0)

