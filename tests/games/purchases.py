"""A stand-in game for the bench tests: the trail's five purchase questions, then five choices.

The questions carry the words the trail's parser keys on, so a policy that reads the prompt sees
a purchase. It shares nothing else with the real game.
"""

for ask in ("OXEN TEAM", "FOOD", "AMMUNITION", "CLOTHING", "MISCELLANEOUS SUPPLIES"):
    input(f"\nHOW MUCH DO YOU WANT TO SPEND ON {ask}: ")
for day in range(1, 6):
    input(f"\nDAY {day}.\nDO YOU WANT TO EAT (1) THINLY (2) FAIRLY (3) RICHLY: ")
print("\nDONE.")
