import traceback

import pa4, pa4sol
import random
import math
from util import format_points, test_passed

S = {2 + 2j, 3 + 2j, 1.75 + 1j, 2 + 1j, 2.25 + 1j, 2.5 + 1j, 2.75 + 1j, 3 + 1j, 3.25 + 1j}


def TestCase():
    parts = [3, 4, 6, 12]
    d = parts[random.randint(0, len(parts) - 1)]
    k = 2 * random.randint(1, 5) + 1
    while math.gcd(k, d) > 1:
        parts = [3, 4, 6, 12]
        d = parts[random.randint(0, len(parts) - 1)]
        k = 2 * random.randint(1, 5) + 1

    tau = k * (math.pi / d)

    msg = f"Created set S = {S}.\n\nRotating by {k}pi/{d} radians."
    try:
        Ans = pa4sol.rotate(S, tau)
        Stud = pa4.rotate(S, tau)
        msg += f"\nOutput:\n"
        msg += format_points(Stud, 2)
        msg += f"\nExpected:\n"
        msg += format_points(Ans, 2)

        if test_passed(Ans, Stud):
            msg += "\n\nTest passed."
            return True, msg
        else:
            msg += "\n\nTest failed."
            return False, msg
    except Exception as e:
        msg += f"\nThe following unexpected error was raised:\n"
        msg += str(traceback.format_exc())
        msg += f"\n\nTest failed."
        return False, msg