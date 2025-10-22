def digits2letters(digits):
    """
    converts the string of double-digit numbers to letters using the map
    00 -> A, 01 -> B, ..., 25 -> Z
    :param a:  str type; string of double-digit numbers in the range 00 - 25
    :return: str type; a string of letters A-Z corresponding to the double-digit numbers
    """
    letters = ""
    start = 0  # initializing starting index of first digit
    while start <= len(digits) - 2:
        digit = digits[start: start + 2]  # accessing the double-digit
        if int(digit) < 26:
            letters += chr(int(digit) + 65)  # concatenating to the string of letters
        start += 2  # updating the starting index for next digit

    return letters


def letters2digits(letters):
    """
    converts the given string of letters to a string of double digits
    using the mapping A -> 00, B - > 01, ..., Z -> 25
    :param letters: str type; the string of letters
    :return: str type; a string of double-digit characters
    """
    digits = ""
    for c in letters:
        if c.isalpha():
            letter = c.upper()  # converting to uppercase
            d = ord(letter) - 65
            if d < 10:
                digits += "0" + str(d)  # concatenating to the string of digits
            else:
                digits += str(d)
    return digits


def blocksize(n):
    """
    returns the size of a block in an RSA encrypted string
    :param: int type; the modulo in the RSA key (n, e)
    :return: int type; the size of an RSA block of characters
    """
    twofive = "25"
    while int(twofive) < n:
        twofive += "25"
    return len(twofive) - 2
  
def primes(a: int, b: int):
    """
    prints all primes in the range [a, b]
    :param a: int type; a positive integer greater than 1
    :param b: int type; a positive integer greater than or equal to a.
    :return: set type; a set of all primes in the range [a, b]
    :raises ValueError if a < 1 or b < a
    """
    if a < 1 or b < a:  # handling invalid range
        raise ValueError("Invalid range given")

    if a == 1:  # handling starting point a = 1
        a = 2  # this ensures 1 is not listed as a prime

    stop = int(b ** 1 / 2)
    P = set(range(a, b + 1))

    for x in range(2, stop):
        multiples_x = set([k * x for k in range(2, b // x + 1)])
        P -= multiples_x  # removing the multiples of x from the set P

    return P
