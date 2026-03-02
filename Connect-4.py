
import numpy as np
import math
import pygame
import sys
pygame.init()
Squaresize = 100
width = 7 * Squaresize
height = 7 * Squaresize
size = (width, height)
screen = pygame.display.set_mode(size)

def create_board():
    board = np.zeros((6,7))
    return board

def drop_piece(board, row, collumn, piece):
    board[row][collumn] = piece


def is_valid_location(board, collumn):
    return board[5][collumn] == 0

def get_next_open_row(board, collumn):
    for row in range(6):
        if board[row][collumn] == 0:
            return row

def winning_move(board, piece):
    #check x axis for winning state
    for collumn in range(4):
        for row in range(6):
            if board[row][collumn] == piece and board[row][collumn+1] == piece and board[row][collumn+2]==piece and board[row][collumn+3] == piece:
             return True 
    #check y axis for winning state
    for collumn in range(7):
        for row in range(3):
            if board[row][collumn] == piece and board[row+1][collumn] == piece and board[row+2][collumn]==piece and board[row+3][collumn] == piece:
             return True 
    #positibe diagonals
    for collumn in range(4):
        for row in range(3):
            if board[row][collumn] == piece and board[row+1][collumn+1] == piece and board[row+2][collumn+2]==piece and board[row+3][collumn+3] == piece:
                return True
    #negative diagonals 
    for collumn in range(4):
        for row in range(3,6):
             if board[row][collumn] == piece and board[row-1][collumn+1] == piece and board[row-2][collumn+2]==piece and board[row-3][collumn+3] == piece:
                return True
def get_valid_location(board):
    valid_locations = []
    for collumn in range(7):
        if is_valid_location(board, collumn):
            valid_locations.append(collumn)
    return valid_locations

def scoring_position(board, piece):
    score = 0
    #horizontal
    for row in range(6):
        row_array = [int(i) for i in list(board[row, :])]
        for collumn in range(4):
            window = row_array[collumn: collumn + 4]
            if window.count(piece) == 4:
                score += 100
            elif window.count(piece) == 3 and window.count(0) == 1:
                score += 10
    for collumn in range(7):
        collumn_array = [int(i) for i in list(board[:,collumn])]
        for row in range(3):
            window = collumn_array[row: row + 4]
            if window.count(piece) == 4:
                score += 100
            elif window.count(piece) == 3 and window.count(0) == 1:
                score += 10
    #positive diagonals
    for row in range(3):
        for collumn in range(4):
            window =[board[row+i][collumn+i] for i in range(4)]
            if window.count(piece) == 4:
                score += 100
            elif window.count(piece) == 3 and window.count(0) == 1:
                score += 10
    #negative diagonals
    for row in range(3,6):
        for collumn in range(4):
            window = [board[row-i][collumn+i] for i in range(4)]
            if window.count(piece) == 4:
                score += 100
            elif window.count(piece) == 3 and window.count(0) == 1:
                score += 10
    return score 
             
def print_board(board):
    print(np.flip(board,axis=0))

def draw_board(board):
    for collumn in range(7):
        for row in range (6):
            pygame.draw.rect(screen,(0,0,255),(collumn*Squaresize, row*Squaresize+Squaresize, Squaresize, Squaresize))
            pygame.draw.circle(screen,(0,0,0),(int(collumn*Squaresize+Squaresize/2), int(row*Squaresize+Squaresize+Squaresize/2)), int(Squaresize/2 - 6))
    for collumn in range(7):
        for row in range(6):
            if board[row][collumn] == 1:
               pygame.draw.circle(screen,(255,0,0),(int(collumn*Squaresize+Squaresize/2), height-int(row*Squaresize+Squaresize/2)), int(Squaresize/2 - 6))
            elif board[row][collumn] == 2:
               pygame.draw.circle(screen,(255,255,0), (int(collumn*Squaresize+Squaresize/2), height- int(row*Squaresize+Squaresize/2)), int(Squaresize/2 - 6))
            
    pygame.display.update()
def terminal_node(board):
    return winning_move(board,1) or winning_move(board, 2) or len(get_valid_location(board)) == 0

def create_node(board, parent=None, move=None, player=2):
    return{
        "board" : board,
        "parent" : parent,
        "move": move,
        "player": player,
        "children": [],
        "wins": 0,
        "visits": 0,
        "untriedmoves": get_valid_location(board)

    }
def UpperBound1(child, exploration=math.sqrt(2)):
    if child['visits'] == 0:
        return float('inf')
    return (child['wins'] / child['visits']) + exploration * math.sqrt(math.log(child['parent']['visits']) / child['visits'])

