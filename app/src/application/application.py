"""
Module implementing the App class
"""

import pygame as pg
from app import config as cf
import pygame_menu as pgm
from pygame_menu import themes
from app.src.engine import clock
from app.src.application import game

class App():
    """
    Main class of the entire application. Implements a pygame_menu wrapper around the Game class used 
    for selecting the game parameters
    """
    def __init__(self):
        pg.init()
        self.display = pg.display.set_mode((cf.DEFAULT_WINDOW_WIDTH, cf.DEFAULT_WINDOW_HEIGHT))
        pg.display.set_caption("Chesss")
        self.init_menu()
        self.curmenu = self.menu
        self.running = True
        self.game = None
        self.mode = None
        self.chessclock = None
        self.start_as_white = None
        self.time_control = None

    def choose_time_control(self):
        """
        Helper menu method
        """
        if self.mode is None:
            self.mode = cf.LOCAL
        self.menu._open(self.time_control_menu)

    def choose_color(self):
        """
        Helper menu method
        """
        self.mode = cf.AGAINST_COMPUTER
        self.menu._open(self.color_menu)

    def set_time_control(self, _, tc):
        """
        Helper menu method
        """
        self.time_control = tc

    def play_as_white(self):
        """
        Helper menu method
        """
        self.start_as_white = True
        self.choose_time_control()

    def play_as_black(self):
        """
        Helper menu method
        """
        self.start_as_white = False
        self.choose_time_control()

    def play(self):
        """
        Run the chess game after selecting the game parameters. Show the result after the game ends
        """
        self.game = game.Game(self.display)
        if self.time_control is not None:
            self.chessclock = clock.ChessClock(self.time_control)
        result = self.game.run(self.chessclock, self.mode, self.start_as_white)
        self.mode = None
        self.chessclock = None
        self.start_as_white = None
        self.show_end_menu(result)

    def show_end_menu(self, result):
        """
        Helper menu method
        """
        if result is not None:
            self.endmenu.set_title(result)
        else:
            self.endmenu.set_title('Game Interrupted')
        self.menu._open(self.endmenu)

    def run(self):
        """
        Main application loop
        """
        while True:
            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT:
                   self.quit()
                   return
            if self.menu.is_enabled():
                self.menu.update(events)
                self.menu.draw(self.display)
            pg.display.update()

    def quit(self):
        """
        Properly exit the application
        """
        self.menu.disable()
        self.running = False
        pg.quit()

    def init_menu(self):
        """
        Define and initialize all the required menus
        """
        self.menu = pgm.Menu("Chesss", cf.DEFAULT_WINDOW_WIDTH, cf.DEFAULT_WINDOW_HEIGHT, theme = themes.THEME_GREEN)
        self.menu.add.button("Play Locally (Two Players)", self.choose_time_control)
        self.menu.add.button("Play Against Computer", self.choose_color)
        
        self.time_control_menu = pgm.Menu("Choose time control", cf.DEFAULT_WINDOW_WIDTH, cf.DEFAULT_WINDOW_HEIGHT, theme = themes.THEME_GREEN)
        self.time_control_menu.add.selector("Time control:", [('Play without clock',None), ('10+0','10+0'), ('3+2','3+2'), 
                                                              ('1+0','1+0'), ('1+2','1+2'), ('5+0','5+0')], onchange = self.set_time_control)
        self.time_control_menu.add.button("Play", self.play)

        self.color_menu = pgm.Menu("Choose starting color", cf.DEFAULT_WINDOW_WIDTH, cf.DEFAULT_WINDOW_HEIGHT, theme = themes.THEME_GREEN)
        self.color_menu.add.button("White", self.play_as_white)
        self.color_menu.add.button("Black", self.play_as_black)

        self.endmenu = pgm.Menu("Game Interrupted", cf.DEFAULT_WINDOW_WIDTH, cf.DEFAULT_WINDOW_HEIGHT, theme = themes.THEME_GREEN)
        self.endmenu.add.button("Quit", self.quit)

        
if __name__ == '__main__':
    App().run()