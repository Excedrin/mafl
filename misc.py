class Some:
    def __init__(self, v=None):
        self.v = v
    def __bool__(self):
        return True
    def __str__(self):
        return "Some(%s)" % self.v
