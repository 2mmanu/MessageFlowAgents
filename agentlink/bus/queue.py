import queue


class QueueManager:

    def __init__(self) -> None:
        self._queues = {}

    def create_queues(self, name: str) -> bool:
        if name in self._queues:
            raise ValueError(f"{name} queues exists")
        self._queues[name] = {
            "in": queue.Queue(),
            "out": queue.Queue(),
        }
        return True

    def get_queue(self, name: str, direction: str):
        if name not in self._queues:
            raise ValueError(f"{name} doesn't exist")
        if direction not in ["in", "out"]:
            raise ValueError(f"{direction} for {name} doesn't exist")
        return self._queues[name][direction]

    def get_queues(self, name: str):
        return self.get_queue(name=name, direction="in"), self.get_queue(name=name, direction="out")
