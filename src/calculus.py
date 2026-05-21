import pygame

import src.constants as constants
from sympy import simplify
import random
from sympy.parsing.latex import parse_latex
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt



class Calculus:
    def __init__(self):
        pass

    def ask_question(self) -> bool | None:
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

