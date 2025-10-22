import traceback

import pa3
import pa3sol
import math
import random


def TestCase():
    """
    This tests affine_encrypt(msg, a, b) where
        'msg' str type; a randomly chosen phrase
        'a' int type; an odd integer satisfying that gcd(a, 26) = 1
        'b' int type; a random integer in the range [3, 22]
    :return: tuple type; the first element is a boolean True if the test passes, False otherwise; the
             second element is a str type, and is the feedback
    """
    plaintext = ["STOP POLLUTION", "MEET AT NOON", "EAGLE LANDED", "CAT IS OUT", "LEAVE ASAP", "ABORT MISSION",
                 "DELIVER NOW", "BRING OP", "COMPROMISED", "GO UNDER", "CONFIRM RED HAT"]

    a = 2 * random.randint(1, 10) + 1
    while math.gcd(a, 26) != 1:
        a = 2 * random.randint(1, 10) + 1

    b = random.randint(3, 22)
    m = plaintext[random.randint(0, len(plaintext) - 1)]
    msg = f"Testing affine_encrypt(\"{m}\", {a}, {b})..."
    ans = pa3sol.affine_encrypt(m, a, b)

    try:
        student = pa3.affine_encrypt(m, a, b)
        msg += "\nOutput: " + str(student) + "\nExpected: " + str(ans)
        if ans.replace(' ', '') == student.replace(' ', ''):
            msg += "\nTest passed."
            return True, msg
        else:
            msg += "\nTest failed."
            return False, msg
    except Exception as e:
        msg += f"\nThe following unexpected error was raised:\n"
        msg += str(traceback.format_exc())
        msg += f"\n\nTest failed."
        return False, msg


# print(TestCase())
