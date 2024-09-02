
class HardcodedTeleAddresses:

    hardcodedTeleAddresses = {
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
        },
        'sf10vapourtec2': { #TODO - hoekom is hierdie waardes nie in "state" nie?
            'fr': {
                'address': ['settings', 'flowrate']
            },
            'pressSys': {
                'address': ['settings', 'pressure']
            }
        },
        'a_bicycle_built_for_two':{
            'exampleSetting':{
                'address':['systemPressure']
            }
        }
    };

    @staticmethod
    def getValFromAddress(data,device,setting):
        device=device.lower()
        value = data
        for key in (HardcodedTeleAddresses.hardcodedTeleAddresses[device][setting]['address']):
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        return value
    
if __name__=="__main__":
    diz={
        "deviceName": "flowsynmaxi1",
        "deviceType": "PumpValveHeater",
        "settings": {
            "flowRatePumpA": 2500,
            "flowRatePumpB": 2500,
            "flowRatePumpC": 0,
            "flowRatePumpD": 0,
            "tempReactor1": 0,
            "tempReactor2": 0,
            "tempReactor3": 0,
            "tempReactor4": 0,
            "valveOpenA": False,
            "valveOpenB": False,
            "valveOpenC": False,
            "valveOpenD": False,
            "valveOpenCW": False,
            "injValveOpenA": False,
            "injValveOpenB": False,
            "injValveOpenC": False,
            "injValveOpenD": False,
            "heaterON": False
        },
        "state": {
            "pressSystem": 2.06,
            "pressFlowSynA": 9.12,
            "pressFlowSynB": 1.65,
            "pressBinaryC": 0,
            "pressBinaryD": 0,
            "tempReactor1": 20.35,
            "tempReactor2": 19.12,
            "tempReactor3": 999,
            "tempReactor4": 999,
            "valveOpenA": False,
            "valveOpenB": False,
            "valveOpenC": False,
            "valveOpenD": False,
            "valveOpenCW": False,
            "valveInjOpenA": False,
            "valveInjOpenB": False,
            "valveInjOpenC": False,
            "valveInjOpenD": False,
            "flowRatePumpA": 3.5,
            "flowRatePumpB": 0,
            "flowRatePumpC": 0,
            "flowRatePumpD": 0,
            "chillerDetected": False
        },
        "timestamp": "1721285147235"
    }


    print(HardcodedTeleAddresses.getValueFromAddress(diz,'flowsynmaxi1','pressSys'))