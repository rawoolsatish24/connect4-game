import numpy as np
from pygame import mixer
import sys
import math
from Constants import *
from Button import *
import re
import random


# This function is used to play music on different occassions.
def play_music(type):
    mixer.init()
    mixer.music.load("sounds/" + type + ".wav")
    mixer.music.play()


# This function is used to initialize the game board position for new game.
def initialize_board():
    board = np.zeros((ROW_COUNT, COLUMN_COUNT))
    return board


# This function is used to add new piece at particular position for particular either 1st or 2nd player.
def add_new_piece(board, row, col, piece):
    board[row][col] = piece


# This function is used to check whether given position is available to add new piece or not.
def is_valid_position(board, col):
    return board[ROW_COUNT - 1][col] == 0


# This function is used to get row no. available to add new piece.
def get_available_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r


# This function is used to check if match is drawn or not.
def is_draw(board):
    for z in range(COLUMN_COUNT):
        for y in range(ROW_COUNT):
            if board[y][z] == 0: return False
    return True


# This function is used to check all possible winning combinations if player is winning or not.
def is_winning(board, piece):
    # Check Horizontal Combination
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT):
            if board[r][c] == piece and board[r][c + 1] == piece and board[r][c + 2] == piece and board[r][c + 3] == piece:
                return True

    # Check Vertical Combination
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 3):
            if board[r][c] == piece and board[r + 1][c] == piece and board[r + 2][c] == piece and board[r + 3][c] == piece:
                return True

    # Check Forward Diagonal Combination
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT - 3):
            if board[r][c] == piece and board[r + 1][c + 1] == piece and board[r + 2][c + 2] == piece and board[r + 3][
                c + 3] == piece:
                return True

    # Check Backward Diagonal Combination
    for c in range(COLUMN_COUNT - 3):
        for r in range(3, ROW_COUNT):
            if board[r][c] == piece and board[r - 1][c + 1] == piece and board[r - 2][c + 2] == piece and board[r - 3][
                c + 3] == piece:
                return True


# This function is used to differentiate different scores as per the situation.
def evaluate_window(window, piece):
    score = 0
    opp_piece = PLAYER_PIECE
    if piece == PLAYER_PIECE:
        opp_piece = AI_PIECE
    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2
    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 4
    return score


# This function is used to print text as an image.
def draw_text(text, y):
    lstLines = text.splitlines()
    for line in lstLines:
        img = fontNote.render(line, True, WHITE)
        screen.blit(img, ((width - img.get_width()) / 2, y))
        y += 20


