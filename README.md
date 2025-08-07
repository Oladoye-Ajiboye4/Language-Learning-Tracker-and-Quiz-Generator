Language Learning Tracker


CLI Quiz Generator – User Guide

Welcome to the CLI Quiz Generator, a simple command-line tool that turns your vocabulary lists into interactive quizzes. This guide walks you—step by step—from setup through your first quiz, with no prior programming experience required.

What Is This Tool?

The CLI Quiz Generator loads a plain-text vocabulary file you supply, estimates your language level (Beginner, Intermediate, Advanced) based on word frequency, generates a 10-question quiz per round tailored to your level. It runs entirely in your terminal—no graphical interface needed.

Prerequisites

Python 3.8 or newer installed
A terminal or command prompt for typing commands
A vocabulary file (vocab.txt) formatted with one word per line or comma-separated
A one-time internet connection to install program dependencies

Installation & Setup

Download the Project

Open your terminal.
Navigate to your desired folder (e.g., cd /path/to/folder).
Ensure you have git installed. You can download git from https://git-scm.com/downloads/win
 Clone or download the repository by running the command below on your terminal:
git clone https://github.com/Oladoye-Ajiboye4/Language-Learning-Tracker-and-Quiz-Generator

Install Dependencies

pip install -r requirements.txt
python -m nltk.downloader wordnet omw-1.4

Preparing Your Vocabulary File

Your vocab.txt can be:
One word per line:

apple
banana
canyon

Comma-separated:

apple, banana, canyon, dolphin

A form of writing like an article or essay:

Learning  new   vocabulary  is  an  essential  part  of  mastering  a  language.
It  helps  you  express  your  thoughts  more  clearly  and  understand  others  better.
Save the file in the project folder or note its full path.

Running Your First Quiz

In the project folder, run:

python main.py

b. Enter your name when prompted (e.g., Alice).
c. Press Enter to use the current folder or type a folder path where your vocabulary text file is.
d. Enter the file name (e.g., vocab.txt).
e. The quiz starts automatically.

Quiz Interaction

Questions appear with a difficulty label, e.g.:
Q1 [Beginner]: Which best defines "apple"?
	a) a fruit
  	b) a device
  	c) a color
  	d) a vehicle
Answer by typing the letter (a–d) or the full word/phrase, then press Enter.
Feedback:  Correct! or Wrong. Answer: a fruit
After 10 questions, you see: Final score: 7/10
You'll then be prompted if you'd like to take another round
Would you like to take another round [yes/no]:
If yes, the process will be repeated. But if not, the user statistics would be shown and the program would stop

Troubleshooting

File not found: check spelling, extension, and path.
NLTK errors: re-run python -m nltk.downloader wordnet omw-1.4 and ensure you have an internet connection
No questions generated: ensure at least 10 distinct words in your file.

Frequently Asked Questions

Q: Can I use CSV or JSON?
A: Only plain .txt is supported.
Q: Where are scores saved?
A: Results append to user_db.json  .

Tips & Best Practices

Clean your word list: remove duplicates and typos.
Use themed lists: e.g., fruits.txt, science_terms.txt.
Review feedback and study missed words.
Repeat quizzes after updating vocab.txt.
Getting Help & Contributing
Report issues on GitHub: https://github.com/Oladoye-Ajiboye4/Language-Learning-Tracker-and-Quiz-Generator
Contribute via pull requests or feature requests.

Thank you for using the CLI Quiz Generator! Happy learning!


