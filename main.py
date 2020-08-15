import pygame

# Initialize pygame
# Solve play sounds latency
pygame.mixer.pre_init(44100, -16, 2, 1024)
pygame.init()

# Palette - RGB colors
blue = (78, 140, 243)
light_blue = (100, 100, 255)
red = (242, 89, 97)
light_red = (255, 100, 100)
dark_grey = (85, 85, 85)
light_grey = (100, 100, 100)
background_color = (225, 225, 225)

# Create the window
screen = pygame.display.set_mode((300, 350))
pygame.display.set_caption('')

# Player images
crossImg = pygame.image.load('Data/Images/crossImg.png')
circleImg = pygame.image.load('Data/Images/circleImg.png')
previewCrossImg = pygame.image.load('Data/Images/prev_crossImg.png')
previewCircleImg = pygame.image.load('Data/Images/prev_circleImg.png')


# Bottom Menu Images
restartImg = pygame.image.load('Data/Images/restart.png')
restartHoveredImg = pygame.image.load('Data/Images/restart_hovered.png')

# Define the board
board = [['', '', ''],
         ['', '', ''],
         ['', '', '']]

# Define Scoreboard
score = {'X': 0, 'O': 0}
font = pygame.font.Font('freesansbold.ttf', 32)
X_score = pygame.image.load('Data/Images/X_scoreImg.png')
O_score = pygame.image.load('Data/Images/O_scoreImg.png')

# Menu Images
buttom1 = pygame.image.load('Data/Images/button1Img.png')
buttom1_rect = buttom1.get_rect()
buttom1_rect.center = (150, 156)
buttom2 = pygame.image.load('Data/Images/button2Img.png')
buttom2_rect = buttom2.get_rect()
buttom2_rect.center = (150, 236)
logo = pygame.image.load('Data/Images/logo.png')


def menu():
    running = True
    while running:
        screen.fill(background_color)
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if buttom1_rect.collidepoint((mx, my)):
                    playSound('Data/Sounds/buttonSound.wav')
                    game(0)
                elif buttom2_rect.collidepoint((mx, my)):
                    playSound('Data/Sounds/buttonSound.wav')
                    game(1)
        screen.blit(logo, (8, 25))
        pygame.draw.rect(screen, dark_grey, (45, 120, 210, 73))
        screen.blit(buttom1, (50, 125))
        pygame.draw.rect(screen, dark_grey, (45, 200, 210, 73))
        screen.blit(buttom2, (50, 205))
        pygame.display.update()

def game(gameMode):
    pygame.mouse.set_pos(150, 175)
    # Set X as the first player
    player = 'X'
    previewImg = previewCrossImg
    # Game loop
    running = True
    while running:
        # Mouse
        mouse = pygame.mouse.get_pos()
        row, col = int(mouse[0] / 100), int(mouse[1] / 100)
        # Analyzes each game event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                resetGame()
                running = False
            elif isBoardFull():
                resetBoard()
            elif gameMode == 1 and player == 'O':
                computerMove(player)
                verifyWinner(player)
                player, previewImg = updatePlayer(player)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # If an empty spot is pressed
                if row < 3 and col < 3 and board[row][col] == '':
                    playerMove(player, row, col)
                    verifyWinner(player)
                    player, previewImg = updatePlayer(player)
                # If reset button is pressed
                elif 250 < mouse[0] < 282 and 310 < mouse[1] < 342:
                    resetGame()
        # Draw in screen graphical elements
        screen.fill(background_color)
        drawBoard()
        drawBottomMenu(mouse)
        if row < 3 and col < 3 and gameMode == 0:
            visualizeMove(row, col, previewImg)
        elif row < 3 and col < 3 and player == 'X':
            visualizeMove(row, col, previewImg)
        pygame.display.update()


def drawBoard():
    # Draws each house
    for row in range(3):
        for col in range(3):
            pos = (row * 100+6, col * 100+6)
            if board[row][col] == 'X':
                screen.blit(crossImg, pos)
            elif board[row][col] == 'O':
                screen.blit(circleImg, pos)
    # Draws the grid
    width = 10
    color = dark_grey
    pygame.draw.line(screen, color, (100, 0), (100, 300), width)
    pygame.draw.line(screen, color, (200, 0), (200, 300), width)
    pygame.draw.line(screen, color, (0, 100), (300, 100), width)
    pygame.draw.line(screen, color, (0, 200), (300, 200), width)
    # Boards
    pygame.draw.rect(screen, color, (0, 0, 5, 300))
    pygame.draw.rect(screen, color, (0, 0, 300, 5))
    pygame.draw.rect(screen, color, (295, 0, 5, 300))


def drawBottomMenu(mouse):
    pygame.draw.rect(screen, dark_grey, (0, 300, 300, 50))
    pygame.draw.rect(screen, light_grey, (5, 305, 290, 40))
    screen.blit(restartImg, (250, 310))
    # Hover animation
    if 250 < mouse[0] < 282 and 310 < mouse[1] < 342:
        screen.blit(restartHoveredImg, (248, 308))
    screen.blit(X_score, (40, 310))
    screen.blit(O_score, (190, 310))
    scoreboard = font.render(': %d x %d :' % (score['X'], score['O']), True, background_color, light_grey)
    screen.blit(scoreboard, (72, 310))


def visualizeMove(row, col, previewImg):
    if board[row][col] == '':
        screen.blit(previewImg, (row*100+6, col*100+6))


def playerMove(player, row, col):
    board[row][col] = player

def computerMove(player):
    # MiniMax algorithm to find the best move
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


def updatePlayer(player):
    if player == 'X':
        newPlayer = 'O'
        previewImg = previewCircleImg
    else:
        newPlayer = 'X'
        previewImg = previewCrossImg
    return newPlayer, previewImg


# Verify if the current player is the winner
def isWinner(player):
    return ((board[0][0] == player and board[0][1] == player and board[0][2] == player) or
            (board[1][0] == player and board[1][1] == player and board[1][2] == player) or
            (board[2][0] == player and board[2][1] == player and board[2][2] == player) or
            (board[0][0] == player and board[1][0] == player and board[2][0] == player) or
            (board[0][1] == player and board[1][1] == player and board[2][1] == player) or
            (board[0][2] == player and board[1][2] == player and board[2][2] == player) or
            (board[0][0] == player and board[1][1] == player and board[2][2] == player) or
            (board[0][2] == player and board[1][1] == player and board[2][0] == player))


def verifyWinner(player):
    if isWinner(player):
        playSound('Data/Sounds/resetSound.wav')
        score[player] += 1
        pygame.time.wait(500)
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


menu()
