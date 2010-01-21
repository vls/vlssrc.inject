class Pos:
    def __init__(self, id, tarx, tary, x, y):
        self.id = id
        self.tarx = tarx
        self.tary = tary
        self.x = x
        self.y = y
        self.dis = (tarx - x) ** 2 + (tary - y) ** 2
    
    def __le__(self, other):
        return self.dis <= other.dis