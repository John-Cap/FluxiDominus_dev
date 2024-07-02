'''
import sys
import os
import socket
import time
import requests

import requests
import time
import base64

#Target URL
my_url = "http://192.168.1.2:1880/nmr1Cmnd"

#Voorbeeld payload
payload = {'deviceName':'nmr1','settings':{'command':'START','protocol':'1D'}}  # Replace with your actual payload

#Sender funksie
def send_post_request(url,data,headers):
    try:
        response = requests.post(url,data=data,headers=headers)
        print(response.json)
        print(f"POST request sent to {url}. Response: {response.status_code}")
    except Exception as e:
        print(f"Error sending POST request: {e}")


# Define login credentials
username = "user"
password = "flowie"

# Create a string with the credentials and encode in Base64
credentials = f'{username}:{password}'
credentials_b64 = base64.b64encode(credentials.encode('ascii')).decode('ascii')
print(credentials_b64)
# Create a dictionary of headers with Basic Authentication credentials
headers = {'Authorization': 'Basic ' + credentials_b64}

#Stuur requests
while True:
    send_post_request(my_url,headers=headers,data=payload)
    time.sleep(1)
'''