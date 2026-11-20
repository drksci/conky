"""A short trail game for the tests: five stretches, numbered choices, no randomness.

Reads one line per choice from standard input and prints to standard output. Supplies and days
change by fixed amounts, so the same choices always give the same journey.
"""

import sys

ROAD = [
    ("Push on", -4, 3, "The wagon keeps moving and so does everyone's temper."),
    ("Rest a day", -2, 1, "Nobody argues with a day off. The oxen certainly do not."),
    ("Hunt", 3, 2, "Two rabbits and a long walk. The party calls it a feast."),
]
RIVER = [
    ("Ford the river", -5, 1, "The wagon crosses. One sack of flour does not."),
    ("Wait for the water to drop", -3, 3, "Three days on the bank, and the river has not noticed."),
    ("Hunt along the bank", 3, 2, "The river has fish. The party has opinions about them."),
]
STRETCHES = [
    ("The farm road", "Fences, fields and a dog that follows the wagon for a mile.", ROAD),
    ("The dry hills", "The road climbs. The water barrel does not.", ROAD),
    ("The wide river", "Brown, fast and wider than the map claimed.", RIVER),
    ("The salt flats", "Flat, white and without a single tree to complain under.", ROAD),
    ("The high pass", "Cold wind, thin air and the last hill of the journey.", ROAD),
]


def choose(options):
    """Show the options and return the one the player picks, asking again on a bad answer."""
    for number, (label, *_rest) in enumerate(options, 1):
        print(f"  {number}. {label}")
    while True:
        print("> ", end="", flush=True)
        line = sys.stdin.readline()
        if not line:
            sys.exit(0)
        if line.strip().isdigit() and 1 <= int(line) <= len(options):
            return options[int(line) - 1]
        print("That is not one of the choices.")


def mood(supplies):
    """Return a few words on how the party feels about the supplies."""
    if supplies <= 0:
        return "hungry"
    if supplies < 12:
        return "careful"
    return "comfortable"


def verdict(supplies, days):
    """Return one dry sentence on how the party fared."""
    if supplies <= 0:
        return "The party arrived hungry, and made sure everyone heard about it."
    if days > 15:
        return "The party arrived late but fed, which is the better way round."
    return "The party arrived on time and fed. The oxen expect a raise."


def main():
    supplies, days = 30, 0
    journal = []
    print("THE LONG ROAD WEST")
    print("A wagon, four people, thirty sacks of supplies and five stretches of road.")
    for number, (name, scene, options) in enumerate(STRETCHES, 1):
        print()
        print(f"Stretch {number} of 5: {name}. {scene}")
        print(f"Day {days}, supplies {supplies}. The party is {mood(supplies)}.")
        label, cost, time_taken, remark = choose(options)
        supplies = max(0, supplies + cost)
        days += time_taken
        journal.append(label.lower())
        print(f"{label}. {remark}")
    print()
    print(f"Journey's end. {days} days on the road, {supplies} sacks of supplies left.")
    print(verdict(supplies, days))
    print("The journal reads: " + ", ".join(journal) + ".")


main()
