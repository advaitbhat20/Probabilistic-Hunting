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
        self.prob = 0
        # type of terrain 1-flat, 2-hill, 3-forest, 0-default
        self.terrain = 0
        # check if cell is already examined
        self.examined = False



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


def examine(hash_map, position, target):
    x = position[0]
    y = position[1]
    cell = hash_map[(x,y)]
    cell.examined = True
    # print("#####Examine#####")

    if position == target.position:
        # print("target terrain", cell.terrain)
        num = random.uniform(0,1)
        if cell.terrain == 1:
            if num > 0.2:
                return True
        elif cell.terrain == 2:
            if num > 0.5:
                return True
        elif cell.terrain == 3:
            if num > 0.8:
                return True

    return False

#This function needs to update all other cells probability depending upon the terrain type of the current cell
# we only call this function when the examination of x,y gives us false
def update_prob(position, belief, hash_map, condition):
    x = position[0]
    y = position[1]
    grid_len = len(belief)
    #UPDATE WHEN CELL ENCOUNTERED IS BLOCKED
    if condition == "blocked":
        for i in range(grid_len):
            for j in range(grid_len):
                if i != x and j != y:
                    prob = belief[i][j]/(1- belief[x][y])
                    belief[i][j] = prob
        belief[x][y] = 0
    #UPDATE WHEN CELL ENCOUNTERED IS FLAT
    if condition == 1:
        summation = 0
        for i in range(grid_len):
            for j in range(grid_len):
                if i != x and j != y and knowledge[i][j] != 1:
                    prob = belief[i][j]/((1- belief[x][y])+(belief[x][y]*0.2))
                    belief[i][j] = prob
                    summation += prob
                    if summation > 1:
                        print("belief overflow", summation, (x,y))
                        # print_grid(belief)
                        # print_grid(knowledge)
                        # print_grid(matrix)
                        sys.exit()
        belief[x][y] = 0.2*belief[x][y]/(0.2*belief[x][y]+(1-belief[x][y]))
    #UPDATE WHEN CELL ENCOUNTERED IS HILLY
    if condition == 2:
        summation = 0
        for i in range(grid_len):
            for j in range(grid_len):
                if i != x and j != y and knowledge[i][j] != 1:
                    prob = belief[i][j]/((1- belief[x][y])+(belief[x][y]*0.5))
                    belief[i][j] = prob
                    summation += prob
                    if summation > 1:
                        print("belief overflow", summation, (x,y))
                        # print_grid(belief)
                        # print_grid(knowledge)
                        # print_grid(matrix)
                        sys.exit()

        belief[x][y] = 0.5*belief[x][y]/(0.2*belief[x][y]+(1-belief[x][y]))
    #UPDATE WHEN CELL ENCOUNTERED IS FOREST
    if condition == 3:
        summation = 0
        for i in range(grid_len):
            for j in range(grid_len):
                if i != x and j != y and knowledge[i][j] != 1:
                    prob = belief[i][j]/((1- belief[x][y])+(belief[x][y]*0.8))
                    belief[i][j] = prob
                    summation += prob
                    if summation > 1:
                        print("belief overflow", summation, (x,y))
                        # print_grid(belief)
                        # print_grid(knowledge)
                        # print_grid(matrix)
                        sys.exit()
        belief[x][y] = 0.8*belief[x][y]/(0.2*belief[x][y]+(1-belief[x][y]))


def get_max_prob(belief, checked, start, hash_map):
    max_prob = -1
    max_pos = (0,0)
    grid_len = len(belief)
    terrain_fnr = (1,0.2,0.5,0.8)

    for i in range(grid_len):
        for j in range(grid_len):
            cell = hash_map[(i,j)]
            terrain_type = cell.terrain
            prob_finding_target = belief[i][j]*(1-terrain_fnr[terrain_type])
            if prob_finding_target > max_prob and checked[i][j]==0 and start[0] != i  and start[1] != j:
                max_prob = prob_finding_target
                max_pos = (i,j)
                checked[i][j]=1
            elif prob_finding_target == max_prob and checked[i][j]==0 and start[0] != i  and start[1] != j:
                if calc_manhattan(start, (i,j)) < calc_manhattan(start,max_pos) and calc_manhattan(start, (i,j)) != 0:
                    max_pos = (i,j)
                    checked[i][j]=1
                elif calc_manhattan(start, (i,j)) == calc_manhattan(start,max_pos):
                    if random.uniform(0, 1) > 0.5:
                        max_pos = (i,j)
                        checked[i][j]=1
    
    return max_pos


