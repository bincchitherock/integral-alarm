#!/usr/bin/env python3

import sys
import os
import math
import wave
import struct
import random
import threading
import tempfile
import platform
import subprocess
import time


def generate_alarm_wav(filepath):
    sample_rate = 44100
    frequency = 880.0
    amplitude = 0.8
    beep_dur = 0.3
    silence_dur = 0.15
    num_cycles = 12

    samples = []
    for _ in range(num_cycles):
        num_beep = int(sample_rate * beep_dur)
        for i in range(num_beep):
            t = i / sample_rate
            value = amplitude * math.sin(2 * math.pi * frequency * t)
            samples.append(int(value * 32767))
        num_silence = int(sample_rate * silence_dur)
        samples.extend([0] * num_silence)

    with wave.open(filepath, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        raw_data = struct.pack('<' + 'h' * len(samples), *samples)
        wf.writeframes(raw_data)


class AlarmPlayer:
    def __init__(self, wav_path):
        self.wav_path = wav_path
        self._stop_event = threading.Event()
        self._thread = None
        self._current_process = None

    def _play_command(self):
        system = platform.system()
        if system == "Darwin":
            return ["afplay", self.wav_path]
        elif system == "Linux":
            return ["aplay", "-q", self.wav_path]
        elif system == "Windows":
            ps_cmd = f'(New-Object Media.SoundPlayer "{self.wav_path}").PlaySync()'
            return ["powershell", "-Command", ps_cmd]
        return []

    def _loop(self):
        cmd = self._play_command()
        if not cmd:
            while not self._stop_event.is_set():
                print("\a", end="", flush=True)
                time.sleep(0.5)
            return
        while not self._stop_event.is_set():
            try:
                self._current_process = subprocess.Popen(
                    cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
                self._current_process.wait()
            except Exception:
                print("\a", end="", flush=True)
                time.sleep(0.5)

    def start(self):
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        if self._current_process:
            try:
                self._current_process.terminate()
            except Exception:
                pass


def get_templates(difficulty):
    from sympy import Symbol, sin, cos, exp, sqrt, log, pi, Rational

    x = Symbol('x')

    hard = [
        {
            "expr": lambda a, b: (a * x + b) / (x**2 + 1),
            "bounds": (0, 1),
            "params": lambda: (random.choice([1, 2, 3]), random.choice([1, 2, -1])),
        },
        {
            "expr": lambda a, b: a / sqrt(b - x**2),
            "bounds": (0, 1),
            "params": lambda: (random.choice([1, 2]), random.choice([4, 9])),
        },
        {
            "expr": lambda a, b: a * x * sin(b * x),
            "bounds": (0, pi),
            "params": lambda: (random.choice([1, 2]), random.choice([1, 2])),
        },
        {
            "expr": lambda a, b: a * sin(x)**2 + b * cos(x),
            "bounds": (0, pi),
            "params": lambda: (random.choice([1, 2, 3]), random.choice([1, -1, 2])),
        },
    ]

    medium = [
        {
            "expr": lambda a, b: (a * x + b) * exp(-x),
            "bounds": (0, 3),
            "params": lambda: (random.choice([1, 2]), random.choice([1, -1, 3])),
        },
        {
            "expr": lambda a, b: a * log(x) + b * x,
            "bounds": (1, Rational(5, 2)),
            "params": lambda: (random.choice([1, 2, -1]), random.choice([1, 2])),
        },
        {
            "expr": lambda a, b: a * sin(x) * cos(x)**b,
            "bounds": (0, pi / 2),
            "params": lambda: (random.choice([1, 2, 3]), random.choice([2, 3])),
        },
    ]

    easy = [
        {
            "expr": lambda a, b: a * x**3 + b * x**2 - x + 2,
            "bounds": (0, 2),
            "params": lambda: (random.choice([1, 2, -1]), random.choice([3, -2, 1])),
        },
        {
            "expr": lambda a, b: a * x**2 + b,
            "bounds": (0, 3),
            "params": lambda: (random.choice([1, 2, -1]), random.choice([1, 3, 5])),
        },
        {
            "expr": lambda a, b: a * exp(b * x),
            "bounds": (0, 1),
            "params": lambda: (random.choice([1, 2]), random.choice([1, -1, 2])),
        },
    ]

    tiers = {"hard": hard, "medium": medium, "easy": easy}
    return tiers[difficulty]


def generate_integral(difficulty):
    from sympy import Symbol, integrate, simplify

    x = Symbol('x')
    templates = get_templates(difficulty)

    template = random.choice(templates)
    params = template["params"]()
    integrand = template["expr"](*params)
    lower, upper = template["bounds"]

    answer = simplify(integrate(integrand, (x, lower, upper)))

    display = (
        f"\n"
        f"   [{difficulty.upper()}] Evaluate the definite integral:\n"
        f"\n"
        f"     {upper}\n"
        f"    S   ({integrand}) dx\n"
        f"     {lower}\n"
    )

    return display, answer


def check_answer(user_input, correct_answer):
    from sympy import sympify, N

    user_input = user_input.strip()
    if not user_input:
        return False

    try:
        user_expr = sympify(user_input)
        diff = correct_answer - user_expr
        if diff.equals(0):
            return True
        if abs(complex(N(diff))) < 1e-4:
            return True
    except Exception:
        pass

    try:
        safe_input = user_input.replace("^", "**")
        val = float(eval(safe_input, {"__builtins__": {}}, {
            "pi": math.pi, "e": math.e, "exp": math.exp,
            "log": math.log, "ln": math.log,
            "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos,
        }))
        correct_float = float(N(correct_answer))
        if abs(val - correct_float) < 1e-3:
            return True
    except Exception:
        pass

    return False


def main():
    print("=" * 60)
    print("           INTEGRAL ALARM CLOCK")
    print("=" * 60)
    print()
    print("  The alarm is about to start.")
    print("  Solve the integral to silence it!")
    print("  Type your answer as a number, fraction, or expression.")
    print("  Examples: 3/4, pi/2, 2*exp(-3)+1, 0.785")
    print("  3 wrong attempts drops you to an easier problem.")
    print()

    try:
        import sympy
    except ImportError:
        print("ERROR: SymPy is required.  Install it with:")
        print("  pip install sympy")
        sys.exit(1)

    tiers = ["hard", "medium", "easy"]
    tier_index = 0
    difficulty = tiers[tier_index]

    display, answer = generate_integral(difficulty)

    tmp_dir = tempfile.mkdtemp()
    wav_path = os.path.join(tmp_dir, "alarm.wav")
    generate_alarm_wav(wav_path)

    player = AlarmPlayer(wav_path)
    player.start()

    print("-" * 60)
    print(display)
    print("-" * 60)

    from sympy import N

    total_attempts = 0
    attempts_this_problem = 0

    while True:
        total_attempts += 1
        attempts_this_problem += 1
        try:
            user_input = input(f"\n  Attempt #{total_attempts} -- Your answer: ")
        except (EOFError, KeyboardInterrupt):
            print(f"\n\n  Giving up? The answer was: {answer}")
            player.stop()
            break

        if check_answer(user_input, answer):
            player.stop()
            print()
            print("  CORRECT! The alarm is silenced.")
            print(f"  The exact answer was: {answer}  ~ {float(N(answer)):.6f}")
            print(f"  Solved in {total_attempts} total attempt(s) at {difficulty} difficulty.")
            print()
            break
        else:
            print("  WRONG! The alarm continues...")

            if attempts_this_problem >= 3 and difficulty != "easy":
                tier_index += 1
                difficulty = tiers[tier_index]
                print(f"\n  Dropping down to {difficulty.upper()}. Here's a new problem:")
                print(f"  (The old answer was: {answer}  ~ {float(N(answer)):.6f})")

                display, answer = generate_integral(difficulty)
                attempts_this_problem = 0

                print("-" * 60)
                print(display)
                print("-" * 60)
            else:
                remaining = 3 - attempts_this_problem
                if difficulty != "easy" and remaining > 0:
                    print(f"  {remaining} more wrong and it gets easier.")

    try:
        os.remove(wav_path)
        os.rmdir(tmp_dir)
    except Exception:
        pass


if __name__ == "__main__":
    main()
