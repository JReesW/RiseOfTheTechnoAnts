class Action:
    name: str
    cost: tuple[int, int, int]

    def onclick():
        pass


#############
# BUILDINGS #
#############


class BuildPod(Action):
    name = "pod"
    cost = (1, 2, 3)


class BuildBarracks(Action):
    name = "barracks"
    cost = (1, 2, 3)


class BuildFoundry(Action):
    name = "foundry"
    cost = (1, 2, 3)


class BuildFarm(Action):
    name = "fungusfarm"
    cost = (1, 2, 3)


class BuildLumbermill(Action):
    name = "lumbermill"
    cost = (1, 2, 3)


class BuildNexus(Action):
    name = "nexus"
    cost = (1, 2, 3)


class BuildSiegery(Action):
    name = "siegery"
    cost = (1, 2, 3)


class BuildTower(Action):
    name = "tower"
    cost = (1, 2, 3)


#########
# UNITS #
#########


class CreateWorker(Action):
    name = "worker"
    cost = (0, 0, 2)


class CreateQueen(Action):
    name = "queen"
    cost = (0, 0, 2)
