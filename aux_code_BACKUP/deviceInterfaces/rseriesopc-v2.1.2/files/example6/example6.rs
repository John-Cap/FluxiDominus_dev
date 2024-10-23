{
    "connections": [
        {
            "in_id": "{3605655c-25ed-4f02-bf61-71001cdf1a38}",
            "in_index": 1,
            "out_id": "{91691743-2c31-4d61-8e60-d89880e346cd}",
            "out_index": 0
        },
        {
            "in_id": "{3605655c-25ed-4f02-bf61-71001cdf1a38}",
            "in_index": 0,
            "out_id": "{d9995171-bd79-462e-9960-0e18b8d9fafd}",
            "out_index": 0
        },
        {
            "in_id": "{1b6213c5-3ea7-4ff0-9ef7-0ba854db248a}",
            "in_index": 0,
            "out_id": "{d933bf71-ff8f-4645-b9d4-fd72be0f55e8}",
            "out_index": 0
        },
        {
            "in_id": "{d933bf71-ff8f-4645-b9d4-fd72be0f55e8}",
            "in_index": 0,
            "out_id": "{3605655c-25ed-4f02-bf61-71001cdf1a38}",
            "out_index": 0
        }
    ],
    "nodes": [
        {
            "id": "{d933bf71-ff8f-4645-b9d4-fd72be0f55e8}",
            "model": {
                "m_property1": "P1",
                "m_property2": "10 ml",
                "m_property3": "",
                "name": "Heated Tubular Reactor - 150 \u00b0C",
                "properties": {
                    "COMPONENT_DISP_MODEL_TYPE": 0,
                    "COMPONENT_NAME": "Heated Tubular Reactor - 150 \u00b0C",
                    "CONNECTION_BORE": 2,
                    "CONNECTION_BORE_LIST": [
                        0.5,
                        0.8,
                        1,
                        1.3,
                        1.5,
                        2.5,
                        3.2
                    ],
                    "CONNECTION_LENGHT": 50,
                    "CONNECTION_TYPE": 0,
                    "CONNECTION_TYPE_LIST": [
                        "PFA",
                        "SS"
                    ],
                    "CONNECTION_VOLUME": 0.39269908169872414,
                    "REACTOR_BORE_R1": 2,
                    "REACTOR_BORE_R1_LIST": [
                        0.5,
                        0.8,
                        1,
                        1.3,
                        1.5,
                        2.5,
                        3.2
                    ],
                    "REACTOR_MAX_TEMP": 150,
                    "REACTOR_MIN_TEMP": 20,
                    "REACTOR_POS": 0,
                    "REACTOR_POS_INDEX": 0,
                    "REACTOR_POS_LIST": [
                        "P1",
                        "P2",
                        "P3",
                        "P4",
                        "P5",
                        "P6",
                        "P7",
                        "P8"
                    ],
                    "REACTOR_TYPE": 0,
                    "REACTOR_TYPE_LIST": [
                        "PFA",
                        "SS"
                    ],
                    "REACTOR_VOLUME_R1": 10
                }
            },
            "position": {
                "x": 900,
                "y": 452
            }
        },
        {
            "id": "{91691743-2c31-4d61-8e60-d89880e346cd}",
            "model": {
                "m_property1": "B",
                "m_property2": "0.93 ml",
                "m_property3": "",
                "name": "V-3 Pump for Bottled Reagents",
                "properties": {
                    "COMPONENT_NAME": "V-3 Pump for Bottled Reagents",
                    "CONNECTION_BORE": 2,
                    "CONNECTION_BORE_LIST": [
                        0.5,
                        0.8,
                        1,
                        1.3,
                        1.5,
                        2.5,
                        3.2
                    ],
                    "CONNECTION_LENGHT": 50,
                    "CONNECTION_TYPE": 0,
                    "CONNECTION_TYPE_LIST": [
                        "PFA",
                        "SS"
                    ],
                    "CONNECTION_VOLUME": 0.39269908169872414,
                    "PUMP_CHANNEL": 1,
                    "PUMP_CHANNEL_LIST": [
                        "A",
                        "B",
                        "C",
                        "D",
                        "E",
                        "F",
                        "G",
                        "H"
                    ],
                    "PUMP_DEAD_VOLUME": 0.93,
                    "PUMP_DISP_MODEL": false,
                    "PUMP_FLOW_SPECIF": 0,
                    "PUMP_FLOW_SPECIF_LIST": [
                        "Flow rates",
                        "Volumetric ratio",
                        "Stoichiometric ratio"
                    ],
                    "PUMP_GAS_TYPE": 0,
                    "PUMP_HEAT_AND_COOL": false,
                    "PUMP_POST_CLEAN": false,
                    "PUMP_PRE_CLEAN": false,
                    "PUMP_REAGENT_CONCENTRATION": 0.5,
                    "PUMP_REAGENT_SOURCE": 0,
                    "PUMP_REAGENT_SOURCE_LIST": [
                        "Reagent",
                        "Autosampler"
                    ]
                }
            },
            "position": {
                "x": 500,
                "y": 452
            }
        },
        {
            "id": "{3605655c-25ed-4f02-bf61-71001cdf1a38}",
            "model": {
                "m_property1": "0.05 ml",
                "m_property2": "",
                "m_property3": "",
                "name": "2-Way Mixer",
                "properties": {
                    "COMPONENT_DISP_MODEL_TYPE": 0,
                    "COMPONENT_NAME": "2-Way Mixer",
                    "CONNECTION_BORE": 2,
                    "CONNECTION_BORE_LIST": [
                        0.5,
                        0.8,
                        1,
                        1.3,
                        1.5,
                        2.5,
                        3.2
                    ],
                    "CONNECTION_LENGHT": 50,
                    "CONNECTION_TYPE": 0,
                    "CONNECTION_TYPE_LIST": [
                        "PFA",
                        "SS"
                    ],
                    "CONNECTION_VOLUME": 0.39269908169872414,
                    "MIXER_VOLUME": 0.05
                }
            },
            "position": {
                "x": 700,
                "y": 352
            }
        },
        {
            "id": "{1b6213c5-3ea7-4ff0-9ef7-0ba854db248a}",
            "model": {
                "m_property1": "Tube: 2 cm",
                "m_property2": "",
                "m_property3": "",
                "name": "Waste Collect Valve",
                "properties": {
                    "COMPONENT_DISP_MODEL_TYPE": 0,
                    "COMPONENT_DISP_MODEL_TYPE_INDEX": 0,
                    "COMPONENT_DISP_MODEL_TYPE_LIST": [
                        "PFA",
                        "SILICA",
                        "CSTR"
                    ],
                    "COMPONENT_NAME": "Waste Collect Valve",
                    "OTHERS_COLLECTION_TUBE_LENGTH": 2,
                    "OTHERS_VOLUME_TUBE": 0.015707963267948967,
                    "OTHERS_WASH_VOLUME": 0.0471238898038469,
                    "OTHERS_WCV_BORE": 2,
                    "OTHERS_WCV_BORE_LIST": [
                        0.5,
                        0.8,
                        1,
                        1.3,
                        1.5,
                        2.5,
                        3.2
                    ]
                }
            },
            "position": {
                "x": 1100,
                "y": 452
            }
        },
        {
            "id": "{d9995171-bd79-462e-9960-0e18b8d9fafd}",
            "model": {
                "m_property1": "A",
                "m_property2": "0 ml",
                "m_property3": "",
                "name": "Bottled Reagents Piston Pump",
                "properties": {
                    "COMPONENT_NAME": "Bottled Reagents Piston Pump",
                    "CONNECTION_BORE": 2,
                    "CONNECTION_BORE_LIST": [
                        0.5,
                        0.8,
                        1,
                        1.3,
                        1.5,
                        2.5,
                        3.2
                    ],
                    "CONNECTION_LENGHT": 50,
                    "CONNECTION_TYPE": 0,
                    "CONNECTION_TYPE_LIST": [
                        "PFA",
                        "SS"
                    ],
                    "CONNECTION_VOLUME": 0.39269908169872414,
                    "PUMP_CHANNEL": 0,
                    "PUMP_CHANNEL_LIST": [
                        "A",
                        "B",
                        "C",
                        "D",
                        "E",
                        "F",
                        "G",
                        "H"
                    ],
                    "PUMP_DEAD_VOLUME": 0,
                    "PUMP_DISP_MODEL": false,
                    "PUMP_FLOW_SPECIF": 0,
                    "PUMP_FLOW_SPECIF_LIST": [
                        "Flow rates",
                        "Volumetric ratio",
                        "Stoichiometric ratio"
                    ],
                    "PUMP_HEAT_AND_COOL": false,
                    "PUMP_POST_CLEAN": false,
                    "PUMP_PRE_CLEAN": false,
                    "PUMP_REAGENT_CONCENTRATION": 0.5,
                    "PUMP_REAGENT_SOURCE": 0,
                    "PUMP_REAGENT_SOURCE_LIST": [
                        "Reagent",
                        "Solvent bottle",
                        "Autosampler"
                    ]
                }
            },
            "position": {
                "x": 500,
                "y": 352
            }
        }
    ]
}