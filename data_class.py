class Data:
    name = ''
    states = {}
    wifi = []
    mel = []
    pompsTimers = [10000,5000]
    autoUpdate = True

    BuldingId = 0


    token = ''

    def __init__(self, mel = ['',''], wifi=['',''], token=''):
        self.states = {'led1': ['Гостинная', '22.0', 2, True, 0],'led2': ['Спальня', '25.0', 1, False, 0]}
        self.mel = mel
        self.wifi = wifi
        self.pompsTimers = [10000,5000]
        self.token = token
        self.autoUpdate = True