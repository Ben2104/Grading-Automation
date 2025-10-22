import math
import util

""" ----------------- NECESSARY IMPORTS ----------------- """


def bezout_coeffs(a, b):
    def helper(a, b):
        if a == 0:
            return (0, 1)
        else:
            x, y = helper(b % a, a)
            return (y - (b // a) * x, x)

    return dict(zip([a, b], helper(a, b)))


def mod_inv(a, m):
    """
    returns the smallest, positive inverse of a modulo m
    raises a ValueError if a and m are not relatively prime
    INPUT: a - integer
             m - positive integer
      OUTPUT: the inverse of a modulo m as an integer
      """

    if math.gcd(a, m) != 1:
        raise ValueError(f"The values {a} and {m} must be relatively prime.")

    coeffs = bezout_coeffs(a, m)
    inverse = coeffs[a]

    while inverse < 0:
        inverse += m

    while inverse > m:
        inverse -= m

    return inverse

""" ----------------- PROBLEM 1 ----------------- """


def affine_encrypt(text, a, b):
    """
    encrypts the plaintext 'text', using an affine transformation key (a, b)
    :param: text - str type; plaintext as a string of letters
    :param: a - int type; integer satisfying gcd(a, 26) = 1
    :param: b - int type; shift value
    :raise: ValueError if gcd(a, 26) is not 1.
    :return: str type; the encrypted message as string of uppercase letters
    """
    if math.gcd(a, 26) != 1:
        raise ValueError("The given key is invalid")

    cipher = ""
    for letter in text:
        if letter.isalpha():
            num = int(util.letters2digits(letter))

            cipher_digits = str((a * num + b) % 26)

            if len(cipher_digits) == 1:
                cipher_digits = "0" + cipher_digits

            cipher += util.digits2letters(cipher_digits)

    return cipher


""" ----------------- PROBLEM 2 ----------------- """


def affine_decrypt(ciphertext, a, b):
    """
    decrypts the given cipher, assuming it was encrypted using an affine transformation key (a, b)
    :param: ciphertext - str type; a string of digits
    :param: a - int type; integer satisfying gcd(a, 26) = 1.
    :param: b - int type; shift value
    :return: str type; the decrypted message as a string of uppercase letters
    """
    if math.gcd(a, 26) != 1:
        raise ValueError("The given key is invalid")

    a_inv = mod_inv(a, 26)

    text = ""
    for letter in ciphertext:
        if letter.isalpha():
            letter = letter.upper()

            num = int(util.letters2digits(letter))

            letter_digits = str((a_inv * (num - b)) % 26)

            if len(letter_digits) == 1:
                letter_digits = "0" + letter_digits

            text += util.digits2letters(letter_digits)

    return text


""" ----------------- PROBLEM 3 ----------------- """


def rsa_encrypt(plaintext, n, e):
    """
    encrypts plaintext using RSA and the key (n, e)
    :param: text - str type; plaintext as a string of letters
    :param: n - int type; positive integer that is the modulo in the RSA key
    :param: e - int type; positive integer that is the exponent in the RSA key
    :return: str type; the encrypted message as a string of digits
    """

    text = plaintext.replace(' ', '')  # removing whitespace
    digits = util.letters2digits(text)
    l = util.blocksize(n)

    while len(digits) % l != 0:
        digits += '23'

    blocks = [digits[i:i + l] for i in range(0, len(digits), l)]

    cipher = ""
    for b in blocks:
        encrypted_block = str(int(b) ** e % n)
        if len(encrypted_block) < l:
            encrypted_block = '0' * (l - len(encrypted_block)) + encrypted_block
        cipher += encrypted_block
    return cipher.strip()


""" ----------------- PROBLEM 4 ----------------- """


def rsa_decrypt(cipher, p, q, e):
    """
    decrypts the cipher, which was encrypted using RSA and the key (p * q, e)
    :param cipher: ciphertext as a string of digits
    :param p: int type; prime number used as part of the key n = p * q to encrypt the ciphertext
    :param q: int type; prime number used as part of the key n = p * q to encrypt the ciphertext
    :param e: int type; integer satisfying gcd((p-1)*(q-1), e) = 1
    :return: str type; the decrypted message as a string of letters
    """
    n = p * q
    l = util.blocksize(n)
    ciphertext = cipher.replace(' ', '')

    blocks = [ciphertext[i: i + l] for i in range(0, len(ciphertext), l)]

    text = ""  # initializing the variable that will hold the decrypted text

    e_inv = mod_inv(e, (p - 1) * (q - 1))

    for b in blocks:
        decrypted_block = str(int(int(b) ** e_inv % n))

        if len(decrypted_block) < l:
            decrypted_block = '0' * (l - len(decrypted_block)) + decrypted_block

        text += util.digits2letters(decrypted_block)

    return text
