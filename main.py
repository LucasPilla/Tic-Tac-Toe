import pygame
import mido
import threading
import time

# Initialize pygame
# Solve play sounds latency
pygame.mixer.pre_init(44100, -16, 2, 1024, allowedchanges=1)
pygame.mixer.init(44100, -16, 2, 1024, allowedchanges=1)
pygame.mixer.set_num_channels(5)
pygame.init()

# Palette - RGB colors
blue = (78, 140, 243)
light_blue = (100, 100, 255)
red = (242, 89, 97)
light_red = (255, 100, 100)
dark_grey = (85, 85, 85)
light_grey = (100, 100, 100)
background_color = (255, 238, 212)

# Create the window
screen = pygame.display.set_mode((300, 350))
pygame.display.set_caption('')

# Player images
crossImg = pygame.image.load('Data/Images/crossImg.png')
crossImg = pygame.transform.scale(crossImg, (90, 90))
circleImg = pygame.image.load('Data/Images/circleImg.png')
circleImg = pygame.transform.scale(circleImg, (90, 90))
previewCrossImg = pygame.image.load('Data/Images/prev_crossImg.png')
previewCrossImg = pygame.transform.scale(previewCrossImg, (90, 90))
previewCircleImg = pygame.image.load('Data/Images/prev_circleImg.png')
previewCircleImg = pygame.transform.scale(previewCircleImg, (90, 90))


# Bottom Menu Images
restartImg = pygame.image.load('Data/Images/restart.png')
restartImg = pygame.transform.scale(restartImg, (32, 32))
restartHoveredImg = pygame.image.load('Data/Images/restart_hovered.png')
restartHoveredImg = pygame.transform.scale(restartHoveredImg, (32, 32))

# Define the board
board = [['', '', ''],
         ['', '', ''],
         ['', '', '']]

# Define Scoreboard
score = {'X': 0, 'O': 0}
font = pygame.font.Font('freesansbold.ttf', 32)
X_score = pygame.transform.scale(crossImg, (32, 32))
O_score = pygame.transform.scale(circleImg, (32, 32))

# Menu Images
buttom1 = pygame.image.load('Data/Images/button1Img_new.png')
buttom1 = pygame.transform.scale(buttom1, (220, 65))
buttom1_rect = buttom1.get_rect()
buttom1_rect.center = (150, 171)

buttom2 = pygame.image.load('Data/Images/button2Img_new.png')
buttom2 = pygame.transform.scale(buttom2, (220, 65))
buttom2_rect = buttom2.get_rect()
buttom2_rect.center = (150, 246)
logo = pygame.image.load('Data/Images/logo_new.png')
logo = pygame.transform.scale(logo, (150, 150))

MUSICPARAM_CURRENT_TURN = 0

# -1 = Nobody, 0 = X, 1 = O, 2 = Both
MUSICPARAM_WINNING_SIDE = -1
# -1 = Nothing, 0 = Horizontal, 1 = Vertical, 2 = Diagonal
MUSICPARAM_SYMMETRY_DIRECTION = -1


bpm = 60;
playing = False;
running = False;

def menu():
    global running
    running = True;
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
        screen.blit(logo, (70, 0))
        #pygame.draw.rect(screen, dark_grey, (45, 120, 210, 73))
        screen.blit(buttom1, (40, 135))
        #pygame.draw.rect(screen, dark_grey, (45, 200, 210, 73))
        screen.blit(buttom2, (40, 215))
        pygame.display.update()

