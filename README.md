# QMK Wiring Diagram Generator

Generate a wiring diagram from a keyboard's QMK `keyboard.json` file.
Outputs each row and column's respective pin in a Pro Micro board

## Usage

```
❯ python generator.py -h
usage: generator.py [-h] (-f FILE_PATH | -p QMK_PATH)

Generate a wiring diagram from qmk keyboard.json.

options:
  -h, --help    show this help message and exit
  -f FILE_PATH  Path to local keyboard.json file.
  -p QMK_PATH   Path to keyboard in upstream qmk repo. (e.g.: handwired/dactyl_manuform/4x5)
```

## Output example

```
❯ python generator.py -p handwired/dactyl_manuform/4x5
         5      6      7      8      9                                         9      8      7      6      5
         |      |      |      |      |                                         |      |      |      |      |
A0 --- [0, 0] [0, 1] [0, 2] [0, 3] [0, 4]                                    [5, 4] [5, 3] [5, 2] [5, 1] [5, 0] --- A0
15 --- [1, 0] [1, 1] [1, 2] [1, 3] [1, 4]                                    [6, 4] [6, 3] [6, 2] [6, 1] [6, 0] --- 15
14 --- [2, 0] [2, 1] [2, 2] [2, 3] [2, 4]                                    [7, 4] [7, 3] [7, 2] [7, 1] [7, 0] --- 14
       16 --- [3, 1] [3, 2]                                                                [8, 2] [8, 1] --- 16
                     16 --- [3, 3] [3, 4]                                    [8, 4] [8, 3] --- 16
                                   10 --- [4, 4] [4, 3]        [9, 3] [9, 4] --- 10
                                   10 --- [4, 2] [4, 1]        [9, 1] [9, 2] --- 10
```
