import traceback

import pa4, pa4sol
import random
from util import format_points, test_passed

S = {2 + 2j, 3 + 2j, 1.75 + 1j, 2 + 1j, 2.25 + 1j, 2.5 + 1j, 2.75 + 1j, 3 + 1j, 3.25 + 1j}

def TestCase():
    a = random.randint(1, 10)
    b = random.randint(1, 10)
    z0 = a + b * 1j

    msg = f"Created set S = {S}.\n\nTranslating by {z0}."
    try:
        Ans = pa4sol.translate(S, z0)
        Stud = pa4.translate(S, z0)
        msg += f"\nOutput:\n"
        msg += format_points(Stud, 3)
        msg += f"\nExpected:\n"
        msg += format_points(Ans, 3)
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