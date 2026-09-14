import game.buildings as buildings


flags = {
    "nothing": True,
    "can_make_queens": False,
    "can_build_siegery": False
}


class Action:
    name: str
    cost: tuple[int, int, int]
    available = True
    time: int
    required: str = "nothing"

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
    cost = (1, 2, 3, False)
    time = 0


class BuildFoundry(Action):
    name = "foundry"
    cost = (1, 2, 3, False)
    time = 0


class BuildFarm(Action):
    name = "fungusfarm"
    cost = (1, 2, 3, False)
    time = 0


class BuildLumbermill(Action):
    name = "lumbermill"
    cost = (1, 2, 3, False)
    time = 0


class BuildNexus(Action):
    name = "nexus"
    cost = (1, 2, 3, False)
    time = 0


class BuildSiegery(Action):
    name = "siegery"
    cost = (1, 2, 3, False)
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
    cost = (0, 0, 2, True)
    time = 120


class CreateQueen(Action):
    name = "queen"
    cost = (0, 0, 2, True)
    time = 300
    required = "can_make_queens"


class CreateSoldier(Action):
    name = "soldier"
    cost = (0, 0, 2, True)
    time = 150


class CreatePhrag(Action):
    name = "phrag"
    cost = (0, 0, 2, True)
    time = 180


class CreateAlate(Action):
    name = "alate"
    cost = (0, 0, 2, True)
    time = 240


class CreateMajor(Action):
    name = "major"
    cost = (0, 0, 2, True)
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
    cost = (1, 2, 3, False)
    time = 600

    def onfinish(self):
        flags["can_make_queens"] = True


class ResearchCybernetics(Upgrade):
    name = "cybernetics"
    cost = (1, 2, 3, False)
    time = 600

    def onfinish(self):
        flags["can_build_siegery"] = True
