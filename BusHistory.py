import json

bushistoryKeys = ["vehicleNumber", "routeId", "varId", "tripList"]

class BusHistory:
    def __init__(self, bus_history = None):
        for key, value in bus_history.items():
            setattr(self, key, value)

    def setProperty(self, key, value):
        setattr(self, key, value)

    def getProperty(self, key):
        return getattr(self, key)

class BusHistoryQuery:
    def __init__(self, bus_historys = []):
        self._bus_historys = bus_historys

    def readJSONInput(self, file_name):
        with open(file_name, 'r', encoding='utf-8') as f:
            for line in f:
                bus_history_data = json.loads(line)
                bus_history = BusHistory(bus_history_data)
                self._bus_historys.append(bus_history)

    def getBusHistorys(self):
        return self._bus_historys
