import pygame
import os
from enum import Enum

# Fix latency when playing sound effects
pygame.mixer.pre_init(44100, -16, 2, 1024, allowedchanges=1)
pygame.mixer.init(44100, -16, 2, 1024, allowedchanges=1)
pygame.mixer.set_num_channels(5)

# Initialize pygame
pygame.init()

# Create the window
screen = pygame.display.set_mode((300, 350))
pygame.display.set_caption('')

# Palette - RGB colors
dark_grey = (85, 85, 85)
light_grey = (100, 100, 100)
background_color = (255, 238, 212)

# Load images, sounds and fonts
sounds_folder = os.path.join('data', 'sounds')
images_folder = os.path.join('data', 'images')
cross_img = pygame.image.load(os.path.join(images_folder, 'cross.png'))
circle_img = pygame.image.load(os.path.join(images_folder, 'circle.png'))
cross_preview_img = pygame.image.load(os.path.join(images_folder, 'cross_preview.png'))
circle_preview_img = pygame.image.load(os.path.join(images_folder, 'circle_preview.png'))
restart_button = pygame.image.load(os.path.join(images_folder, 'restart.png'))
restart_button_hovered = pygame.image.load(os.path.join(images_folder, 'restart_hovered.png'))
player_vs_player_button = pygame.image.load(os.path.join(images_folder, 'player_vs_player.png'))
player_vs_ai_button = pygame.image.load(os.path.join(images_folder, 'player_vs_ai.png'))
logo = pygame.image.load(os.path.join(images_folder, 'logo.png'))
font = pygame.font.Font('freesansbold.ttf', 32)

# Tranform images to desired scale and position
cross_img = pygame.transform.scale(cross_img, (90, 90))
X_score = pygame.transform.scale(cross_img, (32, 32))
circle_img = pygame.transform.scale(circle_img, (90, 90))
O_score = pygame.transform.scale(circle_img, (32, 32))
cross_preview_img = pygame.transform.scale(cross_preview_img, (90, 90))
circle_preview_img = pygame.transform.scale(circle_preview_img, (90, 90))
restart_button = pygame.transform.scale(restart_button, (32, 32))
restart_button_rect = restart_button.get_rect()
restart_button_rect.topleft = (250, 310)
player_vs_player_button = pygame.transform.scale(player_vs_player_button, (220, 65))
player_vs_player_button_rect = player_vs_player_button.get_rect()
player_vs_player_button_rect.topleft = (40, 135)
restart_button_hovered = pygame.transform.scale(restart_button_hovered, (32, 32))
player_vs_ai_button = pygame.transform.scale(player_vs_ai_button, (220, 65))
player_vs_ai_button_rect = player_vs_ai_button.get_rect()
player_vs_ai_button_rect.topleft = (40, 215)
logo = pygame.transform.scale(logo, (150, 150))

# Define the board
board = [['', '', ''],
         ['', '', ''],
         ['', '', '']]

# Define the scoreboard
score = {'X': 0, 'O': 0}

# Define game modes
class GameMode(Enum):
    MENU = 0
    PLAYER_VS_PLAYER = 1
    PLAYER_VS_AI = 2

# Globals variables
running = True;
gameMode = GameMode.MENU
currentPlayer = 'X'
mousePos = None

def main():
    global running, gameMode, mousePos
    while running:
        mousePos = pygame.mouse.get_pos()
        if gameMode == GameMode.MENU:
            renderMenu()
        else:
            renderGame()
        pygame.display.update()

def renderMenu():
    global running, gameMode, mousePos

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if player_vs_player_button_rect.collidepoint(mousePos):
                playSound(os.path.join(sounds_folder, 'buttonSound.wav'))
                gameMode = GameMode.PLAYER_VS_PLAYER
                resetGame()
            elif player_vs_ai_button_rect.collidepoint(mousePos):
                playSound(os.path.join(sounds_folder, 'buttonSound.wav'))
                gameMode = GameMode.PLAYER_VS_AI
                resetGame()
    
    # Handle Drawing
    screen.fill(background_color)
    screen.blit(player_vs_player_button, player_vs_player_button_rect)
    screen.blit(player_vs_ai_button, player_vs_ai_button_rect)
    screen.blit(logo, (70, 0))

def renderGame():
    global running, gameMode, mousePos

    row, col = int(mousePos[0] / 100), int(mousePos[1] / 100)
    validPos = row < 3 and col < 3 and board[row][col] == ''

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            gameMode = GameMode.MENU
        elif isBoardFull():
            resetBoard()
        elif gameMode == GameMode.PLAYER_VS_AI and currentPlayer == 'O':
            computerMove()
            pygame.time.wait(150)
            verifyWinner()
            updatePlayer()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if validPos:
                playerMove(row, col)
                pygame.time.wait(150)
                verifyWinner()
                updatePlayer()
            elif restart_button_rect.collidepoint(mousePos):
                resetGame()

    # Handle drawing
    screen.fill(background_color)
    drawBoard()
    drawBottomMenu()

    if validPos:
        previewMove(row, col)
    
