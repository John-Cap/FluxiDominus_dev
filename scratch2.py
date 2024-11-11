
#Methods for handling flowrate related stuff

from Core.Components.pump_logic import Pump


class PumpFlowrates:
    def __init__(self) -> None:
        self.pumps={}
        self.groups={}
        self.pumpGroups={}
        self.globalCumulative=30 #TODO - Hardcoded
        self.adhereToGroupCumulative={}
        self.maxCumulativesSet={}
        self.minCumulativesSet={}
        
        self._groupCounter=1
        
    def shiftKeepCumulative(self,grp,pumpFlowrates={},snapToMinMax=True):
        #TODO - check if sum is below globalCumulative
        grpPmps=self.groups[grp]
        frUsed=0
        frAvail=self.groupCumulativeFlowrate(grp)
        notAltered=[]
        cum_1=self.groupCumulativeFlowrate(grp)
        maxGrpCumulative=self.allowedMaxCumulative(grp)
        minGrpCumulative=self.allowedMinCumulative(grp)
        for pmp in grpPmps:
            if pmp.pumpName in pumpFlowrates:
                # print("Here 2")
                fr=pumpFlowrates[pmp.pumpName]
                if fr > frAvail: #TODO - Not enough fr left!
                    # print("Here 3")
                    pass
                    if fr <= pmp.flowrateMax and fr >= pmp.flowrateMin:
                        # print("Here 4")
                        pass
                    elif snapToMinMax and fr <= pmp.flowrateMax:
                        # print("Here 5")
                        pass
                    elif snapToMinMax and fr >= pmp.flowrateMin:
                        # print("Here 6")
                        pass
                elif frAvail >= fr:
                    if fr <= pmp.flowrateMax and fr >= pmp.flowrateMin:
                        # print("Here 7")
                        pmp.flowrate=fr
                    elif snapToMinMax and fr >= pmp.flowrateMax:
                        # print("Here 8")
                        pmp.flowrate=pmp.flowrateMax
                    elif snapToMinMax and fr <= pmp.flowrateMin:
                        # print("Here 9")
                        pmp.flowrate=pmp.flowrateMin
                frUsed+=pmp.flowrate
                frAvail-=pmp.flowrate
            else:
                # print("Here 10")
                notAltered.append(pmp)
        if len(notAltered)!=0:
            div=frAvail/(len(notAltered))
            for pmp in notAltered:
                pmp.flowrate=div
        cum_2=self.groupCumulativeFlowrate(grp)
        if abs(cum_2-cum_1) > 0.0005: # TODO - Vra vir moeilikheid
            if cum_2 < cum_1 and cum_2 != 0:
                print("*Scaling flowrates up for group "+grp)
                rat=cum_1/cum_2
                for pmp in self.pumps.values():
                    pmp.flowrate=pmp.flowrate*rat
        return self.groupCumulativeFlowrate(grp)
                            
    def addPump(self,deviceName,settingName,pumpName=None,pumpAlias="",pumpGroup=None,pumpLimits=[None,None],pressureMax=None):
        
        pump=Pump(deviceName,settingName,pumpName=pumpName,flowrateMin=pumpLimits[0],flowrateMax=pumpLimits[1],pressureMax=pressureMax,pumpAlias=pumpAlias)

        if (not pumpGroup):
            self.addPumpGroup(groupName=pumpGroup,pumps=[pump])
        else:
            if not pumpGroup in self.groups:
                self.addPumpGroup(pumpGroup,pumps=[pump])
            else:
                self.groups[pumpGroup].append(pump)
            
        #self.pumpLimits[pumpName]=pumpLimits
        self.pumpGroups[pumpName]=pumpGroup
        self.pumps[pumpName]=pump

        return pump

    def addPumpGroup(self,groupName=None,pumps=[],allowedMaxCumulative=None,adhereToAllowedMaxCumulative=True):
        
        if (not groupName):
            groupName="pumpGroup_"+self._groupCounter
            self._groupCounter+=1

        self.groups[groupName]=pumps
    
        if allowedMaxCumulative == 0:
            allowedMaxCumulative=None
        #self.maxGroupCumulatives[groupName]=allowedMaxCumulative
            
        self.adhereToGroupCumulative[groupName]=adhereToAllowedMaxCumulative
        
    def groupCumulativeFlowrate(self,group):
        if group in self.groups:
            cum=0
            pumps=self.groups[group]
            for pmp in pumps:
                cum+=pmp.flowrate
            return cum
        else:
            return None
                
    def allowedMaxCumulative(self,group):
        if group in self.groups:
            cum=0
            pumps=self.groups[group]
            for pmp in pumps:
                cum+=pmp.flowrateMax
            return cum
        else:
            return None
        
    def allowedMinCumulative(self,group):
        if group in self.groups:
            cum=0
            pumps=self.groups[group]
            for pmp in pumps:
                cum+=pmp.flowrateMin
            return cum
        else:
            return None
                
    def setDesiredMinCumulative(self,group,flowrate,snapTo=True):
        if not group in self.groups:
            return None
        min=self.allowedMinCumulative(group)
        max=self.allowedMaxCumulative(group)
        self.minCumulativesSet[group]=None
        
        if min <= flowrate and max >= flowrate:
            self.minCumulativesSet[group]=flowrate
        else:
            if min >= flowrate and snapTo:
                self.minCumulativesSet[group]=min
            elif max <= flowrate and snapTo:
                self.minCumulativesSet[group]=max
                
        return self.minCumulativesSet[group]
                    
    def setDesiredMaxCumulative(self,group,flowrate,snapTo=True):
        if not group in self.groups:
            return None
        min=self.allowedMinCumulative(group)
        max=self.allowedMaxCumulative(group)
        self.maxCumulativesSet[group]=None
        
        if min <= flowrate and max >= flowrate:
            self.maxCumulativesSet[group]=flowrate
        else:
            if min >= flowrate and snapTo:
                self.maxCumulativesSet[group]=min
            elif max <= flowrate and snapTo:
                self.maxCumulativesSet[group]=max
                
        return self.maxCumulativesSet[group]
    
