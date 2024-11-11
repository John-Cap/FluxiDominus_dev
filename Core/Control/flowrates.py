
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
        
        self._groupCounter=1
        
    def shiftKeepCumulative(self,pumpFlowrates={},snapToMinMax=True):
        groups=[]
        pumps=pumpFlowrates.keys()
        #TODO - check if sum is below globalCumulative
        for x in pumps:
            if not self.pumpGroups[x] in groups:
                groups.append(self.pumpGroups[x])
        for grp in groups:
            grpPmps=self.groups[grp]
            frUsed=0
            frAvail=self.groupCumulativeFlowrate(grp)
            notAltered=[]
            maxGrpCumulative=self.allowedMaxCumulative(grp)
            minGrpCumulative=self.allowedMinCumulative(grp)
            for pmp in grpPmps:
                if pmp.pumpName in pumpFlowrates:
                    fr=pmp.flowrate
                    if frUsed > frAvail: #TODO - Not enough fr left!
                        pass
                        if fr <= pmp.flowrateMax and fr >= pmp.flowrateMin:
                            pass
                        elif snapToMinMax and fr <= pmp.flowrateMax:
                            pass
                        elif snapToMinMax and fr >= pmp.flowrateMin:
                            pass
                    elif frAvail >= fr:
                        if fr <= pmp.flowrateMax and fr >= pmp.flowrateMin:
                            pmp.flowrate=fr
                        elif snapToMinMax and fr >= pmp.flowrateMax:
                            pmp.flowrate=pmp.flowrateMax
                        elif snapToMinMax and fr <= pmp.flowrateMin:
                            pmp.flowrate=pmp.flowrateMin
                    frUsed+=pmp.flowrate
                    frAvail-=pmp.flowrate
                else:
                    notAltered.append(pmp)
            if len(notAltered)==0:
                return self.groupCumulativeFlowrate(grp)
            div=frAvail/(len(notAltered))
            for pmp in notAltered:
                pmp.flowrate=div
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
        pumpLimits=[5, 20],  # Min flowrate 5, Max flowrate 20
        pressureMax=100
    )
    
    pump2 = pump_flowrates.addPump(
        deviceName="Device2",
        settingName="Setting2",
        pumpName="Pump2",
        pumpAlias="Alias2",
        pumpGroup="Group1",
        pumpLimits=[10, 25],  # Min flowrate 10, Max flowrate 25
        pressureMax=120
    )

    # Test cumulative flowrate in Group1
    print("Initial cumulative flowrate for Group1:", pump_flowrates.groupCumulativeFlowrate("Group1"))

    # Set desired maximum cumulative flowrate for Group1 and check result
    desired_flowrate = pump_flowrates.setDesiredMaxCumulative("Group1", flowrate=35)
    print("Desired max cumulative flowrate set for Group1:", desired_flowrate)

    # Check allowed min and max cumulative flowrate for Group1
    print("Allowed max cumulative flowrate for Group1:", pump_flowrates.allowedMaxCumulative("Group1"))
    print("Allowed min cumulative flowrate for Group1:", pump_flowrates.allowedMinCumulative("Group1"))

    # Set specific flowrates for pumps and shift to maintain cumulative balance
    pump_flowrates.shiftKeepCumulative(
        pumpFlowrates={"Pump1": 15, "Pump2": 20},
        snapToMinMax=True
    )
    
    # Print updated flowrates
    print(f"Updated flowrate for Pump1: {pump1.flowrate}")
    print(f"Updated flowrate for Pump2: {pump2.flowrate}")

    # Check final cumulative flowrate for Group1
    print("Final cumulative flowrate for Group1:", pump_flowrates.groupCumulativeFlowrate("Group1"))