def expand(node):
    move = node['untriedmoves'].pop()
    row = get_next_open_row(node['board'], move)
    new_board = node['board'].copy()

    next_player = 1 if node['player'] == 2 else 2
    drop_piece(new_board,row,move, next_player)
    child = create_node(new_board, parent=node, move=move, player=next_player)
    node['children'].append(child)
    return child

def select(node):
    while not terminal_node(node['board']):
        if node['untriedmoves']:
            return expand(node)
        else:
            node = max(node['children'], key=UpperBound1)
    return node

def backpropagate(node, winner):
    while node is not None:
        node['visits'] += 1
        if node['player'] == winner:
            node['wins'] += 1
        node = node['parent']

def simulate(board, player):
    temp_board = board.copy()
    current_player = player

    while not terminal_node(temp_board):
        valid_moves = get_valid_location(temp_board)
        move = np.random.choice(valid_moves)
        row = get_next_open_row(temp_board, move)
        drop_piece(temp_board, row, move, current_player)

        current_player = 1 if current_player == 2 else 2

    if winning_move(temp_board, 2):
        return 2
    elif winning_move(temp_board, 1):
        return 1
    else:
        return 0

def montecarlo(root_board, simulations=1000):
    root = create_node(root_board.copy(), player=1)
    for i in range(simulations):
        node = select(root)
        next_player = 1 if node['player'] == 2 else 2
        winner = simulate(node['board'], next_player)
        backpropagate(node, winner)
    best_child = max(root['children'], key=lambda c: c['visits'])
    return best_child['move'] 


def minimax(board, depth, alpha, beta, maxPlayer):
    valid_locations = get_valid_location(board)
    is_terminal = terminal_node(board)

    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, 2):
                return (None, 1000000000000000)
            elif winning_move(board, 1):
                return (None, -1000000000000000)
            else:
                return (None, 0)
        else:
            return (None, scoring_position(board, 2))

    if maxPlayer:
        value = -math.inf
        col = np.random.choice(valid_locations)
        for column in valid_locations:
            row = get_next_open_row(board, column)
            b_copy = board.copy()
            drop_piece(b_copy, row, column, 2)
            new_score = minimax(b_copy, depth-1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                col = column
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return col, value

    else:
        value = math.inf
        col = np.random.choice(valid_locations)
        for column in valid_locations:
            row = get_next_open_row(board, column)
            b_copy = board.copy()
            drop_piece(b_copy, row, column, 1)
            new_score = minimax(b_copy, depth-1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                col = column
            beta = min(beta, value)
            if alpha >= beta:
                break
        return col, value


board = create_board()
game_over = False
turn = 0
 
pygame.display.set_mode(size)
draw_board(board)
pygame.display.update()
font = pygame.font.SysFont("arial", 75)

GameModes = input("Select Game Mode: 'mtcs'/'AB'")

while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.MOUSEMOTION:
            pygame.draw.rect(screen,(0,0,0), (0,0,width,Squaresize))
            posistion_x = event.pos[0]
            if turn == 0:
                pygame.draw.circle(screen, (255,0,0), (posistion_x, int(Squaresize/2)), int(Squaresize/2 - 6))
            else:
                pygame.draw.circle(screen, (255,255,0), (posistion_x, int(Squaresize/2)), int(Squaresize/2 - 6))
        pygame.display.update()                           
        if event.type == pygame.MOUSEBUTTONDOWN:
           # print(event.pos)
           pygame.draw.rect(screen,(0,0,0), (0,0,width,Squaresize))
           if turn == 0:
               x_position = event.pos[0]
               collumn = math.floor(x_position/Squaresize)
               if is_valid_location(board,collumn):
                  row = get_next_open_row(board, collumn)
                  drop_piece(board, row, collumn, 1)
                  draw_board(board)
                  if winning_move(board, 1):
                       label = font.render("Player 1 wins", 1, (255,0,0))
                       screen.blit(label, (40,10))
                       pygame.display.update()
                       game_over = True
                  turn += 1
                  turn = turn % 2
                

    if turn == 1 and not game_over:
        if GameModes == 'mtcs':
            collumn = montecarlo(board, simulations=3000)
        elif GameModes == 'AB':
            collumn, score = minimax(board, 4, -math.inf, math.inf, True)
        if is_valid_location(board,collumn):
            row = get_next_open_row(board, collumn)
            drop_piece(board, row, collumn, 2)
            draw_board(board)
            if winning_move(board, 2):
               label = font.render("Player 2 wins", 1, (255,255,0))
               screen.blit(label, (40,10))
               pygame.display.update()
               game_over = True
            print_board(board)
            draw_board(board)
            turn += 1
            turn = turn % 2
    
    
    if game_over:
        pygame.time.wait(3000)

    



