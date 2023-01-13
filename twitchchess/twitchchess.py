import asyncio
import chess
import os
from dotenv import load_dotenv
from twitchio.ext import commands
from pygame import mixer

import chessboard.display as display
from chessai import Chessai

# commands:
# !init [color] [time]
# !play
# !quit

#TODO: create_chess_poll() sometimes has twitchio error, find and fix (maybe fixed?)
#TODO: fix line 68
#TODO: add stockfish to chessai

class Bot(commands.Bot):

    def __init__(self, token, user_id, user_name, prefix, channels, valid_users):
        super().__init__(token=token, prefix=prefix,
                         initial_channels=channels)

        # twitch vars
        self.user = commands.Bot.create_user(self, user_id=user_id,
                                             user_name=user_name)
        self.valid_users = valid_users
        self.token = token
        self.poll = None

        # chess vars
        self.chessai = Chessai(chess.Board())
        self.initialized = False
        self.playing = False
        self.time = None
        self.color = None
        self.last_move = None

    async def event_ready(self):
        print(f'Logged in as | {self.nick}')

    async def event_message(self, message):
        if message.echo:
            return
        # print(message.content)
        await self.handle_commands(message)

    async def wait(self, x):
        for _ in range(0, (x * 100) // 3, 1):
            await asyncio.sleep(0.01)
            if not self.playing:
                return

    async def create_chess_poll(self, time):
        if not self.initialized:
            return

        try:
            await self.user.end_poll(token=self.token, poll_id=self.poll, status='TERMINATED')
        except Exception as e:
            if not str(e) == 'Failed to fulfil request (400).': 
                print(e)

        movs = self.chessai.best_moves()
        while self.poll is None:
            if len(movs) == 1: movs = movs * 2 # this is very sussy. fix later
            try:
                await self.user.create_poll(token=self.token, title='Which move?', 
                                            choices=movs, duration=time)
                self.poll = (await self.user.fetch_polls(token=self.token, first=1))[0].id
            except Exception as e:
                print(e); print("error creating poll.")

        await self.wait(self.time) 
        try:
            await self.user.end_poll(token=self.token, poll_id=self.poll, status='TERMINATED')
        except Exception as e:
            if not str(e) == 'Failed to fulfil request (400).': 
                print(e)

        self.poll = None

    async def get_poll_winner(self):
        if not self.initialized:
            return
        fetched = False
        while not fetched:
            try:
                poll = (await self.user.fetch_polls(token=self.token, first=1))[0]
                fetched = True
            except Exception as e:
                print(e); print("error fetching poll.")

        votes = [(choice.title, choice.votes) for choice in poll.choices]
        return max(votes, key=lambda x: x[1])

    async def quit_game(self):
        self.initialized = False
        self.playing = False
        self.last_move = None
        try:
            await self.user.end_poll(token=self.token, poll_id=self.poll, status='TERMINATED')
        except Exception as e:
            if not str(e) == 'Failed to fulfil request (400).': 
                print(e)

    def play_sound(self, last_move, is_capture):
        if last_move is None or self.chessai.is_game_over():
            return

        if self.chessai.board.is_check():
            mixer.music.load('sound/check.mp3')
        elif is_capture:
            mixer.music.load('sound/take.mp3')
        else:
            mixer.music.load('sound/move.mp3')

        mixer.music.play()

    # starts running game loop
    @commands.command()
    async def init(self, ctx: commands.Context, color: str = 'white', time: int = 15):
        if ctx.author.name not in self.valid_users:
            return

        if not 15 <= time <= 1800: 
            await ctx.send('invalid time.'); return

        if not (color == 'white' or color == 'black'): 
            await ctx.send('invalid color.'); return

        if self.initialized:
            await ctx.send('quit before initializing.'); return

        self.chessai.board.reset()
        self.initialized = True
        self.color = color
        self.time = time
        
        game_board = display.start(self.chessai.board.fen())
        try:
            while True:
                display.update(self.chessai.board.fen(), game_board, self.last_move)
                await asyncio.sleep(0.01) # to allow for other commands to run

        except Exception as e:
            if str(e) == 'video system not initialized':
                await self.quit_game()
            else:
                print(e)

    @commands.command()
    async def play(self, ctx: commands.Context):
        if ctx.author.name not in self.valid_users:
            return

        if not self.initialized: 
            await ctx.send(f'not initialized.'); return

        if self.playing:
            await ctx.send(f'already playing.'); return
        self.playing = True

        mixer.music.load('sound/start.mp3')
        mixer.music.play()

        count = 0
        while not self.chessai.is_game_over() and self.initialized:
            
            if (self.color == 'white') ^ self.chessai.board.turn: # AI's move
                if not self.color == 'white':
                    print(f'\nturn number {count}:') 
                    count += 1

                await self.wait(1)
                self.last_move, is_capture = self.chessai.ai_move()
                self.play_sound(self.last_move, is_capture)

            else: # chat's move
                if self.color == 'white':
                    print(f'\nturn number {count}:') 
                    count += 1

                await self.wait(1) # helps rate limit?
                await self.create_chess_poll(self.time)
                
                winner = await self.get_poll_winner()
                if winner is not None:
                    await ctx.send(f'{winner[0]} was chosen.')
                    is_capture = self.chessai.board.is_capture(chess.Move.from_uci(winner[0]))
                    self.chessai.board.push_san(winner[0])
                    self.last_move = chess.Move.from_uci(winner[0])
                
                self.play_sound(self.last_move, is_capture)
            
            await asyncio.sleep(0.01) # to allow for other commands to run

        # sound
        if self.chessai.check_winner() == 'It\'s a draw!':
            mixer.music.load('sound/draw.mp3')
            mixer.music.play()
        else:
            mixer.music.load('sound/checkmate.mp3')
            mixer.music.play()

        print('\n' + self.chessai.check_winner())
        await ctx.send(self.chessai.check_winner())

    @commands.command()
    async def quit(self, ctx: commands.Context):
        if ctx.author.name not in self.valid_users:
            return

        if not self.initialized:
            await ctx.send(f'not initialized.'); return

        await self.quit_game()
        display.terminate()

if __name__ == '__main__':
    load_dotenv()
    bot_token = os.getenv('BOT_TOKEN')
    user_id = os.getenv('USER_ID')
    user_name = os.getenv('USER_NAME')
    prefix = os.getenv('PREFIX')
    channels = [os.getenv('CHANNEL')]

    mixer.init()
    mixer.music.set_volume(0.7)

    bot = Bot(token=bot_token, user_id=user_id, user_name=user_name, prefix=prefix,
              channels=channels, valid_users=channels)
    bot.run()
