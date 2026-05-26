import pygame

import src.constants as constants
from sympy import simplify, Sum, symbols
import random
from sympy import sympify
from sympy.parsing.latex import parse_latex
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.figure import Figure



class Calculus:
    def __init__(self):
        pass

    def ask_question(self):

        x = symbols("x")

        LaTeX_string, correct_answer, category = constants.Problems[random.randint(0, len(constants.Problems) - 1)]
        correct_answer = sympify(correct_answer)

        prompts = {
            "sum": "Find the sum of the series.",
            "radius": "Find the radius of convergence.",
            "integral": "Evaluate the definite integral.",
            "lhopital": "Evaluate the limit using L'Hôpital's Rule.",
            "taylor": "Find the coefficient of the given term in the Maclaurin series.",
            "ibp": "Evaluate the integral using integration by parts.",
            "parametric": "Find dy/dx at the given point.",
        }

        result = {"correct": False}

        BG = "#111111"
        CARD = "#1d1d1d"
        SELECTED = "#3b82f6"
        TEXT = "#ffffff"
        SUB = "#999999"

        def format_answer(value):
            return str(simplify(value))

        def generate_choices(correct):

            correct = simplify(correct)

            wrong = [
                correct + 1,
                correct - 1,
                correct * 2,
                correct / 2,
                -correct,
                correct + 2,
            ]

            choices = [correct]

            for c in wrong:
                c = simplify(c)

                if c not in choices:
                    choices.append(c)

                if len(choices) == 4:
                    break

            random.shuffle(choices)

            return choices

        choices = generate_choices(correct_answer)

        root = tk.Tk()
        root.configure(bg=BG)

        selected = {"idx": None}
        answer_cards = []

        container = tk.Frame(
            root,
            bg=CARD,
            padx=40,
            pady=30
        )

        container.pack(padx=20, pady=20)
        title = tk.Label(
            container,
            text=prompts[category],
            font=("Segoe UI", 25),
            fg=SUB,
            bg=CARD
        )
        title.pack(pady=(0, 10))

        fig = Figure(
            figsize=(7, 1.4),
            dpi=140,
            facecolor=CARD
        )
        ax = fig.add_subplot(111)
        ax.text(
            .5,
            .5,
            LaTeX_string,
            fontsize=24,
            color="white",
            ha="center",
            va="center"
        )
        ax.axis("off")
        ax.set_facecolor(CARD)

        canvas = FigureCanvasTkAgg(fig, master=container)
        canvas.draw()
        equation = canvas.get_tk_widget()
        equation.configure(bg=CARD, highlightthickness=0)
        equation.pack(pady=(0, 25))

        def select(index):
            selected["idx"] = index
            for i, frame in enumerate(answer_cards):
                if i == index:
                    frame.config(bg=SELECTED)
                    frame.label.config(bg=SELECTED)
                else:
                    frame.config(bg="#2a2a2a")
                    frame.label.config(bg="#2a2a2a")

        for i, choice in enumerate(choices):
            card = tk.Frame(
                container,
                bg="#2a2a2a",
                padx=18,
                pady=14,
                cursor="hand2"
            )

            card.pack(fill="x", pady=5)
            text = (
                f"{chr(65 + i)}. "
                f"{format_answer(choice)}"
            )

            label = tk.Label(
                card,
                text=text,
                font=("Segoe UI", 15),
                fg=TEXT,
                bg="#2a2a2a",
                anchor="w"
            )

            label.pack(fill="x")

            card.label = label

            card.bind("<Button-1>", lambda e, idx=i: select(idx))

            label.bind("<Button-1>", lambda e, idx=i: select(idx))

            answer_cards.append(card)

        feedback = tk.Label(
            container,
            text="",
            font=("Segoe UI", 11),
            fg="#ff6666",
            bg=CARD
        )

        feedback.pack(pady=(10, 0))

        def submit():
            idx = selected["idx"]
            if idx is None:
                feedback.config(text="Select an answer")
                return

            result["correct"] = (simplify(choices[idx]) == simplify(correct_answer))

            root.destroy()

        submit_btn = tk.Button(
            container,
            text="Submit",
            command=submit,
            bg=SELECTED,
            fg="white",
            activebackground="#2563eb",
            relief="flat",
            font=("Segoe UI", 15),
            padx=25,
            pady=12
        )

        submit_btn.pack(fill="x", pady=(20, 0))

        root.update_idletasks()
        width = container.winfo_reqwidth()
        height = container.winfo_reqheight()

        x = (root.winfo_screenwidth() - width) // 2
        y = (root.winfo_screenheight() - height) // 2

        root.geometry(f"{width}x{height}+{x}+{y}")

        root.mainloop()
        plt.close(fig)

        return result["correct"]

