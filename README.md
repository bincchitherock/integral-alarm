# integral_alarm

idea that came to me while watching the MIT integration bee. i made this public because i wanted to send this to my dad to get him to do integrals, but it isn't polished just yet. 

## how it works

the program generates a beeping alarm tone from raw sine-wave samples and loops it in a background thread. meanwhile, it picks a random integral from a set of parameterized templates and uses SymPy to find the exact symbolic answer like a cas system akin to wolfram alpha. you'll be able to type your answer in any form -- exact (`pi/4`), decimal (`0.785`), or expression (`2*exp(-3)+1`) -- all work! the alarm only stops when you get it right.

## difficulty tiers (for tiered_integral_alarm.py)

problems will start at hard and drop down after 3 wrong attempts per tier.

| tier   | techniques                                              |
|--------|---------------------------------------------------------|
| hard   | partial fractions, trig substitution, by parts with trig, half-angle identities |
| medium | exponential by parts, log integrals, trig u-substitution |
| easy   | power rule, basic quadratics, simple exponentials        |

when you drop a tier, the old answer is revealed and a new problem is generated.

## reqs.

- Python 3.7+
- [SymPy](https://www.sympy.org/)

```
pip install sympy
```

Audio playback should use OS's native player (`afplay` on macOS, `aplay` on Linux, PowerShell on Windows). No additional audio libraries are needed.

## project structure

- **audio generation** -- builds a WAV file from raw sine-wave math using the `wave` module.
- **alarm playback** -- loops the WAV on a daemon thread with a shared stop-flag.
- **integral generation** -- picks a template, randomizes coefficients, and solves via `integrate()` + `simplify()`.
- **answer checking** -- compares user input against the exact answer both symbolically and numerically.

## Extending

to add new integrals. each template is a dictionary with three keys:

```python
{
    "expr": lambda a, b: a * x * cos(b * x),   # the integrand
    "bounds": (0, pi),                           # limits of integration
    "params": lambda: (random.choice([1, 2]), random.choice([1, 3])),  # coefficient pools
}
```

just append it to the appropriate tier list in `get_templates()` and you're done.
