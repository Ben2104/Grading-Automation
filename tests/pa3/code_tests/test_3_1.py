# To call a student's method, uncomment the following line and call <fileName>.<method>
import traceback

# import <insert student's fileName here>

import pa3
import pa3sol
import util
import random
import math


def TestCase():
    p_primes = list(util.primes(30, 50))
    p = p_primes[random.randint(0, len(p_primes) - 1)]
    q_primes = list(util.primes(51, 100))
    q = q_primes[random.randint(0, len(q_primes) - 1)]
    while p * q < 2525:
        p = p_primes[random.randint(0, len(p_primes) - 1)]
        q = q_primes[random.randint(0, len(q_primes) - 1)]
    # print(f"p: {p}, q: {q}")

    e = random.randint(3, 100)
    while math.gcd(e, (p - 1) * (q - 1)) != 1:
        e = random.randint(3, 100)
    n = p * q

    plaintext = ["STOP POLLUTION", "MEET AT NOON", "EAGLE LANDED", "CAT IS OUT", "LEAVE ASAP", "ABORT MISSION",
                 "DELIVER NOW", "BRING OP", "COMPROMISED", "GO UNDER", "CONFIRM RED HAT", "MOVE SOUTH NOW"]
    p = plaintext[random.randint(0, len(plaintext) - 1)]

    msg = f"Testing rsa_encrypt(\"{p}\", {n}, {e})..."
    ans = pa3sol.rsa_encrypt(p, n, e)
    try:
        student = pa3.rsa_encrypt(p, n, e)
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