def drawBoard():
    for row in range(3):
        for col in range(3):
            pos = (row * 100+6, col * 100+6)
            if board[row][col] == 'X':
                screen.blit(cross_img, pos)
            elif board[row][col] == 'O':
                screen.blit(circle_img, pos)

    width = 10
    color = dark_grey
    pygame.draw.line(screen, color, (100, 0), (100, 300), width)
    pygame.draw.line(screen, color, (200, 0), (200, 300), width)
    pygame.draw.line(screen, color, (0, 100), (300, 100), width)
    pygame.draw.line(screen, color, (0, 200), (300, 200), width)
    pygame.draw.rect(screen, color, (0, 0, 5, 300))
    pygame.draw.rect(screen, color, (0, 0, 300, 5))
    pygame.draw.rect(screen, color, (295, 0, 5, 300))

def drawBottomMenu():
    global mousePos
    pygame.draw.rect(screen, dark_grey, (0, 300, 300, 50))
    pygame.draw.rect(screen, light_grey, (5, 305, 290, 40))
    screen.blit(restart_button, restart_button_rect)
    if restart_button_rect.collidepoint(mousePos):
        screen.blit(restart_button_hovered, restart_button_rect)
    screen.blit(X_score, (40, 310))
    screen.blit(O_score, (190, 310))
    scoreboard = font.render(': %d x %d :' % (score['X'], score['O']), True, background_color, light_grey)
    screen.blit(scoreboard, (72, 310))

def previewMove(row, col):
    global currentPlayer
    if board[row][col] == '':
        previewImg = cross_preview_img if currentPlayer == 'X' else circle_preview_img
        screen.blit(previewImg, (row*100+6, col*100+6))

def playerMove(row, col):
    global currentPlayer
    board[row][col] = currentPlayer

# Apply MiniMax algorithm to find the best move
# Computer/AI plays with 'O'
def computerMove():
    bestScore = float('inf')
    for row in range(3):
        for col in range(3):
            if board[row][col] == '':
                board[row][col] = 'O'
                score = minimax(board, 'X')
                board[row][col] = ''
                if score < bestScore:
                    bestScore = score
                    bestMove = (row, col)
    board[bestMove[0]][bestMove[1]] = 'O'

scores = {'X': 1, 'O': -1, 'tie': 0}
def minimax(board, cur_player):
    # Calculate the board score
    if isWinner('X'):
        return scores['X']
    elif isWinner('O'):
        return scores['O']
    elif isBoardFull():
        return scores['tie']
    
    # Verify if it is the maximizing or minimizing player
    if cur_player == 'X':
        bestScore = float('-inf')
        nextPlayer = 'O'
        minORmax = max
    else:
        bestScore = float('inf')
        nextPlayer = 'X'
        minORmax = min

    for row in range(3):
        for col in range(3):
            if board[row][col] == '':
                board[row][col] = cur_player
                score = minimax(board, nextPlayer)
                board[row][col] = ''
                bestScore = minORmax(score, bestScore)
            # In case the 'AI' finds the best possible score
            if bestScore == scores[cur_player]:
                return bestScore
    return bestScore

def updatePlayer():
    global currentPlayer
    currentPlayer = 'X' if currentPlayer == 'O' else 'O'

def isWinner(player):
    return ((board[0][0] == player and board[0][1] == player and board[0][2] == player) or
            (board[1][0] == player and board[1][1] == player and board[1][2] == player) or
            (board[2][0] == player and board[2][1] == player and board[2][2] == player) or
            (board[0][0] == player and board[1][0] == player and board[2][0] == player) or
            (board[0][1] == player and board[1][1] == player and board[2][1] == player) or
            (board[0][2] == player and board[1][2] == player and board[2][2] == player) or
            (board[0][0] == player and board[1][1] == player and board[2][2] == player) or
            (board[0][2] == player and board[1][1] == player and board[2][0] == player))
        
def verifyWinner():
    global currentPlayer
    if isWinner(currentPlayer):
        playSound(os.path.join(sounds_folder, 'resetSound.wav'))
        pygame.time.wait(500)
        score[currentPlayer] += 1
        resetBoard()

def isBoardFull():
    for i in range(3):
        for j in range(3):
            if board[i][j] == '':
                return False
    return True

def resetBoard():
    for i in range(3):
        for j in range(3):
            board[i][j] = ''

def resetGame():
    resetBoard()
    score['X'] = 0
    score['O'] = 0

def playSound(sound):
    pygame.mixer.music.load(sound)
    pygame.mixer.music.play()

main()
