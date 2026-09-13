import game.buildings as buildings


class Action:
    name: str
    cost: tuple[int, int, int]
    available = True
    time: int

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

    def add(self, action: type[Action]):
        if len(self.actions) < 5:
            self.actions.append(action)
            action.onstart()


#############
# BUILDINGS #
#############


class BuildPod(Action):
    name = "pod"
    cost = (1, 2, 3)
    time = 0


class BuildBarracks(Action):
    name = "barracks"
    cost = (1, 2, 3)
    time = 0


class BuildFoundry(Action):
    name = "foundry"
    cost = (1, 2, 3)
    time = 0


class BuildFarm(Action):
    name = "fungusfarm"
    cost = (1, 2, 3)
    time = 0


class BuildLumbermill(Action):
    name = "lumbermill"
    cost = (1, 2, 3)
    time = 0


class BuildNexus(Action):
    name = "nexus"
    cost = (1, 2, 3)
    time = 0


class BuildSiegery(Action):
    name = "siegery"
    cost = (1, 2, 3)
    time = 0


class BuildTower(Action):
    name = "tower"
    cost = (1, 2, 3)
    time = 0


#########
# UNITS #
#########


class CreateWorker(Action):
    name = "worker"
    cost = (0, 0, 2)
    time = 120


class CreateQueen(Action):
    name = "queen"
    cost = (0, 0, 2)
    time = 300


class CreateSoldier(Action):
    name = "soldier"
    cost = (0, 0, 2)
    time = 150


class CreatePhrag(Action):
    name = "phrag"
    cost = (0, 0, 2)
    time = 180


class CreateAlate(Action):
    name = "alate"
    cost = (0, 0, 2)
    time = 240


class CreateMajor(Action):
    name = "major"
    cost = (0, 0, 2)
    time = 270


############
# UPGRADES #
############


class Upgrade(Action):
    def onstart(self):
        upgrade_type = type(self)
        upgrade_type.available = False


class ResearchArrhenotoky(Upgrade):
    name = "arrhenotoky"
    cost = (1, 2, 3)
    time = 600
