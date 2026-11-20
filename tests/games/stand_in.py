"""A stand-in game for the bench tests: five questions answered with a number, read by input().

It shares nothing with any real game but its shape: a status line, a question, a number typed.
"""

import random

stock = 20
for day in range(1, 6):
    print(f"\nDAY {day}. STOCK {stock}.")
    choice = int(input("PICK (1) WALK OR (2) REST: "))
    stock -= 3 if choice == 1 else 1
    stock += random.randint(0, 2)
print(f"\nDONE WITH STOCK {stock}.")
