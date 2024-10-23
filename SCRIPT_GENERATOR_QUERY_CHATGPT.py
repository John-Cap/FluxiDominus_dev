{
    "vapourtecR4P1700_pafr":'''
        {
            "deviceName": "vapourtecR4P1700",
            "inUse":True,
            "connDetails": {
                "ipCom": {
                    "addr": "192.168.1.53",
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
                    "addr": "192.168.1.53",
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
                    "addr": "192.168.1.53",
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
                    "addr": "192.168.1.53",
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
                    "addr": "192.168.1.53",
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
                    "addr": "192.168.1.53",
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
                    "addr": "192.168.1.53",
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
                    "addr": "192.168.1.53",
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
                    "addr": "192.168.1.53",
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
                    "addr": "192.168.1.53",
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
                    "addr": "192.168.1.53",
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
    '''
}