import heapq

class Mqueue:
    def __init__(self):
        self.heap = []
    def enqueue(self, item):
        heapq.heappush(self.heap, item)
    def __iter__(self):
        return MqueueIter(self)
    def __bool__(self):
        return bool(self.heap)
    def __str__(self):
        return ("queue with %s items" % len(self.heap))
    def __add__(self, other):
        return heapq.merge(self.heap, other.heap)
    def merge(self, other):
        self.heap = list(heapq.merge(self.heap, other.heap))
    def pop(self):
        return heapq.heappop(self.heap)

# have to make a copy since heappop is destructive
class MqueueIter:
    def __init__(self, q):
        self.heap = list(q.heap)
    def __next__(self):
        while self.heap:
            return heapq.heappop(self.heap)
        raise StopIteration