# This function is used to get possible score for the current data.
def score_position(board, piece):
    score = 0

    # Score Center Combination
    center_array = [int(i) for i in list(board[:, COLUMN_COUNT // 2])]
    center_count = center_array.count(piece)
    score += center_count * 3

    # Score Horizontal Combination
    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[r, :])]
        for c in range(COLUMN_COUNT - 3):
            window = row_array[c:c + WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # Score Vertical Combination
    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(board[:, c])]
        for r in range(ROW_COUNT - 3):
            window = col_array[r:r + WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # Score Forward Diagonal Combination
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r + i][c + i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    # Score Backward Diagonal Combination
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r + 3 - i][c + i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    return score


# This function is used to display board as per progress.
def draw_board(board):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE, (c * SQUARESIZE, r * SQUARESIZE + SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, BLACK, (
                int(c * SQUARESIZE + SQUARESIZE / 2), int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2)), RADIUS)

    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            if board[r][c] == 1:
                pygame.draw.circle(screen, RED, (
                    int(c * SQUARESIZE + SQUARESIZE / 2), height - int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)
            elif board[r][c] == 2:
                pygame.draw.circle(screen, YELLOW, (
                    int(c * SQUARESIZE + SQUARESIZE / 2), height - int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)
    pygame.display.update()


# This function is used to get valid move for AI.
def get_valid_move_for_AI(board):
    valid_locations = []
    for col in range(COLUMN_COUNT):
        if is_valid_position(board, col):
            valid_locations.append(col)
    return valid_locations


def is_root_node(board):
    return is_winning(board, PLAYER_PIECE) or is_winning(board, AI_PIECE) or len(get_valid_move_for_AI(board)) == 0


# This function is used to calculate best move for AI.
def mini_max(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_move_for_AI(board)
    is_terminal = is_root_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if is_winning(board, AI_PIECE):
                return None, 100000000000000
            elif is_winning(board, PLAYER_PIECE):
                return None, -10000000000000
            else:
                return None, 0
        else:  # Depth is zero
            return None, score_position(board, AI_PIECE)
    if maximizingPlayer:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_available_row(board, col)
            b_copy = board.copy()
            add_new_piece(b_copy, row, col, AI_PIECE)
            new_score = mini_max(b_copy, depth - 1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value
    else:  # Minimizing player
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_available_row(board, col)
            b_copy = board.copy()
            add_new_piece(b_copy, row, col, PLAYER_PIECE)
            new_score = mini_max(b_copy, depth - 1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value


# Initializing Game
play_music("entrance")
board = initialize_board()
isGameOver = True
curTurn = 0
menu_state = "Main"
player1name = ""
player2name = ""
noOfPlayers = 0

# Initializing Game Machine
pygame.init()
pygame.display.set_caption("Connect4 - Main Menu")

# Defining Size Of The Screen
width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT + 1) * SQUARESIZE
size = (width, height)
RADIUS = int(SQUARESIZE / 2 - 5)
screen = pygame.display.set_mode(size)

fontDefault = pygame.font.SysFont("monospace", 30)
fontDefault.bold = True
fontNote = pygame.font.SysFont("monospace", 17)
fontNote.bold = True
fontBase = pygame.font.Font(None, 32)
fontBase.bold = True

# Menu Image Objects
imgLogo = pygame.image.load("images/game_logo.png").convert_alpha()
imgPlay = pygame.image.load("images/menu_play.png").convert_alpha()
imgQuit = pygame.image.load("images/menu_quit.png").convert_alpha()
img1Player = pygame.image.load("images/menu_1player.png").convert_alpha()
img2Player = pygame.image.load("images/menu_2player.png").convert_alpha()
imgRetry = pygame.image.load("images/menu_retry.png").convert_alpha()
imgMainMenu = pygame.image.load("images/menu_main_menu.png").convert_alpha()
imgSubmit = pygame.image.load("images/menu_submit.png").convert_alpha()
imgNewGame = pygame.image.load("images/menu_new_game.png").convert_alpha()
# imgRules = pygame.image.load("images/menu_rules.png").convert_alpha()
posMainMenuLogo = (height - imgPlay.get_height() - imgQuit.get_height() - imgLogo.get_height()) / 2
posMainMenuPlay = posMainMenuLogo + imgLogo.get_height()
posMainMenuQuit = posMainMenuPlay + imgPlay.get_height()
posPlay1Player = (height - img1Player.get_height() - img2Player.get_height() - imgMainMenu.get_height()) / 2 - 100
posPlay2Player = posPlay1Player + img1Player.get_height()
posPlayMainMenu = posPlay2Player + img2Player.get_height()
posPlayRules = posPlayMainMenu + imgMainMenu.get_height() + 20

# Menu Button Objects
mnuPlay = Button((width - imgPlay.get_width()) / 2, posMainMenuPlay, imgPlay, 1)
mnuQuit1 = Button((width - imgQuit.get_width()) / 2, posMainMenuQuit, imgQuit, 1)
mnuQuit2 = Button((width - imgQuit.get_width()) / 2, posMainMenuQuit, imgQuit, 1)
mnu1Player = Button((width - img1Player.get_width()) / 2, posPlay1Player, img1Player, 1)
mnu2Player = Button((width - img2Player.get_width()) / 2, posPlay2Player, img2Player, 1)
mnuSubmit = Button((width - imgSubmit.get_width()) / 2, posPlay2Player, imgSubmit, 1)
mnuMainMenu = Button((width - imgMainMenu.get_width()) / 2, posPlayMainMenu, imgMainMenu, 1)
mnuNewGame = Button((width - imgNewGame.get_width()) / 2, posMainMenuQuit, imgNewGame, 1)
mnuRetry = Button((width - imgRetry.get_width()) / 2, posMainMenuPlay, imgRetry, 1)

input1Rectangle = pygame.Rect((width - 380) / 2, posPlay1Player + 50, 380, 30)

while True:
    if isGameOver:
        if menu_state == "Main":
            noOfPlayers = 0
            pygame.display.set_caption("Connect4 - Main Menu")
            screen.fill(BLACK)
            screen.blit(imgLogo, ((width - imgLogo.get_width()) / 2, posMainMenuLogo))
            if mnuPlay.draw(screen):
                menu_state = "Play"
            if mnuQuit1.draw(screen):
                sys.exit()
        if menu_state == "Play":
            pygame.display.set_caption("Connect4 - Play Menu")
            screen.fill(BLACK)
            if mnu1Player.draw(screen):
                pygame.display.set_caption("Connect4 - 1Player")
                menu_state = "Player1Name"
                player1name = ""
                noOfPlayers = 1
            if mnu2Player.draw(screen):
                pygame.display.set_caption("Connect4 - 2Player")
                menu_state = "Player1Name"
                player1name = ""
                noOfPlayers = 2
                continue
            if mnuMainMenu.draw(screen):
                menu_state = "Main"
            draw_text("Rules: " + GAME_RULE, posPlayRules)
        if menu_state == "Player1Name":
            screen.fill(BLACK)
            draw_text("Enter 1st Player Name", input1Rectangle.y - 30)
            pygame.draw.rect(screen, WHITE, input1Rectangle)
            screen.blit(fontBase.render(player1name, True, BLACK), (input1Rectangle.x + 10, input1Rectangle.y + 5))
            if mnuSubmit.draw(screen):
                if noOfPlayers == 1:
                    player2name = "COMPUTER"
                    screen.fill(BLACK)
                    isGameOver = False
                    menu_state = "1PGame"
                    board = initialize_board()
                    curTurn = 0
                    draw_board(board)
                elif player1name != "":
                    player2name = ""
                    menu_state = "Player2Name"
                    continue
            if mnuMainMenu.draw(screen):
                menu_state = "Play"
        if menu_state == "Player2Name":
            screen.fill(BLACK)
            draw_text("Enter 2nd Player Name", input1Rectangle.y - 30)
            pygame.draw.rect(screen, WHITE, input1Rectangle)
            screen.blit(fontBase.render(player2name, True, BLACK), (input1Rectangle.x + 10, input1Rectangle.y + 5))
            if mnuSubmit.draw(screen):
                player1name = player1name.strip()
                if player1name == "": player1name = "PLAYER 1"
                player2name = player2name.strip()
                if player2name == "": player2name = "PLAYER 2"
                screen.fill(BLACK)
                isGameOver = False
                menu_state = "2PGame"
                board = initialize_board()
                curTurn = 0
                draw_board(board)
            if mnuMainMenu.draw(screen):
                menu_state = "Play"
        if menu_state == "Retry":
            screen.fill(BLACK)
            pygame.display.set_caption("Connect4 - Retry")
            if mnuRetry.draw(screen):
                screen.fill(BLACK)
                isGameOver = False
                board = initialize_board()
                curTurn = 0
                draw_board(board)
                if noOfPlayers == 1:
                    menu_state = "1PGame"
                    pygame.display.set_caption("Connect4 - 1Player")
                else:
                    menu_state = "2PGame"
                    pygame.display.set_caption("Connect4 - 2Player")
            if mnuNewGame.draw(screen):
                menu_state = "Play"
    else:
        draw_board(board)

    for curEvent in pygame.event.get():
        if curEvent.type == pygame.QUIT:
            sys.exit()

        if menu_state == "Player1Name":
            if curEvent.type == pygame.KEYDOWN:
                if curEvent.key == pygame.K_BACKSPACE:
                    player1name = player1name[:-1]
                elif len(player1name) < 20 and re.fullmatch('[A-z ]', curEvent.unicode):
                    player1name += str(curEvent.unicode).upper()

        if menu_state == "Player2Name":
            if curEvent.type == pygame.KEYDOWN:
                if curEvent.key == pygame.K_BACKSPACE:
                    player2name = player2name[:-1]
                elif len(player2name) < 20 and re.fullmatch('[A-z ]', curEvent.unicode):
                    player2name += str(curEvent.unicode).upper()

        if menu_state in ["1PGame", "2PGame"]:
            screen.fill(BLACK)
            label = (fontDefault.render(player1name + " Turn", 1, RED) if curTurn == 0 else fontDefault.render(
                player2name + " Turn", 1, YELLOW))
            screen.blit(label, ((width - label.get_width()) / 2, (SQUARESIZE - label.get_height()) / 2))
            if curEvent.type == pygame.MOUSEMOTION:
                pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
                posx = curEvent.pos[0]
                if posx <= RADIUS + 4:
                    posx = RADIUS + 5
                elif posx >= (width - RADIUS - 4):
                    posx = (width - RADIUS - 5)
                if RADIUS + 4 < posx < (width - RADIUS - 4):
                    if curTurn == 0:
                        pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE / 2)), RADIUS)
                    else:
                        pygame.draw.circle(screen, YELLOW, (posx, int(SQUARESIZE / 2)), RADIUS)
            if curEvent.type == pygame.MOUSEBUTTONDOWN:
                pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
                if curTurn == 0:
                    posx = curEvent.pos[0]
                    col = int(math.floor(posx / SQUARESIZE))

                    if is_valid_position(board, col):
                        row = get_available_row(board, col)
                        add_new_piece(board, row, col, 1)

                        if is_draw(board):
                            screen.fill(BLACK)
                            draw_board(board)
                            label = fontDefault.render("Match Drawn !!", 1, RED)
                            pygame.display.set_caption("Connect4 - Match Drawn !!")
                            screen.blit(label, ((width - label.get_width()) / 2, (SQUARESIZE - label.get_height()) / 2))
                            isGameOver = True
                        elif is_winning(board, 1):
                            screen.fill(BLACK)
                            draw_board(board)
                            play_music("game_win")
                            label = fontDefault.render(player1name + " Win !!", 1, RED)
                            pygame.display.set_caption("Connect4 - " + player1name + " Win !!")
                            screen.blit(label, ((width - label.get_width()) / 2, (SQUARESIZE - label.get_height()) / 2))
                            isGameOver = True

                    if menu_state == "1PGame" and not isGameOver:
                        screen.fill(BLACK)
                        label = fontDefault.render(player2name + " Turn", 1, YELLOW)
                        screen.blit(label, ((width - label.get_width()) / 2, (SQUARESIZE - label.get_height()) / 2))
                        draw_board(board)
                        pygame.time.wait(2000)
                        col, Minimax_Score = mini_max(board, 5, -math.inf, math.inf, True)
                        if is_valid_position(board, col):
                            row = get_available_row(board, col)
                            add_new_piece(board, row, col, 2)

                            if is_draw(board):
                                screen.fill(BLACK)
                                draw_board(board)
                                label = fontDefault.render("Match Drawn !!", 1, RED)
                                pygame.display.set_caption("Connect4 - Match Drawn !!")
                                screen.blit(label,
                                            ((width - label.get_width()) / 2, (SQUARESIZE - label.get_height()) / 2))
                                isGameOver = True
                            elif is_winning(board, 2):
                                screen.fill(BLACK)
                                draw_board(board)
                                play_music("game_lose")
                                label = fontDefault.render(player2name + " Win !!", 1, YELLOW)
                                pygame.display.set_caption("Connect4 - " + player2name + " Win !!")
                                screen.blit(label,
                                            ((width - label.get_width()) / 2, (SQUARESIZE - label.get_height()) / 2))
                                isGameOver = True

                else:
                    posx = curEvent.pos[0]
                    col = int(math.floor(posx / SQUARESIZE))

                    if is_valid_position(board, col):
                        row = get_available_row(board, col)
                        add_new_piece(board, row, col, 2)

                        if is_draw(board):
                            screen.fill(BLACK)
                            draw_board(board)
                            label = fontDefault.render("Match Drawn !!", 1, RED)
                            pygame.display.set_caption("Connect4 - Match Drawn !!")
                            screen.blit(label, ((width - label.get_width()) / 2, (SQUARESIZE - label.get_height()) / 2))
                            isGameOver = True
                        elif is_winning(board, 2):
                            screen.fill(BLACK)
                            draw_board(board)
                            play_music("game_win")
                            label = fontDefault.render(player2name + " Win !!", 1, YELLOW)
                            pygame.display.set_caption("Connect4 - " + player2name + " Win !!")
                            screen.blit(label, ((width - label.get_width()) / 2, (SQUARESIZE - label.get_height()) / 2))
                            isGameOver = True

                draw_board(board)

                if menu_state != "1PGame": curTurn = (1 if curTurn == 0 else 0)
                if isGameOver:
                    pygame.time.wait(3000)
                    menu_state = "Retry"

    pygame.display.update()