####################################################################################
#################################     MAIN    ######################################
####################################################################################

if __name__ == "__main__":
    grid_len = 100
    actual_path = []
    shortest_path = []
    #Dictionary to store nodes
    hash_map = {} 

    #creating random grid world by providing it a p value of 0.3
    matrix = create_grid(grid_len, 0.3)

    #initializing knowledge of agent
    knowledge = [ [ "-" for i in range(grid_len) ] for j in range(grid_len) ]
    
    #initialize dim X dim matrix to maintain the belief
    initial_prob = 1/(grid_len*grid_len)
    belief = [ [initial_prob for i in range(grid_len)] for j in range(grid_len) ]

    #Set the start and goal
    start = Node()
    start.position = (random.randint(0,grid_len-1), random.randint(0,grid_len-1))
    matrix[start.position[0]][start.position[1]] = 0
    target = Node()
    target.position = (random.randint(0,grid_len-1), random.randint(0,grid_len-1))
    matrix[target.position[0]][target.position[1]] = 0

    print("start", start.position)
    print("target", target.position)

    # print("FULL KNOWN GRIDWORLD")
    # print_grid(matrix)

    target_count = 0

    #create node for each cell and assign a terrain type to it:
    for i in range(grid_len):
        for j in range(grid_len):
            cell = Node((i,j))
            # assigning terrain types for unblocked cells
            if (matrix[i][j] == 0):
                num = random.uniform(0, 1)
                if(num < 0.33):
                    cell.terrain = 1 #flat
                elif(num < 0.66):
                    cell.terrain = 2 #mountain
                else:
                    cell.terrain = 3 #forrest
            hash_map[(i,j)] = cell

    # for any given grid ... first check whether the target is reachable from start
    res = Astar(matrix, start, target)
    if res == None:
        sys.exit()
    print("path", res)

    #run the agent until target found
    flag = True
    steps = 0
    while flag:
        checked = [ [0 for i in range(grid_len)] for j in range(grid_len) ]
        #find path from current to prob_target
        count = 0
        while True:
            prob_target = get_max_prob(belief, checked, start.position,hash_map)
            prob_target = hash_map[prob_target] 
            # print("target",prob_target)
            target_count += 1
            path = Astar(knowledge, start, prob_target)[0]
            if path:
                break
            else:
                update_prob(prob_target.position, belief, hash_map, "blocked")
            if count==grid_len^2-1:
                print("all targets checked")
                flag = False
                break
            count += 1

        #move along the path provided by A-star
        if path:
            itr = 1    
            while itr < len(path):
                steps += 1
                x = path[itr][0]
                y = path[itr][1]

                if matrix[x][y] == 1:
                    print("blocked",x,y)
                    knowledge[x][y] = 1
                    update_prob((x, y), belief, hash_map, "blocked")
                    if itr-1>=0:
                        start = hash_map[path[itr-1]]
                        # print("start" , start)
                        checked = [ [0 for i in range(grid_len)] for j in range(grid_len) ]
                        count = 0
                        while True:
                            prob_target = get_max_prob(belief, checked, start.position, hash_map)
                            prob_target = hash_map[prob_target] 
                            path = Astar(knowledge, start, prob_target)
                            if path:
                                break
                            else:
                                update_prob(prob_target.position, belief, hash_map, "blocked")
                            if count==grid_len^2-1:
                                print("all targets checked")
                                flag = False
                                break
                            count += 1
                        itr = 1
                    
                else:
                    if examine(hash_map, (x,y), target):
                        print("target found ", x, y)
                        flag = False
                        break
                    else:
                        update_prob((x,y), belief, hash_map, hash_map[(x,y)].terrain)
                        # update_prob((x,y), belief, hash_map, hash_map[(x,y)].terrain)
                    itr += 1
        else:
            print("path not found")
            print("exit loop")
            break
    print("matrix")
    print_grid(matrix)
    print("knowledge")
    print_grid(knowledge)
    print("belied")
    print_grid(belief)
    print("targets", target_count)
    print("steps", steps)