
class HardcodedCommandTemplates:
    commandTemplates={
        #Vapourtec SF10's
        "sf10vapourtec1_fr":'''
            {
                "deviceName":"sf10Vapourtec1",
                "inUse":True,
                "connDetails":{
                    "serialCom":{
                        "port":"/dev/ttyUSB0",
                        "baud":9600,
                        "dataLength":8,
                        "parity":"N",
                        "stopbits":1
                    }
                },
                "settings":{"command":"SET","mode":"FLOW","flowrate":>float<},
                "topic":"subflow/sf10vapourtec1/cmnd",
                "client":"client"
            }
        ''',
        "sf10vapourtec2_fr":'''
            {
                "deviceName":"sf10Vapourtec2",
                "inUse":True,
                "connDetails":{
                    "serialCom":{
                        "port":"/dev/ttyUSB0",
                        "baud":9600,
                        "dataLength":8,
                        "parity":"N",
                        "stopbits":1
                    }
                },
                "settings":{"command":"SET","mode":"FLOW","flowrate":>float<},
                "topic":"subflow/sf10vapourtec2/cmnd",
                "client":"client"
            }
        ''',
        
        #Hotcoils
        "hotcoil1_temp":'''
            {
                "deviceName":"hotcoil1",
                "inUse":True,
                "connDetails":{
                    "ipCom":{
                        "addr":"192.168.1.213",
                        "port":81
                    }
                },
                "settings": {"command":"SET","temp":>float<},
                "topic":"subflow/hotcoil1/cmnd",
                "client":"client"
            }
        ''',
        "hotcoil2_temp":'''
            {
                "deviceName":"hotcoil2",
                "inUse":True,
                "connDetails":{
                    "ipCom":{
                        "addr":"192.168.1.202", !!Change IP
                        "port":81
                    }
                },
                "settings": {"command":"SET","temp":>float<},
                "topic":"subflow/hotcoil2/cmnd",
                "client":"client"
            }
        ''',
        
        #Hotchips
        "hotchip1_temp":''' #TODO
            {
                "deviceName":"hotchip1", 
                "inUse" : True,
                "command":"SET", 
                "temperatureSet":>float<,
                "topic":"subflow/hotchip1/cmnd",
                "client":"client"                    
            }
        ''',
        "hotchip2_temp":'''
            {
                "deviceName":"hotchip2", 
                "inUse" : True,
                "command":"SET", 
                "temperatureSet":>float<,
                "topic":"subflow/hotchip2/cmnd",
                "client":"client"                    
            }
        ''',
        
        #Maxi
        "flowsynmaxi1_pafr":'''
            {
                "deviceName": "flowsynmaxi1",
                "inUse":True,
                "connDetails": {
                    "ipCom": {
                        "addr": "192.168.1.202",
                        "port": 80
                    }
                },
                "settings": {
                    "command": "SET",
                    "subDevice": "PumpAFlowRate",
                    "value": >float<
                },
                "topic":"subflow/flowsynmaxi1/cmnd",
                "client":"client"
            }
        ''',
        "flowsynmaxi1_pbfr":'''
            {
                "deviceName": "flowsynmaxi1",
                "inUse":True,
                "connDetails": {
                    "ipCom": {
                        "addr": "192.168.1.202",
                        "port": 80
                    }
                },
                "settings": {
                    "command": "SET",
                    "subDevice": "PumpBFlowRate",
                    "value": >float<
                },
                "topic":"subflow/flowsynmaxi1/cmnd",
                "client":"client"
            }
        ''',
        "flowsynmaxi1_sva":'''
            {
                "deviceName": "flowsynmaxi1",
                "inUse": True,
                "connDetails": {
                    "ipCom": {
                        "addr": "192.168.1.202",
                        "port": 80
                    }
                },
                "settings":{"command":"SET", "subDevice":"FlowSynValveA", "value":>bool<},
                "topic":"subflow/flowsynmaxi1/cmnd",
                "client":"client"
            }
        ''',
        "flowsynmaxi1_svb":'''
            {
                "deviceName": "flowsynmaxi1",
                "inUse": True,
                "connDetails": {
                    "ipCom": {
                        "addr": "192.168.1.202",
                        "port": 80
                    }
                },
                "settings":{"command":"SET","subDevice":"FlowSynValveB","value":>bool<},
                "topic":"subflow/flowsynmaxi1/cmnd",
                "client":"client"
            }
        ''',
        "flowsynmaxi1_svcw":'''
            {
                "deviceName": "flowsynmaxi1",
                "inUse": True,
                "connDetails": {
                    "ipCom": {
                        "addr": "192.168.1.202",
                        "port": 80
                    }
                },
                "settings": {
                    "subDevice": "FlowCWValve",
                    "command": "SET",
                    "value": >bool<
                },
                "topic":"subflow/flowsynmaxi1/cmnd",
                "client":"client"
            }
        ''',
        "flowsynmaxi1_svia":'''
            {
                "deviceName": "flowsynmaxi1",
                "inUse": True,
                "connDetails": {
                    "ipCom": {
                        "addr": "192.168.1.202",
                        "port": 80
                    }
                },
                "settings":{"command":"SET", "subDevice":"FlowSynInjValveA", "value": >bool<},
                "topic":"subflow/flowsynmaxi1/cmnd",
                "client":"client"
            }
        ''',
        "flowsynmaxi1_svib":'''
            {
                "deviceName": "flowsynmaxi1",
                "inUse": True,
                "connDetails": {
                    "ipCom": {
                        "addr": "192.168.1.202",
                        "port": 80
                    }
                },
                "settings":{"command":"SET", "subDevice":"FlowSynInjValveB", "value": >bool<},
                "topic":"subflow/flowsynmaxi1/cmnd",
                "client":"client"
            }
        ''',
        "flowsynmaxi2_pafr":'''
            {
                "deviceName": "flowsynmaxi2",
                "inUse": True,
                "connDetails": {
                    "ipCom": {
                        "addr": "192.168.1.201",
                        "port": 80
                    }
                },
                "settings": {
                    "subDevice": "PumpAFlowRate",
                    "command": "SET",
                    "value": >float<
                },
                "topic":"subflow/flowsynmaxi2/cmnd",
                "client":"client"
            }
        ''',
        "flowsynmaxi2_pbfr":'''
            {
                "deviceName": "flowsynmaxi2",
                "inUse": True,
                "connDetails": {
                    "ipCom": {
                        "addr": "192.168.1.201",
                        "port": 80
                    }
                },
                "settings": {
                    "subDevice": "PumpBFlowRate",
                    "command": "SET",
                    "value": >float<
                },
                "topic":"subflow/flowsynmaxi2/cmnd",
                "client":"client"
            }
        ''',
        "flowsynmaxi2_sva":'''
            {
                "deviceName": "flowsynmaxi2",
                "inUse": True,
                "connDetails": {
                    "ipCom": {
                        "addr": "192.168.1.201",
                        "port": 80
                    }
                },
                "settings": {
                    "subDevice": "FlowSynValveA",
                    "command": "SET",
                    "value": >bool<
                },
                "topic":"subflow/flowsynmaxi2/cmnd",
                "client":"client"
            }
        ''',
        "flowsynmaxi2_svb":'''
            {
                "deviceName": "flowsynmaxi2",
                "inUse": True,
                "connDetails": {
                    "ipCom": {
                        "addr": "192.168.1.201",
                        "port": 80
                    }
                },
                "settings": {
                    "subDevice": "FlowSynValveB",
                    "command": "SET",
                    "value": >bool<
                },
                "topic":"subflow/flowsynmaxi2/cmnd",
                "client":"client"
            }
        ''',
        "flowsynmaxi2_svcw":'''
            {
                "deviceName": "flowsynmaxi2",
                "inUse": True,
                "connDetails": {
                    "ipCom": {
                        "addr": "192.168.1.201",
                        "port": 80
                    }
                },
                "settings": {
                    "subDevice": "FlowCWValve",
                    "command": "SET",
                    "value": >bool<
                },
                "topic":"subflow/flowsynmaxi2/cmnd",
                "client":"client"
            }
        ''',
        "flowsynmaxi2_svia":'''
            {
                "deviceName": "flowsynmaxi2",
                "inUse": True,
                "connDetails": {
                    "ipCom": {
                        "addr": "192.168.1.201",
                        "port": 80
                    }
                },
                "settings":{"command":"SET", "subDevice":"FlowSynInjValveA", "value": >bool<},
                "topic":"subflow/flowsynmaxi2/cmnd",
                "client":"client"
            }
        ''',
        "flowsynmaxi2_svib":'''
            {
                "deviceName": "flowsynmaxi2",
                "inUse": True,
                "connDetails": {
                    "ipCom": {
                        "addr": "192.168.1.201",
                        "port": 80
                    }
                },
                "settings":{"command":"SET", "subDevice":"FlowSynInjValveB", "value": >bool<},
                "topic":"subflow/flowsynmaxi2/cmnd",
                "client":"client"
            }
        ''',
        #Vapourtec R4 P1700
        "vapourtecR4P1700_pafr":'''
            {
                "deviceName": "vapourtecR4P1700",
                "inUse":True,
                "connDetails": {
                    "ipCom": {
                        "addr": "192.168.1.51",
                        "port": 43344
                    }
                },
                "settings": {
                    "command": "SET",
                    "subDevice": "PumpAFlowRate",
                    "value": >float<
                },
                "topic":"subflow/vapourtecR4P1700/cmnd",
                "client":"client"
            }
        ''',
        "vapourtecR4P1700_pbfr":'''
            {
                "deviceName": "vapourtecR4P1700",
                "inUse":True,
                "connDetails": {
                    "ipCom": {
                        "addr": "192.168.1.51",
                        "port": 43344
                    }
                },
                "settings": {
                    "command": "SET",
                    "subDevice": "PumpBFlowRate",
                    "value": >float<
                },
                "topic":"subflow/vapourtecR4P1700/cmnd",
                "client":"client"
            }
        ''',
        #Switch valve A solv/reag
        "vapourtecR4P1700_svasr":'''
            {
                "deviceName": "vapourtecR4P1700",
                "inUse": True,
                "connDetails": {
                    "ipCom": {
                        "addr": "192.168.1.51",
                        "port": 43344
                    }
                },
                "settings":{"command":"SET", "subDevice":"valveASR", "value":>bool<},
                "topic":"subflow/vapourtecR4P1700/cmnd",
                "client":"client"
            }
        ''',
        #Switch valve B solv/reag
        "vapourtecR4P1700_svbsr":'''
            {
                "deviceName": "vapourtecR4P1700",
                "inUse": True,
                "connDetails": {
                    "ipCom": {
                        "addr": "192.168.1.51",
                        "port": 43344
                    }
                },
                "settings":{"command":"SET","subDevice":"valveBSR","value":>bool<},
                "topic":"subflow/vapourtecR4P1700/cmnd",
                "client":"client"
            }
        ''',
        "vapourtecR4P1700_svcw":'''
            {
                "deviceName": "vapourtecR4P1700",
                "inUse": True,
                "connDetails": {
                    "ipCom": {
                        "addr": "192.168.1.51",
                        "port": 43344
                    }
                },
                "settings": {
                    "subDevice": "valveCW",
                    "command": "SET",
                    "value": >bool<
                },
                "topic":"subflow/vapourtecR4P1700/cmnd",
                "client":"client"
            }
        ''',
        #Switch valve A inject/load
        "vapourtecR4P1700_svail":'''
            {
                "deviceName": "vapourtecR4P1700",
                "inUse": True,
                "connDetails": {
                    "ipCom": {
                        "addr": "192.168.1.51",
                        "port": 43344
                    }
                },
                "settings":{"command":"SET", "subDevice":"valveAIL", "value": >bool<},
                "topic":"subflow/vapourtecR4P1700/cmnd",
                "client":"client"
            }
        ''',
        "vapourtecR4P1700_svbil":'''
            {
                "deviceName": "vapourtecR4P1700",
                "inUse": True,
                "connDetails": {
                    "ipCom": {
                        "addr": "192.168.1.51",
                        "port": 43344
                    }
                },
                "settings":{"command":"SET", "subDevice":"valveBIL", "value": >bool<},
                "topic":"subflow/vapourtecR4P1700/cmnd",
                "client":"client"
            }
        ''',
        "vapourtecR4P1700_r1temp":'''
            {
                "deviceName": "vapourtecR4P1700",
                "inUse":True,
                "connDetails": {
                    "ipCom": {
                        "addr": "192.168.1.51",
                        "port": 43344
                    }
                },
                "settings": {
                    "command": "SET",
                    "subDevice": "Reactor1Temp",
                    "value": >float<
                },
                "topic":"subflow/vapourtecR4P1700/cmnd",
                "client":"client"
            }
        ''',
        "vapourtecR4P1700_r2temp":'''
            {
                "deviceName": "vapourtecR4P1700",
                "inUse":True,
                "connDetails": {
                    "ipCom": {
                        "addr": "192.168.1.51",
                        "port": 43344
                    }
                },
                "settings": {
                    "command": "SET",
                    "subDevice": "Reactor2Temp",
                    "value": >float<
                },
                "topic":"subflow/vapourtecR4P1700/cmnd",
                "client":"client"
            }
        ''',
        "vapourtecR4P1700_r3temp":'''
            {
                "deviceName": "vapourtecR4P1700",
                "inUse":True,
                "connDetails": {
                    "ipCom": {
                        "addr": "192.168.1.51",
                        "port": 43344
                    }
                },
                "settings": {
                    "command": "SET",
                    "subDevice": "Reactor3Temp",
                    "value": >float<
                },
                "topic":"subflow/vapourtecR4P1700/cmnd",
                "client":"client"
            }
        ''',
        "vapourtecR4P1700_r4temp":'''
            {
                "deviceName": "vapourtecR4P1700",
                "inUse":True,
                "connDetails": {
                    "ipCom": {
                        "addr": "192.168.1.51",
                        "port": 43344
                    }
                },
                "settings": {
                    "command": "SET",
                    "subDevice": "Reactor4Temp",
                    "value": >float<
                },
                "topic":"subflow/vapourtecR4P1700/cmnd",
                "client":"client"
            }
        ''',
        #Custom commands
        "Delay":'''
            {"Delay": {"initTimestamp": None, "sleepTime": >float<}}
        ''',
        "WaitUntil":'''
            {"WaitUntil": {"conditionFunc": "checkTempFunc", "conditionParam": "pullTemp", "timeout": >float<, "initTimestamp": None, "completionMessage": "No message!"}},
        '''
    }
    commandTemplatesNested = {
        "Delay":{
            "sleepTime":'''
                {"Delay": {"initTimestamp": None, "sleepTime": >float<}}
            '''
        },
        "WaitUntil":{
            "timeout":'''
                {"WaitUntil": {"conditionFunc": "checkValFunc", "conditionParam": "getLivingValue", "timeout": >float<, "initTimestamp": None, "completionMessage": "No message!"}},
            '''
        },
        "sf10vapourtec1": {
            "fr":commandTemplates["sf10vapourtec1_fr"]
        },
        "sf10vapourtec2": {
            "fr":commandTemplates["sf10vapourtec2_fr"]
        },
        "hotcoil1": {
            "temp":commandTemplates["hotcoil1_temp"]
        },
        "hotcoil2": {
            "temp":commandTemplates["hotcoil2_temp"]
        },
        "hotchip1": {
            "temp":commandTemplates["hotchip1_temp"]
        },
        "hotchip2": {
            "temp":commandTemplates["hotchip2_temp"]
        },
        "flowsynmaxi1": {
            "pafr":commandTemplates["flowsynmaxi1_pafr"],
            "pbfr":commandTemplates["flowsynmaxi1_pbfr"],
            "sva":commandTemplates["flowsynmaxi1_sva"],
            "svb":commandTemplates["flowsynmaxi1_svb"],
            "svcw":commandTemplates["flowsynmaxi1_svcw"],
            "svia":commandTemplates["flowsynmaxi1_svia"],
            "svib":commandTemplates["flowsynmaxi1_svib"]
        },
        "flowsynmaxi2": {
            "pafr":commandTemplates["flowsynmaxi2_pafr"],
            "pbfr":commandTemplates["flowsynmaxi2_pbfr"],
            "sva":commandTemplates["flowsynmaxi2_sva"],
            "svb":commandTemplates["flowsynmaxi2_svb"],
            "svcw":commandTemplates["flowsynmaxi2_svcw"],
            "svia":commandTemplates["flowsynmaxi2_svia"],
            "svib":commandTemplates["flowsynmaxi2_svib"]
        },
        "vapourtecR4P1700":{
            "pafr":commandTemplates["vapourtecR4P1700_pafr"],
            "pbfr":commandTemplates["vapourtecR4P1700_pbfr"],
            "svail":commandTemplates["vapourtecR4P1700_svail"],
            "svbil":commandTemplates["vapourtecR4P1700_svbil"],
            "svcw":commandTemplates["vapourtecR4P1700_svcw"],
            "svasr":commandTemplates["vapourtecR4P1700_svasr"],
            "svbsr":commandTemplates["vapourtecR4P1700_svbsr"],
            "r1temp":commandTemplates["vapourtecR4P1700_r1temp"],
            "r2temp":commandTemplates["vapourtecR4P1700_r2temp"],
            "r3temp":commandTemplates["vapourtecR4P1700_r3temp"],
            "r4temp":commandTemplates["vapourtecR4P1700_r4temp"]
        }
    }
    
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
        'vapourtecR4P1700':{ #"valveASR": False, "valveBSR": False, "valveCSR": False, "valveDSR": False, "valveAIL": False, "valveBIL": False, "valveCIL": False, "valveDIL": False, "valveWC": False, "flowRatePumpA": 0, "flowRatePumpB": 0, "flowRatePumpC": 0, "flowRatePumpD": 0, "pressSystem": 0.03999999910593033, "pressPumpA": 0.25, "pressPumpB": 0.3400000035762787, "pressSystem2": 0.0, "pressPumpC": 0.0, "pressPumpD": 0.0, "tempReactor1": -100.0, "tempReactor2": -100.0, "tempReactor3": -100.0, "tempReactor4": -100.0}
            'pafr': {
                'address': ['tele','state','pressPumpA'],
                'displayName': 'Pump A Flowrate'
            },
            'pbfr': {
                'address': ['tele','state', 'pressPumpB'],
                'displayName': 'Pump B Flowrate'
            },
            'svasr': {
                'address': ['tele','state', 'valveASR'],
                'displayName': 'Solv/Reag A'
            },
            'svbsr': {
                'address': ['tele','state', 'valveBSR'],
                'displayName': 'Solv/Reag B'
            },
            'svail': {
                'address': ['tele','state', 'valveAIL'],
                'displayName': 'Inj/Load A'
            },
            'svbil': {
                'address': ['tele','state', 'valveBIL'],
                'displayName': 'Inj/Load B'
            },
            'svcw': {
                'address': ['tele','state', 'valveWC'],
                'displayName': 'Collecting'
            },
            'pressA': {
                'address': ['tele','state', 'pressPumpA'],
                'displayName': 'Pump A Pressure'
            },
            'pressB': {
                'address': ['tele','state', 'pressPumpB'],
                'displayName': 'Pump B Pressure'
            },
            'pressSys': {
                'address': ['tele','state', 'pressSystem'],
                'displayName': 'System Pressure 1'
            },
            'pressSys2': {
                'address': ['tele','state', 'pressSystem2'],
                'displayName': 'System Pressure 2'
            },
            'temp_1': {
                'address': ['tele','state', 'tempReactor1'],
                'displayName': 'Heater 1 Temperature'
            },
            'temp_2': {
                'address': ['tele','state', 'tempReactor2'],
                'displayName': 'Heater 2 Temperature'
            },
            'temp_3': {
                'address': ['tele','state', 'tempReactor3'],
                'displayName': 'Heater 3 Temperature'
            },
            'temp_4': {
                'address': ['tele','state', 'tempReactor4'],
                'displayName': 'Heater 4 Temperature'
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
        'sf10Vapourtec1': { #TODO - hoekom is hierdie waardes nie in "state" nie?
            'fr': {
                'address': ['tele','settings', 'flowrate'],
                'displayName':'Flowrate'
            },
            'pressSys': {
                'address': ['tele','settings', 'pressure'],
                'displayName':'Pressure'
            }
        },
        'sf10Vapourtec2': { #TODO - hoekom is hierdie waardes nie in "state" nie?
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
        #device=device.lower()
        value = data
        for key in (HardcodedTeleAddresses.hardcodedTeleAddresses[device][setting]['address']):
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        return value

    @staticmethod
    def getDisplayName(device,setting):
        #device=device.lower()
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