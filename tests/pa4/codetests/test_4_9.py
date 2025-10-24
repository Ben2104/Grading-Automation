import traceback

import pa4, pa4sol
import random


def TestCase():
    n = random.randint(4, 7)
    elements = [random.randint(-20, 20) for i in range(n)]
    alpha = round(random.uniform(0.2, 0.99), 2)
    while abs(alpha) == 1 or alpha == 0:
        alpha = random.randint(-5, 5)
    msg = f"Created Vec: {elements}.\n\nTesting v * {alpha}:"

    try:
        student_vec = pa4.Vec(elements.copy())
        ans_vec = pa4sol.Vec(elements.copy())

        student_ans = student_vec * alpha
        ans = ans_vec * alpha

        student_ans_lst = [round(x, 2) for x in student_ans.elements]
        ans_lst = [round(x, 2) for x in ans.elements]

        msg += f"\nOutput: {student_ans}"
        msg += f"\nExpected: {ans}"

        if student_ans_lst != ans_lst:
            msg += "\n\nTest failed."
            return False, msg
        elif student_vec is student_ans:
            msg += "\nMultiplication operator modifies an original vector rather than creating a new resultant vector."
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
