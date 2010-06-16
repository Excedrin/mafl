import random

class Target:
    def gettargets(state, actor, targets):
        return [state.slotbyname(x) for x in targets]

class Self(Target):
    def gettargets(state, actor, targets):
        return [state.slotbyplayer(actor)]

class Random(Target):
    def gettargets(state, actor, targets):
        return [random.choice(state.livingslots())]
