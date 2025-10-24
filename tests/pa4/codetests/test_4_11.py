import traceback

import pa4
import random


def TestCase():
    n = random.randint(4, 7)
    u_elements = [random.randint(-20, 20) for i in range(n)]
    v_elements = [random.randint(-20, 20) for i in range(n - 2)]

    msg = f"Created Vec u = {u_elements}.\nCreated Vec v = {v_elements}.\n\nTesting u * v:"
    try:
        student_u = pa4.Vec(u_elements)
        student_v = pa4.Vec(v_elements)
        student_ans = student_u * student_v
        msg += f"\nOutput: {student_ans}"
        msg += f"\nExpected: Error"
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

