import math
from pathlib import Path
import pygame
from sympy import pi, oo, Rational, sqrt, exp, ln, factorial, sin, cos

# File paths (where AI policies are stored)
BASE_DIR = Path(__file__).resolve().parent.parent
POLICY_DIR = BASE_DIR / 'policies'

# File name of policy used when in Human play AI mode
POLICY_FILE = "policy_player2_20260217-1127.pkl"

# ----------------------------------------------------------------------------------------------------------------------

# AI Training Constants

# How strong to update a states value when learning new information
#   Higher value (ex > 0.5)  - learns faster but can become unstable
#   Lower values (ex < 0.05) - learns more smoothly but will take longer to train
# Choose a value between 0.01 and 0.3 for state based Reinforcement Learning
#
# When you are making your new game in your team you will want to experiment with different values
LEARNING_RATE = 0.2

# Discount factor: how much the AI should care about future rewards compared to immediate rewards
# Closer to 0: Care more about immediate rewards.
# Closer to 1: Care more about future (long term rewards)
# For tic-tac-toe this means care more about making the best more each turn (closer to 0), or care more about winning (closer to 1)
# If too small the AI will not learn multistep strategies that take more than one turn to develop.
DECAY_GAMMA = 0.9

# The starting value for our exploration vs exploitation. For exploration the AI will choose a random valid move.
# For exploitation the AI will choose the move has a better change in eventually winning.
EXPLORATION_RATE = 1.0

# How much the exploration rate decreases each episode (games played). The new exploration rate is calculated by
# new_exploration = EXPLORATION_RATE * EXPLORATION_DECAY_RATE
# When training we should start by exploring a lot. Then over the duration of time explore less and less
EXPLORATION_DECAY_RATE = 0.99987

# The minimum probability the AI will choose to explore
MIN_EXPLORATION_RATE = 0.05

# Total number of training episodes. Each episode is one game complete game.
EPISODES = 25000

# How often to print training diagnostics to the console
TRAINING_DIAGNOSTICS_INTERVAL = 100

# ----------------------------------------------------------------------------------------------------------------------

# Graphics Constants
FRAME_RATE = 90
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 600
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

