from pickle import FALSE
import pygame
import math
from queue import PriorityQueue
from operator import ne
#from astar import get_clicked_pos

WIDTH = 800
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("Dijksra's Path Finding Algorithm")

RED = (255, 0, 0)  # if seen/closed
GREEN = (0, 255, 0)
BLUE = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)  # marks barrier
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)  # marks start position
GREY = (128, 128, 128)
TURQUOISE = (64, 244, 208)


class Spot:
    def __init__(self, row, col, width, total_rows) -> None:
        # width refers to the gap here
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    # get position
    def get_pos(self):
        return self.row, self.col

    # check if spot is closed
    def is_closed(self):
        return self.color == RED

    # check if spot is open
    def is_open(self):
        return self.color == GREEN

    # check if spot is a barrier
    def is_barrier(self):
        return self.color == BLACK

    # checks if its the starting spot
    def is_start(self):
        return self.color == ORANGE

    # checks if its the ending spot
    def is_end(self):
        return self.color == TURQUOISE

    # marks spot as white again
    def reset(self):
        self.color = WHITE

    # marks the start position
    def make_start(self):
        self.color = ORANGE

    # marks as closed
    def make_closed(self):
        self.color = RED

    # mark as open
    def make_open(self):
        self.color = GREEN

    # make a barrier
    def make_barrier(self):
        self.color = BLACK
    # marks end

    def make_end(self):
        self.color = TURQUOISE
    # makes path

    def make_path(self):
        self.color = PURPLE

    # create rectangle on grid?
    def draw(self, win):
        pygame.draw.rect(
            win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []
        # DOWN
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():  # UP
            self.neighbors.append(grid[self.row - 1][self.col])

        # RIGHT
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():  # LEFT
            self.neighbors.append(grid[self.row][self.col - 1])


def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            spot = Spot(i, j, gap, rows)
            grid[i].append(spot)

    return grid


def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i*gap), (width, i*gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j*gap, 0), (j*gap, width))


def draw(win, grid, rows, width):
    win.fill(WHITE)

    for row in grid:
        for spot in row:
            spot.draw(win)

    draw_grid(win, rows, width)
    pygame.display.update()


def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y, x = pos

    row = y // gap
    col = x // gap
    return row, col


def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()


def algorithm(draw, grid, start, end):
    count = 0
    visited = {spot: False for row in grid for spot in row}
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    shortest_distance = {spot: float("inf") for row in grid for spot in row}
    shortest_distance[start] = 0

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.quit:
                pygame.quit()

        current = open_set.get()[2]
        visited[current] = True
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(came_from, current, draw)
            end.make_end()
            return True

        for neighbor in current.neighbors:
            temp_shortest_distance = shortest_distance[current] + 1

            if temp_shortest_distance < shortest_distance[neighbor]:
                came_from[neighbor] = current
                shortest_distance[neighbor] = temp_shortest_distance

                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put(
                        (shortest_distance[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()

        draw()

        if current != start:
            current.make_closed()

    return False


def main(win, width):
    ROWS = 50
    grid = make_grid(ROWS, width)

    start = None
    end = None

    run = True
    started = False

    while run:
        draw(win, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            # LEFT mouse button pressed
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]

            # if we havent found a start and pos is not the end
                if not start and spot != end:
                    start = spot
                    start.make_start()

            # if we havent found the end and the pos is not the start
                elif not end and spot != start:
                    end = spot
                    end.make_end()

                elif spot != end and spot != start:
                    spot.make_barrier()

            # RIGHT mouse button pressed
            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]
                spot.reset()
                if spot == start:
                    start = None
                elif spot == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for spot in row:
                            spot.update_neighbors(grid)
                    # run algo
                    algorithm(lambda: draw(win, grid, ROWS, width),
                              grid, start, end)

                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)
    pygame.quit()


main(WIN, WIDTH)
