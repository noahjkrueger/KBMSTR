# <img src="docs/images/KBMSTR_logo.png" alt="KBMSTR Logo" height="64"> KBMSTR - Personalized Keyboards

# <img src="docs/images/book.png" alt="Book Icon" height="32"> Table of Contents
**[Visit the Official Website!](href)**<br>
**[Introduction](#introduction)**<br>
**[Installation](#installation)**<br>
**[Creating a Keyboard](#creating-a-keyboard)**<br>
**[Practice New Keyboards](#practice-new-keyboards)**<br>

# <img src="docs/images/KBMSTR_logo.png" alt="KBMSTR Logo" height="32" id="introduction"> Introduction

KBMSTER provides an array of tools for a user to find the best layout of a keyboard for their own personalized use.
By utilizing these tools, a user is able to collect data on actual typing habits and in turn use this data to generate
a keyboard layout to their exact needs. The goal of a generating a layout is to minimize the finger travel distance when
using a keyboard to type. The beauty of this tool is that it considers various methods of typing and furthermore
will prove useful to anyone looking to improve their typing efficiency. The development process of a brand new keyboard
layout, personalized to an individual, is involved, yet simple. KBMSTR works with the user to collect actual keystrokes
from the user in a transparent and non-invasive way by utilizing [KBMSTR's data collection tool](link-to-website).
Once a sufficient amount of data is collected and the user utilizes [KBMSTR's configuration tool](link-to-website) to let the algorithm know
actual typing habits, KBMSTR will then utilize these two items to employ a genetic algorithm to find the absolute best keyboard layout
for you. This, paired with [KBMSTR's practice tool](link-to-website) allow for users to dramatically speed up their typing speeds
and reduce hand fatigue while using the computer.

# <img src="docs/images/download.png" alt="Download Icon" height="32" id="installation"> Installation

To get started, clone this repo:

    git clone https://github.com/noahjkrueger/KBMSTR.git

You can also download the .zip archive. Once you have the files unzipped, navigate to /python/

    cd KBMSTR/python

And install the required libraries:

    pip install -r requirements.txt

And that's it! You are ready to start using the tools!

# <img src="docs/images/create.png" alt="Hammer Icon" height="32" id="creating-a-keyboard"> Creating a Keyboard

## Getting a Dataset
Generating a keyboard needs data. We recommend using collect_data.py, but you can provide the data in other ways. We reccomend
a dataset with at least 1 million (1,000,000) character, but the more the merrier[**](#generating-the-keyboard).

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

### Not using collect_data.p
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
- **code** - This dataset contains the entire soruce code of the KBMSTR project.
- **shakespeare** - This dataset contains ever work of William Shakespeare.

## Creating a config
A configuration file is required to generate keyboards. This file defines which fingers a person uses to type which keys, 
the distances between those keys, alternate key symbols, and whether or not the user returns their fingers to the home row after each keystroke.

### Using [KBMSTR Online Tool](link-to-site)
By utilizing this tool, creating a config is very easy! Just select the keys that each finger is responsible for and indicate if
you prefer to return the fingers back to the home keys or not! All of this is done with a intuitive interface; the configuration file
is generated for you!

### Not Using KBMSTR Online Tool

json structure

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

**Standard**: The Standard configuration assumes that the user uses eight fingers to type. This configuration is the standard way
most people are taught to type on a keyboard.

<img src="docs/images/standard.layout.png" alt="standard typing config" width="45%"> <img src="docs/images/huntpeck.layout.png" alt="hunt peck typing config" width="45%">

## Generating the Keyboard
**Assumption:** The distance to type _SPACE_ key is 0. This holds true in most cases.

**Computation Time Note:** If it is taking to long to find a keyboard layout, try a combination of the following (with most effecitve first):
- Change the ['return_to_home'](#the-return_to_home-flag) flag to 'False' in your configuration.
- Use a smaller dataset to generate the keyboard.
- Change the [char_checkpoint]() optional flag w
<br>
<br>
<br>
A quick overview of running KBMSTR.py:

    python3 KBMSTR.py [-h] [-dataset DATASET] [-char_checkpoint SIZE] [-name NAME] [-gen_size SIZE] [-mutation_rate RATE] [-epsilon EPSILON] [-steps_to_converge STEPS] [-save_stats] [-analyze] [-display] keyboard config

### Positional Arguments

#### keyboard

This is very important.

#### config
here

### Optional Arguments

# <img src="docs/images/gear.png" alt="Gear Icon" height="32" id="pre-made-keyboards"> Pre-made Keyboards

## Included Keyboards

- **QWERTY** - Standard QWERTY keyboard
- **DVORAK** - A much less common, but still standard keyboard developed in 1932.
- **KBMSTR HuntPeck** - two flavors included (remain/return).
  - Remain: The best keyboard layout for using the HuntPeck method of typing without returning fingers to home keys after each stroke.
  - Return: The best keyboard layput for using the HuntPeck method of typing with returning fingers to home keys after each stroke.
- **KBMSTR Standard** - two flavors included (remain/return)
  - Remain: The best keyboard layout for using the Standard method of typing without returning fingers to home keys after each stroke.
  - Return: The best keyboard layput for using the Standard method of typing with returning fingers to home keys after each stroke.

# <img src="docs/images/learn.png" alt="Student Icon" height="32" id="practice-new-keyboards"> Practice New Keyboards
By visting [The Official KBMSTR Website](link-to-site), a user will be able to practice their typing both on the keyboard
layouts previously mentioned as well as their own personalized keyboards. Users are presented with the option to upload their
own personalized keyboard and configuration to the website (produced by our other tools!) that will then display a virtual keyboard.
It is here where a user is able to use their physical keyboard to practice their new keyboard, or just try out their results.

Challange youself and improve your typing speed!