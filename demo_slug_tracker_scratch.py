
import json
import random
import time
from Core.Fluids.FlowPath import FlowPath, FlowSystem, Slugs, Valve
import os

from Core.UI.plutter import MqttService


if __name__ == "__main__":

    # mqttService=MqttService(broker_address="192.168.1.141")172.30.243.138
    mqttService=MqttService(broker_address="172.30.243.138")
    mqttService.connectDb=False
    mqttService.arm()
    mqttService.start()
    
    while not mqttService.connected:
        time.sleep(1)
    # path.mqttService.publish("ui/FlowSketcher",json.dumps(example))
    while True:
        path=mqttService.flowSystem.flowpath
        path.reset()
        
        print("Waiting for flowsketch to be set")
        while not path.terminiMapped:
            time.sleep(1)
            
        print("Termini mapped!")
        
        path.startFlowPathLoop()
        
        origins=path.allOrigins()
        termini=path.allTermini()
        
        doExample=True
        numOfDisp=0
        numCollectedSlugs=1
        
        path.publishUI=True
        
        _now=time.time()
        _nowRefresh=time.time()

        while doExample:
            try:
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
                    setFlow=random.choice([1,2,3,4,5])
                    x.setFlowrate(setFlow/60)
                    report.append(f"Flowrate for {x.name} set to {setFlow}")
                    
                path.pullFromOrigin(random.choice(origins))
                
                amountToDispense=random.choice([1,2,3,4,5])
                report.append(f"{path.currRelOrigin.name} will dispense {amountToDispense} mL")
                
                print(f"Report: {report}")
                
                slug=path.dispense(amountToDispense)
                report.append(f"Slug dispensing from {slug.tailHost.name}")
                print(f"Slug dispensing from {slug.tailHost.name}")
                time.sleep(2)
                expectedSlugSize=1#(thisTerminus.flowrateIn/slug.tailHost.flowrateOut)*amountToDispense
                report.append(f"Expected slug volume at collection: {expectedSlugSize} mL")
                print(f"Expected slug volume at collection: {expectedSlugSize} mL")
                
                # path.publishSlugTrackingInfo(slug)
                
                stampStamp=time.time()
                
                while len(path.collectedSlugs) != numCollectedSlugs and (mqttService.runTest and not mqttService.abort):
                    if time.time() - _nowRefresh > 1:
                        _vol=slug.slugVolume()
                        _nowRefresh=time.time()
                        rep=f"--------------------------------------------------\nTime: {round(time.time() - _now, 0)} sec,\nAll fr: {[orig.flowrateOut*60 for orig in origins]}\nFront in: {slug.frontHost.name},\n {round(slug.frontHost.flowrateOut*60, 2)} mL.min-1,\n {round(slug.frontHostPos, 2)}/{slug.frontHost.volume} mL\nTail in: {slug.tailHost.name},\n {round(slug.tailHost.flowrateOut*60, 2)} mL.min-1,\n {round(slug.tailHostPos, 2)}/{slug.tailHost.volume} mL\nslug vol: {round(_vol, 2)} mL, vol collected: {(round(slug.collectedVol, 2))} mL\n Current valve states:\n"
                        print(rep)
                        print(f"Slugs: {path.slugs} and {path.collectedSlugs}")
                    time.sleep(2)
                
                numCollectedSlugs+=1
                numOfDisp+=1
                rep=f"--------------------------------------------------\nTime: {round(time.time() - _now, 0)} sec,\nAll fr: {[orig.flowrateOut*60 for orig in origins]}\nFront in: {slug.frontHost.name},\n {round(slug.frontHost.flowrateOut*60, 2)} mL.min-1,\n {round(slug.frontHostPos, 2)}/{slug.frontHost.volume} mL\nTail in: {slug.tailHost.name},\n {round(slug.tailHost.flowrateOut*60, 2)} mL.min-1,\n {round(slug.tailHostPos, 2)}/{slug.tailHost.volume} mL\nslug vol: {round(_vol, 2)} mL, vol collected: {(round(slug.collectedVol, 2))} mL\n Current valve states:\n"
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
                
                for comp in path.segments:
                    comp.slugs=[]
                path.slugs=[]
                mqttService.flowSystem.flowpath.stopFlowPathLoop()
                time.sleep(1)
                doExample=False
            except:
                
                for comp in path.segments:
                    comp.slugs=[]
                path.slugs=[]
                mqttService.flowSystem.flowpath.stopFlowPathLoop()
                time.sleep(1)
                doExample=False
                continue