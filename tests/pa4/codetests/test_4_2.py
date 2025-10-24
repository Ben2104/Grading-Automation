import traceback

import pa4, pa4sol
import random


def TestCase():
    n = random.randint(4, 7)
    u_elements = [random.randint(-20, 20) for i in range(n)]
    v_elements = [random.randint(-20, 20) for i in range(n)]

    msg = f"Created Vec u = {u_elements}.\nCreated Vec v = {v_elements}\n\nTesting u + v:"
    try:
        student_u = pa4.Vec(u_elements)
        student_v = pa4.Vec(v_elements)

        u = pa4sol.Vec(u_elements.copy())
        v = pa4sol.Vec(v_elements.copy())

        student_ans = student_u + student_v
        ans = u + v
        msg += f"\nOutput: {student_ans}"
        msg += f"\nExpected: {ans}"

        if student_ans.elements != ans.elements:
            msg += "\n\nTest failed."
            return False, msg
        elif student_u is student_ans or student_v is student_ans:
            msg += "\nAddition operator modifies an original vector rather than creating a new resultant vector."
            msg += "\n\nTest failed."
            return False, msg
        else:
            msg += "\n\nTest passed."
            return True, msg

    except Exception as e:
        msg += f"\nThe following unexpected error was raised:\n"
        msg += str(traceback.format_exc())
        msg += f"\n\nTest failed."
        return False, msg


