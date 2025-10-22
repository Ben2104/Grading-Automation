import traceback

import pa3
import random


def TestCase():
    """
    This tests affine_encrypt("ERROR", a, b) where
        'a' int type; an even integer satisfying that gcd(a, 26) != 1
        'b' int type; a random integer in the range [3, 22]
        This test expects affine_encrypt() to raise a ValueError
    :return: tuple type; the first element is a boolean True if the test passes, False otherwise; the
             second element is a str type, and is the feedback
    """
    a = random.randint(3, 15) * 2
    b = random.randint(3, 25)
    msg = f"Testing affine_encrypt(\"ERROR\", {a}, {b})..."
    try:
        ans = pa3.affine_encrypt("ERROR", a, b)
        msg += "\nOutput: " + str(ans) + "\nExpected: ValueError\nTest failed."
        return (False, msg)
    except ValueError:
        msg += "\nOutput: ValueError\nExpected: ValueError\nTest passed."
        return (True, msg)
    except Exception as e:
        msg += f"\nThe following unexpected error was raised:\n"
        msg += str(traceback.format_exc())
        msg += f"\n\nTest failed."
        return False, msg


# print(TestCase())