if __name__ == "__main__":
    # Initialize PumpFlowrates instance
    pump_flowrates = PumpFlowrates()

    # Add pumps with specific flowrate limits and groups
    pump1 = pump_flowrates.addPump(
        deviceName="Device1",
        settingName="Setting1",
        pumpName="Pump1",
        pumpAlias="Alias1",
        pumpGroup="Group1",
        pumpLimits=[3, 20],  # Min flowrate 5, Max flowrate 20
        pressureMax=100
    )
    
    pump2 = pump_flowrates.addPump(
        deviceName="Device2",
        settingName="Setting2",
        pumpName="Pump2",
        pumpAlias="Alias2",
        pumpGroup="Group1",
        pumpLimits=[3, 25],  # Min flowrate 10, Max flowrate 25
        pressureMax=120
    )
    
    pump3 = pump_flowrates.addPump(
        deviceName="Device3",
        settingName="Setting2",
        pumpName="Pump3",
        pumpAlias="Alias3",
        pumpGroup="Group1",
        pumpLimits=[3, 25],  # Min flowrate 10, Max flowrate 25
        pressureMax=120
    )
    
    pump4 = pump_flowrates.addPump(
        deviceName="Device4",
        settingName="Setting5",
        pumpName="Pump4",
        pumpAlias="Alias4",
        pumpGroup="Group1",
        pumpLimits=[3, 25],  # Min flowrate 10, Max flowrate 25
        pressureMax=120
    )
    
    for pmp in pump_flowrates.pumps.values():
        pmp.flowrate=5

    # Set desired maximum cumulative flowrate for Group1 and check result
    desired_flowrate = pump_flowrates.setDesiredMinCumulative("Group1", flowrate=12)
    print("Desired min cumulative flowrate set for Group1:", desired_flowrate)
    desired_flowrate = pump_flowrates.setDesiredMaxCumulative("Group1", flowrate=30)
    print("Desired max cumulative flowrate set for Group1:", desired_flowrate)

    # Check allowed min and max cumulative flowrate for Group1
    print("Allowed min cumulative flowrate for Group1:", pump_flowrates.allowedMinCumulative("Group1"))
    print("Allowed max cumulative flowrate for Group1:", pump_flowrates.allowedMaxCumulative("Group1"))

    # Test cumulative flowrate in Group1
    _adjustments=[{"Pump1":7,"Pump2":2},{"Pump1":3,"Pump2":4},{"Pump1":3,"Pump3":4},{"Pump1":3,"Pump2":4,"Pump3":3},{"Pump1":5,"Pump2":5,"Pump3":5},{"Pump1":2,"Pump2":3,"Pump3":3,"Pump4":7},{"Pump1":5,"Pump2":5,"Pump3":5},{"Pump1":7,"Pump2":7,"Pump3":7,"Pump4":7},{"Pump1":2,"Pump2":3,"Pump3":2,"Pump4":3}]
    for _ad in _adjustments:
        
        print('#########################')
        print('###')
        print('Cumulative: ' + str(pump_flowrates.groupCumulativeFlowrate("Group1")))
        for b in pump_flowrates.pumps.values():
            print(b.pumpName + ": " + str(b.flowrate))
        print('---')
        pump_flowrates.shiftKeepCumulative(
            grp="Group1",
            pumpFlowrates=_ad,
            snapToMinMax=True
        )
        print('Cumulative: ' + str(pump_flowrates.groupCumulativeFlowrate("Group1")))
        for b in pump_flowrates.pumps.values():
            print(b.flowrate)