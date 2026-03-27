class BaseEntity:
    def __init__(self, io=None):
        self.io = io

    def set_io(self, io_obj):
        self.io = io_obj

    def __getstate__(self):
        state = self.__dict__.copy()
        if "io" in state:
            del state["io"]
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.io = None

    def __str__(self):
        return f"{self.__class__.__name__}()"
