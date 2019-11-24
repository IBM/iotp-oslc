import requests
import json
import string
import random
import os
from dotenv import load_dotenv
load_dotenv()


sample_output = '[ { "address": "/dev/cu.usbmodem1411", "protocol": "serial", "protocol_label": "Serial Port (USB)", "boards": [ { "name": "Adafruit Feather M0", "FQBN": "adafruit:samd:adafruit_feather_m0" } ] }]'
devices = json.loads(sample_output)
print("Please select device")
count = 0
print("0: N/A")

if not devices:
    print("No devices found, please enter device type")
    device_type = input()
else:
    for device in devices[0]['boards']:
        count += 1
        print(str(count) + ": " + device['name'])
    print("Device # > ", end='')
    selection = input()
    device_type = devices[0]['boards'][int(selection)]["FQBN"].replace(":", "-")
# devices[int(selection) - 1]
# print("Provide unique device type (or press enter to generate one)")
# device_id = input()

if int(selection) > 0:
    print("Bootstrapping new device of type - " + device_type)

print("Provide unique device id (or press enter to generate one)")
device_id = input()
if (len(device_id) == 0):
    letters = string.ascii_lowercase
    length = 6
    device_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    print("Registering device with id - " + device_id )
else:
    print("Registering device with id - " + selection)

print("Registering device in Watson IoTP via OSLC APIs")
iotp_url = os.get_env('iotp_oslc_url') or "127.0.0.1"
iotp_org = os.get_env('iotp_org')
endpoint = "/iotp/services/iotp" + iotp_org

# See if device type is already registered
check_device_type = requests.get( iotp_url + endpoint + "/devicetype/" + device_type )
if ( check_device_type.status == 200):
    # if get request is not 200, device type doesn't exist, so create it here
    create_device_type = requests.post( iotp_url + endpoint + "/devicetype/" + device_type )
    print("Device Type " + device_type + " created" )
create_device = requests.post( iotp_url + endpoint + "/device/" + device_id )
# requests.post(iotp_url, headers)
print("IoTP Device Registered")


print("Registering device in Maximo via OSLC APIs")
max_token = os.getenv('max_token')
headers = {'maxauth': max_token, 'contentType': 'application/json'}
maximo_url = os.getenv('maximo_url')
endpoint = "/maxrest/rest/mbo/ASSET/?assetnum=" + device_id + "&siteid=BEDFORD&_format=json"

# first check to see if asset is already registered
# asset_req = requests.get(maximo_url + "/maximo/oslc/os/mxasset?oslc.select=asset&oslc.where=assetnum=" + device_id)
# if asset_req.res == 200:
#     print("Asset already exists in Maximo, skipping")
# else:
create_maximo_asset = requests.post(maximo_url + endpoint, headers=headers)
print(create_maximo_asset)
print(create_maximo_asset.text)
print("Maximo Asset Registered")
