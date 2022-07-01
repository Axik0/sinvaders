import math as m


class Obstacle:
    def __init__(self, window_size, grid_size):
        self.bars, self.edge, self.lines = {}, {}, {}
        # I have some block of screen, containing all our bars-turtles inside and set up their height and width
        # so that they are filling the block in two directions with separators inbetween (quantities from grid_size)
        self.SEP = 4
        self.BTM_LEVEL = 150
        # get dimension of the block
        self.MAX_DIM = (window_size[0], window_size[1]/2 - self.BTM_LEVEL)
        # N elements require N+1 separator, subtract their overall length from available width and divide it onto N
        # it doesn't matter yet, but suppose that we start from indent = separator and proceed with fixed steps
        self.BAR_SEMI_WIDTH = ((self.MAX_DIM[0]-self.SEP)/grid_size[0] - self.SEP)/2
        self.BAR_SEMI_HEIGHT = ((self.MAX_DIM[1]-self.SEP)/grid_size[1] - self.SEP)/2
        # We assured that there is enough space for all bars. Now I need center coordinates.
        # We are ready to establish a whole range of possible centers, have to make it integer though
        self.y_cor_range = \
            (self.BTM_LEVEL + self.SEP + self.BAR_SEMI_HEIGHT, self.BTM_LEVEL + self.MAX_DIM[1] - self.BAR_SEMI_HEIGHT)
        self.x_cor_range = \
            (-self.MAX_DIM[0]/2 + self.SEP + self.BAR_SEMI_WIDTH, self.MAX_DIM[0]/2 - self.BAR_SEMI_WIDTH)
        # I want to use the distance between 2 centres to generate those and fill self.bars
        self.V_STEP = 2 * self.BAR_SEMI_HEIGHT + self.SEP
        self.H_STEP = 2 * self.BAR_SEMI_WIDTH + self.SEP
        # I want to get upper and lower bounds to use in main module
        self.LL, self.UL = round(self.y_cor_range[0]), round(self.y_cor_range[1])
        self.prev_bar = None

    def find_edge(self):
        # this structure contains bars (their center's) on edges of our block, line by line
        # assume that levels differ no more than by 1 bar by width, i.e. there is no 2nd order blocks (rare chance)
        self.edge = {}
        for lvl in self.bars:
            self.edge[lvl] = [self.bars[lvl][0][0], self.bars[lvl][-1][0]]
        self.UL = round(max(self.edge) + self.BAR_SEMI_HEIGHT, 2)
        self.LL = round(min(self.edge) - self.BAR_SEMI_HEIGHT, 2)

    def load(self):
        # This dictionary is a special structure, containing centers of each block, ordered in a clever (I hope so) way
        self.bars = {}
        for y in range(round(self.y_cor_range[0]), round(self.y_cor_range[1]) + 1, m.floor(self.V_STEP)):
            c_level = []
            for x in range(round(self.x_cor_range[0]), round(self.x_cor_range[1]) + 1, m.floor(self.H_STEP)):
                c_level.append((x, y))
            self.bars[y] = c_level
        self.find_edge()

    def remove(self, bar):
        self.bars[bar[1]].remove(bar)
        if len(self.bars[bar[1]]) == 0:
            # in case there aren't any items in the list left, get rid of the corresponding key
            self.bars.pop(bar[1])
        self.prev_bar = bar

    def getlog(self, extended=False):
        import pprint as p
        if extended:
            p.pprint(self.bars)
            p.pprint(self.lines)
        print("bar size", self.BAR_SEMI_WIDTH, self.BAR_SEMI_HEIGHT)
        print("range X,Y", self.x_cor_range, self.y_cor_range)
        print("raw steps H,V", self.H_STEP, self.V_STEP)
        print("rounded! bounds U, L", self.UL, self.LL)


