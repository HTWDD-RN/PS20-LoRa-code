import time
import ttn
import codecs 
from configparser import ConfigParser
import csv
import signal 
import sys


#Read config.ini file
config_object = ConfigParser()
config_object.read("config.ini")

app_id = "test-lora-uni"
access_key = config_object["TEST-LORA-UNI"]["access_key"]

def signal_handler(signal, frame):
    sys.exit(0)

def uplink_callback(msg, client):
  with open('test.csv', 'a', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    writer.writerow([ msg.metadata.time, 
                      msg.payload_fields.Text])
  print(msg.metadata.time)
  print(msg.payload_fields.Text)


signal.signal(signal.SIGINT, signal_handler)
print("Beende die Application mit [CTRL] + [C]\n")

handler = ttn.HandlerClient(app_id, access_key)

# using mqtt client
mqtt_client = handler.data()
mqtt_client.set_uplink_callback(uplink_callback)
mqtt_client.connect()
# time.sleep(60)
# mqtt_client.close()
while True :
    pass
