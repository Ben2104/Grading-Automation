import traceback

import pa4
import pa4sol
from util import format_points, test_passed

S = {2 + 2j, 3 + 2j, 1.75 + 1j, 2 + 1j, 2.25 + 1j, 2.5 + 1j, 2.75 + 1j, 3 + 1j, 3.25 + 1j}


def TestCase():
    tau = 0

    msg = f"Created set S = {S}.\n\nRotating by {tau} radians."
    try:
        expected = pa4sol.rotate(S, tau)
        student_out = pa4.rotate(S, tau)
        msg += f"\nOutput:\n"
        msg += format_points(student_out, 2)
        msg += f"\nExpected:\n"
        msg += format_points(expected, 2)

        if test_passed(expected, student_out):
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


