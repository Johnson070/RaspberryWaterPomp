from threading import Thread

from flask import Flask, render_template, request
import time, jsonpickle, pymelcloud, requests

import data_class, MEL_work


number_of_mels = 5
startTime = time.time()

app = Flask(__name__)
data = data_class.Data(wifi=['', ''], mel=['', ''])
mel_cloud = MEL_work.MelWork('', number_of_mels)

def WorkPomps():
    while True:
        pass

def threaded_task():
    if data.token == '':
        data.name, data.token = mel_cloud.login(data.mel[0], data.mel[1])

        UpdateStatesDevices()
    while True:
        if data.autoUpdate:
            for key in data.states.keys():
                print(mel_cloud.UpdateCond(data.states[key][4]))

            UpdateStatesDevices()
        time.sleep(60 * 5)

def UpdateStatesDevices():
    raw_data = {}
    data.BuldingId, raw_data = mel_cloud.GetDevices()

    if raw_data == {}:
        data.token = "SERVER IS DOWN or UNKNOWN ERROR"
        return

    for key in raw_data.keys():
        pin = 1
        if key in data.states.keys():
            pin = data.states[key][2]

        data.states[key] = raw_data[key]
        data.states[key][2] = pin

@app.route('/GP_update', methods=['GET'])
def update():
    keys_update = list(request.args.keys())
    if 'update' in keys_update:
        uptime = time.time() - startTime
        json = {'devices': {key: value[3] for (key, value) in zip(data.states.keys(), data.states.values())}}
        json[
            'uptime'] = f"{round(uptime / 60 / 60 / 24)} d {round(uptime / 60 / 60 % 24)} h {round(uptime / 60 % 60)} m {round(uptime % 60)} s"
        return jsonpickle.encode(
            json,
            unpicklable=False
        )

    return ""


@app.route('/GP_click', methods=['POST'])
def click():
    keys_update = list(request.args.keys())

    if 'ssid' in keys_update:
        data.wifi[0] = request.args.get('ssid')
    elif 'ssidPass' in keys_update:
        data.wifi[1] = request.args.get('ssidPass')
    elif 'email' in keys_update:
        data.mel[0] = request.args.get('email')
    elif 'emailPass' in keys_update:
        data.mel[1] = request.args.get('emailPass')
    elif 'enabTime' in keys_update:
        data.pompsTimers[0] = request.args.get('enabTime')
    elif 'stbTime' in keys_update:
        data.pompsTimers[1] = request.args.get('stbTime')
    elif 'btnSavePins' in keys_update:
        pass
        pass
    elif 'saveMelBtn' in keys_update:
        pass
    elif 'saveWifiBtn' in keys_update:
        pass
    elif 'rebootBtn' in keys_update:
        exit()
    elif 'swAuto' in keys_update:
        data.autoUpdate = True if request.args.get('swAuto') == '1' else False
    elif keys_update[0] in ['sw' + str(i+1) for i in range(0, number_of_mels)]:
        name = keys_update[0].replace('sw', 'led')
        data.states[name][3] = True if request.args.get(keys_update[0]) == '1' else False
    elif keys_update[0] in ['sel' + str(i+1) for i in range(0, number_of_mels)]:
        name = keys_update[0].replace('sel', 'led')
        data.states[name][2] = int(request.args.get(keys_update[0]))
        print(data.states)

    return ""


@app.route('/', methods=['GET'])
def main_page():
    return render_template('index.html',
                           name=data.name,
                           SSID=data.wifi[0],
                           SSIDPass=data.wifi[1],
                           Email=data.mel[0],
                           EmailPass=data.mel[1],
                           enabTime=data.pompsTimers[0],
                           stbTime=data.pompsTimers[1],
                           content=add_device(),
                           autoUpdate='checked' if data.autoUpdate else '',
                           uptime='----',
                           token=data.token)


def add_device():
    out_list_devices = ''
    for key, value in data.states.items():
        out_list_devices += f'<label id="">{value[0]} |</label>' \
                            f'<label id="">{value[1]} C </label>' \
                            f'<select name="{key.replace("led", "sel")}" id="{key.replace("led", "sel")}" onchange="GP_click(this)">' \
                            f'{get_check_ports(key)}' \
                            '</select>' \
                            f'<input class="led green" type="radio" {"checked" if value[3] else ""} disabled="" name="{key}" id="{key}">' \
                            '<label class="switch" style="">' \
                            f'<input type="checkbox" {"checked" if value[3] else ""} name="{key.replace("led", "sw")}" id="{key.replace("led", "sw")}" onclick="GP_click(this)">' \
                            '<span class="slider"></span></label><br>'
    return out_list_devices


def get_check_ports(select_port):
    return "".join(
        [f'<option value="{i}" {"selected" if data.states[select_port][2] == i else ""}>{i}</option>)' for i in
         range(1, number_of_mels + 1)])


if __name__ == '__main__':
    thread = Thread(target=threaded_task)
    thread.daemon = True
    thread.start()

    threadPomps = Thread(target=WorkPomps)
    threadPomps.daemon = True
    threadPomps.start()

    app.run(port=80, debug=False, threaded=True)