# Colors
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (255, 0, 0)
COLOR_YELLOW = (255, 255, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_ORANGE = (255, 94, 14)
COLOR_BLUE = (85, 152, 160)

PLAYER_1_COLOR = COLOR_YELLOW
PLAYER_2_COLOR = COLOR_RED

# Game Board
BOARD_CENTER_X = int(WINDOW_WIDTH / 2)
BOARD_CENTER_Y = int(WINDOW_HEIGHT / 2)

# Calculus Stuff
# Format: (LaTeX string, correct_answer, category)
# Categories: "sum", "radius", "interval"

Problems = [
    # ── SUMS ──────────────────────────────────────────────────────────────────
    (r"$\sum_{n=0}^{\infty} \left(\frac{1}{2}\right)^n$", 2, "sum"),
    (r"$\sum_{n=0}^{\infty} \left(\frac{1}{3}\right)^n$", Rational(3, 2), "sum"),
    (r"$\sum_{n=0}^{\infty} \left(\frac{2}{3}\right)^n$", 3, "sum"),
    (r"$\sum_{n=0}^{\infty} \frac{1}{4^n}$", Rational(4, 3), "sum"),
    (r"$\sum_{n=0}^{\infty} \frac{3}{5^n}$", Rational(15, 4), "sum"),
    (r"$\sum_{n=1}^{\infty} \frac{1}{n^2}$", pi**2 / 6, "sum"),
    (r"$\sum_{n=1}^{\infty} \frac{1}{n^4}$", pi**4 / 90, "sum"),
    (r"$\sum_{n=0}^{\infty} \frac{(-1)^n}{3^n}$", Rational(3, 4), "sum"),
    (r"$\sum_{n=0}^{\infty} \frac{2^n}{3^n}$", 3, "sum"),
    (r"$\sum_{n=1}^{\infty} \frac{4}{(n)(n+2)}$", 3, "sum"),
    (r"$\sum_{n=0}^{\infty} \left(\frac{1}{4}\right)^n$", Rational(4, 3), "sum"),
    (r"$\sum_{n=0}^{\infty} \left(\frac{3}{4}\right)^n$", 4, "sum"),
    (r"$\sum_{n=0}^{\infty} \left(\frac{1}{5}\right)^n$", Rational(5, 4), "sum"),
    (r"$\sum_{n=0}^{\infty} \left(\frac{2}{5}\right)^n$", Rational(5, 3), "sum"),
    (r"$\sum_{n=0}^{\infty} \left(\frac{3}{5}\right)^n$", Rational(5, 2), "sum"),
    (r"$\sum_{n=0}^{\infty} \left(\frac{4}{5}\right)^n$", 5, "sum"),
    (r"$\sum_{n=0}^{\infty} \frac{2}{3^n}$", 3, "sum"),
    (r"$\sum_{n=0}^{\infty} \frac{5}{4^n}$", Rational(20, 3), "sum"),
    (r"$\sum_{n=0}^{\infty} \frac{(-1)^n}{2^n}$", Rational(2, 3), "sum"),
    (r"$\sum_{n=0}^{\infty} \frac{(-1)^n}{4^n}$", Rational(4, 5), "sum"),
    (r"$\sum_{n=0}^{\infty} \frac{(-1)^n}{5^n}$", Rational(5, 6), "sum"),
    (r"$\sum_{n=0}^{\infty} \frac{3^n}{4^n}$", 4, "sum"),
    (r"$\sum_{n=0}^{\infty} \frac{2^n}{5^n}$", Rational(5, 3), "sum"),
    (r"$\sum_{n=0}^{\infty} \frac{4^n}{5^n}$", 5, "sum"),
    (r"$\sum_{n=1}^{\infty} \frac{2}{n(n+1)}$", 2, "sum"),
    (r"$\sum_{n=1}^{\infty} \frac{6}{n(n+2)}$", Rational(9, 2), "sum"),
    (r"$\sum_{n=1}^{\infty} \frac{1}{n(n+3)}$", Rational(11, 18), "sum"),
    (r"$\sum_{n=0}^{\infty} \frac{4}{5^n}$", 5, "sum"),
    (r"$\sum_{n=0}^{\infty} \frac{(-2)^n}{3^n}$", 3, "sum"),
    (r"$\sum_{n=1}^{\infty} \frac{1}{n^2 \pi^2} \cdot \pi^2$", Rational(1, 6), "sum"),
    (r"$\sum_{n=0}^{\infty} \frac{1}{2^n} + \frac{1}{3^n}$", Rational(7, 2), "sum"),
    (r"$\sum_{n=1}^{\infty} \frac{3}{n(n+1)}$", 3, "sum"),
    (r"$\sum_{n=0}^{\infty} \frac{(-1)^n}{3^n} \cdot 2$", Rational(3, 2), "sum"),
    (r"$\sum_{n=0}^{\infty} \left(\frac{1}{2}\right)^n + \left(\frac{1}{3}\right)^n$", Rational(7, 2), "sum"),

    # ── RADIUS OF CONVERGENCE ─────────────────────────────────────────────────
    (r"$\sum_{n=0}^{\infty} \frac{x^n}{n!}$", oo, "radius"),
    (r"$\sum_{n=0}^{\infty} n! \cdot x^n$", 0, "radius"),
    (r"$\sum_{n=0}^{\infty} x^n$", 1, "radius"),
    (r"$\sum_{n=1}^{\infty} \frac{x^n}{n}$", 1, "radius"),
    (r"$\sum_{n=0}^{\infty} \frac{x^n}{2^n}$", 2, "radius"),
    (r"$\sum_{n=0}^{\infty} \frac{(2x)^n}{n!}$", oo, "radius"),
    (r"$\sum_{n=1}^{\infty} \frac{n \cdot x^n}{3^n}$", 3, "radius"),
    (r"$\sum_{n=0}^{\infty} \frac{x^n}{n^2 + 1}$", 1, "radius"),
    (r"$\sum_{n=0}^{\infty} \frac{(-1)^n x^n}{4^n}$", 4, "radius"),
    (r"$\sum_{n=1}^{\infty} \frac{x^n}{\sqrt{n}}$", 1, "radius"),
    (r"$\sum_{n=0}^{\infty} \frac{3^n x^n}{n!}$", oo, "radius"),
    (r"$\sum_{n=1}^{\infty} \frac{n^2 x^n}{5^n}$", 5, "radius"),
    (r"$\sum_{n=0}^{\infty} \left(\frac{x}{3}\right)^n$", 3, "radius"),
    (r"$\sum_{n=1}^{\infty} \frac{x^n}{n \cdot 2^n}$", 2, "radius"),
    (r"$\sum_{n=0}^{\infty} \frac{x^n}{3^n}$", 3, "radius"),
    (r"$\sum_{n=0}^{\infty} \frac{x^n}{5^n}$", 5, "radius"),
    (r"$\sum_{n=1}^{\infty} \frac{x^n}{n \cdot 3^n}$", 3, "radius"),
    (r"$\sum_{n=1}^{\infty} \frac{x^n}{n \cdot 5^n}$", 5, "radius"),
    (r"$\sum_{n=0}^{\infty} \frac{(-1)^n x^n}{2^n}$", 2, "radius"),
    (r"$\sum_{n=0}^{\infty} \frac{(-1)^n x^n}{3^n}$", 3, "radius"),
    (r"$\sum_{n=1}^{\infty} \frac{n^2 x^n}{4^n}$", 4, "radius"),
    (r"$\sum_{n=1}^{\infty} \frac{n^3 x^n}{2^n}$", 2, "radius"),
    (r"$\sum_{n=0}^{\infty} \frac{x^n}{n^2 + 4}$", 1, "radius"),
    (r"$\sum_{n=0}^{\infty} \frac{2^n x^n}{n!}$", oo, "radius"),
    (r"$\sum_{n=0}^{\infty} \frac{4^n x^n}{n!}$", oo, "radius"),
    (r"$\sum_{n=0}^{\infty} (2n)! \cdot x^n$", 0, "radius"),
    (r"$\sum_{n=0}^{\infty} \frac{x^n}{\sqrt{n+1}}$", 1, "radius"),
    (r"$\sum_{n=1}^{\infty} \frac{(-1)^n x^n}{n^2}$", 1, "radius"),
    (r"$\sum_{n=0}^{\infty} \frac{x^n}{4^n}$", 4, "radius"),
    (r"$\sum_{n=1}^{\infty} \frac{x^n}{n \cdot 4^n}$", 4, "radius"),
    (r"$\sum_{n=0}^{\infty} \left(\frac{x}{5}\right)^n$", 5, "radius"),
    (r"$\sum_{n=0}^{\infty} \left(\frac{x}{4}\right)^n$", 4, "radius"),
    (r"$\sum_{n=1}^{\infty} \frac{n! \cdot x^n}{n^n}$", exp(1), "radius"),
    (r"$\sum_{n=0}^{\infty} \frac{x^{2n}}{n!}$", oo, "radius"),
    (r"$\sum_{n=1}^{\infty} \frac{x^n}{\ln(n+1)}$", 1, "radius"),
    (r"$\sum_{n=0}^{\infty} \frac{(-3)^n x^n}{n!}$", oo, "radius"),
    (r"$\sum_{n=1}^{\infty} \frac{x^n}{n^2 \cdot 3^n}$", 3, "radius"),
    (r"$\sum_{n=0}^{\infty} \frac{n^2 x^n}{3^n}$", 3, "radius"),

    # ── INTEGRALS ───────────────────────────────────────────────────────────
    (r"$\int_0^4 x \, dx$", 8, "integral"),
    (r"$\int_0^3 x^2 \, dx$", 9, "integral"),
    (r"$\int_1^3 (2x + 1) \, dx$", 10, "integral"),
    (r"$\int_0^2 (3x^2 + 1) \, dx$", 10, "integral"),
    (r"$\int_1^4 3x^2 \, dx$", 63, "integral"),
    (r"$\int_0^3 (4x + 2) \, dx$", 24, "integral"),
    (r"$\int_2^4 (2x - 1) \, dx$", 10, "integral"),
    (r"$\int_0^2 (x^3 + 2x) \, dx$", 8, "integral"),
    (r"$\int_0^4 (x^2 - 2x + 1) \, dx$", Rational(28, 3), "integral"),
    (r"$\int_0^2 6x^2 \, dx$", 16, "integral"),
    (r"$\int_1^4 (2x + 3) \, dx$", 24, "integral"),
    (r"$\int_0^3 (2x^2 - x) \, dx$", Rational(27, 2), "integral"),
    (r"$\int_2^5 3x^2 \, dx$", 117, "integral"),
    (r"$\int_0^4 (3x^2 - 4x + 2) \, dx$", 40, "integral"),
    (r"$\int_0^2 x^3 \, dx$", 4, "integral"),
    (r"$\int_0^3 2x \, dx$", 9, "integral"),
    (r"$\int_1^3 x^2 \, dx$", Rational(26, 3), "integral"),
    (r"$\int_0^4 2x + 3 \, dx$", 28, "integral"),
    (r"$\int_0^2 x^4 \, dx$", Rational(32, 5), "integral"),
    (r"$\int_1^2 x^3 \, dx$", Rational(15, 4), "integral"),
    (r"$\int_0^3 x^3 \, dx$", Rational(81, 4), "integral"),
    (r"$\int_0^5 x \, dx$", Rational(25, 2), "integral"),
    (r"$\int_0^4 x^2 \, dx$", Rational(64, 3), "integral"),
    (r"$\int_0^2 (x^2 + x) \, dx$", Rational(14, 3), "integral"),
    (r"$\int_1^4 (x + 2) \, dx$", Rational(21, 2), "integral"),
    (r"$\int_0^3 (x^2 + 2x) \, dx$", 18, "integral"),
    (r"$\int_0^2 (2x^2 + 3x) \, dx$", Rational(34, 3), "integral"),
    (r"$\int_1^3 (4x - 1) \, dx$", 14, "integral"),
    (r"$\int_0^4 (x^2 + 1) \, dx$", Rational(76, 3), "integral"),
    (r"$\int_0^2 (x^3 + x^2) \, dx$", Rational(28, 3), "integral"),
    (r"$\int_2^4 x^2 \, dx$", Rational(56, 3), "integral"),
    (r"$\int_0^3 (3x^2 + 2x) \, dx$", 36, "integral"),
    (r"$\int_1^2 (2x^2 + 1) \, dx$", Rational(17, 3), "integral"),
    (r"$\int_0^2 (4x^3 + 2x) \, dx$", 20, "integral"),
    (r"$\int_1^3 (x^3 + 1) \, dx$", 22, "integral"),
    (r"$\int_0^4 (2x + 1) \, dx$", 20, "integral"),
    (r"$\int_2^5 (x^2 - 1) \, dx$", 30, "integral"),
    (r"$\int_0^3 (x^2 - x) \, dx$", Rational(9, 2), "integral"),

    # ── L'HÔPITAL'S RULE ──────────────────────────────────────────────────────
    (r"$\lim_{x \to 0} \frac{\sin x}{x}$", 1, "lhopital"),
    (r"$\lim_{x \to 0} \frac{1 - \cos x}{x}$", 0, "lhopital"),
    (r"$\lim_{x \to 0} \frac{e^x - 1}{x}$", 1, "lhopital"),
    (r"$\lim_{x \to 0} \frac{\tan x}{x}$", 1, "lhopital"),
    (r"$\lim_{x \to \infty} \frac{\ln x}{x}$", 0, "lhopital"),
    (r"$\lim_{x \to \infty} \frac{x^2}{e^x}$", 0, "lhopital"),
    (r"$\lim_{x \to 0} \frac{x - \sin x}{x^3}$", Rational(1, 6), "lhopital"),
    (r"$\lim_{x \to 0} \frac{e^x - 1 - x}{x^2}$", Rational(1, 2), "lhopital"),
    (r"$\lim_{x \to 1} \frac{\ln x}{x - 1}$", 1, "lhopital"),
    (r"$\lim_{x \to 0} \frac{\sin 3x}{x}$", 3, "lhopital"),
    (r"$\lim_{x \to \infty} \frac{3x^2 + 1}{x^2 - 5}$", 3, "lhopital"),
    (r"$\lim_{x \to 0} \frac{1 - \cos x}{x^2}$", Rational(1, 2), "lhopital"),
    (r"$\lim_{x \to \infty} \frac{\ln x}{\sqrt{x}}$", 0, "lhopital"),
    (r"$\lim_{x \to 0} \frac{\sin x - x}{x^3}$", Rational(-1, 6), "lhopital"),
    (r"$\lim_{x \to 0} \frac{e^{2x} - 1}{x}$", 2, "lhopital"),
    (r"$\lim_{x \to \infty} \frac{x^3}{e^x}$", 0, "lhopital"),
    (r"$\lim_{x \to 0} \frac{\tan x - x}{x^3}$", Rational(1, 3), "lhopital"),
    (r"$\lim_{x \to 0} \frac{\sin 2x}{x}$", 2, "lhopital"),
    (r"$\lim_{x \to 0} \frac{\sin 5x}{x}$", 5, "lhopital"),
    (r"$\lim_{x \to 0} \frac{\tan 2x}{x}$", 2, "lhopital"),
    (r"$\lim_{x \to 0} \frac{e^{3x} - 1}{x}$", 3, "lhopital"),
    (r"$\lim_{x \to 0} \frac{e^{-x} - 1}{x}$", -1, "lhopital"),
    (r"$\lim_{x \to 0} \frac{1 - \cos 2x}{x^2}$", 2, "lhopital"),
    (r"$\lim_{x \to 0} \frac{\sin x^2}{x^2}$", 1, "lhopital"),
    (r"$\lim_{x \to \infty} \frac{2x^2}{e^x}$", 0, "lhopital"),
    (r"$\lim_{x \to \infty} \frac{x^3}{e^{2x}}$", 0, "lhopital"),
    (r"$\lim_{x \to \infty} \frac{\ln x}{x^2}$", 0, "lhopital"),
    (r"$\lim_{x \to 1} \frac{x^2 - 1}{x - 1}$", 2, "lhopital"),
    (r"$\lim_{x \to 2} \frac{x^2 - 4}{x - 2}$", 4, "lhopital"),
    (r"$\lim_{x \to 0} \frac{\ln(1 + x)}{x}$", 1, "lhopital"),
    (r"$\lim_{x \to 0} \frac{\ln(1 + 2x)}{x}$", 2, "lhopital"),
    (r"$\lim_{x \to \infty} \frac{5x^2 + 1}{2x^2 + 3}$", Rational(5, 2), "lhopital"),
    (r"$\lim_{x \to 0} \frac{\sin 4x}{\sin 2x}$", 2, "lhopital"),
    (r"$\lim_{x \to 0} \frac{x^2}{\sin^2 x}$", 1, "lhopital"),
    (r"$\lim_{x \to \infty} x \cdot e^{-x}$", 0, "lhopital"),
    (r"$\lim_{x \to 0^+} x \ln x$", 0, "lhopital"),
    (r"$\lim_{x \to 0} \frac{e^x - 1 - x - \frac{x^2}{2}}{x^3}$", Rational(1, 6), "lhopital"),
    (r"$\lim_{x \to 3} \frac{x^2 - 9}{x - 3}$", 6, "lhopital"),
    (r"$\lim_{x \to 0} \frac{\tan 3x}{\sin 3x}$", 1, "lhopital"),
    (r"$\lim_{x \to \infty} \frac{4x^3 + 1}{2x^3 - 5}$", 2, "lhopital"),
    (r"$\lim_{x \to 0} \frac{x - \tan x}{x^3}$", Rational(-1, 3), "lhopital"),

    # ── TAYLOR SERIES COEFFICIENTS ────────────────────────────────────────────
    (r"$e^x, \text{ coefficient of } x^3$", Rational(1, 6), "taylor"),
    (r"$e^x, \text{ coefficient of } x^4$", Rational(1, 24), "taylor"),
    (r"$\sin x, \text{ coefficient of } x^3$", Rational(-1, 6), "taylor"),
    (r"$\sin x, \text{ coefficient of } x^5$", Rational(1, 120), "taylor"),
    (r"$\cos x, \text{ coefficient of } x^2$", Rational(-1, 2), "taylor"),
    (r"$\cos x, \text{ coefficient of } x^4$", Rational(1, 24), "taylor"),
    (r"$\frac{1}{1-x}, \text{ coefficient of } x^5$", 1, "taylor"),
    (r"$\ln(1+x), \text{ coefficient of } x^3$", Rational(-1, 3), "taylor"),
    (r"$\ln(1+x), \text{ coefficient of } x^4$", Rational(1, 4), "taylor"),
    (r"$e^{2x}, \text{ coefficient of } x^3$", Rational(4, 3), "taylor"),
    (r"$e^{-x}, \text{ coefficient of } x^2$", Rational(1, 2), "taylor"),
    (r"$\sin x, \text{ coefficient of } x^7$", Rational(-1, 5040), "taylor"),
    (r"$\cos x, \text{ coefficient of } x^6$", Rational(-1, 720), "taylor"),
    (r"$\frac{1}{1+x}, \text{ coefficient of } x^4$", 1, "taylor"),
    (r"$e^x, \text{ coefficient of } x^5$", Rational(1, 120), "taylor"),
    (r"$\ln(1+x), \text{ coefficient of } x^2$", Rational(-1, 2), "taylor"),
    (r"$e^{3x}, \text{ coefficient of } x^2$", Rational(9, 2), "taylor"),
    (r"$e^{-x}, \text{ coefficient of } x^3$", Rational(-1, 6), "taylor"),
    (r"$e^{-2x}, \text{ coefficient of } x^2$", 2, "taylor"),
    (r"$\sin 2x, \text{ coefficient of } x^3$", Rational(-4, 3), "taylor"),
    (r"$\cos 2x, \text{ coefficient of } x^2$", -2, "taylor"),
    (r"$\cos 3x, \text{ coefficient of } x^2$", Rational(-9, 2), "taylor"),
    (r"$\sin 3x, \text{ coefficient of } x^3$", Rational(-9, 2), "taylor"),
    (r"$\ln(1 + 2x), \text{ coefficient of } x^2$", -2, "taylor"),
    (r"$\ln(1 + 3x), \text{ coefficient of } x^2$", Rational(-9, 2), "taylor"),
    (r"$\frac{1}{1-2x}, \text{ coefficient of } x^3$", 8, "taylor"),
    (r"$\frac{1}{1+2x}, \text{ coefficient of } x^3$", -8, "taylor"),
    (r"$\frac{1}{1-3x}, \text{ coefficient of } x^2$", 9, "taylor"),
    (r"$e^{x^2}, \text{ coefficient of } x^4$", Rational(1, 2), "taylor"),
    (r"$\sin x^2, \text{ coefficient of } x^6$", Rational(-1, 6), "taylor"),
    (r"$\cos x^2, \text{ coefficient of } x^4$", Rational(-1, 2), "taylor"),
    (r"$e^{2x}, \text{ coefficient of } x^2$", 2, "taylor"),
    (r"$e^{2x}, \text{ coefficient of } x^4$", Rational(2, 3), "taylor"),
    (r"$\ln(1-x), \text{ coefficient of } x^3$", Rational(-1, 3), "taylor"),
    (r"$\ln(1-x), \text{ coefficient of } x^2$", Rational(-1, 2), "taylor"),
    (r"$\frac{1}{1+x^2}, \text{ coefficient of } x^4$", 1, "taylor"),
    (r"$\sin x, \text{ coefficient of } x^9$", Rational(1, 362880), "taylor"),
    (r"$\cos x, \text{ coefficient of } x^8$", Rational(1, 40320), "taylor"),
    (r"$e^{-x^2}, \text{ coefficient of } x^4$", Rational(1, 2), "taylor"),
    (r"$\frac{1}{1-x^2}, \text{ coefficient of } x^4$", 1, "taylor"),

    # ── INTEGRATION BY PARTS ──────────────────────────────────────────────────
    (r"$\int_0^1 x e^x \, dx$", 1, "ibp"),
    (r"$\int_0^1 x e^{2x} \, dx$", Rational(1, 4) * (exp(2) + 1), "ibp"),
    (r"$\int_1^e \ln x \, dx$", 1, "ibp"),
    (r"$\int_0^{\pi} x \sin x \, dx$", pi, "ibp"),
    (r"$\int_0^{\pi/2} x \cos x \, dx$", -1 + pi/2, "ibp"),
    (r"$\int_0^1 x^2 e^x \, dx$", -2 + exp(1), "ibp"),
    (r"$\int_1^e x \ln x \, dx$", Rational(1, 4) * (exp(2) + 1), "ibp"),
    (r"$\int_0^{\pi} x \cos x \, dx$", -2, "ibp"),
    (r"$\int_0^1 \ln(x + 1) \, dx$", -1 + ln(2), "ibp"),
    (r"$\int_0^2 x e^x \, dx$", exp(2) + 1, "ibp"),
    (r"$\int_0^{\pi/2} x \sin x \, dx$", 1, "ibp"),
    (r"$\int_1^e \ln x^2 \, dx$", 2, "ibp"),
    (r"$\int_0^1 x^2 \ln(x+1) \, dx$", Rational(-1,9) + ln(2)/3 + Rational(1, 3)*ln(2), "ibp"),
    (r"$\int_0^{\pi} x^2 \cos x \, dx$", -4, "ibp"),
    (r"$\int_0^1 x \ln(x+1) \, dx$", Rational(1,4) * (2*ln(2) - 1), "ibp"),
    (r"$\int_0^1 x e^{3x} \, dx$", Rational(1, 9) * (2 * exp(3) + 1), "ibp"),
    (r"$\int_0^{\pi} x \sin 2x \, dx$", Rational(-1, 2) * pi, "ibp"),
    (r"$\int_0^{\pi/2} x \cos 2x \, dx$", Rational(-1, 4), "ibp"),
    (r"$\int_1^e x^2 \ln x \, dx$", Rational(1, 9) * (2 * exp(3) + 1), "ibp"),
    (r"$\int_0^1 x^2 e^{-x} \, dx$", 2 - 5 / exp(1), "ibp"),
    (r"$\int_0^2 x^2 e^x \, dx$", 2 * exp(2) - 2, "ibp"),
    (r"$\int_1^e \ln x^3 \, dx$", 3, "ibp"),
    (r"$\int_0^{\pi} x^2 \sin x \, dx$", pi**2 - 4, "ibp"),
    (r"$\int_0^1 x e^{-x} \, dx$", 1 - 2 / exp(1), "ibp"),
    (r"$\int_0^{\pi/2} x^2 \sin x \, dx$", pi**2 / 4 - 2, "ibp"),
    (r"$\int_1^e \frac{\ln x}{x^2} \, dx$", 1 - 2 / exp(1), "ibp"),
    (r"$\int_0^1 x^3 e^x \, dx$", 6 - 2 * exp(1), "ibp"),
    (r"$\int_0^{\pi} x \cos 2x \, dx$", 0, "ibp"),
    (r"$\int_1^2 x \ln x \, dx$", 2 * ln(2) - Rational(3, 4), "ibp"),
    (r"$\int_0^1 \arctan x \, dx$", pi / 4 - ln(2) / 2, "ibp"),
    (r"$\int_0^1 x^2 \ln x \, dx$", Rational(-1, 9), "ibp"),
    (r"$\int_0^{\pi/2} x \sin 2x \, dx$", Rational(1, 4), "ibp"),
    (r"$\int_0^2 x \ln(x+1) \, dx$", 2 * ln(3) - 1, "ibp"),
    (r"$\int_0^1 e^x \sin x \, dx$", Rational(1, 2) * (exp(1) * sin(1) - exp(1) * cos(1) + 1), "ibp"),
    (r"$\int_0^{\pi/4} x \sec^2 x \, dx$", pi / 4 - ln(2) / 2, "ibp"),
    (r"$\int_0^1 x^3 \ln x \, dx$", Rational(-1, 16), "ibp"),

    # ── PARAMETRIC DERIVATIVES ────────────────────────────────────────────────
    (r"$x = t^2,\ y = t^3,\ \text{find } \frac{dy}{dx} \text{ at } t=2$", 3, "parametric"),
    (r"$x = t^2,\ y = t^3,\ \text{find } \frac{dy}{dx} \text{ at } t=1$", Rational(3, 2), "parametric"),
    (r"$x = \cos t,\ y = \sin t,\ \text{find } \frac{dy}{dx} \text{ at } t=0$", 0, "parametric"),
    (r"$x = e^t,\ y = e^{2t},\ \text{find } \frac{dy}{dx} \text{ at } t=0$", 2, "parametric"),
    (r"$x = t^2 + 1,\ y = 2t,\ \text{find } \frac{dy}{dx} \text{ at } t=2$", 1, "parametric"),
    (r"$x = \sin t,\ y = \cos t,\ \text{find } \frac{dy}{dx} \text{ at } t=0$", 0, "parametric"),
    (r"$x = t^3,\ y = t^2,\ \text{find } \frac{dy}{dx} \text{ at } t=3$", Rational(2, 9), "parametric"),
    (r"$x = 2t,\ y = t^2 - 1,\ \text{find } \frac{dy}{dx} \text{ at } t=3$", 3, "parametric"),
    (r"$x = \ln t,\ y = t^2,\ \text{find } \frac{dy}{dx} \text{ at } t=1$", 2, "parametric"),
    (r"$x = t^2,\ y = 4t,\ \text{find } \frac{dy}{dx} \text{ at } t=2$", 1, "parametric"),
    (r"$x = e^t,\ y = t^2,\ \text{find } \frac{dy}{dx} \text{ at } t=1$", 2 / exp(1), "parametric"),
    (r"$x = \cos t,\ y = \sin t,\ \text{find } \frac{dy}{dx} \text{ at } t = \frac{\pi}{4}$", -1, "parametric"),
    (r"$x = t^2 - t,\ y = t^3,\ \text{find } \frac{dy}{dx} \text{ at } t=2$", 4, "parametric"),
    (r"$x = 3t^2,\ y = 2t^3,\ \text{find } \frac{dy}{dx} \text{ at } t=1$", 1, "parametric"),
    (r"$x = t + 1,\ y = t^2 + t,\ \text{find } \frac{dy}{dx} \text{ at } t=2$", 5, "parametric"),
    (r"$x = \sin 2t,\ y = \cos t,\ \text{find } \frac{dy}{dx} \text{ at } t=0$", 0, "parametric"),
    (r"$x = t^3,\ y = t^2,\ \text{find } \frac{dy}{dx} \text{ at } t=1$", Rational(2, 3), "parametric"),
    (r"$x = t^2,\ y = t^4,\ \text{find } \frac{dy}{dx} \text{ at } t=2$", 4, "parametric"),
    (r"$x = 2t^2,\ y = 4t,\ \text{find } \frac{dy}{dx} \text{ at } t=1$", 1, "parametric"),
    (r"$x = t^3 + t,\ y = t^2,\ \text{find } \frac{dy}{dx} \text{ at } t=1$", Rational(1, 2), "parametric"),
    (r"$x = e^{2t},\ y = e^t,\ \text{find } \frac{dy}{dx} \text{ at } t=0$", Rational(1, 2), "parametric"),
    (r"$x = \sin t,\ y = \cos 2t,\ \text{find } \frac{dy}{dx} \text{ at } t=0$", 0, "parametric"),
    (r"$x = t^2 + 2t,\ y = t^3,\ \text{find } \frac{dy}{dx} \text{ at } t=2$", 2, "parametric"),
    (r"$x = \cos 2t,\ y = \sin t,\ \text{find } \frac{dy}{dx} \text{ at } t = \frac{\pi}{6}$", Rational(-1, 2), "parametric"),
    (r"$x = 3t^2,\ y = t^3 - t,\ \text{find } \frac{dy}{dx} \text{ at } t=2$", Rational(11, 12), "parametric"),
    (r"$x = t^2,\ y = 2t^3,\ \text{find } \frac{dy}{dx} \text{ at } t=1$", 3, "parametric"),
    (r"$x = \ln t,\ y = t^3,\ \text{find } \frac{dy}{dx} \text{ at } t=1$", 3, "parametric"),
    (r"$x = e^t,\ y = e^{3t},\ \text{find } \frac{dy}{dx} \text{ at } t=0$", 3, "parametric"),
    (r"$x = 4t,\ y = t^2 + 1,\ \text{find } \frac{dy}{dx} \text{ at } t=2$", 1, "parametric"),
    (r"$x = t^3 - t,\ y = t^2 + 1,\ \text{find } \frac{dy}{dx} \text{ at } t=2$", Rational(4, 11), "parametric"),
    (r"$x = \sin 2t,\ y = \cos t,\ \text{find } \frac{dy}{dx} \text{ at } t = \frac{\pi}{6}$", Rational(-1, 2), "parametric"),
    (r"$x = t^2 - 1,\ y = t^3 + t,\ \text{find } \frac{dy}{dx} \text{ at } t=1$", 2, "parametric"),
    (r"$x = 2\cos t,\ y = 3\sin t,\ \text{find } \frac{dy}{dx} \text{ at } t = \frac{\pi}{4}$", Rational(-3, 2), "parametric"),
    (r"$x = t^4,\ y = t^3,\ \text{find } \frac{dy}{dx} \text{ at } t=2$", Rational(3, 8), "parametric"),
    (r"$x = e^t + 1,\ y = e^{2t},\ \text{find } \frac{dy}{dx} \text{ at } t=0$", 2, "parametric"),
    (r"$x = \cos t,\ y = \cos 2t,\ \text{find } \frac{dy}{dx} \text{ at } t = \frac{\pi}{3}$", 2, "parametric"),
    (r"$x = t^2 + t,\ y = t^3 - t,\ \text{find } \frac{dy}{dx} \text{ at } t=2$", 2, "parametric"),
    (r"$x = 3\sin t,\ y = 4\cos t,\ \text{find } \frac{dy}{dx} \text{ at } t = \frac{\pi}{6}$", Rational(-8, 3) * sqrt(3), "parametric"),
    (r"$x = \ln(t+1),\ y = t^2,\ \text{find } \frac{dy}{dx} \text{ at } t=1$", 4, "parametric"),
    (r"$x = t^3,\ y = t^3 + t,\ \text{find } \frac{dy}{dx} \text{ at } t=1$", Rational(4, 3), "parametric"),
]