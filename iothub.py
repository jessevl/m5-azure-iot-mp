from umqtt.robust import MQTTClient
from hashlib._sha256 import sha256
import base64
import hmac
import urlencode
import _ntptime as ntptime
import time

class IothubClient():

    def __init__(self, connection_string):
        self._connection_string = connection_string
        self._lastUpdated = 0
        self._updateSas = True
        
        parsed_connection = self._parse_connection()
        self._shared_access_key = parsed_connection.get("SharedAccessKey")
        self._shared_access_key_name =  parsed_connection.get("SharedAccessKeyName")
        self._gateway_hostname = parsed_connection.get("GatewayHostName")
        self._hostname = parsed_connection.get("HostName")
        self._device_id = parsed_connection.get("DeviceId")
        self._module_id = parsed_connection.get("ModuleId")
        self._username = self._hostname + '/' + self._device_id
        self._c2d_cb = None
        
        self._sas = self._generate_sas_token()
        
        c = MQTTClient(client_id=self._device_id, server=self._hostname, port=8883, user=self._username, password=self._sas, keepalive=120, ssl=True)
        c.DEBUG = True
        c.set_callback(self._callback_handler)
        
        self._mqtt_client = c
        
    def connect(self):
        try:
            self._mqtt_client.reconnect()
            print("Connected to IoT Hub")
        except:
            print("Could not connect")
            
    def send_telemetry(self, msg):  
        try:
            topic=self._get_topic_base() + "/messages/events/"
            self._mqtt_client.publish(topic=topic, msg=msg)
        except:
            print("Could not send telemetry")
    
    def set_c2d_cb(self, cb):
        try:
            self._mqtt_client.subscribe(topic=self._get_topic_base() + "/messages/devicebound/#")
            self._c2d_cb = cb
        except:
            print("Could not set cloud2device msg callback")
            
    def check_msg(self):
        self._mqtt_client.check_msg()

    def _get_topic_base(self):
        if self._module_id:
            base_str = "devices/" + self._device_id + "/modules/" + self._module_id
        else:
            base_str = "devices/" + self._device_id
        return base_str

    def _parse_connection(self):
        cs_args = self._connection_string.split(";")
        dictionary = dict(arg.split("=", 1) for arg in cs_args)
        
        return dictionary
    
    def _generate_sas_token(self, expiry = 86400):  # default to one day expiry period
        print("Retrieving NTP time for token expiration")
        urlencoder=urlencode.Urlencode()

        now=0
        while now == 0:
            try:
                now=ntptime.time() + 946684800 # offset for embedded vs POSIX epoch.
            except:
                time.sleep(1)
                print("Failed retrieving NTP time, retrying.")
                
        print("Generating SAS token from key")
        ttl=now + expiry
        urlToSign=urlencoder.quote(self._hostname + '/devices/' + self._device_id)
        msg="{0}\n{1}".format(urlToSign, ttl).encode('utf-8')
        key=base64.b64decode(self._shared_access_key)
        h=hmac.HMAC(key, msg = msg, digestmod = sha256)
        decodedDigest=base64.b64encode(h.digest()).decode()
        signature=urlencoder.quote(decodedDigest)
        sas="SharedAccessSignature sr={0}&sig={1}&se={2}".format(
            urlToSign, signature, ttl)
        return sas
    
    def _renew_sas_token(self):     
        if time.ticks_diff(time.time(), self._lastUpdated) > 60 * 15:
            self._lastUpdated = time.time()
            self._updateSas = True

        if self._updateSas:
            self._sas = self._generate_sas_token()
            print('Updating Sas')
            self._updateSas = False
            
    def _callback_handler(self, topic, msg):
        print("Received c2d message: "+msg)
