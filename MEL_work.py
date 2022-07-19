import jsonpickle
import requests


class MelWork:
    MELCloudURI = ''
    number_of_mels = 0
    token = ''

    def __init__(self, token, number_of_mels):
        self.token = token
        self.number_of_mels = number_of_mels
        self.MELCloudURI = 'https://app.melcloud.com/Mitsubishi.Wifi.Client'

    def login(self, email, password):
        data_mel = requests.post(self.MELCloudURI + '/Login/ClientLogin',
                                 data=jsonpickle.encode(
                                     {'Email': email, 'Password': password,
                                      'Language': 16, 'AppVersion': '1.19.1.1', 'Persist': True,
                                      'CaptchaResponse': None},
                                     unpicklable=False),
                                 headers={"Content-Type": "application/json",
                                          "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:73.0) Gecko/20100101 Firefox/73.0"})
        if data_mel.status_code == 200:
            json_data = data_mel.json()
            if json_data['ErrorId'] != None:
                print('WrongPassword')
                return '',"CHANGE CREDITALS"

            self.token = json_data['LoginData']['ContextKey']

            return json_data['LoginData']['Name'], self.token
        else:
            return '', "CHANGE CREDITALS"

    def GetDevices(self):
        devices = requests.get(self.MELCloudURI + '/User/ListDevices',
                               headers={"Content-Type": "application/json",
                                        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:73.0) Gecko/20100101 Firefox/73.0",
                                        "Accept": "application/json, text/javascript, */*; q=0.01",
                                        "Accept-Language": "en-US,en;q=0.5",
                                        "Accept-Encoding": "gzip, deflate, br",
                                        "X-MitsContextKey": self.token,
                                        "X-Requested-With": "XMLHttpRequest",
                                        "Cookie": "policyaccepted=true"})
        if devices.status_code == 200:
            devices = devices.json()[0]["Structure"]["Floors"][0]["Areas"]

            BuldingId = devices[0]['BuildingId']
            out_devices = {}

            for i in range(1, self.number_of_mels + 1):
                device = devices[i-1]['Devices'][0]
                out_devices['led'+str(i)] = [device['DeviceName'], device['Device']['RoomTemperature'], -1, device['Device']['Power'], device['DeviceID']]

            return BuldingId, out_devices
        else:
            print(devices.status_code)
            return 0, {}

    def UpdateCond(self, id):
        state_update = requests.get(self.MELCloudURI + f"/Device/RequestRefresh?id={id}",
                                    headers={"Content-Type": "application/json",
                                             "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:73.0) Gecko/20100101 Firefox/73.0",
                                             "Accept": "application/json, text/javascript, */*; q=0.01",
                                             "Accept-Language": "en-US,en;q=0.5",
                                             "Accept-Encoding": "gzip, deflate, br",
                                             "X-MitsContextKey": self.token,
                                             "X-Requested-With": "XMLHttpRequest",
                                             "Cookie": "policyaccepted=true"})
        if state_update.status_code == 200:
            if state_update.text == 'true':
                return True
            else:
                return False
        else:
            return f'ERROR: {state_update.status_code}'