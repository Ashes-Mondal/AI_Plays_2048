from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtGui import *
from numpy.random import choice
import sys
import random
import copy
import time
import math
import numpy as np

CELL_COLORS = {
    2: "#fcefe6",
    4: "#f2e8cb",
    8: "#f5b682",
    16: "#f29446",
    32: "#ff775c",
    64: "#e64c2e",
    128: "#ede291",
    256: "#fce130",
    512: "#ffdb4a",
    1024: "#f0b922",
    2048: "#fad74d"
}

CELL_NUMBER_COLORS = {
    2: "#695c57",
    4: "#695c57",
    8: "#ffffff",
    16: "#ffffff",
    32: "#ffffff",
    64: "#ffffff",
    128: "#ffffff",
    256: "#ffffff",
    512: "#ffffff",
    1024: "#ffffff",
    2048: "#ffffff"
}

CELL_NUMBER_FONTS = {
    2: ("Helvetica", 35, "bold"),
    4: ("Helvetica", 35, "bold"),
    8: ("Helvetica", 35, "bold"),
    16: ("Helvetica", 30, "bold"),
    32: ("Helvetica", 30, "bold"),
    64: ("Helvetica", 30, "bold"),
    128: ("Helvetica", 25, "bold"),
    256: ("Helvetica", 25, "bold"),
    512: ("Helvetica", 25, "bold"),
    1024: ("Helvetica", 20, "bold"),
    2048: ("Helvetica", 20, "bold")
}
class Ui_MainWindow(QMainWindow):
    def __init__(self):
        self.flag = True
        self.matrix = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        self.Score = 0
        super(Ui_MainWindow, self).__init__()
        self.setupUi()
        self.playGame()

    ######################################## AI MOVE ###############################################
    def expectimaxAlgo(self, board):
        best_move, _ = self.maximize(board)
        return best_move

    def eval_board(self, board, n_empty):
        grid = board

        utility = 0
        smoothness = 0

        big_t = np.sum(np.power(grid, 2))
        s_grid = np.sqrt(grid)
        smoothness -= np.sum(np.abs(s_grid[::, 0] - s_grid[::, 1]))
        smoothness -= np.sum(np.abs(s_grid[::, 1] - s_grid[::, 2]))
        smoothness -= np.sum(np.abs(s_grid[::, 2] - s_grid[::, 3]))
        smoothness -= np.sum(np.abs(s_grid[0, ::] - s_grid[1, ::]))
        smoothness -= np.sum(np.abs(s_grid[1, ::] - s_grid[2, ::]))
        smoothness -= np.sum(np.abs(s_grid[2, ::] - s_grid[3, ::]))

        empty_w = 100000
        smoothness_w = 3

        empty_u = n_empty * empty_w
        smooth_u = smoothness ** smoothness_w
        big_t_u = big_t

        utility +=big_t
        utility +=empty_u
        utility +=smooth_u
  
        return (utility, empty_u, smooth_u, big_t_u)

    def maximize(self, board, depth=0):
        moves_boards = self.getAvailableMoves(board)

        max_utility = (float('-inf'), 0, 0, 0)
        best_direction = None

        for mb in moves_boards:
            utility = self.chance(mb[1], depth + 1)

            if utility[0] >= max_utility[0]:
                max_utility = utility
                best_direction = mb[0]

        return best_direction, max_utility

    def chance(self, board, depth=0):
        empty_cells = self.getEmptyCells(board)
        n_empty = len(empty_cells)

        if (n_empty >= 6 and depth >= 3) or (n_empty >= 0 and depth >= 5) :
            return self.eval_board(board, n_empty)

        if n_empty == 0:
            _, utility = self.maximize(board, depth + 1)
            return utility

        possible_tiles = []

        chance_2 = (.9 * (1 / n_empty))
        chance_4 = (.1 * (1 / n_empty))

        for empty_cell in empty_cells:
            possible_tiles.append((empty_cell, 2, chance_2))
            possible_tiles.append((empty_cell, 4, chance_4))

        utility_sum = [0, 0, 0, 0]

        for t in possible_tiles:
            t_board = copy.deepcopy(board)
            t_board[t[0]//4][t[0] % 4] = t[1]
            _, utility = self.maximize(t_board, depth + 1)

            for i in range(4):
                utility_sum[i] += utility[i] * t[2]

        return tuple(utility_sum)

    def aiMove(self):
        self.move(self.matrix, self.expectimaxAlgo(self.matrix))

    def getEmptyCells(self, mat):
        emptyCells = []
        for i in range(16):
            if mat[i//4][i % 4] == 0:
                emptyCells.append(i)
        return emptyCells

    def getAvailableMoves(self, mat):
        availableMoves = []
        for i in range(4):
            copy_Matrix = copy.deepcopy(mat)
            self.move(copy_Matrix, i)
            if copy_Matrix != mat:
                availableMoves.append((i, copy_Matrix))
        return availableMoves

    ######################################## Actions ###############################################

    def giveRow(self, mat, n):
        result = []
        for c in mat[n]:
            if c != 0:
                result.append(c)
        return result

    def giveCol(self, mat, n):
        result = []
        for i in range(4):
            if mat[i][n] != 0:
                result.append(mat[i][n])
        return result

    def moveLeft(self, mat):
        scr = 0
        for r in range(4):
            rw = self.giveRow(mat, r)
            i = 0
            while i < len(rw)-1:
                if rw[i] == rw[i+1]:
                    rw[i] *= 2
                    scr += rw[i]
                    rw.pop(i+1)
                i += 1
            for j in range(4):
                if j < len(rw):
                    mat[r][j] = rw[j]
                else:
                    mat[r][j] = 0
        return scr

    def moveRight(self, mat):
        scr = 0
        for r in range(4):
            rw = self.giveRow(mat, r)[::-1]
            i = 0
            while i < len(rw)-1:
                if rw[i] == rw[i+1]:
                    rw[i] *= 2
                    scr += rw[i]
                    rw.pop(i+1)
                i += 1
            for j in range(4):
                if j < len(rw):
                    mat[r][j] = rw[j]
                else:
                    mat[r][j] = 0
            mat[r] = (mat[r])[::-1]
        return scr

    def moveUp(self, mat):
        scr = 0
        for c in range(4):
            colm = self.giveCol(mat, c)
            i = 0
            while i < len(colm)-1:
                if colm[i] == colm[i+1]:
                    colm[i] *= 2
                    scr += colm[i]
                    colm.pop(i+1)
                i += 1
            for j in range(4):
                if j < len(colm):
                    mat[j][c] = colm[j]
                else:
                    mat[j][c] = 0
        return scr

    def moveDown(self, mat):
        scr = 0
        for c in range(4):
            colm = (self.giveCol(mat, c))[::-1]
            i = 0
            while i < len(colm)-1:
                if colm[i] == colm[i+1]:
                    colm[i] *= 2
                    scr += colm[i]
                    colm.pop(i+1)
                i += 1
            for j in range(4):
                if j < len(colm):
                    mat[3-j][c] = colm[j]
                else:
                    mat[3-j][c] = 0
        return scr

    def move(self, mat, i):
        scr = 0
        if id(mat) == id(self.matrix):
            if i == 0:
                self.status.setText("Up")
            elif i == 3:
                self.status.setText("Right")
            elif i == 1:
                self.status.setText("Down")
            elif i == 2:
                self.status.setText("Left")
        if i == 0:
            scr = self.moveUp(mat)
        elif i == 3:
            scr = self.moveRight(mat)
        elif i == 1:
            scr = self.moveDown(mat)
        elif i == 2:
            scr = self.moveLeft(mat)

        if id(mat) == id(self.matrix):
            self.updateScore(scr)
        return scr
    ######################################## MAIN GAME ###############################################

    def tile(self, n):
        return {
            0: self.tile00,
            1: self.tile01,
            2: self.tile02,
            3: self.tile03,
            4: self.tile10,
            5: self.tile11,
            6: self.tile12,
            7: self.tile13,
            8: self.tile20,
            9: self.tile21,
            10: self.tile22,
            11: self.tile23,
            12: self.tile30,
            13: self.tile31,
            14: self.tile32,
            15: self.tile33,
        }.get(n)

    def playGame(self):
        self.updateGameBoard()
        self.Reset.clicked.connect(self.resetGame)
        self.start.clicked.connect(lambda: self.computerPlay())
        self.computer.toggled.connect(self.resetGame)

    def computerPlay(self):
        if self.computer.isChecked():
            self.start.setEnabled(False)
            self.Reset.setEnabled(False)
            while self.computer.isChecked() and (not self.checkGameEnded(self.matrix)):
                preMat = copy.deepcopy(self.matrix)
                self.aiMove()
                if preMat != self.matrix:
                    QApplication.processEvents()
                    self.updateGameBoard()
        self.resetGame()
        self.Reset.setEnabled(True)

    def updateScore(self, scr):
        self.Score += scr

    def resetTile(self, n):
        self.tile(n).setText("")
        self.tile(n).setStyleSheet("")
        self.status.setText("IDLE")

    def resetGame(self):
        if self.human.isChecked():
            self.start.setEnabled(False)
        else:
            self.start.setEnabled(True)
        self.flag = 1
        self.matrix = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        self.Score = 0
        for i in range(16):
            self.resetTile(i)
        self.updateGameBoard()

    def updateTile(self, n):
        self.tile(n).setText(str(self.matrix[n//4][n % 4]))
        self.tile(n).setStyleSheet("font-family:Helvetica;font-size: {}pt;font-weight: bold;background-color: {};color:{}".format(CELL_NUMBER_FONTS.get(self.matrix[n//4][n % 4],(("Helvetica", 15, "bold")))[1],CELL_COLORS.get(
            self.matrix[n//4][n % 4],"#A9A9A9"), CELL_NUMBER_COLORS.get(self.matrix[n//4][n % 4],"#FFFFFF")))

    def updateGameBoard(self):
        emptyTile = []
        for i in range(16):
            if self.matrix[i//4][i % 4] == 0:
                emptyTile.append(i)
                self.tile(i).setText("")
                self.tile(i).setStyleSheet("background-color:#c2b3a9")
            else:
                self.updateTile(i)
        self.score.setText(str(self.Score))
        randomEmptyTile = random.choice(emptyTile)
        self.matrix[randomEmptyTile//4][randomEmptyTile %
                                        4] = choice([2, 4], 1, p=[0.8, 0.2])[0]
        self.updateTile(randomEmptyTile)

    def gameOver(self, mat):
        return True if len(self.getAvailableMoves(mat)) == 0 else False

    def gameWon(self, mat):
        for r in mat:
            for c in r:
                if c == 2048:
                    return True
        return False
    
    def popup_clicked(self,i):
        if i.text() == "&No":
            self.resetGame()
        else:
            self.flag = False
            
    def checkGameEnded(self, mat):
        if self.flag and id(mat) == id(self.matrix) and self.gameWon(mat):
            msg = QMessageBox()
            msg.setWindowTitle("Game Ended")
            s = "2048 reached!! \n Want to continue?"
            msg.setText(s)
            msg.setIcon(QMessageBox.Information)
            msg.setStandardButtons(QMessageBox.Yes| QMessageBox.No)
            msg.buttonClicked.connect(self.popup_clicked)
            msg.exec_()
            return True if self.flag else False
        elif id(mat) == id(self.matrix) and self.gameOver(mat):
            s = "Game Over"
            msg = QMessageBox()
            msg.setWindowTitle("Game Ended")
            msg.setText(s)
            msg.setIcon(QMessageBox.Information)
            msg.exec_()
            self.resetGame()
            return True
        elif id(mat) != id(self.matrix) and (self.gameWon(mat) or self.gameOver(mat)):
            return True
        return False

########################################  keyPressEvent ###############################################
    def keyPressEvent(self, event):
        if self.human.isChecked():
            preMat = copy.deepcopy(self.matrix)
            if event.key() == QtCore.Qt.Key_Up:
                self.move(self.matrix, 0)
            elif event.key() == QtCore.Qt.Key_Down:
                self.move(self.matrix, 1)
            elif event.key() == QtCore.Qt.Key_Right:
                self.move(self.matrix, 3)
            elif event.key() == QtCore.Qt.Key_Left:
                self.move(self.matrix, 2)
            else:
                self.status.setText("Invalid")
                return none
            if preMat != self.matrix:
                self.updateGameBoard()
            self.checkGameEnded(self.matrix)

######################################## UI ###############################################
    def setupUi(self):
        self.setObjectName("MainWindow")
        self.resize(510, 570)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(30, 100, 451, 411))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        # title font
        font = QtGui.QFont()
        font.setPointSize(22)
        # tile21
        self.tile21 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.tile21.setAutoFillBackground(False)
        self.tile21.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.tile21.setFrameShadow(QtWidgets.QFrame.Plain)
        self.tile21.setAlignment(QtCore.Qt.AlignCenter)
        self.tile21.setWordWrap(False)
        self.tile21.setObjectName("tile21")
        self.tile21.setFont(font)
        self.gridLayout.addWidget(self.tile21, 2, 1, 1, 1)
        # tile20
        self.tile20 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.tile20.setAutoFillBackground(False)
        self.tile20.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.tile20.setFrameShadow(QtWidgets.QFrame.Plain)
        self.tile20.setAlignment(QtCore.Qt.AlignCenter)
        self.tile20.setWordWrap(False)
        self.tile20.setObjectName("tile20")
        self.tile20.setFont(font)
        self.gridLayout.addWidget(self.tile20, 2, 0, 1, 1)
        # tile00
        self.tile00 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.tile00.setAutoFillBackground(False)
        self.tile00.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.tile00.setFrameShadow(QtWidgets.QFrame.Plain)
        self.tile00.setAlignment(QtCore.Qt.AlignCenter)
        self.tile00.setWordWrap(False)
        self.tile00.setObjectName("tile00")
        self.tile00.setFont(font)
        self.gridLayout.addWidget(self.tile00, 0, 0, 1, 1)
        # tile31
        self.tile31 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.tile31.setAutoFillBackground(False)
        self.tile31.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.tile31.setFrameShadow(QtWidgets.QFrame.Plain)
        self.tile31.setAlignment(QtCore.Qt.AlignCenter)
        self.tile31.setWordWrap(False)
        self.tile31.setObjectName("tile31")
        self.tile31.setFont(font)
        self.gridLayout.addWidget(self.tile31, 3, 1, 1, 1)
        # tile23
        self.tile23 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.tile23.setAutoFillBackground(False)
        self.tile23.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.tile23.setFrameShadow(QtWidgets.QFrame.Plain)
        self.tile23.setAlignment(QtCore.Qt.AlignCenter)
        self.tile23.setWordWrap(False)
        self.tile23.setObjectName("tile23")
        self.tile23.setFont(font)
        self.gridLayout.addWidget(self.tile23, 2, 3, 1, 1)
        # tile11
        self.tile11 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.tile11.setAutoFillBackground(False)
        self.tile11.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.tile11.setFrameShadow(QtWidgets.QFrame.Plain)
        self.tile11.setAlignment(QtCore.Qt.AlignCenter)
        self.tile11.setWordWrap(False)
        self.tile11.setObjectName("tile11")
        self.tile11.setFont(font)
        self.gridLayout.addWidget(self.tile11, 1, 1, 1, 1)
        # tile01
        self.tile01 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.tile01.setAutoFillBackground(False)
        self.tile01.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.tile01.setFrameShadow(QtWidgets.QFrame.Plain)
        self.tile01.setAlignment(QtCore.Qt.AlignCenter)
        self.tile01.setWordWrap(False)
        self.tile01.setObjectName("tile01")
        self.tile01.setFont(font)
        self.gridLayout.addWidget(self.tile01, 0, 1, 1, 1)
        # tile02
        self.tile02 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.tile02.setAutoFillBackground(False)
        self.tile02.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.tile02.setFrameShadow(QtWidgets.QFrame.Plain)
        self.tile02.setAlignment(QtCore.Qt.AlignCenter)
        self.tile02.setWordWrap(False)
        self.tile02.setObjectName("tile02")
        self.tile02.setFont(font)
        self.gridLayout.addWidget(self.tile02, 0, 2, 1, 1)
        # tile03
        self.tile03 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.tile03.setAutoFillBackground(False)
        self.tile03.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.tile03.setFrameShadow(QtWidgets.QFrame.Plain)
        self.tile03.setAlignment(QtCore.Qt.AlignCenter)
        self.tile03.setWordWrap(False)
        self.tile03.setObjectName("tile03")
        self.tile03.setFont(font)
        self.gridLayout.addWidget(self.tile03, 0, 3, 1, 1)
        # tile32
        self.tile32 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.tile32.setAutoFillBackground(False)
        self.tile32.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.tile32.setFrameShadow(QtWidgets.QFrame.Plain)
        self.tile32.setAlignment(QtCore.Qt.AlignCenter)
        self.tile32.setWordWrap(False)
        self.tile32.setObjectName("tile32")
        self.tile32.setFont(font)
        self.gridLayout.addWidget(self.tile32, 3, 2, 1, 1)
        # tile30
        self.tile30 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.tile30.setAutoFillBackground(False)
        self.tile30.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.tile30.setFrameShadow(QtWidgets.QFrame.Plain)
        self.tile30.setAlignment(QtCore.Qt.AlignCenter)
        self.tile30.setWordWrap(False)
        self.tile30.setObjectName("tile30")
        self.tile30.setFont(font)
        self.gridLayout.addWidget(self.tile30, 3, 0, 1, 1)
        # tile22
        self.tile22 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.tile22.setAutoFillBackground(False)
        self.tile22.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.tile22.setFrameShadow(QtWidgets.QFrame.Plain)
        self.tile22.setAlignment(QtCore.Qt.AlignCenter)
        self.tile22.setWordWrap(False)
        self.tile22.setObjectName("tile22")
        self.tile22.setFont(font)
        self.gridLayout.addWidget(self.tile22, 2, 2, 1, 1)
        # tile12
        self.tile12 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.tile12.setAutoFillBackground(False)
        self.tile12.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.tile12.setFrameShadow(QtWidgets.QFrame.Plain)
        self.tile12.setAlignment(QtCore.Qt.AlignCenter)
        self.tile12.setWordWrap(False)
        self.tile12.setObjectName("tile12")
        self.tile12.setFont(font)
        self.gridLayout.addWidget(self.tile12, 1, 2, 1, 1)
        # tile10
        self.tile10 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.tile10.setAutoFillBackground(False)
        self.tile10.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.tile10.setFrameShadow(QtWidgets.QFrame.Plain)
        self.tile10.setAlignment(QtCore.Qt.AlignCenter)
        self.tile10.setWordWrap(False)
        self.tile10.setObjectName("tile10")
        self.tile10.setFont(font)
        self.gridLayout.addWidget(self.tile10, 1, 0, 1, 1)
        # tile13
        self.tile13 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.tile13.setAutoFillBackground(False)
        self.tile13.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.tile13.setFrameShadow(QtWidgets.QFrame.Plain)
        self.tile13.setAlignment(QtCore.Qt.AlignCenter)
        self.tile13.setWordWrap(False)
        self.tile13.setObjectName("tile13")
        self.tile13.setFont(font)
        self.gridLayout.addWidget(self.tile13, 1, 3, 1, 1)
        # tile33
        self.tile33 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.tile33.setAutoFillBackground(False)
        self.tile33.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.tile33.setFrameShadow(QtWidgets.QFrame.Plain)
        self.tile33.setAlignment(QtCore.Qt.AlignCenter)
        self.tile33.setWordWrap(False)
        self.tile33.setObjectName("tile33")
        self.tile33.setFont(font)
        self.gridLayout.addWidget(self.tile33, 3, 3, 1, 1)
        # frame
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setGeometry(QtCore.QRect(20, 90, 471, 431))
        self.frame.setFrameShape(QtWidgets.QFrame.WinPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame.setObjectName("frame")
        # Reset
        self.Reset = QtWidgets.QPushButton(self.centralwidget)
        self.Reset.setGeometry(QtCore.QRect(400, 50, 89, 25))
        self.Reset.setObjectName("Reset")
        self.Reset.setFocusPolicy(QtCore.Qt.NoFocus)
        # start
        self.start = QtWidgets.QPushButton(self.centralwidget)
        self.start.setGeometry(QtCore.QRect(300, 50, 89, 25))
        self.start.setObjectName("<--")
        self.start.setFocusPolicy(QtCore.Qt.NoFocus)
        self.start.setEnabled(False)
        # score
        self.score = QtWidgets.QLabel(self.centralwidget)
        self.score.setGeometry(QtCore.QRect(80, 50, 121, 21))
        font.setPointSize(13)
        self.score.setFont(font)
        self.score.setObjectName("score")
        # status
        self.status = QtWidgets.QLabel(self.centralwidget)
        self.status.setGeometry(QtCore.QRect(210, 50, 81, 31))
        self.status.setAutoFillBackground(False)
        self.status.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.status.setFrameShadow(QtWidgets.QFrame.Plain)
        self.status.setAlignment(QtCore.Qt.AlignCenter)
        self.status.setObjectName("status")
        # human radio
        self.human = QtWidgets.QRadioButton(self.centralwidget)
        self.human.setEnabled(True)
        self.human.setGeometry(QtCore.QRect(130, 10, 112, 23))
        self.human.setChecked(True)
        self.human.setObjectName("human")
        self.human.setFocusPolicy(QtCore.Qt.NoFocus)
        # computer radio
        self.computer = QtWidgets.QRadioButton(self.centralwidget)
        self.computer.setGeometry(QtCore.QRect(260, 10, 112, 23))
        self.computer.setObjectName("computer")
        self.computer.setFocusPolicy(QtCore.Qt.NoFocus)
        # other
        self.label_17 = QtWidgets.QLabel(self.centralwidget)
        self.label_17.setGeometry(QtCore.QRect(20, 50, 61, 21))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label_17.setFont(font)
        self.label_17.setObjectName("label_17")
        self.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 510, 22))
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "2048"))
        self.tile21.setText(_translate("MainWindow", ""))
        self.tile20.setText(_translate("MainWindow", ""))
        self.tile00.setText(_translate("MainWindow", ""))
        self.tile31.setText(_translate("MainWindow", ""))
        self.tile23.setText(_translate("MainWindow", ""))
        self.tile11.setText(_translate("MainWindow", ""))
        self.tile01.setText(_translate("MainWindow", ""))
        self.tile02.setText(_translate("MainWindow", ""))
        self.tile03.setText(_translate("MainWindow", ""))
        self.tile32.setText(_translate("MainWindow", ""))
        self.tile30.setText(_translate("MainWindow", ""))
        self.tile22.setText(_translate("MainWindow", ""))
        self.tile12.setText(_translate("MainWindow", ""))
        self.tile10.setText(_translate("MainWindow", ""))
        self.tile13.setText(_translate("MainWindow", ""))
        self.tile33.setText(_translate("MainWindow", ""))
        self.Reset.setText(_translate("MainWindow", "Reset"))
        self.start.setText(_translate("MainWindow", "Start"))
        self.label_17.setText(_translate("MainWindow", "Score :"))
        self.score.setText(_translate("MainWindow", "0"))
        self.status.setText(_translate("MainWindow", "IDLE"))
        self.human.setText(_translate("MainWindow", "Human"))
        self.computer.setText(_translate("MainWindow", "Computer"))


def window():
    app = QApplication(sys.argv)
    win = Ui_MainWindow()
    win.show()
    app.exit(app.exec_())


window()
