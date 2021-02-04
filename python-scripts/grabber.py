import time
import ttn
import codecs 
from configparser import ConfigParser
import csv
import signal 
import sys

# Global Variable
id = 1

def signal_handler(signal, frame):
    sys.exit(0)

def uplink_callback(msg, client):
  global id
  with open('data.csv', 'a', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    for gateway in msg.metadata.gateways:
      writer.writerow([ id, gateway.gtw_id,
                        msg.metadata.time, msg.metadata.frequency,
                        msg.metadata.data_rate, gateway.rssi,
                        msg.payload_fields.gps_3.altitude, msg.payload_fields.gps_3.latitude, msg.payload_fields.gps_3.longitude])
      print(
        str(id) + "," + gateway.gtw_id + "," +
        msg.metadata.time + "," + str(msg.metadata.frequency) + "," +
        msg.metadata.data_rate + "," + str(gateway.rssi) + "," +
        str(msg.payload_fields.gps_3.altitude) + "," + str(msg.payload_fields.gps_3.latitude) + "," + str(msg.payload_fields.gps_3.longitude)
      )
  id += 1


if __name__ == "__main__":
  # Read config.ini file and setup variables
  config_object = ConfigParser()
  config_object.read("config.ini")
  app_id = "ps20-lora-htw-dresden"
  access_key = config_object["PS20-LORA-HTW-DRESDEN"]["access_key"]

  # Setup Signal Handler
  signal.signal(signal.SIGINT, signal_handler)
  print("Beende die Application mit [CTRL] + [C]\n")

  # Connect to TTN
  handler = ttn.HandlerClient(app_id, access_key)
  mqtt_client = handler.data()
  mqtt_client.set_uplink_callback(uplink_callback)
  mqtt_client.connect()

  # Setup Table + Headers
  with open('data.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    writer.writerow([ "id", 
                      "gtw-id",
                      "time", 
                      "frequency",
                      "data-rate", 
                      "rssi",
                      "alt",
                      "lat", 
                      "long"])

  while True :
    # Endless Loop
    pass