import copy

strDel = ","
decDel = "."


class Reaction:
    # TODO : check reaction documentation
    """
    This class represents a Reaction in a Reaction List.
    Allows the user to load a Reaction and make copies with different
    configurations.
    """

    def __init__(self):
        self.name = ""
        self.residenceTime = None
        self.reactor = {
            1: self.Reactor(),  # 1
            2: self.Reactor(),  # 2
            3: self.UVReactor(),  # 3
            4: self.Reactor(),  # 4
            5: self.Reactor(),  # 5
            6: self.UVReactor(),  # 6
            7: self.Reactor(),  # 7
            8: self.Reactor(),  # 8
        }
        self.pump = {
            "A": self.Pump(),  # A
            "B": self.Pump(),  # B
            "C": self.Pump(),  # C
            "D": self.Pump(),  # D
            "E": self.Pump(),  # E
            "F": self.Pump(),  # F
            "G": self.Pump(),  # G
            "H": self.Pump(),  # H
        }
        self.wash = {
            "pre": self.Wash(),
            "post": self.Wash(),
        }
        self.collection = self.Collection()
        self.autosampler = self.AutoSampler()

    def makeCSVRow(self, stringDelimiter, decimalDelimiter):
        accum = self.name + strDel
        accum += str(self.residenceTime) + strDel
        for reactor in self.reactor.values():
            accum += str(reactor) + strDel
        for pump in self.pump.values():
            accum += str(pump) + strDel
        for wash in self.wash.values():
            accum += (
                str(wash) + strDel
            )  # .replace(decDel, decimalDelimiter).replace(strDel, stringDelimiter)
        accum += (
            str(self.collection) + strDel
        )  # .replace(decDel, decimalDelimiter).replace(strDel, stringDelimiter) + stringDelimiter
        accum += str(
            self.autosampler
        )  # .replace(decDel, decimalDelimiter).replace(strDel, stringDelimiter)
        auxDelimiter = strDel
        if decimalDelimiter == strDel:
            auxDelimiter = "<StringDelimiter>"
            accum = accum.replace(strDel, auxDelimiter)
        accum = accum.replace(decDel, decimalDelimiter).replace(
            auxDelimiter, stringDelimiter
        )
        return accum

    def load(self, reaction):
        data = list(reaction).copy()
        self.name = data.pop(0)
        self.residenceTime = data.pop(0)
        for reactor in self.reactor.values():
            reactor.load(data)
        for pump in self.pump.values():
            pump.load(data)
        for wash in self.wash.values():
            wash.load(data)
        self.collection.load(data)
        self.autosampler.load(data)

    def tempStepper(self, reactorIndex, fromValue, toValue, step=10):
        if not isinstance(self.reactor[reactorIndex], self.Reactor):
            return
        reactions = list()
        while fromValue <= toValue:
            reaction = copy.deepcopy(self)
            reaction.reactor[reactorIndex].setTemperature(fromValue)
            reactions.append(reaction)
            fromValue += step
        return reactions

    def uvPowerStepper(self, reactorIndex, fromValue, toValue, step=10):
        if not isinstance(self.reactor[reactorIndex], self.Reactor()):
            return
        reactions = list()
        while fromValue <= toValue:
            reaction = copy.deepcopy(self)
            reaction.reactor[reactorIndex].setPower(fromValue)
            reactions.append(reaction)
            fromValue += step
        return reactions

    def flowrateStepper(self, pumpIndex, fromValue, toValue, step=0.5):
        if not isinstance(self.pump[pumpIndex], self.Pump):
            return
        reactions = list()
        while fromValue <= toValue:
            reaction = copy.deepcopy(self)
            reaction.pump[pumpIndex].setFlowRate(fromValue)
            reactions.append(reaction)
            fromValue += step
        return reactions

    def volumeRatioStepper(self, pumpIndex, fromValue, toValue, step=0.1):
        if not isinstance(self.pump[pumpIndex], self.Pump):
            return
        reactions = list()
        while fromValue <= toValue:
            reaction = copy.deepcopy(self)
            reaction.pump[pumpIndex].setVolumeRatio(fromValue)
            reactions.append(reaction)
            fromValue += step
        return reactions

    def advanceRetardStepper(self, pumpIndex, fromValue, toValue, step):
        if not isinstance(self.pump[pumpIndex], self.Pump):
            return
        reactions = list()
        while fromValue <= toValue:
            reaction = copy.deepcopy(self)
            reaction.pump[pumpIndex].setAdvanceRetard(fromValue)
            reactions.append(reaction)
            fromValue += step
        return reactions

    def reagentConcentrationStepper(self, pumpIndex, fromValue, toValue, step):
        if not isinstance(self.pump[pumpIndex], self.Pump):
            return
        reactions = list()
        while fromValue <= toValue:
            reaction = copy.deepcopy(self)
            reaction.pump[pumpIndex].setReagentConcentration(fromValue)
            reactions.append(reaction)
            fromValue += step
        return reactions

    class Reactor:
        """
        A reactor has a tempreature and a residence time.
        Each Reaction has 8 reactors, numbered from 1 to 8.
        """

        booleans = ["FALSE", "TRUE"]

        def __init__(self):
            self.temperature = 0
            self.residenceTime = False

        def __str__(self) -> str:
            string = str(self.temperature) + strDel
            string += str(self.residenceTime)
            return string

        def load(self, reaction):
            self.setTemperature(float(reaction.pop(0)))
            self.residenceTime = reaction.pop(0)

        def setTemperature(self, temp):
            self.temperature = temp

        def setResidenceTime(self, rt):
            if rt not in self.booleans:
                return
            self.residenceTime = rt == self.booleans[1]

    class UVReactor(Reactor):
        """
        An UVReactor is a kind of Reactor which has an extra UV power.
        """

        def __init__(self):
            super().__init__()
            self.power = 0

        def __str__(self) -> str:
            string = super().__str__() + strDel
            string += str(self.power)
            return string

        def load(self, reaction):
            super().load(reaction)
            self.setPower(int(reaction.pop(0)))

        def setPower(self, power):
            self.power = power

    class Pump:
        """
        A Pump has Flowrate, Volume Ratio, Concentration Ratio, Quantity,
        Advance Retard and Regent Concentration.
        It depends of the kind of Pump the experiment has, the valid changes
        of Volume or Conentration Ratio.
        The time which the pump is working is a function of flowrate and
        quantity selected.
        A Reactor has 8 Pumps, stored in a list numbered from 1 to 8.
        """

        def __init__(self):
            self.flowRate = 0
            self.volumeRatio = 0
            self.concentrationRatio = 0
            self.quantity = 0
            self.advanceRetard = 0
            self.reagentConcentration = 0

        def __str__(self) -> str:
            string = str(self.flowRate) + strDel
            string += str(self.volumeRatio) + strDel
            string += str(self.concentrationRatio) + strDel
            string += str(self.quantity) + strDel
            string += str(self.advanceRetard) + strDel
            string += str(self.reagentConcentration)
            return string

        def load(self, reaction):
            self.setFlowRate(float(reaction.pop(0)))
            self.setVolumeRatio(float(reaction.pop(0)))
            self.setConcentrationRatio(float(reaction.pop(0)))
            self.setQuantity(float(reaction.pop(0)))
            self.setAdvanceRetard(float(reaction.pop(0)))
            self.setReagentConcentration(float(reaction.pop(0)))

        def setFlowRate(self, fr):
            self.flowRate = fr

        def setVolumeRatio(self, vr):
            self.volumeRatio = vr

        def setQuantity(self, quantity):
            self.quantity = quantity

        def setConcentrationRatio(self, cr):
            self.concentrationRatio = cr

        def setAdvanceRetard(self, ar):
            self.advanceRetard = ar

        def setReagentConcentration(self, rc):
            self.reagentConcentration = rc

    class Wash:
        """
        A wash is a time where a Pump is cleaning its system.
        A wash has a flowrate and a volume, which defines the wash time.
        A Reaction has two different times for wash before and after the
        Reaction is run.
        """

        def __init__(self):
            self.flowRate = 0
            self.volume = 0

        def __str__(self) -> str:
            string = str(self.volume) + strDel
            string += str(self.flowRate)
            return string

        def load(self, reaction):
            self.setVolume(float(reaction.pop(0)))
            self.setFlowRate(float(reaction.pop(0)))

        def setVolume(self, volume):
            self.volume = volume

        def setFlowRate(self, flowRate):
            self.flowRate = flowRate

    class Collection:
        """
        A collection is the way how reaction stores the final produt.
        It has an state, a diverterTime, a collectionTime, a number of vials,
        a total volume and a volume for each vial.
        A Reaction has information of one Collection.
        """

        states = ["ALL", "STEADY_STATE", "DO_NOT_COLLECT", "MANUAL"]

        def __init__(self):
            self.state = 0
            self.diverterTime = 0
            self.collectionTime = 0
            self.vials = 0
            self.totalVolume = 0
            self.vialVolume = 0

        def __str__(self) -> str:
            string = self.states[self.state] + strDel
            string += str(self.diverterTime) + strDel
            string += str(self.collectionTime) + strDel
            string += str(self.vials) + strDel
            string += str(self.totalVolume) + strDel
            string += str(self.vialVolume)
            return string

        def load(self, reaction):
            self.setState(reaction.pop(0))
            self.setDiverterTime(float(reaction.pop(0)))
            self.setCollectionTime(float(reaction.pop(0)))
            self._setTotalVolumeString(reaction.pop(0))
            self._setVialVolumeString(reaction.pop(0))
            self.setVials(int(reaction.pop(0)))

        def setState(self, state: str):
            self.state = self.states.index(state)

        def setDiverterTime(self, time):
            self.diverterTime = time

        def setCollectionTime(self, ct):
            self.collectionTime = ct

        def setVials(self, v):
            self.vials = v

        def setTotalVolume(self, volume: float):
            if volume == self.totalVolume:
                return
            self.totalVolume = volume
            if self.vials != 0:
                return self.setVialVolume(self.totalVolume / self.vials)
            return self.setVialVolume(0)

        def _setTotalVolumeString(self, volume):
            self.totalVolume = float(volume)

        def _setVialVolumeString(self, volume):
            self.vialVolume = float(volume)

        def setVialVolume(self, volume):
            if volume == self.vialVolume:
                return
            self.vialVolume = volume
            self.setTotalVolume(self.vialVolume * self.vials)

    class AutoSampler:
        modes = ["AUTOSAMPLER", "MANUAL INJECTION"]

        def __init__(self) -> None:
            self.injection = False
            self.loop = {
                "A": self.Loop(),
                "B": self.Loop(),
                "C": self.Loop(),
                "D": self.Loop(),
                "E": self.Loop(),
                "F": self.Loop(),
                "G": self.Loop(),
                "H": self.Loop(),
            }

        def __str__(self) -> str:
            if self.injection:
                string = self.modes[0]
            else:
                string = self.modes[1]
            for loop in self.loop.values():
                string += strDel
                string += str(loop)
            return string

        def load(self, reaction) -> None:
            self.setInjectionMode(reaction.pop(0))
            for loop in self.loop.values():
                loop.load(reaction)
            pass

        def setInjectionMode(self, mode):
            if mode not in self.modes:
                return
            inj = False
            if mode is self.modes[0]:
                inj = True
            self.injection = inj

        class Loop:
            booleans = ["FALSE", "TRUE"]

            def __init__(self) -> None:
                self.site = 0
                self.description = None
                self.fill = False
                self.cleanAtStart = False

            def __str__(self) -> str:
                string = str(self.site) + strDel
                if self.description is not None:
                    string += self.description + strDel
                string += str(not self.fill).upper() + strDel
                string += str(self.cleanAtStart)
                return string

            def load(self, reaction) -> None:
                self.setLoadingSite(reaction.pop(0))
                data = reaction.pop(0)
                if data not in self.booleans:
                    self.setDescription(data)
                    data = reaction.pop(0)
                self.setFill(data)
                self.setCleanAtStart(reaction.pop(0))

            def setLoadingSite(self, site):
                self.site = site

            def setDescription(self, description):
                self.description = description

            def setFill(self, notFill):
                fill = notFill == self.booleans[0]
                self.fill = fill

            def setCleanAtStart(self, clean):
                clean = clean == self.booleans[1]
                self.cleanAtStart = clean
