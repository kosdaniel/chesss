"""
Module implementing the chess clock class
"""
import time
from app import config as cf

class ChessClock():
    """
    Class representing a chess clock
    """
    def __init__(self, time_control: str = cf.DEFAULT_TIME_CONTROL):
        """
        Constructor takes a string arg in form of "time+increment"
        The object stores player times in milliseconds
        """
        time_control = time_control.split('+')
        time_per_player = float(time_control[0]) * 60 * 1000
        self.remaining_times = {0: time_per_player, 1: time_per_player}
        self.increment = float(time_control[1]) * 1000
        self.time_of_last_update = None
        self.running = False
        self.to_move = None
        self.timeout = False

    def start(self, to_move: int = 0):
        """
        Start the clock for the player of arg color
        """
        self.time_of_last_update = time.time() * 1000
        self.running = True
        self.to_move = to_move

    def press(self):
        """
        Pause clock for player currently on turn, add increment to his time and start the clock for the other player
        """
        if not self.running or self.timeout:
            return
        self.update()
        if self.timeout:
            return
        self.remaining_times[self.to_move] += self.increment
        self.to_move = 1 - self.to_move

    def update(self):
        """
        Remove time passed since last update from the clock of the player currently on move
        """
        if not self.running or self.timeout:
            return 
        cur_time = time.time() * 1000    
        self.remaining_times[self.to_move] -= (cur_time - self.time_of_last_update)
        if self.remaining_times[self.to_move] <= 0:
            self.remaining_times[self.to_move] = 0
            self.timeout = True
            self.running = False
        else:
            self.time_of_last_update = cur_time

    def pause(self):
        """
        Pause the clock
        """
        self.running = False

    def get_player_times(self) -> dict[int : str]:
        """
        Return times of both players as a dict of color : string
        """
        return {0: self.get_time_as_string(self.remaining_times[0]),
                1: self.get_time_as_string(self.remaining_times[1])}

    def get_time_as_string(self, time: float) -> str:
        """
        Take time in argument in milliseconds, return it as a string in the format
        (M)M:SS or 0:SS.(S/10) if time is lower than 10s
        """
        minutes = time // (60 * 1000)
        seconds = ( time % (60 * 1000) ) // 1000
        tenths = (time % 1000) // 100
        res = str(int(minutes)) + ':'
        if seconds < 10:
            res += '0' + str(int(seconds))
            if minutes == 0:
                res += '.' + str(int(tenths))
        else:
            res += str(int(seconds))
        return res
        
        


    