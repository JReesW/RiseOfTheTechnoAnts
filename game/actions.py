import game.buildings as buildings


flags = {
    "nothing": True,
    "can_make_queens": False,
    "can_build_siegery": False,
    "can_make_alate": False
}


class Action:
    name: str
    cost: tuple[int, int, int]
    available = True
    time: int
    required: str = "nothing"

    def __init__(self, owner: buildings.Building):
        self.owner = owner

    def onclick(self):
        pass

    def onstart(self):
        pass

    def onfinish(self):
        pass


class ActionProcessor:
    def __init__(self, owner: buildings.Building):
        self.owner = owner
        self.actions = []
        self.progress = 0

    def update(self):
        if self.actions:
            self.progress += 1
            if self.progress >= self.actions[0].time:
                self.actions[0].onfinish()
                self.progress = 0
                self.actions.pop(0)

    def add(self, action: Action):
        action.owner = self.owner
        self.actions.append(action)
        action.onstart()


#############
# BUILDINGS #
#############


class BuildPod(Action):
    name = "pod"
    cost = (50, 20, 0, False)
    time = 0


class BuildBarracks(Action):
    name = "barracks"
    cost = (150, 200, 50, False)
    time = 0


class BuildFoundry(Action):
    name = "foundry"
    cost = (100, 50, 0, False)
    time = 0


class BuildFarm(Action):
    name = "fungusfarm"
    cost = (100, 50, 0, False)
    time = 0


class BuildLumbermill(Action):
    name = "lumbermill"
    cost = (20, 50, 0, False)
    time = 0


class BuildNexus(Action):
    name = "nexus"
    cost = (0, 0, 0, False)
    time = 0


class BuildSiegery(Action):
    name = "siegery"
    cost = (200, 500, 100, False)
    time = 0
    required = "can_build_siegery"


class BuildTower(Action):
    name = "tower"
    cost = (1, 2, 3, False)
    time = 0


#########
# UNITS #
#########


class CreateWorker(Action):
    name = "worker"
    cost = (0, 0, 30, True)
    time = 240


class CreateQueen(Action):
    name = "queen"
    cost = (250, 250, 500, True)
    time = 600
    required = "can_make_queens"


class CreateSoldier(Action):
    name = "soldier"
    cost = (0, 10, 40, True)
    time = 300


class CreatePhrag(Action):
    name = "phrag"
    cost = (0, 30, 50, True)
    time = 400


class CreateAlate(Action):
    name = "alate"
    cost = (0, 300, 50, True)
    time = 480
    required = "can_make_alate"


class CreateMajor(Action):
    name = "major"
    cost = (0, 100, 75, True)
    time = 480


############
# UPGRADES #
############


class Upgrade(Action):
    def onstart(self):
        upgrade_type = type(self)
        upgrade_type.available = False


class ResearchArrhenotoky(Upgrade):
    name = "arrhenotoky"
    cost = (100, 100, 300, False)
    time = 600

    def onfinish(self):
        flags["can_make_queens"] = True


class ResearchCybernetics(Upgrade):
    name = "cybernetics"
    cost = (200, 300, 50, False)
    time = 600

    def onfinish(self):
        flags["can_build_siegery"] = True


class ResearchPropulsion(Upgrade):
    name = "propulsion"
    cost = (200, 400, 100, False)
    time = 600

    def onfinish(self):
        flags["can_make_alate"] = True