def game(gameMode):
    global MUSICPARAM_WINNING_SIDE
    global MUSICPARAM_SYMMETRY_DIRECTION
    global playing
    global running
    pygame.mouse.set_pos(150, 175)
    # Set X as the first player
    player = 'X'
    previewImg = previewCrossImg
    # Game loop
    #playMusic("Data/Sounds/ticky.mp3",1)
    x = threading.Thread(target=musicMidi, args=())
    #logging.info("Main    : before running thread")
    x.start()
    

    playing=True;
    running=True;
    MUSICPARAM_CURRENT_TURN = 0
    while running:
        # Mouse
        mouse = pygame.mouse.get_pos()
        row, col = int(mouse[0] / 100), int(mouse[1] / 100)
        # Analyzes each game event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                
                playing=False
                running = False
                x.join();
                
                resetGame()
            elif isBoardFull():
                resetBoard()
            elif gameMode == 1 and player == 'O':
                computerMove(player)
                drawBoard()
                pygame.display.update()
                pygame.time.wait(150)
                verifyWinner(player)
                player, previewImg = updatePlayer(player)
                #player, previewImg = updatePlayer(player)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # If an empty spot is pressed
                if row < 3 and col < 3 and board[row][col] == '':
                    MUSICPARAM_CURRENT_TURN += 1
                    if(player=="X"):
                        playSound('Data/Sounds/sfx_X.wav')
                    else:
                        playSound('Data/Sounds/sfx_O.wav')
                    playerMove(player, row, col)
                    verifyWinner(player)
                    x_symmetry = symmetry_check(board, "X")
                    o_symmetry = symmetry_check(board, "O")
                    if x_symmetry != -1:
                        MUSICPARAM_SYMMETRY_DIRECTION = x_symmetry
                    else:
                        MUSICPARAM_SYMMETRY_DIRECTION = o_symmetry
                    MUSICPARAM_WINNING_SIDE = checkPotentialWinner(x_symmetry, o_symmetry)
                    print(f"Music Param symmetry {MUSICPARAM_SYMMETRY_DIRECTION}, winning side {MUSICPARAM_WINNING_SIDE}, turn {MUSICPARAM_CURRENT_TURN}")
                    
                    player, previewImg = updatePlayer(player)
                    changeTempo(110)
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


def checkPotentialWinner(x_symmetry, o_symmetry):
    if x_symmetry != -1 and o_symmetry != -1:
        return 2
    elif x_symmetry != -1:
        return 0
    elif o_symmetry != -1:
        return 1
    else:
        return -1

def symmetry_check(board, player):
    # -1 = Nothing, 0 = Horizontal, 1 = Vertical, 2 = Diagonal
    for direction in range(0, 3):
        if direction == 0:
            for row in range(0, 3):
                prev_piece = 'NONE'
                for column in range(0, 3):
                    if column == 0:
                        if board[row][column] == player:
                            prev_piece = board[row][column]
                    elif prev_piece == board[row][column]:
                        return 0
                    else:
                        if board[row][column] == player:
                            prev_piece = board[row][column]
        elif direction == 1:
            for column in range(0, 3):
                prev_piece = 'NONE'
                for row in range(0, 3):
                    if row == 0:
                        if board[row][column] == player:
                            prev_piece = board[row][column]
                    elif prev_piece == board[row][column]:
                        return 1
                    else:
                        if board[row][column] == player:
                            prev_piece = board[row][column]
        else:
            for diagonal_direction in range(0,1):
                prev_piece = 'NONE'
                for diagonal_row_column in range(0, 3):
                    to_access = diagonal_row_column
                    if diagonal_direction == 1:
                        to_access = 2-diagonal_row_column
                    if prev_piece == board[to_access][to_access]:
                        return 2
                    else:
                        if board[to_access][to_access]  == player:
                            prev_piece = board[to_access][to_access]
    return -1


def isWinning(player):
    if (MUSICPARAM_WINNING_SIDE==2):
        return True   
    if (MUSICPARAM_WINNING_SIDE==-1):    
        return False   
    if(player=="X" and MUSICPARAM_WINNING_SIDE==0 ):
        return True
    if(player=="O"and MUSICPARAM_WINNING_SIDE==0): 
        return True
    return False           



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
    global bpm 
    bpm= 60;
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

def playMusic(file, ch):

    pygame.mixer.Channel(ch).play(pygame.mixer.Sound(file))




def getperiod():
    return int(60000/bpm)

def changeTempo(percent):
    global bpm
    bpm = int(bpm*percent/100)



