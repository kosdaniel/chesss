# Chesss

## Chess desktop application written in Python, only using the Pygame and Pygame_menu libraries.

## Functionalities:
- local play: both players use mouse as input
- play against a computer: play against a simple bot as either white or black
- choose time control: application implements chess clocks with selectable starting time and increment

## chess.com-style GUI:
- ingame gui was written to be as smooth and to feel and look the same as the default chess.com gui
- the piece images and board colors were directly taken from chess.com

## custom chess engine:
- no chess libraries imported, all game logic is written by hand
- engine detects all the possible types of game conclusion

## HOW TO RUN:
- have Python installed
- from root run ```pip install -r requirements.txt```
- launch the application by running ```python -m app.src.application.application```
- or on Windows by running:
  
  ```powershell
  $env:PYTHONPATH = (Get-Location).Path
  python app/src/application/application.py
  ```

- or on Linux by running:

  ```bash
  export PYTHONPATH="$(pwd)"
  python app/src/application/application.py
  ```

![chess1](https://github.com/user-attachments/assets/af3bd124-66b3-41c4-b0db-ff059ddb2534)

![chess2](https://github.com/user-attachments/assets/df5f93d8-e19e-4a7a-bff0-323c02db7369)


  
