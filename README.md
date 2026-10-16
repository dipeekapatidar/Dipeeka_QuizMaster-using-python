# Dipeeka's QuizMaster
*Test your knowledge. Beat the clock!*

A GUI quiz application in Python (Tkinter + SQLite).

**Developed by: Dipeeka Patidar**

## Features
- Random question selection from a SQLite database (loaded from `questions.json`)
- Timer-based quiz (20 seconds per question; time up = skipped)
- Negative marking (+1 correct, -0.25 wrong, 0 skipped)
- Leaderboard (top 10, filter by category)
- Category-based quiz (Python, General Knowledge, Science, Computer Basics, or All)
- Tkinter GUI

## Project Files
| File | Purpose |
|------|---------|
| `main.py` | GUI and quiz logic (run this file) |
| `database.py` | SQLite database code (questions + leaderboard) |
| `questions.json` | Question bank (40 questions) |
| `quiz.db` | Created automatically on first run |

## Setup
1. Install Python 3.8 or newer from https://www.python.org/downloads/
   (Windows: tick "Add Python to PATH" during install).
2. Unzip this folder.
3. Open a terminal / Command Prompt inside the `dipeeka_quizmaster` folder.
4. Run:
   - Windows: `python main.py`
   - Mac/Linux: `python3 main.py`

No extra packages are needed. Tkinter and SQLite come with Python.
On Linux, if you get "No module named tkinter": `sudo apt install python3-tk`

## Add Your Own Questions
Open `questions.json` and add an entry like this:
```json
{
  "category": "Maths",
  "question": "What is 5 + 7?",
  "options": ["10", "11", "12", "13"],
  "answer": 2
}
```
`answer` is the position of the correct option (0 = first, 3 = last).
Restart the app and the new question (and category) is loaded automatically.

## Change Settings
At the top of `main.py` you can change `QUESTION_TIME`, `CORRECT_MARKS`,
`NEGATIVE_MARKS` and `DEFAULT_QUESTIONS`.

## Reset Leaderboard
Close the app and delete `quiz.db`. It is re-created on the next run.
