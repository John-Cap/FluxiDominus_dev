
class HardcodedTeleAddresses:

    def __init__(self) -> None:
        self.hardcodedDeviceTemplates = {
        'flowsynmaxi1': {
            'pafr': {
                'address': ['state', 'flowRatePumpA']
            },
            'pbfr': {
                'address': ['state', 'flowRatePumpB']
            },
            'sva': {
                'address': ['state', 'valveOpenA']
            },
            'svb': {
                'address': ['state', 'valveOpenB']
            },
            'svcw': {
                'address': ['state', 'valveOpenCW']
            },
            'pressA': {
                'address': ['state', 'pressFlowSynA']
            },
            'pressB': {
                'address': ['state', 'pressFlowSynB']
            },
            'pressSys': {
                'address': ['state', 'pressSystem']
            },
            'temp_1': {
                'address': ['state', 'tempReactor1']
            },
            'temp_2': {
                'address': ['state', 'tempReactor2']
            },
        },
        'flowsynmaxi2': {
            'pafr': {
                'address': ['state', 'flowRatePumpA']
            },
            'pbfr': {
                'address': ['state', 'flowRatePumpB']
            },
            'sva': {
                'address': ['state', 'valveOpenA']
            },
            'svb': {
                'address': ['state', 'valveOpenB']
            },
            'svcw': {
                'address': ['state', 'valveOpenCW']
            },
            'pressA': {
                'address': ['state', 'pressFlowSynA']
            },
            'pressB': {
                'address': ['state', 'pressFlowSynB']
            },
            'pressSys': {
                'address': ['state', 'pressSystem']
            },
            'temp_1': {
                'address': ['state', 'tempReactor1']
            },
            'temp_2': {
                'address': ['state', 'tempReactor2']
            },
        },
        'hotcoil1': {
            'temp': {
                'address': ['state','temp']
            },
            'status': {
                'address': ['state','state']
            }
        },
        'hotcoil2': {
            'temp': {
                'address': ['state','temp']
            },
            'status': {
                'address': ['state','state']
            }
        },
        'hotchip1': {
            'temp': {
                'address': ['state','temp']
            },
            'status': {
                'address': ['state','state']
            }
        },
        'hotchip2': {
            'temp': {
                'address': ['state','temp']
            },
            'status': {
                'address': ['state','state']
            }
        },
        'sf10vapourtec1': { #TODO - hoekom is hierdie waardes nie in "state" nie?
            'fr': {
                'address': ['settings', 'flowrate']
            },
            'pressSys': {
                'address': ['settings', 'pressure']
            }
        },
        'sf10vapourtec2': { #TODO - hoekom is hierdie waardes nie in "state" nie?
            'fr': {
                'address': ['settings', 'flowrate']
            },
            'pressSys': {
                'address': ['settings', 'pressure']
            }
        }
    };

    def getValueFromAddress(data, address):
        value = data
        for key in address:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        return value
    
if __name__=="__main__":
    diz={
        "deviceName": "sf10Vapourtec1",
        "deviceType": "Pump",
        "cmnd": "",
        "settings": {
            "mode": "",
            "flowrate": 0,
            "pressure": 0,
            "dose": 0,
            "gasflowrate": 0,
            "rampStartRate": 0,
            "rampStopRate": 0,
            "rampTime": 0
        },
        "state": {
            "status": "STOP",
            "valve": "A",
            "response": ""
        },
        "timestamp": "1721293412961"
    }
