import pygame
import os
from enum import Enum

# Palette - RGB colors
DARK_GRAY = (85, 85, 85)
LIGHT_GRAY = (100, 100, 100)
BACKGROUND_COLOR = (255, 238, 212)

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

# Tranform images to desired scale
cross_img = pygame.transform.scale(cross_img, (90, 90))
X_score = pygame.transform.scale(cross_img, (32, 32))
circle_img = pygame.transform.scale(circle_img, (90, 90))
O_score = pygame.transform.scale(circle_img, (32, 32))
cross_preview_img = pygame.transform.scale(cross_preview_img, (90, 90))
circle_preview_img = pygame.transform.scale(circle_preview_img, (90, 90))
restart_button = pygame.transform.scale(restart_button, (32, 32))
player_vs_player_button = pygame.transform.scale(player_vs_player_button, (220, 65))
restart_button_hovered = pygame.transform.scale(restart_button_hovered, (32, 32))
player_vs_ai_button = pygame.transform.scale(player_vs_ai_button, (220, 65))
logo = pygame.transform.scale(logo, (150, 150))

# Create rects for iterative elements
restart_button_rect = restart_button.get_rect()
restart_button_rect.topleft = (250, 310)
player_vs_player_button_rect = player_vs_player_button.get_rect()
player_vs_player_button_rect.topleft = (40, 135)
player_vs_ai_button_rect = player_vs_ai_button.get_rect()
player_vs_ai_button_rect.topleft = (40, 215)

class GameMode(Enum):
    MENU = 0
    PLAYER_VS_PLAYER = 1
    PLAYER_VS_AI = 2

