# randomly choose among adjacent moves
import json
import random
BOARD_SIZE = 15
board = [[0 for x in range(BOARD_SIZE)] for y in range(BOARD_SIZE)]


def adjacent(grid, x, y):
    if grid[x][y] != 0:
        return False
    if x - 1 >= 0 and grid[x-1][y] != 0:
        return True
    if y - 1 >= 0 and grid[x][y-1] != 0:
        return True
    if x + 1 < 15 and grid[x+1][y] != 0:
        return True
    if y + 1 < 15 and grid[x][y+1] != 0:
        return True
    if x + 1 < 15 and y + 1 < 15 and grid[x+1][y+1] != 0:
        return True
    if x + 1 < 15 and y - 1 >= 0 and grid[x+1][y-1] != 0:
        return True
    if x - 1 >= 0 and y + 1 < 15 and grid[x-1][y+1] != 0:
        return True
    if x - 1 >= 0 and y - 1 >= 0 and grid[x-1][y-1] != 0:
        return True
    return False
    
def get_all_moves(grid):
    all_moves = []
    for x in range(15):
        for y in range(15):
            if adjacent(grid, x, y):
                all_moves.append((x, y))
    if len(all_moves) == 0:
        return [(x, y) for x in range(15) for y in range(15)]
    return all_moves

def place_at(x, y, stone):
    if x >= 0 and y >= 0:
        board[x][y] = stone
        
if __name__ == "__main__":
    # 解析读入的JSON
    full_input = json.loads(input())
    if "data" in full_input:
        my_data = full_input["data"]; # 该对局中，上回合该Bot运行时存储的信息
    else:
        my_data = None

    # 分析自己收到的输入和自己过往的输出，并恢复状态
    all_requests = full_input["requests"]
    all_responses = full_input["responses"]
    if all_requests[0]['x'] == all_requests[0]['y'] == -1:
        stone = 1
    else:
        stone = 2

    for i in range(len(all_responses)):
        my_input = all_requests[i] # i回合我的输入
        my_output = all_responses[i] # i回合我的输出
        # TODO: 根据规则，处理这些输入输出，从而逐渐恢复状态到当前回合
        place_at(my_input['x'], my_input['y'], 3 - stone)
        place_at(my_output['x'], my_output['y'], stone)

    # 看看自己最新一回合输入
    curr_input = all_requests[-1]
    place_at(curr_input['x'], curr_input['y'], stone)

    # TODO: 作出决策并输出
    x, y = random.choice(get_all_moves(board))
    my_action = {'x': x, 'y': y}

    print(json.dumps({"response": my_action}))
