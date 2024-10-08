
class HardcodedTeleAddresses:

    hardcodedTeleAddresses = {
        'flowsynmaxi1': {
            'pafr': {
                'address': ['tele','state','flowRatePumpA'],
                'displayName': 'Pump A Flowrate'
            },
            'pbfr': {
                'address': ['tele','state', 'flowRatePumpB'],
                'displayName': 'Pump B Flowrate'
            },
            'sva': {
                'address': ['tele','state', 'valveOpenA'],
                'displayName': 'Valve A Open'
            },
            'svb': {
                'address': ['tele','state', 'valveOpenB'],
                'displayName': 'Valve B Open'
            },
            'svcw': {
                'address': ['tele','state', 'valveOpenCW'],
                'displayName': 'Collecting'
            },
            'pressA': {
                'address': ['tele','state', 'pressFlowSynA'],
                'displayName': 'Pump A Pressure'
            },
            'pressB': {
                'address': ['tele','state', 'pressFlowSynB'],
                'displayName': 'Pump B Pressure'
            },
            'pressSys': {
                'address': ['tele','state', 'pressSystem'],
                'displayName': 'System Pressure'
            },
            'temp_1': {
                'address': ['tele','state', 'tempReactor1'],
                'displayName': 'Heater Temperature'
            },
            'temp_2': {
                'address': ['tele','state', 'tempReactor2'],
                'displayName': 'Coil Temperature'
            }
        },
        'flowsynmaxi2': {
            'pafr': {
                'address': ['tele','state','flowRatePumpA'],
                'displayName': 'Pump A Flowrate'
            },
            'pbfr': {
                'address': ['tele','state', 'flowRatePumpB'],
                'displayName': 'Pump B Flowrate'
            },
            'sva': {
                'address': ['tele','state', 'valveOpenA'],
                'displayName': 'Valve A Open'
            },
            'svb': {
                'address': ['tele','state', 'valveOpenB'],
                'displayName': 'Valve B Open'
            },
            'svcw': {
                'address': ['tele','state', 'valveOpenCW'],
                'displayName': 'Collecting'
            },
            'pressA': {
                'address': ['tele','state', 'pressFlowSynA'],
                'displayName': 'Pump A Pressure'
            },
            'pressB': {
                'address': ['tele','state', 'pressFlowSynB'],
                'displayName': 'Pump B Pressure'
            },
            'pressSys': {
                'address': ['tele','state', 'pressSystem'],
                'displayName': 'System Pressure'
            },
            'temp_1': {
                'address': ['tele','state', 'tempReactor1'],
                'displayName': 'Heater Temperature'
            },
            'temp_2': {
                'address': ['tele','state', 'tempReactor2'],
                'displayName': 'Coil Temperature'
            }
        },
        'hotcoil1': {
            'temp': {
                'address': ['tele','state','temp'],
                'displayName': 'Temperature'
            },
            'status': {
                'address': ['tele','state','state'],
                'displayName': 'Status'
            }
        },
        'hotcoil2': {
            'temp': {
                'address': ['tele','state','temp'],
                'displayName': 'Temperature'
            },
            'status': {
                'address': ['tele','state','state'],
                'displayName': 'Status'
            }
        },
        'hotchip1': {
            'temp': {
                'address': ['tele','state','temp'],
                'displayName': 'Temperature'
            },
            'status': {
                'address': ['tele','state','state'],
                'displayName': 'Status'
            }
        },
        'hotchip2': {
            'temp': {
                'address': ['tele','state','temp'],
                'displayName': 'Temperature'
            },
            'status': {
                'address': ['tele','state','state'],
                'displayName': 'Status'
            }
        },
        'sf10vapourtec1': { #TODO - hoekom is hierdie waardes nie in "state" nie?
            'fr': {
                'address': ['tele','settings', 'flowrate'],
                'displayName':'Flowrate'
            },
            'pressSys': {
                'address': ['tele','settings', 'pressure'],
                'displayName':'Pressure'
            }
        },
        'sf10vapourtec2': { #TODO - hoekom is hierdie waardes nie in "state" nie?
            'fr': {
                'address': ['tele','settings', 'flowrate'],
                'displayName':'Flowrate'
            },
            'pressSys': {
                'address': ['tele','settings', 'pressure'],
                'displayName':'Pressure'
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

    @staticmethod
    def getDisplayName(device,setting):
        device=device.lower()
        return (HardcodedTeleAddresses.hardcodedTeleAddresses[device][setting]).get('displayName','UNKNOWN')
    
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


    print(HardcodedTeleAddresses.getValFromAddress(diz,'flowsynmaxi1','pressSys'))
    print(HardcodedTeleAddresses.getDisplayName('sf10vapourtec1','pressSys'))