"""
Dipeeka's QuizMaster - Python + Tkinter + SQLite
Features: random questions, per-question timer, negative marking,
          leaderboard, category-based quiz.
Developed by: Dipeeka Patidar
"""
import tkinter as tk
from tkinter import ttk, messagebox

import database as db

# ---------------- Settings (change these as you like) ----------------
AUTHOR = "Dipeeka Patidar"
APP_NAME = "Dipeeka's QuizMaster"
TAGLINE = "Test your knowledge. Beat the clock!"
QUESTION_TIME = 20        # seconds allowed for each question
CORRECT_MARKS = 1.0       # marks for a correct answer
NEGATIVE_MARKS = 0.25     # marks deducted for a wrong answer
DEFAULT_QUESTIONS = 10    # default number of questions per quiz

BG = "#f4f6fb"
PRIMARY = "#3b5bdb"
FONT = "Segoe UI"


class QuizApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME}  |  by {AUTHOR}")
        self.geometry("720x540")
        self.resizable(False, False)
        self.configure(bg=BG)

        db.init_db()

        # footer stays visible on every screen
        tk.Label(self, text=f"\u00a9 Developed by {AUTHOR}  |  {APP_NAME}", bg=BG,
                 fg="#868e96", font=(FONT, 9)).pack(side="bottom", pady=(0, 6))

        self.container = tk.Frame(self, bg=BG)
        self.container.pack(fill="both", expand=True, padx=25, pady=(20, 5))

        self.timer_id = None
        self.player = tk.StringVar()
        self.category = tk.StringVar(value="All")
        self.num_questions = tk.IntVar(value=DEFAULT_QUESTIONS)

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.show_start()

    # ------------------------------------------------------------ helpers
    def clear(self):
        self.cancel_timer()
        for w in self.container.winfo_children():
            w.destroy()

    def cancel_timer(self):
        if self.timer_id is not None:
            self.after_cancel(self.timer_id)
            self.timer_id = None

    def on_close(self):
        self.cancel_timer()
        self.destroy()

    def label(self, parent, text, size=11, bold=False, color="#222", **kw):
        return tk.Label(parent, text=text, bg=BG, fg=color,
                        font=(FONT, size, "bold" if bold else "normal"), **kw)

    def button(self, parent, text, command, color=PRIMARY, width=16):
        return tk.Button(parent, text=text, command=command, bg=color, fg="white",
                         activebackground=color, activeforeground="white",
                         font=(FONT, 11, "bold"), width=width, relief="flat",
                         cursor="hand2", pady=6)

    # ------------------------------------------------------------ start screen
    def show_start(self):
        self.clear()
        self.label(self.container, APP_NAME.upper(), 26, True, PRIMARY).pack(pady=(5, 0))
        self.label(self.container, TAGLINE, 11, color="#444").pack()
        self.label(self.container, f"Developed by {AUTHOR}", 10, True, "#666").pack(pady=(2, 15))

        form = tk.Frame(self.container, bg=BG)
        form.pack(pady=5)

        self.label(form, "Your Name:").grid(row=0, column=0, sticky="e", padx=8, pady=8)
        tk.Entry(form, textvariable=self.player, font=(FONT, 11), width=26).grid(row=0, column=1, pady=8)

        self.label(form, "Category:").grid(row=1, column=0, sticky="e", padx=8, pady=8)
        ttk.Combobox(form, textvariable=self.category, state="readonly", width=24,
                     values=["All"] + db.get_categories(), font=(FONT, 10)).grid(row=1, column=1, pady=8)

        self.label(form, "No. of Questions:").grid(row=2, column=0, sticky="e", padx=8, pady=8)
        tk.Spinbox(form, from_=3, to=40, textvariable=self.num_questions, width=6,
                   font=(FONT, 11)).grid(row=2, column=1, sticky="w", pady=8)

        rules = (f"Rules:  +{CORRECT_MARKS:g} for correct   |   -{NEGATIVE_MARKS:g} for wrong   |   "
                 f"0 for skipped\nTime limit: {QUESTION_TIME} seconds per question")
        self.label(self.container, rules, 10, color="#444", justify="center").pack(pady=14)

        self.button(self.container, "Start Quiz", self.start_quiz).pack(pady=5)
        self.button(self.container, "Leaderboard", self.show_leaderboard, "#2f9e44").pack(pady=5)
        self.button(self.container, "Exit", self.on_close, "#c92a2a").pack(pady=5)

    # ------------------------------------------------------------ quiz logic
    def start_quiz(self):
        name = self.player.get().strip()
        if not name:
            messagebox.showwarning("Name required", "Please enter your name to start.")
            return
        try:
            n = int(self.num_questions.get())
        except (tk.TclError, ValueError):
            messagebox.showwarning("Invalid number", "Enter a valid number of questions.")
            return

        self.questions = db.get_random_questions(self.category.get(), n)
        if not self.questions:
            messagebox.showerror("No questions", "No questions found for this category.")
            return

        self.index = 0
        self.score = 0.0
        self.correct = self.wrong = self.skipped = 0
        self.show_quiz()

    def show_quiz(self):
        self.clear()
        top = tk.Frame(self.container, bg=BG)
        top.pack(fill="x")
        self.lbl_player = self.label(top, f"Player: {self.player.get().strip()}", 10, True)
        self.lbl_player.pack(side="left")
        self.lbl_score = self.label(top, "", 10, True, "#2f9e44")
        self.lbl_score.pack(side="right")

        info = tk.Frame(self.container, bg=BG)
        info.pack(fill="x", pady=(8, 0))
        self.lbl_progress = self.label(info, "", 10, color="#555")
        self.lbl_progress.pack(side="left")
        self.lbl_timer = self.label(info, "", 14, True, PRIMARY)
        self.lbl_timer.pack(side="right")

        self.lbl_cat = self.label(self.container, "", 10, True, "#868e96")
        self.lbl_cat.pack(anchor="w", pady=(10, 0))
        self.lbl_question = self.label(self.container, "", 15, True, wraplength=650, justify="left")
        self.lbl_question.pack(anchor="w", pady=(4, 15))

        self.selected = tk.IntVar(value=-1)
        self.radios = []
        for i in range(4):
            rb = tk.Radiobutton(self.container, variable=self.selected, value=i, bg=BG,
                                font=(FONT, 12), anchor="w", justify="left",
                                activebackground=BG, wraplength=620)
            rb.pack(fill="x", pady=4, padx=10)
            self.radios.append(rb)

        btns = tk.Frame(self.container, bg=BG)
        btns.pack(pady=20)
        self.btn_next = self.button(btns, "Submit & Next", self.submit_answer)
        self.btn_next.pack(side="left", padx=8)
        self.button(btns, "Skip", self.skip_question, "#868e96", 10).pack(side="left", padx=8)

        self.load_question()

    def load_question(self):
        if self.index >= len(self.questions):
            self.finish_quiz()
            return
        q = self.questions[self.index]
        self.lbl_progress.config(text=f"Question {self.index + 1} of {len(self.questions)}")
        self.lbl_score.config(text=f"Score: {self.score:g}")
        self.lbl_cat.config(text=q["category"].upper())
        self.lbl_question.config(text=q["question"])
        for i, rb in enumerate(self.radios):
            rb.config(text=f"{chr(65 + i)}.  {q['options'][i]}")
        self.selected.set(-1)
        self.btn_next.config(
            text="Submit & Finish" if self.index == len(self.questions) - 1 else "Submit & Next")

        self.time_left = QUESTION_TIME
        self.update_timer_label()
        self.cancel_timer()
        self.timer_id = self.after(1000, self.tick)

    def update_timer_label(self):
        color = "#c92a2a" if self.time_left <= 5 else PRIMARY
        self.lbl_timer.config(text=f"Time: {self.time_left}s", fg=color)

    def tick(self):
        self.time_left -= 1
        self.update_timer_label()
        if self.time_left <= 0:
            self.timer_id = None
            self.skipped += 1          # time up -> counted as skipped (no penalty)
            self.next_question()
        else:
            self.timer_id = self.after(1000, self.tick)

    def submit_answer(self):
        choice = self.selected.get()
        if choice == -1:
            messagebox.showwarning("Select an answer", "Choose an option or press Skip.")
            return
        self.cancel_timer()
        if choice == self.questions[self.index]["answer"]:
            self.correct += 1
            self.score += CORRECT_MARKS
        else:
            self.wrong += 1
            self.score -= NEGATIVE_MARKS
        self.next_question()

    def skip_question(self):
        self.cancel_timer()
        self.skipped += 1
        self.next_question()

    def next_question(self):
        self.index += 1
        self.load_question()

    def finish_quiz(self):
        self.cancel_timer()
        self.score = round(self.score, 2)
        db.save_score(self.player.get().strip(), self.category.get(),
                      self.score, self.correct, self.wrong, self.skipped)
        self.show_result()

    # ------------------------------------------------------------ result screen
    def show_result(self):
        self.clear()
        total = len(self.questions)
        max_marks = total * CORRECT_MARKS
        self.label(self.container, "Quiz Completed!", 26, True, PRIMARY).pack(pady=(10, 5))
        self.label(self.container, f"Well played, {self.player.get().strip()}! - {APP_NAME}", 13).pack()
        self.label(self.container, f"{self.score:g} / {max_marks:g}", 36, True, "#2f9e44").pack(pady=15)

        stats = (f"Correct: {self.correct}      Wrong: {self.wrong}      Skipped: {self.skipped}\n"
                 f"Category: {self.category.get()}      Total Questions: {total}")
        self.label(self.container, stats, 12, justify="center").pack(pady=10)
        self.label(self.container, "Your score has been saved to the leaderboard.",
                   10, color="#666").pack(pady=5)

        self.button(self.container, "Play Again", self.show_start).pack(pady=6)
        self.button(self.container, "Leaderboard", self.show_leaderboard, "#2f9e44").pack(pady=6)
        self.button(self.container, "Exit", self.on_close, "#c92a2a").pack(pady=6)

    # ------------------------------------------------------------ leaderboard
    def show_leaderboard(self):
        self.clear()
        self.label(self.container, f"{APP_NAME.upper()} - HALL OF FAME", 18, True, PRIMARY).pack(pady=(0, 10))

        bar = tk.Frame(self.container, bg=BG)
        bar.pack(pady=5)
        self.label(bar, "Category:").pack(side="left", padx=5)
        self.lb_category = tk.StringVar(value="All")
        combo = ttk.Combobox(bar, textvariable=self.lb_category, state="readonly", width=22,
                             values=["All"] + db.get_categories())
        combo.pack(side="left")
        combo.bind("<<ComboboxSelected>>", lambda e: self.fill_leaderboard())

        cols = ("rank", "player", "category", "score", "correct", "wrong", "date")
        self.tree = ttk.Treeview(self.container, columns=cols, show="headings", height=12)
        widths = (50, 120, 130, 70, 70, 60, 130)
        for c, w in zip(cols, widths):
            self.tree.heading(c, text=c.capitalize())
            self.tree.column(c, width=w, anchor="center")
        self.tree.pack(pady=10)

        self.button(self.container, "Back", self.show_start, "#868e96").pack(pady=5)
        self.fill_leaderboard()

    def fill_leaderboard(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for rank, r in enumerate(db.get_leaderboard(self.lb_category.get()), start=1):
            player, cat, score, correct, wrong, date = r
            self.tree.insert("", "end", values=(rank, player, cat, f"{score:g}", correct, wrong, date))


if __name__ == "__main__":
    QuizApp().mainloop()
