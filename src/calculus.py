import pygame

import src.constants as constants
from sympy import simplify, Sum, symbols
import random
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

        LaTeX_string = constants.SERIES[random.randint(0, len(constants.INTEGRALS) - 1)]
        correct_answer = 2



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
            text="Find the interval of convergence.",
            font=("Segoe UI", 25),
            fg=SUB,
            bg=CARD
        )
        title.pack(pady=(0, 10))

        fig = Figure(
            figsize=(7, 1.4),
            dpi=120,
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



    def ask_question_OLD(self) -> bool | None:
        LaTeX_string = constants.INTEGRALS[random.randint(0, len(constants.INTEGRALS) - 1)]

        correct_answer = parse_latex(LaTeX_string[1:-1]).doit()
        print(str(correct_answer))

        result = {"correct": False}

        def format_answer(value):
            value = simplify(value)

            return str(value)

        def generate_choices(correct):
            correct = simplify(correct)

            possible_wrong = [
                correct + 1,
                correct - 1,
                correct * 2,
                correct / 2,
                -correct,
                correct + 2,
            ]

            choices = [correct]

            for wrong in possible_wrong:
                wrong = simplify(wrong)
                if wrong not in choices:
                    choices.append(wrong)

                if len(choices) == 4:
                    break

            random.shuffle(choices)
            return choices

        choices = generate_choices(correct_answer)

        root = tk.Tk()
        root.title("Solve the Integral")

        fig = plt.figure(figsize=(4, 1), dpi=100)
        ax = fig.add_subplot(111)
        ax.text(0.5, 0.5, LaTeX_string, fontsize=18, ha="center", va="center")
        ax.axis("off")

        canvas = FigureCanvasTkAgg(fig, master=root)
        canvas.draw()
        canvas.get_tk_widget().pack(padx=20, pady=20)

        selected_choice = tk.IntVar(value=-1)

        for index, choice in enumerate(choices):
            button = tk.Radiobutton(
                root,
                text=format_answer(choice),
                variable=selected_choice,
                value=index,
                font=("Arial", 14),
                padx=10,
                pady=5
            )
            button.pack(anchor="w", padx=30)

        def submit():
            selected_index = selected_choice.get()

            chosen_answer = choices[selected_index]
            if chosen_answer == correct_answer:
                print("true")
                result["correct"] = True
            root.destroy()


        submit_button = tk.Button(root, text="Submit", command=submit, font=("Arial", 14))
        submit_button.pack(pady=15)

        print("Finished initializing")


        plt.close(fig)
        root.mainloop()

        print(result["correct"])

        return result["correct"]

