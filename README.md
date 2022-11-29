# <img src="docs/images/KBMSTR_logo.png" alt="KBMSTR Logo" height="64"> KBMSTR - Personalized Keyboards

# <img src="docs/images/book.png" alt="Book Icon" height="32"> Table of Contents
- **[Visit the Official Website!](https://www.kbmstr.com)**
- **[Introduction](#introduction)**
- **[Installation](#installation)**
- **[Creating a Keyboard](#creating-a-keyboard)**
  - [Getting a Dataset](#getting-a-dataset)
  - [Creating a Config](#creating-a-config)
  - [Generating the Keyboard](#generating-the-keyboard)
- **[Pre-Made Keyboards](#pre-made-keyboards)**
- **[Practice New Keyboards](#practice-new-keyboards)**

# <img src="docs/images/KBMSTR_logo.png" alt="KBMSTR Logo" height="32" id="introduction"> Introduction

## Purpose
KBMSTER provides an array of tools for a user to find the best layout of a keyboard for their own personalized use.
By utilizing these tools, a user is able to collect data on actual typing habits and in turn use this data to generate
a keyboard layout to their exact needs. The goal of a generating a layout is to minimize the finger travel distance when
using a keyboard to type. The beauty of this tool is that it considers various methods of typing and furthermore
will prove useful to anyone looking to improve their typing efficiency. The development process of a brand new keyboard
layout, personalized to an individual, is involved, yet simple. KBMSTR works with the user to collect actual keystrokes
from the user in a transparent and non-invasive way by utilizing [KBMSTR's data collection tool](https://www.kbmstr.com).
Once a sufficient amount of data is collected and the user utilizes [KBMSTR's configuration tool](https://www.kbmstr.com) to let the algorithm know
actual typing habits, KBMSTR will then utilize these two items to employ [a unique algorithm](#the-algorithm) to find the absolute best keyboard layout
for you. This, paired with [KBMSTR's practice tool](https://www.kbmstr.com) allow for users to dramaGtically speed up their typing speeds
and reduce hand fatigue while using the computer.

## The Algorithm
The KBMSTR uses a unique algorithm to find the best keyboard layout. This algorithm is best described as a cross
between a local search and genetic algorithm. It is definitely greedy. The algorithm takes the best known layout (at the beginning, this can be anything)
and generates (# chars in layout)^2 / 2 succeeding layouts. Each one of these layouts can be achieved by swapping any
2 keys of the current best layout. The current iteration of the algorithm only knows its adjacent states, hence the 
local search aspect. If we consider the set of succeeding states as the population of the current generation, then
we can look for the best aspects in the generation and use them to make a new generation - hence the genetic aspect. This is done by
first looking at each one of the succeeding layouts and putting it through a fitness evaluation function. Since we know which two keys are swapped to achieve
each succeeding state, we are able to find swaps that improve efficiency, and making said swaps
if the key has not already been swapped at this iteration. The algorithm only does this with succeeding states that have the same or better
fitness evaluation than the current state. As a result, we make as many swaps possible that will improve the performance
of the layout in the fitness function.

The algorithm was designed this way to reduce the socratic element of a genetic algorithm and shorten the number
of generations needed to find the absolute best keyboard. The algorithm terminates knowing the best keyboard
relative to the dataset and configuration.

# <img src="docs/images/download.png" alt="Download Icon" height="32" id="installation"> Installation

To get started, clone this repo:

    git clone https://github.com/noahjkrueger/KBMSTR.git
You can also download the .zip archive. Once you have the files unzipped, navigate to /KBMSTR

    cd KBMSTR/
And install the required libraries:

    pip install -r requirements.txt
And that's it! You are ready to start using the tools!

# <img src="docs/images/create.png" alt="Hammer Icon" height="32" id="creating-a-keyboard"> Creating a Keyboard

## Getting a Dataset
Generating a keyboard needs data. We recommend using collect_data.py, but you can provide the data in other ways. We reccomend
a dataset with at least 1 million (1,000,000) characters, but the more the merrier[**](#generating-the-keyboard).

### Using collect_data.py
This is probably the best way to provide the KBMSTR tool the data it needs. It is simple, non-invasive, and the most accurate
to your use of the keyboard. We recommend creating a directory to store your data. Navigate to the /python/ directory and type the command:
    
    mkdir my_data && mv collect_data.py my_data && python3 my_data/collect_data.py
A process will start and every key you type will be recorded. **DO NOT UPLOAD THIS DATA ANYWHERE** - KBMSTR takes privacy very
seriously. The data collected could possibly contain some sensitive information, such as _passwords_ and _personal information_.
This data collected is intended for use in the KBMSTR genetic algorithm, and we do not send this data to _anyone_, not
even ourselves; this data does **not** leave your computer.

Once you have collected enough data, press <kbd>CRTL</kbd> + <kbd>C</kbd> within the terminal to signal the program to stop. If you exit out of the
program before doing this, there is no guarantee that all data will be saved and packed nicely into a compressed file - ready for use
in generating keyboard layouts.

Once the program terminates, a .zip archive containing all the collected data will appear in the same directory.
You are able to do this as many times as you want, as the generation can read multiple zip archives.

We highly recommend the deletion of this data once a personalized
keyboard layout is generated. You can easily do this with the command **(after you create your keyboard!)**:

    rm -rf my_data

### Not using collect_data.py
Alternatively, you can dig up some old files (work, novels, code, etc) and convert the contents to .txt files. You will then have to
compress the collection of files into a .zip archive as the generator requires this file structure. To assist with the conversion of
files to .txt format, we recommend using a tool such as [Online Convert](https://document.online-convert.com/convert-to-txt). However, 
you will have to compress the results.

A visual representation how the program reads a dataset:
    
    (directory as input to KBMSTR.py)
            |
            |--------- collection1.zip
            |              |
            |              |--------- dir1
            |              |            |
            |              |            |--------- file0.txt
            |              |             ...
            |              |
            |              |--------- file1.txt
            |               ...
            |
            |--------- dir 2
            |            |
            |            |--------- collection2.zip
            |             ...           |
            |                           |--------- file2.txt
             ...                         ...
Again, the program is able to read multiple zip archives that may contain other folders - however, only .txt files inside .zip archives will be read.

### Included Datasets
- **books** - Thanks to [Project Guntenberg](https://www.gutenberg.org/), this dataset contains around 300 free books.
- **brown** - This dataset contains a portion of the Brown English Corpus.
- **KBMSTR_code** - This dataset contains the entire source code of the KBMSTR project.
- **shakespeare** - This dataset contains ever work of William Shakespeare.

## Creating a config
A configuration file is required to generate keyboards. This file defines which fingers a person uses to type which keys, 
the distances between those keys, alternate key symbols, and whether or not the user returns their fingers to the home row after each keystroke.

### Using [KBMSTR Online Tool](https://www.kbmstr.com)
By utilizing this tool, creating a config is very easy! Just select the keys that each finger is responsible for and indicate if
you prefer to return the fingers back to the home keys or not! All of this is done with a intuitive interface; the configuration file
is generated for you! This is the recommended method.

### Not Using KBMSTR Online Tool
For reference while creating a configuration using this method, check out [a pre-made config](#included-configs)
A usable config is  a JSON file structured as:
  
    {
      "return_to_home": Bool,
      "alt_keys": {
        ...
      },
      "finger_duty": [ ... ],
      "original_finger_position": {
        ...
      }
    }
#### return_to_home
See ['The "return_to_home" Flag](#the-return_to_home-flag) for explanation. Boolean.

#### alt_keys
This data structure maps a String to String. They keys of each is the alternative input for a key (when pressing shift),
and the values is the input of the key (not pressing shift). For example:

    "alt_keys": {
        "!": "1",
        ":": ";",
        "X": "x",
        ...
      }
These are usually the same for every keyboard - we have not expanded the problem to consider switching around the values
of alternative keys for a better layout - something we hope to do in the future.

#### finger_duty
This data structure is an array that represents which finger is responsible or which key. The index of each value is the
key the value is responsible for. For this to integrate with the [display](#display) argument and the [KBMSTR webapp](https://www.kbmstr.com), 
there must be a value for each index that is one of the following:
- "l_p": the left pinky finger is responsible.
- "l_r": the left ring finger is responsible.
- "l_m": the left middle finger is responsible.
- "l_i": the left index finger is responsible.
- "r_i": the right index finger is responsible.
- "r_m": the right middle finger is responsible.
- "r_r": the right ring finger is responsible.
- "r_p": the right pinky finger is responsible.
The length of this array must be equal to the length of the layout, i.e. a one-to-one mapping.

#### original_finger_position
This data structure represents your home keys, or where your fingers start when you start typing.
You must have a home key for each finger contained in the [finger_duty](#finger_duty).

For example, if finger_duty only contains the left and right index finger:

    "original_finger_position": {
      "l_i": Integer,
      "r_i": Integer,
      ...
    }

### The "return_to_home" Flag
This is a magical flag, deserving of its own section. It is this flag within the configuration file that changes how keyboard 
layouts are generated, both in terms of final layout and efficiency. 

After the dataset is initialized, how the data is used differs with respect to the value of this flag.

When this flag is set to 'True', the fitness judgement of
each keyboard in each generation assumes that once a keystroke is completed by a finger, that finger returns to it's initial position.
This means that the program can calculate the fitness for a keyboard in constant time; we can simply calculate the distance from the home 
key to the key corresponding to the character times the numer of occurrences of that character (times two, as the finger moves back to the home key).

However, what if we care about the order of the keys? This is where setting this flag to 'False' comes into play.
With this configuration, the fitness judgement of each keyboard in each generation assumes that one a key is pressed, the finger
remains there until the same finger is needed again (i.e. the finger does not return to home). This is more accurate to how a person
actually types, but in order to achieve this, more complex calculations are needed. As a result, we need to iterate through each
character of the dataset for each keyboard in order to preserve the ordering of charters. This means that calculating the fitness
for each generation is a linear operation, and thus the larger the dataset, the longer this will take.

### Included Configs
The included configuration files each have two versions. One for returning fingers to the home keys after each keystroke,
and one for leaving each finger on the last pressed key. These are denoted by:

    *.return.config.json, *.remain.config.json
**HuntPeck**: The HuntPeck configuration assumes that the user is typing with both index fingers, with the left index responsible
for the left half of the keyboard and the right index for the right.

<img src="docs/images/huntpeck.layout.png" alt="hunt peck typing config" width="45%">

**Standard**: The Standard configuration assumes that the user uses eight fingers to type. This configuration is the standard way
most people are taught to type on a keyboard.

<img src="docs/images/standard.layout.png" alt="standard typing config" width="45%"> 

## Generating the Keyboard
**Assumption:** The distance to type _SPACE_ key is 0. This holds true in most cases.

**Computation Time Note:** If it is taking to long to find a keyboard layout, try a combination of the following (with most effecitve first):
- Change the ['return_to_home'](#the-return_to_home-flag) flag to 'True' in your configuration.
- Use a smaller dataset to generate the keyboard.
<br>

A quick overview of running KBMSTR.py:
  
    python3 KBMSTR.py [-h] [-dataset DATASET] [-breaker_lim LIMIT] [-name NAME] [-analyze] [-display] keyboard config

### Positional Arguments
These arguments are required for every use of KBMSTR.py
#### keyboard
The value of this argument is the path to a keyboard JSON file. If you are generating a fresh keyboard, use:
    
    keyboards/generic.json

If you wish to analyze a keyboard against dataset(s) or display the keyboard, this value is the path to that keyboard.

#### config
The values of this argument is the path to a [configuration file](#included-configs). This tells the program
useful information, such as what fingers are responsible for what keys, the home keys, whether or not fingers return to the home
keys, and the mapping from alternative keys.

### Optional Arguments
These arguments change the behavior of KBMSTR.py

#### dataset
This argument is an optional argument only because of another argument, [display](#display).
It is required for analyzing or generating a keyboard layout. The value for this argument
is a path the the directory that houses the datasets to use. This argument is ignored if
the [display](#display) argument is present.

#### breaker_lim
This argument is an optional argument that helps the algorithm break out of local maximums. 
The default is 5. This is only used when the [return_to_home](#return_to_home) flag in the
configuration is set to False. This argument is ignored if the [display](#display) or [analyze](#analyze) arguments are present.


#### name
The value of this argument is a string and will be the name of the keyboard outputted, the file
containing the keyboard, and the generation statistic graph is the [save_stats](#save_stats)
argument is present. The default is the time and day the program terminates.
This argument is ignored if the [display](#display) or [analyze](#analyze) arguments are present.

#### analyze
The presence of this argument ignores everything except the [dataset argument](#dataset), the [keyboard argument](#keyboard)
and the [config argument](#config). The program will analyze the efficiency of the keyboard provided using the
config and dataset provided. On program termination, the file passed into the keyboard argument will be overwritten
to reflect this analysis.

#### display
The presence of this argument ignores everything except the [keyboard argument](#keyboard)
and the [config argument](#config). The program will start a new window displaying a virtual keyboard
as defined in keyboard and config.

# <img src="docs/images/gear.png" alt="Gear Icon" height="32" id="pre-made-keyboards"> Pre-made Keyboards
- **QWERTY** - Standard QWERTY keyboard developed in the 1870s.
- **DVORAK** - A much less common, but still standard keyboard developed in 1932.
- **KBMSTR HuntPeck** - two flavors included (remain/return).
  - Remain: ~30.25% efficiency increase compared to QWERTY and ~26.5% Efficiency increase compared to Dvorak on the brown dataset using the HuntPeck configuration while keeping fingers on keys after each keystroke.
  - Return: ~35.5% efficiency increase compared to QWERTY and ~23% Efficiency increase compared to Dvorak on the brown dataset using the HuntPeck configuration while returning fingers home after each keystroke.
- **KBMSTR Standard** - two flavors included (remain/return)
  - Remain:  ~27% efficiency increase compared to QWERTY and ~9% Efficiency increase compared to Dvorak on the brown dataset using the HuntPeck configuration while keeping fingers on keys after each keystroke.
  - Return: ~55.5% efficiency increase compared to QWERTY and ~17% Efficiency increase compared to Dvorak on the brown dataset using the Standard configuration while returning fingers home after each keystroke.
- **Noah's Coding Keyboard** - two flavors included (remain/return)
  - Remain: The best keyboard layout for using the Noah's method of typing without returning fingers to home keys after each stroke.
  - Return: The best keyboard layout for using the Noah's method of typing with returning fingers to home keys after each stroke.

# <img src="docs/images/learn.png" alt="Student Icon" height="32" id="practice-new-keyboards"> Practice New Keyboards
By visiting [The Official KBMSTR Website](https://www.kbmstr.com), a user will be able to practice their typing both on the keyboard
layouts previously mentioned as well as their own personalized keyboards. Users are presented with the option to upload their
own personalized keyboard and configuration to the website (produced by our other tools!) that will then display a virtual keyboard.
It is here where a user is able to use their physical keyboard to practice their new keyboard, or just try out their results.

Challenge yourself and improve your typing speed!
