import time
import json
import threading
import paho.mqtt.client as mqtt_client
import os
import sys
from connection import Objet
import RPi.GPIO as GPIO
import smbus

class Temperatue_sensor(Objet):

    # class attributes
    FREQUENCY        = 5
    subID            = None  # id of the object instance
    
    # attributes
    _status = None
    courseTime  = 30;       # (seconds) max. time for resend the data


    _curCmd     = None
    _thread     = None      # thread to handle shutter's course

    def __init__(self, unitID,subID, MQTT_PUB_TOPIC,MQTT_SUB_TOPIC,MQTT_SERVER,MQTT_PORT,FREQUENCY=60, *args, **kwargs):
       
        ''' Initialize object '''
        self.subID = subID
        super().__init__(unitID,MQTT_PUB_TOPIC,MQTT_SUB_TOPIC,MQTT_SERVER,MQTT_PORT)
      
    def get_temperature(self):
        
        bus = smbus.SMBus(1)
        config = [0x00, 0x00]
        bus.write_i2c_block_data(self.subID, 0x01, config)
        bus.write_byte_data(self.subID, 0x08, 0x03)

        time.sleep(0.05) 

        data = bus.read_i2c_block_data(self.subID, 0x05, 2)

        ctemp = ((data[0] & 0x1F) * 256) + data[1]

        if ctemp > 4095 :
            ctemp -= 8192

        ctemp = ctemp * 0.0625
        return ctemp
    
    
    def do_every(self):      
        #publish the detected value
        data = {
                "unitID": self.unitID,
                "subID": self.subID,
                "value": self.get_temperature(),   
                "value-units": "Celsius"
         }
        data_out = json.dumps(data)

        # send current data 
        self.connection.publish(self.mqtt_pub_topic, data_out)
        self._thread = threading.Timer(self.FREQUENCY, self.do_every)
        self._thread.start()
        

    

    def on_connect(self, client, userdata, flags, rc):
        if rc==0:
            self.connection.connected_flag = True
            print("Connection returned code: "+ str(rc))
            self.do_every()
            self.connection.subscribe(self.mqtt_sub_topic,qos=0)
        else:
             print("Bad connection Returned code= "+str(rc))
              
        
             
    def on_message(self, client, userdata, msg):
        
        payload = json.loads(msg.payload)
        # if this sensor in the destination
        if payload['dest'] == "all" or payload['dest'] == self.subID :
            #execute the commande
            print(payload)
            if payload['order'] == "frequency":
               self.FREQUENCY = payload['value']
                   
            elif payload['order'] =="capture":
                # sense the luminosity
                print("here")
                data = {
                        "unitID": self.unitID,
                        "subID": self.subID,
                        "value": self.get_temperature(),   
                        "value-units": "Celsius"
                 }
                data_out = json.dumps(data)
                # send the sensed data 
                self.connection.publish(self.mqtt_pub_topic, data_out)
            
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
    # Start executing
    main()