def playbeat(beat,out):
    viovelocity=40
    flutevelocity=50
    if(board[beat-1][2]=='X'):
        out.send(mido.Message('note_on', note=60, velocity=viovelocity, channel=1,time=0))
    if(board[beat-1][1]=='X'):
        out.send(mido.Message('note_on', note=64, velocity=viovelocity, channel=1,time=0))   
    if(board[beat-1][0]=='X'):
        out.send(mido.Message('note_on', note=67, velocity=viovelocity, channel=1,time=0))   

    if(board[beat-1][2]=='O'):
        out.send(mido.Message('note_on', note=64, velocity=flutevelocity, channel=2,time=0)) 
    if(board[beat-1][1]=='O'):
        out.send(mido.Message('note_on', note=67, velocity=flutevelocity, channel=2,time=0)) 
    if(board[beat-1][0]=='O'):  
        out.send(mido.Message('note_on', note=70, velocity=flutevelocity, channel=2,time=0))  

def silentbeat(out):
    out.send(mido.Message('note_off', note=60, velocity=50, channel=1,time=0))
    out.send(mido.Message('note_off', note=64, velocity=50, channel=1,time=0))
    out.send(mido.Message('note_off', note=67, velocity=50, channel=1,time=0))  
    out.send(mido.Message('note_off', note=64, velocity=50, channel=2,time=0))
    out.send(mido.Message('note_off', note=67, velocity=50, channel=2,time=0))
    out.send(mido.Message('note_off', note=70, velocity=50, channel=2,time=0))  


def musicMidi():
    global playing
    global MUSICPARAM_WINNING_SIDE
    #print(mido.get_output_names())
    out = mido.open_output(mido.get_output_names()[0])
    print("Connected to Midi port: " + mido.get_output_names()[0])

    out.send(mido.Message('program_change', channel=1, program=41)) #violin/a
    out.send(mido.Message('program_change', channel=2, program=74)) #flute/recorder
    
    out.send(mido.Message('program_change', channel=3, program=43)) #cello/a
    out.send(mido.Message('program_change', channel=4, program=70)) #fclarioboe
    out.send(mido.Message('control_change', control=93, value=75)) #cello/a
    out.send(mido.Message('control_change', control=93, value=75)) #fclarioboe

    ticvelocity= 40

    while(playing):

    
        #beat 1 

        #is someone winning=?
    
 
        if(MUSICPARAM_WINNING_SIDE==2):
            print("both winning")
            out.send(mido.Message('note_on', note=36, velocity=20, channel=3,time=0))
            out.send(mido.Message('note_on', note=40, velocity=20, channel=4,time=0))
        elif(MUSICPARAM_WINNING_SIDE==0):
            print("x winning")
            out.send(mido.Message('note_on', note=36, velocity=20, channel=3,time=0))
        elif(MUSICPARAM_WINNING_SIDE==1):
            print("o winning")
            out.send(mido.Message('note_on', note=40, velocity=20, channel=4,time=0))




        playbeat(1,out); 

        out.send(mido.Message('note_on', note=32, velocity=ticvelocity, channel=9,time=0))
        time.sleep(0.1);
        out.send(mido.Message('note_off', note=32, velocity=ticvelocity,channel=9, time=0))
        time.sleep((getperiod()/1000)-0.2);
        silentbeat(out);
        time.sleep(0.1);
        #beat 2 

        playbeat(2,out)
        out.send(mido.Message('note_on', note=32, velocity=ticvelocity, channel=9,time=0))
        time.sleep(0.1);
        out.send(mido.Message('note_off', note=32, velocity=ticvelocity,channel=9, time=0))
        time.sleep((getperiod()/1000)-0.2);
        silentbeat(out)
        time.sleep(0.1);

        #beat 3 
        playbeat(3,out)
        out.send(mido.Message('note_on', note=32, velocity=ticvelocity, channel=9,time=0))
        time.sleep(0.1);
        out.send(mido.Message('note_off', note=32, velocity=ticvelocity,channel=9, time=0))
        time.sleep((getperiod()/1000)-0.2);
        silentbeat(out)
        time.sleep(0.1);

        out.send(mido.Message('note_off', note=36, velocity=20, channel=3,time=0))
        out.send(mido.Message('note_off', note=40, velocity=20, channel=4,time=0))

    out.send(mido.Message('note_off', note=36, velocity=0, channel=3,time=0))
    out.send(mido.Message('note_off', note=40, velocity=0, channel=4,time=0))
    out.send(mido.Message('stop'))


menu()
