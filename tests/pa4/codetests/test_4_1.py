import traceback

import pa4, pa4sol
import random


def TestCase():
    n = random.randint(4, 7)
    elements = [random.randint(-20, 20) for i in range(n)]
    try:
        student_vec = pa4.Vec(elements)
        answer_vec = pa4sol.Vec(elements)
        msg = f"Created Vec: {student_vec}.\n\nTesting abs({student_vec})"

        student_ans = abs(student_vec)
        ans = abs(answer_vec)
        msg += f"\nOutput: {round(student_ans, 2)}"
        msg += f"\nExpected: {round(ans, 2)}"

        if (student_ans == ans):
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

