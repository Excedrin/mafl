class Player:
    def __init__(self, name):
        self.name = name
        self.align = "unknown"
        self.living = True
        self.faction = None
    def __str__(self):
        return self.name
