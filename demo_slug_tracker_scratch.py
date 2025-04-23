
import json
import random
import time
from Core.Fluids.FlowPath import Valve
from OPTIMIZATION_TEMP.Plutter_TEMP.plutter import MqttService
import os


if __name__ == "__main__":
    
    example={
    "reqUI": {
        "FlowSketcher": {
        "parseFlowsketch":{
            "3f6e37eb-40ee-4ed3-862e-d9800cd0c43e": {
            "name": "R4 Pump A",
            "flowsInto": [
                "tubing_1_3f6e37eb-40ee-4ed3-862e-d9800cd0c43e_29b52a6f-8bb5-41c0-baa8-3bab6d685ae9"
            ],
            "deviceName": "vapourtecR4P1700",
            "deviceType": "Pump",
            "volume": 1
            },
            "tubing_1_3f6e37eb-40ee-4ed3-862e-d9800cd0c43e_29b52a6f-8bb5-41c0-baa8-3bab6d685ae9": {
            "name": "Tubing",
            "flowsInto": [
                "29b52a6f-8bb5-41c0-baa8-3bab6d685ae9"
            ],
            "deviceName": "tubingStandard",
            "deviceType": "Tubing",
            "volume": 0.123
            },
            "11aff382-a458-4a25-a311-db62c3c45843": {
            "name": "SR_A",
            "flowsInto": [
                "tubing_2_11aff382-a458-4a25-a311-db62c3c45843_3f6e37eb-40ee-4ed3-862e-d9800cd0c43e"
            ],
            "deviceName": "null",
            "deviceType": "Valve",
            "volume": 0.25
            },
            "tubing_2_11aff382-a458-4a25-a311-db62c3c45843_3f6e37eb-40ee-4ed3-862e-d9800cd0c43e": {
            "name": "Tubing",
            "flowsInto": [
                "3f6e37eb-40ee-4ed3-862e-d9800cd0c43e"
            ],
            "deviceName": "tubingStandard",
            "deviceType": "Tubing",
            "volume": 0.123
            },
            "ad33a7da-5b9d-4963-b9b3-9ed61d029bd2": {
            "name": "AllylIsoval",
            "flowsInto": [
                "tubing_3_ad33a7da-5b9d-4963-b9b3-9ed61d029bd2_11aff382-a458-4a25-a311-db62c3c45843"
            ],
            "deviceName": "null",
            "deviceType": "FlowOrigin",
            "volume": 0
            },
            "tubing_3_ad33a7da-5b9d-4963-b9b3-9ed61d029bd2_11aff382-a458-4a25-a311-db62c3c45843": {
            "name": "Tubing",
            "flowsInto": [
                "11aff382-a458-4a25-a311-db62c3c45843"
            ],
            "deviceName": "tubingStandard",
            "deviceType": "Tubing",
            "volume": 0.123
            },
            "e76868c1-4c46-4c35-be71-7cf388c4765d": {
            "name": "PushSolventA",
            "flowsInto": [
                "tubing_4_e76868c1-4c46-4c35-be71-7cf388c4765d_11aff382-a458-4a25-a311-db62c3c45843"
            ],
            "deviceName": "null",
            "deviceType": "FlowOrigin",
            "volume": 0
            },
            "tubing_4_e76868c1-4c46-4c35-be71-7cf388c4765d_11aff382-a458-4a25-a311-db62c3c45843": {
            "name": "Tubing",
            "flowsInto": [
                "11aff382-a458-4a25-a311-db62c3c45843"
            ],
            "deviceName": "tubingStandard",
            "deviceType": "Tubing",
            "volume": 0.123
            },
            "fcd5fb07-66aa-4b21-a306-6d8a873d60d9": {
            "name": "SR_B",
            "flowsInto": [
                "tubing_5_fcd5fb07-66aa-4b21-a306-6d8a873d60d9_59e6ec63-6719-483c-8467-c5ccffa0f563"
            ],
            "deviceName": "null",
            "deviceType": "Valve",
            "volume": 0.25
            },
            "tubing_5_fcd5fb07-66aa-4b21-a306-6d8a873d60d9_59e6ec63-6719-483c-8467-c5ccffa0f563": {
            "name": "Tubing",
            "flowsInto": [
                "59e6ec63-6719-483c-8467-c5ccffa0f563"
            ],
            "deviceName": "tubingStandard",
            "deviceType": "Tubing",
            "volume": 0.123
            },
            "59e6ec63-6719-483c-8467-c5ccffa0f563": {
            "name": "R4 Pump B",
            "flowsInto": [
                "tubing_6_59e6ec63-6719-483c-8467-c5ccffa0f563_29b52a6f-8bb5-41c0-baa8-3bab6d685ae9"
            ],
            "deviceName": "vapourtecR4P1700",
            "deviceType": "Pump",
            "volume": 1
            },
            "tubing_6_59e6ec63-6719-483c-8467-c5ccffa0f563_29b52a6f-8bb5-41c0-baa8-3bab6d685ae9": {
            "name": "Tubing",
            "flowsInto": [
                "29b52a6f-8bb5-41c0-baa8-3bab6d685ae9"
            ],
            "deviceName": "tubingStandard",
            "deviceType": "Tubing",
            "volume": 0.123
            },
            "5915e364-75c6-49d0-b6af-f641f7b45754": {
            "name": "KOH_sol",
            "flowsInto": [
                "tubing_7_5915e364-75c6-49d0-b6af-f641f7b45754_fcd5fb07-66aa-4b21-a306-6d8a873d60d9"
            ],
            "deviceName": "null",
            "deviceType": "FlowOrigin",
            "volume": 0
            },
            "tubing_7_5915e364-75c6-49d0-b6af-f641f7b45754_fcd5fb07-66aa-4b21-a306-6d8a873d60d9": {
            "name": "Tubing",
            "flowsInto": [
                "fcd5fb07-66aa-4b21-a306-6d8a873d60d9"
            ],
            "deviceName": "tubingStandard",
            "deviceType": "Tubing",
            "volume": 0.123
            },
            "f926cf59-bfbc-4a69-9d52-e63d58f0d695": {
            "name": "PushSolventB",
            "flowsInto": [
                "tubing_8_f926cf59-bfbc-4a69-9d52-e63d58f0d695_fcd5fb07-66aa-4b21-a306-6d8a873d60d9"
            ],
            "deviceName": "null",
            "deviceType": "FlowOrigin",
            "volume": 0
            },
            "tubing_8_f926cf59-bfbc-4a69-9d52-e63d58f0d695_fcd5fb07-66aa-4b21-a306-6d8a873d60d9": {
            "name": "Tubing",
            "flowsInto": [
                "fcd5fb07-66aa-4b21-a306-6d8a873d60d9"
            ],
            "deviceName": "tubingStandard",
            "deviceType": "Tubing",
            "volume": 0.123
            },
            "29b52a6f-8bb5-41c0-baa8-3bab6d685ae9": {
            "name": "StaticMixer",
            "flowsInto": [
                "tubing_9_29b52a6f-8bb5-41c0-baa8-3bab6d685ae9_d25f31e2-002b-48c7-b060-992d321ed9c4"
            ],
            "deviceName": "null",
            "deviceType": "TPiece",
            "volume": 0.05
            },
            "tubing_9_29b52a6f-8bb5-41c0-baa8-3bab6d685ae9_d25f31e2-002b-48c7-b060-992d321ed9c4": {
            "name": "Tubing",
            "flowsInto": [
                "d25f31e2-002b-48c7-b060-992d321ed9c4"
            ],
            "deviceName": "tubingStandard",
            "deviceType": "Tubing",
            "volume": 0.123
            },
            "d25f31e2-002b-48c7-b060-992d321ed9c4": {
            "name": "Hotcoil_1",
            "flowsInto": [
                "tubing_10_d25f31e2-002b-48c7-b060-992d321ed9c4_fdcc2834-213b-42f7-bdde-b38e6a5c8172"
            ],
            "deviceName": "hotcoil1",
            "deviceType": "Coil",
            "volume": 2
            },
            "tubing_10_d25f31e2-002b-48c7-b060-992d321ed9c4_fdcc2834-213b-42f7-bdde-b38e6a5c8172": {
            "name": "Tubing",
            "flowsInto": [
                "fdcc2834-213b-42f7-bdde-b38e6a5c8172"
            ],
            "deviceName": "tubingStandard",
            "deviceType": "Tubing",
            "volume": 0.123
            },
            "fdcc2834-213b-42f7-bdde-b38e6a5c8172": {
            "name": "ReactIR 702L1",
            "flowsInto": [
                "tubing_11_fdcc2834-213b-42f7-bdde-b38e6a5c8172_e64f27b7-c346-4c86-94cd-c00398796894"
            ],
            "deviceName": "reactIR702L1",
            "deviceType": "IR",
            "volume": 0.25
            },
            "tubing_11_fdcc2834-213b-42f7-bdde-b38e6a5c8172_e64f27b7-c346-4c86-94cd-c00398796894": {
            "name": "Tubing",
            "flowsInto": [
                "e64f27b7-c346-4c86-94cd-c00398796894"
            ],
            "deviceName": "tubingStandard",
            "deviceType": "Tubing",
            "volume": 0.123
            },
            "e64f27b7-c346-4c86-94cd-c00398796894": {
            "name": "WasteOrCollect",
            "flowsInto": [
                "tubing_12_e64f27b7-c346-4c86-94cd-c00398796894_27151161-8edf-4152-9ea6-ce1df14f6f46",
                "tubing_13_e64f27b7-c346-4c86-94cd-c00398796894_f14f0372-3504-4559-ad7e-6a8661fdb7b4"
            ],
            "deviceName": "null",
            "deviceType": "Valve",
            "volume": 0.25
            },
            "tubing_12_e64f27b7-c346-4c86-94cd-c00398796894_27151161-8edf-4152-9ea6-ce1df14f6f46": {
            "name": "Tubing",
            "flowsInto": [
                "27151161-8edf-4152-9ea6-ce1df14f6f46"
            ],
            "deviceName": "tubingStandard",
            "deviceType": "Tubing",
            "volume": 0.123
            },
            "tubing_13_e64f27b7-c346-4c86-94cd-c00398796894_f14f0372-3504-4559-ad7e-6a8661fdb7b4": {
            "name": "Tubing",
            "flowsInto": [
                "f14f0372-3504-4559-ad7e-6a8661fdb7b4"
            ],
            "deviceName": "tubingStandard",
            "deviceType": "Tubing",
            "volume": 0.123
            },
            "27151161-8edf-4152-9ea6-ce1df14f6f46": {
            "name": "Product",
            "flowsInto": [],
            "deviceName": "null",
            "deviceType": "FlowTerminus",
            "volume": 0
            },
            "f14f0372-3504-4559-ad7e-6a8661fdb7b4": {
            "name": "Waste",
            "flowsInto": [],
            "deviceName": "null",
            "deviceType": "FlowTerminus",
            "volume": 0
            }
        }
        }
    }
    }

    mqttService=MqttService(broker_address="172.30.243.138")
    mqttService.connectDb=False
    mqttService.arm()
    mqttService.start()
    
    while not mqttService.connected:
        time.sleep(1)
    
    path=mqttService.flowSystem.flowpath
    # path.mqttService.publish("ui/FlowSketcher",json.dumps(example))
    
    while not path.terminiMapped:
        time.sleep(1)
    
    path.startFlowPathLoop()
    
    origins=path.allOrigins()
    termini=path.allTermini()
    
    doExample=True
    numOfDisp=0
    numCollectedSlugs=1
    
    _now=time.time()
    _nowRefresh=time.time()
    
    while doExample and numOfDisp < 15:
        
        print("Waiting for go-ahead from UI")
        while mqttService.abort:
            time.sleep(1)
        while not mqttService.runTest:
            time.sleep(1)
            
        report=[]   
    
        thisOrigin=random.choice(origins)
        thisTerminus=random.choice(termini)
        path.setCurrDestination(thisTerminus)
        report.append(f"Round #{numOfDisp + 1}")
        report.append(f"Setting current destination to {thisTerminus.name}")
        
        # path.visualizeFlowPath()
        for x in origins:
            setFlow=random.choice([0])
            x.setFlowrate(setFlow/60)
            report.append(f"Flowrate for {x.name} set to {setFlow}")
            
        path.pullFromOrigin(random.choice(origins))
        
        amountToDispense=random.choice([1,2,3,4,5])
        report.append(f"{path.currRelOrigin.name} will dispense {amountToDispense} mL")
        slug=path.dispense(amountToDispense)
        report.append(f"Slug dispensing from {slug.tailHost.name}")
        print(f"Slug dispensing from {slug.tailHost.name}")
        time.sleep(2)
        expectedSlugSize=1#(thisTerminus.flowrateIn/slug.tailHost.flowrateOut)*amountToDispense
        report.append(f"Expected slug volume at collection: {expectedSlugSize} mL")
        print(f"Expected slug volume at collection: {expectedSlugSize} mL")
        
        path.publishSlugTrackingInfo(slug)
        
        stampStamp=time.time()
        
        while len(path.collectedSlugs) != numCollectedSlugs and (mqttService.runTest and not mqttService.abort):
            if time.time() - _nowRefresh > 1:
                _vol=slug.slugVolume()
                _nowRefresh=time.time()
                rep=f"--------------------------------------------------\nTime: {round(time.time() - _now, 0)} sec,\nAll fr: {[orig.flowrateOut*60 for orig in origins]}\nFront in: {slug.frontHost.name},\n {round(slug.frontHost.flowrateOut*60, 2)} mL.min-1,\n {round(slug.frontHostPos, 2)}/{slug.frontHost.volume} mL\nTail in: {slug.tailHost.name},\n {round(slug.tailHost.flowrateOut*60, 2)} mL.min-1,\n {round(slug.tailHostPos, 2)}/{slug.tailHost.volume} mL\nslug vol: {round(_vol, 2)} mL, vol collected: {(round(slug.collectedVol, 2))} mL\n Current valve states:\n {
                    [[x.flowrateOut,x.name,x.inlets[0].name,x.outlets[0].name] for x in path.segments if isinstance(x,Valve)]  
                }"
                print(rep)
                print(f"Slugs: {path.slugs} and {path.collectedSlugs}")
            time.sleep(2)
        
        numCollectedSlugs+=1
        numOfDisp+=1
        rep=f"--------------------------------------------------\nTime: {round(time.time() - _now, 0)} sec,\nAll fr: {[orig.flowrateOut*60 for orig in origins]}\nFront in: {slug.frontHost.name},\n {round(slug.frontHost.flowrateOut*60, 2)} mL.min-1,\n {round(slug.frontHostPos, 2)}/{slug.frontHost.volume} mL\nTail in: {slug.tailHost.name},\n {round(slug.tailHost.flowrateOut*60, 2)} mL.min-1,\n {round(slug.tailHostPos, 2)}/{slug.tailHost.volume} mL\nslug vol: {round(_vol, 2)} mL, vol collected: {(round(slug.collectedVol, 2))} mL\n Current valve states:\n {
            [[x.name,x.inlets[0].name,x.outlets[0].name] for x in path.segments if isinstance(x,Valve)]  
        }"
        print(rep)
        print(f"Slugs: {path.slugs} and {[x.collectedVol for x in path.collectedSlugs]}")
        report.append(f"Slug #{numCollectedSlugs - 1} collected with volume {slug.collectedVol} at {slug.frontHost.name} after being routed to {thisTerminus.name}")
        report.append(f"All this took {time.time() - stampStamp} seconds")
        # Path to desktop
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")

        # File path
        file_path = os.path.join(desktop, "output.txt")

        # Write to file
        with open(file_path, "a") as f:
            for x in report:
                f.write(x + "\n")                
            f.write(".........................." + "\n")

        print(f"Wrote to: {file_path}")
        
        time.sleep(2)
        
        