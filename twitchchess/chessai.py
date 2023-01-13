import os
import random
import chess
import chess.svg
import chess.polyglot
import numpy as np
from tqdm import tqdm

# heavily used https://github.com/AnshGaikwad/Chess-World/blob/master/play.py

class Chessai():

    def __init__(self, board):
        self.pawntable = [
            0, 0, 0, 0, 0, 0, 0, 0,
            5, 10, 10, -20, -20, 10, 10, 5,
            5, -5, -10, 0, 0, -10, -5, 5,
            0, 0, 0, 20, 20, 0, 0, 0,
            5, 5, 10, 25, 25, 10, 5, 5,
            10, 10, 20, 30, 30, 20, 10, 10,
            50, 50, 50, 50, 50, 50, 50, 50,
            0, 0, 0, 0, 0, 0, 0, 0]

        self.knightstable = [
            -50, -40, -30, -30, -30, -30, -40, -50,
            -40, -20, 0, 5, 5, 0, -20, -40,
            -30, 5, 10, 15, 15, 10, 5, -30,
            -30, 0, 15, 20, 20, 15, 0, -30,
            -30, 5, 15, 20, 20, 15, 5, -30,
            -30, 0, 10, 15, 15, 10, 0, -30,
            -40, -20, 0, 0, 0, 0, -20, -40,
            -50, -40, -30, -30, -30, -30, -40, -50]

        self.bishopstable = [
            -20, -10, -10, -10, -10, -10, -10, -20,
            -10, 5, 0, 0, 0, 0, 5, -10,
            -10, 10, 10, 10, 10, 10, 10, -10,
            -10, 0, 10, 10, 10, 10, 0, -10,
            -10, 5, 5, 10, 10, 5, 5, -10,
            -10, 0, 5, 10, 10, 5, 0, -10,
            -10, 0, 0, 0, 0, 0, 0, -10,
            -20, -10, -10, -10, -10, -10, -10, -20]

        self.rookstable = [
            0, 0, 0, 5, 5, 0, 0, 0,
            -5, 0, 0, 0, 0, 0, 0, -5,
            -5, 0, 0, 0, 0, 0, 0, -5,
            -5, 0, 0, 0, 0, 0, 0, -5,
            -5, 0, 0, 0, 0, 0, 0, -5,
            -5, 0, 0, 0, 0, 0, 0, -5,
            5, 10, 10, 10, 10, 10, 10, 5,
            0, 0, 0, 0, 0, 0, 0, 0]

        self.queenstable = [
            -20, -10, -10, -5, -5, -10, -10, -20,
            -10, 0, 0, 0, 0, 0, 0, -10,
            -10, 5, 5, 5, 5, 5, 0, -10,
            0, 0, 5, 5, 5, 5, 0, -5,
            -5, 0, 5, 5, 5, 5, 0, -5,
            -10, 0, 5, 5, 5, 5, 0, -10,
            -10, 0, 0, 0, 0, 0, 0, -10,
            -20, -10, -10, -5, -5, -10, -10, -20]

        self.kingstable = [
            20, 30, 10, 0, 0, 10, 30, 20,
            20, 20, 0, 0, 0, 0, 20, 20,
            -10, -20, -20, -20, -20, -20, -20, -10,
            -20, -30, -30, -40, -40, -30, -30, -20,
            -30, -40, -40, -50, -50, -40, -40, -30,
            -30, -40, -40, -50, -50, -40, -40, -30,
            -30, -40, -40, -50, -50, -40, -40, -30,
            -30, -40, -40, -50, -50, -40, -40, -30]

        self.board = board

    # Evaluating the board
    def evaluate_board(self):
        if self.board.is_checkmate():
            if self.board.turn:
                return -9999
            else:
                return 9999
        if self.board.is_stalemate():
            return 0
        if self.board.is_insufficient_material():
            return 0

        wp = len(self.board.pieces(chess.PAWN, chess.WHITE))
        bp = len(self.board.pieces(chess.PAWN, chess.BLACK))
        wn = len(self.board.pieces(chess.KNIGHT, chess.WHITE))
        bn = len(self.board.pieces(chess.KNIGHT, chess.BLACK))
        wb = len(self.board.pieces(chess.BISHOP, chess.WHITE))
        bb = len(self.board.pieces(chess.BISHOP, chess.BLACK))
        wr = len(self.board.pieces(chess.ROOK, chess.WHITE))
        br = len(self.board.pieces(chess.ROOK, chess.BLACK))
        wq = len(self.board.pieces(chess.QUEEN, chess.WHITE))
        bq = len(self.board.pieces(chess.QUEEN, chess.BLACK))

        material = 100 * (wp - bp) + 320 * (wn - bn) + 330 * \
            (wb - bb) + 500 * (wr - br) + 900 * (wq - bq)

        pawnsq = sum([self.pawntable[i]
                     for i in self.board.pieces(chess.PAWN, chess.WHITE)])
        pawnsq = pawnsq + sum([-self.pawntable[chess.square_mirror(i)]
                               for i in self.board.pieces(chess.PAWN, chess.BLACK)])
        knightsq = sum([self.knightstable[i]
                        for i in self.board.pieces(chess.KNIGHT, chess.WHITE)])
        knightsq = knightsq + sum([-self.knightstable[chess.square_mirror(i)]
                                   for i in self.board.pieces(chess.KNIGHT, chess.BLACK)])
        bishopsq = sum([self.bishopstable[i]
                        for i in self.board.pieces(chess.BISHOP, chess.WHITE)])
        bishopsq = bishopsq + sum([-self.bishopstable[chess.square_mirror(i)]
                                   for i in self.board.pieces(chess.BISHOP, chess.BLACK)])
        rooksq = sum([self.rookstable[i]
                      for i in self.board.pieces(chess.ROOK, chess.WHITE)])
        rooksq = rooksq + sum([-self.rookstable[chess.square_mirror(i)]
                               for i in self.board.pieces(chess.ROOK, chess.BLACK)])
        queensq = sum([self.queenstable[i]
                       for i in self.board.pieces(chess.QUEEN, chess.WHITE)])
        queensq = queensq + sum([-self.queenstable[chess.square_mirror(i)]
                                for i in self.board.pieces(chess.QUEEN, chess.BLACK)])
        kingsq = sum([self.kingstable[i]
                      for i in self.board.pieces(chess.KING, chess.WHITE)])
        kingsq = kingsq + sum([-self.kingstable[chess.square_mirror(i)]
                               for i in self.board.pieces(chess.KING, chess.BLACK)])

        eval = material + pawnsq + knightsq + bishopsq + rooksq + queensq + kingsq
        if self.board.turn:
            return eval
        else:
            return -eval

    # Searching the best move using minimax and alphabeta algorithm with negamax implementation
    def alphabeta(self, alpha, beta, depthleft):
        bestscore = -9999
        if (depthleft == 0):
            return self.quiesce(alpha, beta)
        for move in self.board.legal_moves:
            self.board.push(move)
            score = -self.alphabeta(-beta, -alpha, depthleft - 1)
            self.board.pop()
            if (score >= beta):
                return score
            if (score > bestscore):
                bestscore = score
            if (score > alpha):
                alpha = score
        return bestscore

    def quiesce(self, alpha, beta):
        stand_pat = self.evaluate_board()
        if (stand_pat >= beta):
            return beta
        if (alpha < stand_pat):
            alpha = stand_pat

        for move in self.board.legal_moves:
            if self.board.is_capture(move):
                self.board.push(move)
                score = -self.quiesce(-beta, -alpha)
                self.board.pop()

                if (score >= beta):
                    return beta
                if (score > alpha):
                    alpha = score
        return alpha

    def selectmove(self, depth):
        print('\ncalculating moves...')
        bestMoves = [chess.Move.null()
                     for _ in range(min(5, len(list(self.board.legal_moves))))]
        bestValues = [-99999 for _ in range(min(5,
                                            len(list(self.board.legal_moves))))]
        alpha = -100000
        beta = 100000
        for move in tqdm(self.board.legal_moves): # tqdm for printing progress
            self.board.push(move)
            boardValue = -self.alphabeta(-beta, -alpha, depth - 1)
            if boardValue > min(bestValues):
                x = np.argmin(bestValues)
                bestValues[x] = boardValue
                bestMoves[x] = move
            if (boardValue > alpha):
                alpha = boardValue
            self.board.pop()
        try:
            book_move = chess.polyglot.MemoryMappedReader(
                os.getcwd() + '/books/human.bin').weighted_choice(self.board).move
            if book_move in bestMoves:
                return (bestMoves, np.argmax(bestValues))
            else:
                x = np.argmin(bestValues)
                bestMoves[x] = book_move
                bestValues[x] = 99999  # arbitrary big value
                return (bestMoves, x)
        except:
            return (bestMoves, np.argmax(bestValues))

    def ai_move(self):
        movs, num = self.selectmove(2)
        is_capture = self.board.is_capture(movs[num])
        self.board.push(movs[num])
        return movs[num], is_capture

    def best_moves(self):
        res = []
        movs, _ = self.selectmove(2)
        for mov in movs:
            res.append(mov.uci())
        return res

    def is_game_over(self):
        return self.board.is_game_over(claim_draw=True)

    def check_winner(self):
        out = self.board.outcome()
        if out == None:
            return 'It\'s a draw!'
        if out.winner == None:
            return 'It\'s a draw!'
        else:
            if out.winner: #white
                return 'White wins!'
            else:
                return 'Black wins!'
