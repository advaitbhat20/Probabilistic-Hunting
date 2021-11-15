# Node class for storing position, cost and heuristic for each grid encountered
class Node:
    # Initialize the class
    def __init__(self, position=None, parent=None):
        self.position = position
        self.parent = parent
        self.g = 0
        self.h = 0
        self.f = 0
        # type of terrain 1-flat, 2-hill, 3-forest, 0-default
        self.terrain = 0

    
####################################################################################
##########################    HELPER FUNCTIONS    ##################################
####################################################################################


####################################################################################
##########################   ASTAR and Implement  ##################################
####################################################################################

def examine(hash_map, position, target):
    x = position[0]
    y = position[1]
    cell = hash_map[(x,y)]

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
    summation = 0
    #UPDATE WHEN CELL ENCOUNTERED IS BLOCKED
    if condition == "blocked":
        for i in range(grid_len):
            for j in range(grid_len):
                if i != x and j != y:
                    prob = belief[i][j]/(1- belief[x][y])
                    belief[i][j] = prob
                    summation += prob
        belief[x][y] = 0
    #UPDATE WHEN CELL ENCOUNTERED IS FLAT
    elif condition == 1:
        for i in range(grid_len):
            for j in range(grid_len):
                if i != x and j != y and knowledge[i][j] != 1:
                    prob = belief[i][j]/((1- belief[x][y])+(belief[x][y]*0.2))
                    belief[i][j] = prob
                    summation += prob
                    # if summation > 1:
                        # print("belief overflow", summation, (x,y))
                        # print_grid(belief)
                        # print_grid(knowledge)
                        # print_grid(matrix)
                        # sys.exit()
        belief[x][y] = 0.2*belief[x][y]/(0.2*belief[x][y]+(1-belief[x][y]))
        summation += belief[x][y]
    #UPDATE WHEN CELL ENCOUNTERED IS HILLY
    elif condition == 2:
        for i in range(grid_len):
            for j in range(grid_len):
                if i != x and j != y and knowledge[i][j] != 1:
                    prob = belief[i][j]/((1- belief[x][y])+(belief[x][y]*0.5))
                    belief[i][j] = prob
                    summation += prob
                    # if summation > 1:
                    #     print("belief overflow", summation, (x,y))
                        # print_grid(belief)
                        # print_grid(knowledge)
                        # print_grid(matrix)
                        # sys.exit()
        belief[x][y] = 0.5*belief[x][y]/(0.5*belief[x][y]+(1-belief[x][y]))
        summation += belief[x][y]
    #UPDATE WHEN CELL ENCOUNTERED IS FOREST
    elif condition == 3:
        for i in range(grid_len):
            for j in range(grid_len):
                if i != x and j != y and knowledge[i][j] != 1:
                    prob = belief[i][j]/((1- belief[x][y])+(belief[x][y]*0.8))
                    belief[i][j] = prob
                    summation += prob
                    # if summation > 1:
                    #     print("belief overflow", summation, (x,y))
                        # print_grid(belief)
                        # print_grid(knowledge)
                        # print_grid(matrix)
                        # sys.exit()
        belief[x][y] = 0.8*belief[x][y]/(0.8*belief[x][y]+(1-belief[x][y]))
        summation += belief[x][y]

    
    for i in range(grid_len):
        for j in range(grid_len):
            belief[i][j] = belief[i][j]/summation


def get_max_prob(belief, checked, start):
    max_prob = -1
    max_pos = (0,0)
    grid_len = len(belief)

    for i in range(grid_len):
        for j in range(grid_len):
            if belief[i][j] > max_prob and checked[i][j]==0 and start[0] != i  and start[1] != j:
                max_prob = belief[i][j]
                max_pos = (i,j)
                checked[i][j]=1
            elif belief[i][j] == max_prob and checked[i][j]==0 and start[0] != i  and start[1] != j:
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
    grid_len = 20
    actual_path = []
    shortest_path = []
    #Dictionary to store nodes
    hash_map = {} 

    #creating random grid world by providing it a p value of 0.3
    matrix = create_grid(grid_len, 0.3)


    #Set the start and goal
    start = Node()
    start.position = (random.randint(0,grid_len-1), random.randint(0,grid_len-1))
    matrix[start.position[0]][start.position[1]] = 0
    target = Node()
    target.position = (random.randint(0,grid_len-1), random.randint(0,grid_len-1))
    matrix[target.position[0]][target.position[1]] = 0
    targetx = target.position[0]
    targety = target.position[1]
    print("start", start.position)
    print("target", target.position)


    #######################################################################


    #initializing knowledge of agent
    knowledge = [ [ "-" for i in range(grid_len) ] for j in range(grid_len) ]
    
    #initialize dim X dim matrix to maintain the belief
    initial_prob = 1/(grid_len*grid_len)
    belief = [ [initial_prob for i in range(grid_len)] for j in range(grid_len) ]

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
    if res == [None]:
        print("not solvable")
        sys.exit()
    # print("path", res)
    target_count = 0

    #run the agent until target found
    flag = True
    steps = 0
    while flag:
        checked = [ [0 for i in range(grid_len)] for j in range(grid_len) ]
        #find path from current to prob_target
        count = 0
        while True:
            # print("here")
            prob_target = get_max_prob(belief, checked, start.position)
            prob_target = hash_map[prob_target] 
            target_count += 1
            path = Astar(knowledge, start, prob_target)[0]
            if path:
                # print("found the true path", path)
                break
            else:
                update_prob(prob_target.position, belief, hash_map, "blocked")
            count += 1

        #move along the path provided by A-star
        if path:
            itr = 1    
            while itr < len(path):
                steps += 1
                x = path[itr][0]
                y = path[itr][1]

                if matrix[x][y] == 1:
                    knowledge[x][y] = 1
                    update_prob((x, y), belief, hash_map, "blocked")
                    if itr-1>=0:
                        start = hash_map[path[itr-1]]
                        checked = [ [0 for i in range(grid_len)] for j in range(grid_len) ]
                        count = 0
                        while True:
                            prob_target = get_max_prob(belief, checked, start.position)
                            prob_target = hash_map[prob_target] 
                            path = Astar(knowledge, start, prob_target)
                            if path:
                                break
                            count += 1
                else:
                    if examine(hash_map, (x,y), target):
                        print("target found ", x, y)
                        flag = False
                        break
                    else:
                        update_prob((x,y), belief, hash_map, hash_map[(x,y)].terrain)
                
                itr += 1
    print("Agent6 targets", target_count)
    print("Agent6 steps", steps)