class TicTacToe:

    def __init__(self):
        self.running = True
        self.mousePos = None
        self.gameMode = GameMode.MENU
        self.currentPlayer = 'X'
        self.board = [
            ['', '', ''],
            ['', '', ''],
            ['', '', '']
        ]
        self.score = {
            'X': 0, 
            'O': 0
        }

    def play(self):
        # Fix latency when playing sound effects
        pygame.mixer.pre_init(44100, -16, 2, 1024, allowedchanges=1)
        pygame.mixer.init(44100, -16, 2, 1024, allowedchanges=1)
        pygame.mixer.set_num_channels(5)

        # Create the window
        pygame.display.set_caption('Tic Tac Toe')
        self.screen = pygame.display.set_mode((300, 350))

        # Initialize pygame
        pygame.init()
        self.font = pygame.font.Font('freesansbold.ttf', 32)
        
        while self.running:
            self.mousePos = pygame.mouse.get_pos()
            if self.gameMode == GameMode.MENU:
                self.renderMenu()
            else:
                self.renderGame()
            pygame.display.update()

    def renderMenu(self):
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if player_vs_player_button_rect.collidepoint(self.mousePos):
                    self.playSound(os.path.join(sounds_folder, 'buttonSound.wav'))
                    self.gameMode = GameMode.PLAYER_VS_PLAYER
                    self.resetGame()
                elif player_vs_ai_button_rect.collidepoint(self.mousePos):
                    self.playSound(os.path.join(sounds_folder, 'buttonSound.wav'))
                    self.gameMode = GameMode.PLAYER_VS_AI
                    self.resetGame()
        
        # Handle Drawing
        self.screen.fill(BACKGROUND_COLOR)
        self.screen.blit(player_vs_player_button, player_vs_player_button_rect)
        self.screen.blit(player_vs_ai_button, player_vs_ai_button_rect)
        self.screen.blit(logo, (70, 0))

    def renderGame(self):
        # Handle events
        row, col = int(self.mousePos[0] / 100), int(self.mousePos[1] / 100)
        isPosValid = row < 3 and col < 3 and self.board[row][col] == ''
        played = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.gameMode = GameMode.MENU
            elif event.type == pygame.MOUSEBUTTONDOWN and restart_button_rect.collidepoint(self.mousePos):
                self.resetGame()
            elif event.type == pygame.MOUSEBUTTONDOWN and isPosValid:
                self.playerMove(row, col)
                played = True

        if self.gameMode == GameMode.PLAYER_VS_AI and self.currentPlayer == 'O':
            self.computerMove()
            played = True
        
        if played:
            # Check if there is a winner and restart game
            if self.isWinner(self.currentPlayer):
                self.playSound(os.path.join(sounds_folder, 'resetSound.wav'))
                self.score[self.currentPlayer] += 1
                pygame.time.wait(500)
                self.resetBoard()

            if self.isBoardFull():
                self.resetBoard()
            
            # Update cyrrent player
            self.currentPlayer = 'X' if self.currentPlayer == 'O' else 'O'
            played = False
        
        # Handle drawing
        self.screen.fill(BACKGROUND_COLOR)

        # Draw move preview
        if isPosValid:
            previewImg = cross_preview_img if self.currentPlayer == 'X' else circle_preview_img
            self.screen.blit(previewImg, (row*100+6, col*100+6))
        
        # Draw board
        for row in range(3):
            for col in range(3):
                pos = (row * 100+6, col * 100+6)
                if self.board[row][col] == 'X':
                    self.screen.blit(cross_img, pos)
                elif self.board[row][col] == 'O':
                    self.screen.blit(circle_img, pos)
        width = 10
        pygame.draw.line(self.screen, DARK_GRAY, (100, 0), (100, 300), width)
        pygame.draw.line(self.screen, DARK_GRAY, (200, 0), (200, 300), width)
        pygame.draw.line(self.screen, DARK_GRAY, (0, 100), (300, 100), width)
        pygame.draw.line(self.screen, DARK_GRAY, (0, 200), (300, 200), width)
        pygame.draw.rect(self.screen, DARK_GRAY, (0, 0, 5, 300))
        pygame.draw.rect(self.screen, DARK_GRAY, (0, 0, 300, 5))
        pygame.draw.rect(self.screen, DARK_GRAY, (295, 0, 5, 300))

        # Draw bottom menu
        pygame.draw.rect(self.screen, DARK_GRAY, (0, 300, 300, 50))
        pygame.draw.rect(self.screen, LIGHT_GRAY, (5, 305, 290, 40))
        self.screen.blit(restart_button, restart_button_rect)
        if restart_button_rect.collidepoint(self.mousePos):
            self.screen.blit(restart_button_hovered, restart_button_rect)
        self.screen.blit(X_score, (40, 310))
        self.screen.blit(O_score, (190, 310))
        scoreboard = self.font.render(': %d x %d :' % (self.score['X'], self.score['O']), True, BACKGROUND_COLOR, LIGHT_GRAY)
        self.screen.blit(scoreboard, (72, 310))

    def playerMove(self, row, col):
       self.board[row][col] = self.currentPlayer

    # Apply MiniMax algorithm to find the best move
    # Computer/AI plays with 'O'
    def computerMove(self):

        def minimax(board, cur_player):
            # Calculate the board score
            scores = {'X': 1, 'O': -1, 'tie': 0}
            if self.isWinner('X'):
                return scores['X'], None
            elif self.isWinner('O'):
                return scores['O'], None
            elif self.isBoardFull():
                return scores['tie'], None
            
            # Verify if it is the maximizing or minimizing player
            if cur_player == 'X':
                bestScore = float('-inf')
                nextPlayer = 'O'
                minORmax = max
            else:
                bestScore = float('inf')
                nextPlayer = 'X'
                minORmax = min

            bestMove = None
            for row in range(3):
                for col in range(3):
                    if board[row][col] == '':
                        board[row][col] = cur_player
                        score, _ = minimax(board, nextPlayer)
                        board[row][col] = ''
                        if minORmax(score, bestScore) != bestScore:
                            bestScore = minORmax(score, bestScore)
                            bestMove = (row, col)
                    # In case 'AI' finds the best possible score
                    if bestScore == scores[cur_player]:
                        return bestScore, bestMove
            return bestScore, bestMove
    
        _, bestMove = minimax(self.board, 'O')
        self.board[bestMove[0]][bestMove[1]] = 'O'

    def isWinner(self, player):
        return ((self.board[0][0] == player and self.board[0][1] == player and self.board[0][2] == player) or
                (self.board[1][0] == player and self.board[1][1] == player and self.board[1][2] == player) or
                (self.board[2][0] == player and self.board[2][1] == player and self.board[2][2] == player) or
                (self.board[0][0] == player and self.board[1][0] == player and self.board[2][0] == player) or
                (self.board[0][1] == player and self.board[1][1] == player and self.board[2][1] == player) or
                (self.board[0][2] == player and self.board[1][2] == player and self.board[2][2] == player) or
                (self.board[0][0] == player and self.board[1][1] == player and self.board[2][2] == player) or
                (self.board[0][2] == player and self.board[1][1] == player and self.board[2][0] == player))

    def isBoardFull(self):
        for i in range(3):
            for j in range(3):
                if self.board[i][j] == '':
                    return False
        return True

    def resetBoard(self):
        for i in range(3):
            for j in range(3):
                self.board[i][j] = ''

    def resetGame(self):
        self.resetBoard()
        self.score['X'] = 0
        self.score['O'] = 0

    def playSound(self, sound):
        pygame.mixer.music.load(sound)
        pygame.mixer.music.play()

game = TicTacToe()
game.play()
