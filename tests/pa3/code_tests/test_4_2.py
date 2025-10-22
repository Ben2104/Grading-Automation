import traceback

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

    e = random.randint(3, 26)
    while math.gcd(e, (p - 1) * (q - 1)) != 1:
        e = random.randint(3, 26)

    n = p * q
    texts = ["STOPS", "MOVE ONE", "STAYS", "TURNS", "GO ON RED", "SABOTAGED", "WATER", "FINISH NOW", "DUE EAST",
             "RETREAT"]
    message = texts[random.randint(0, len(texts) - 1)]
    encryption = pa3sol.rsa_encrypt(message, n, e)

    msg = f"Testing rsa_decrypt(\"{encryption}\", {p}, {q}, {e})..."
    ans = pa3sol.rsa_decrypt(encryption, p, q, e)
    try:
        student = pa3.rsa_decrypt(encryption, p, q, e)
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