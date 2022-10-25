# <img src="docs/images/KBMSTR_logo.png" alt="KBMSTR Logo" height="64"> KBMSTR - Personalized Keyboards

### <img src="docs/images/book.png" alt="Book Icon" height="32"> Table of Contents
**[Visit the Official Website!](href)**<br>
**[Introduction](#introduction)**<br>
**[Assumptions](#assumptions)**<br>
**[Installation](#installation)**<br>
**[Creating a Keyboard](#creating-a-keyboard)**<br>
**[Pre-made Keyboards](#pre-made-keyboards)**<br>
**[Practice New Keyboards](#practice-new-keyboards)**<br>

## <img src="docs/images/KBMSTR_logo.png" alt="KBMSTR Logo" height="32"> Introduction
here is the intro

## <img src="docs/images/exclaim.png" alt="Exlaimation Mark Icon" height="32"> Assumptions
here are assumptions

## <img src="docs/images/download.png" alt="Download Icon" height="32"> Installation
here is how to clone/download and do requirements.txt

## <img src="docs/images/create.png" alt="Hammer Icon" height="32"> Creating a Keyboard
The following information is also on our website - [Visit the Official Website!](href)
### KBMSTR.py

    > python3 KBMSTR.py [-h] [-config CONFIG] [-dataset DATASET] [-char_checkpoint SIZE] [-name NAME] [-gen_size SIZE] [-mutation_rate RATE] [-epsilon EPSILON] [-steps_to_converge STEPS] [-save_stats] [-analyze] [-display] keyboard

    positional arguments:
      keyboard              Name of the keyboard layout to improve upon, stored in /keyboards.
    
    options:
      -h, --help            Show this help message and exit.
      -config CONFIG        Name of the config JSON to initialize the cost matrix, finger responsibilities and initial finger positions.
      -dataset DATASET      A single or a collection of (.zip) of datasets (.txt) to be used in the generation. Enter a directory or a single .zip compressed file. Only .txt files within a .zip file are used to rank the keyboards. Directories of multiple .zip collections
                            are allowed.
      -char_checkpoint SIZE
                            Create character checkpoints for large datasets. For each keyboard, disregaurd if the total distance is greater than the 0.95 * last best total distance at every [char_checkpoint] number of characters.
      -name NAME            Name the keyboard being generated. Default naming scheme: yyyy/mm/dd:hh:mm:ss.raw
      -gen_size SIZE        Chose the number of members for each generation. (Default: 100)
      -mutation_rate RATE   Change the rate at which mutations occur. (Default: 0.75)
      -epsilon EPSILON      Change the threshold of convergence. (Default: 0.0)
      -steps_to_converge STEPS
                            Change the threshold of convergence. (Default: 0.005)
      -save_stats           Create a visual plot for the generation statistic in /run_stats.
      -analyze              Analyze the efficiency of the inputted keyboard against dataset(s) provided in -dataset and places results in /keyboards. Ignores all other options.
      -display              Create a visual display of the keyboard inputted. Ignores all other options.

    
##### Arguments

    -config
This option

### generate_config.py
use
### collect_data.py
use

## <img src="docs/images/gear.png" alt="Gear Icon" height="32"> Pre-made Keyboards
### Dataset Sources
- https://www.gutenberg.org/
### Included Keyboards
- **QWERTY** - Standard
- **DVORAK** - Less common
- **SHAKESPEAR**
- **ENGLISH**
- **JAVA**

## <img src="docs/images/learn.png" alt="Student Icon" height="32"> Practice New Keyboards
go to website here is more explanation