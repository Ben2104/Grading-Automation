import traceback

import pa4
import pa4sol
import random

S = {2 + 2j, 3 + 2j, 1.75 + 1j, 2 + 1j, 2.25 + 1j, 2.5 + 1j, 2.75 + 1j, 3 + 1j, 3.25 + 1j}


def TestCase():
    alpha = random.randint(-5, -1)

    msg = f"Created set S = {S}.\n\nScaling by {alpha}."
    try:
        expected = pa4sol.scale(S, alpha)
        student_out = pa4.scale(S, alpha)
        msg += f"\nOutput: {student_out}"
        msg += f"\nExpected: ValueError"
        msg += "\n\nTest failed."
        return False, msg
    except ValueError:
        msg += f"\nOutput: ValueError"
        msg += f"\nExpected: ValueError"
        msg += "\n\nTest passed."
        return True, msg
    except Exception as e:
        msg += f"\nThe following unexpected error was raised:\n"
        msg += str(traceback.format_exc())
        msg += f"\n\nTest failed."
        return False, msg



