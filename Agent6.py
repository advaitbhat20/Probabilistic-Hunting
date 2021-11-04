from queue import PriorityQueue
from dataclasses import dataclass, field
import random
import math
import sys

max = sys.maxsize

neighbour_cardinal = [(-1, 0),(0, -1),(0, 1),(1, 0)]

# Node class for storing position, cost and heuristic for each grid encountered
class Node:
    # Initialize the class
    def __init__(self, position=None, parent=None):
        self.position = position
        self.parent = parent
        self.g = 0
        self.h = 0
        self.f = 0
        # probability of the cell being the target 
        self.prob = 1
        # type of terrain 1-flat, 2-hill, 3-forest, 0-default
        self.terrain = 0



    # Compare nodes
    def __eq__(self, other):
        return self.position == other.position

    def __ne__(self, other):
        return not (self.position == other.position)

    def __lt__(self, other):
        return (self.f < other.f)

    def __gt__(self, other):
        return (self.f > other.f)

    def __hash__(self):
        # hash(custom_object)
        return hash((self.position, self.parent))

    # Print node
    def __repr__(self):
        return ('({0},{1})'.format(self.position, self.f))


    #This returns the neighbours of the Node
    def get_neigbours(self, matrix):
        current_x = self.position[0]
        current_y = self.position[1]
        neighbours = []
        for n in neighbour_cardinal:
            x = current_x + n[0]
            y = current_y + n[1]
            if 0 <= x < len(matrix) and 0 <= y < len(matrix):
                c = Node()
                c.position = (x, y)
                c.parent = self
                c.g = self.g + 1
                neighbours.append(c)
        return neighbours

    
####################################################################################
##########################    HELPER FUNCTIONS    ##################################
####################################################################################

#creating a randomized grid world
def create_grid(n, p):
    matrix = [ [ 0 for i in range(n) ] for j in range(n) ]
    for i in range(n):
        for j in range(n):
            if (i == 0 and j == 0) or (i==n-1 and j==n-1):
                matrix[i][j] = 0
            else:
                prob = random.uniform(0, 1)
                if prob >= p:
                    matrix[i][j] = 0
                else:
                    matrix[i][j] = 1
    return matrix

#print the gridworld/knowledge
def print_grid(matrix):
    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            print(matrix[i][j], end=" ")
        print("")

def count_blocks(matrix):
    count = 0
    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            if matrix[i][j] == 1:
                count+=1
    return count

def calc_manhattan(a,b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])


####################################################################################
##########################   ASTAR and Implement  ##################################
####################################################################################

@dataclass(order=True)
class PrioritizedItem:
    priority: float
    item: object = field()

def Astar(knowledge_grid, start, end, flag=True, heuristic="manhattan"):
    grid_len = len(knowledge_grid)

    # Initialize a priority queue
    pQueue = PriorityQueue()
    pQueue.put(PrioritizedItem(0.0, start))
    closed_hash = {}    
    counter = 0

    while not pQueue.empty():
    #     # print(counter, len(pQueue.queue))
    #     if counter > 20000:
    #         return [None]

        current = pQueue.get().item

        #Using dictionary instead of a list, to make retrival easier
        closed_hash[current.position] = True

        # Check if we have reached the goal, return the path
        if current == end:
            path = []
            while current != start:
                path.append(current.position)
                current = current.parent
            path.append(start.position)
            # Return reversed path
            return [path[::-1]]

        for n in current.get_neigbours(knowledge_grid):
            #check if neighbor is in closed set
            if n.position in closed_hash:
                continue
            #calculate heuristics for the neighbor
            if heuristic == "manhattan":
                n.h = calc_manhattan(n.position, [grid_len-1,grid_len-1])


            if flag:
                n.f = n.g + n.h
                #check if node is in priority queue if yes does it have lower value?

                #add n to priority queue
                (x, y) = n.position
                if knowledge_grid[x][y] != 1:
                    pQueue.put(PrioritizedItem(float(n.f), n))

            #When using ASTAR to verify our solution consider undiscovered node's g to be infinity
            else:
                if knowledge_grid[n.position[0]][n.position[1]] ==  '-':
                    n.g = max
                n.f = n.g + n.h
                #check if node is in priority queue if yes does it have lower value?

                #add n to priority queue
                (x, y) = n.position
                if knowledge_grid[x][y] != 1:
                    pQueue.put(PrioritizedItem(float(n.f), n))

    return [None]



# def agent6():


####################################################################################
#################################     MAIN    ######################################
####################################################################################

if __name__ == "__main__":
    grid_len = 10
    actual_path = []
    shortest_path = []
    hash_map = {} #Dictionary to store nodes

    #creating random grid world by providing it a p value of 0.3
    matrix = create_grid(grid_len, 0.30)

    print("FULL KNOWN GRIDWORLD")
    print_grid(matrix)

    c_flat = 0
    c_hill = 0
    c_forrest = 0

    #create node for each cell and assign a terrain type to it:
    for i in range(grid_len):
        for j in range(grid_len):
            cell = Node(i,j)
            if (matrix[i][j] ==0):
                num = random.uniform(0, 1)
                if(num < 0.33):
                    cell.terrain = 1
                    c_flat += 1
                elif(num < 0.66):
                    cell.terrain = 2
                    c_hill += 1
                else:
                    cell.terrain = 3
                    c_forrest += 1

    
    print("flat", c_flat)
    print("hill", c_hill)
    print("forrest", c_forrest)


    # #initializing knowledge of agent
    knowledge = [ [ "-" for i in range(grid_len) ] for j in range(grid_len) ]
    
    #Set the start and goal
    start = Node()
    start.position = (random.randint(0,grid_len-1), random.randint(0,grid_len-1))
    target = Node()
    target.position = (random.randint(0,grid_len-1), random.randint(0,grid_len-1))

    print("start", start.position)
    print("target", target.position)

    # for any given grid ... first check whether the target is reachable from start
    res = Astar(knowledge, start, target)
    print("path", res)


    #Call the Agent
    # res = agent_3(matrix, knowledge, start, goal, "manhattan")

    
    #CHECKING CONSISTENCY OF DATA IN KNOWLEDGE AND MATRIX
    # for i in range(grid_len):
    #     for j in range(grid_len):
    #         if (matrix[i][j] != knowledge[i][j] and knowledge[i][j] != '-'):
    #             print(i, j, "mismatch should be ", matrix[i][j], " is ", knowledge[i][j])
    #             hash_map[(i,j)].print_attributes()
    #             break