class Some:
    def __init__(self, v=None):
        self.v = v
    def __bool__(self):
        return True
