# primes_refactored.py

from typing import List


def is_prime(num: int) -> bool:
    """
    Checks if the number is prime or not.

    Args:
        num (int): The number to check for primality.

    Returns:
        bool: True if prime, False otherwise.
    """
    if not isinstance(num, int):
        raise TypeError("The number must be an integer.")
    if num < 2:
        return False
    for i in range(2, int(num**0.5) + 1):
        if num % i == 0:
            return False
    return True


def prime_numbers(n: int) -> List[int]:
    """
    Returns the first n prime numbers.

    Args:
        n (int): The number of prime numbers to retrieve.

    Returns:
        List[int]: A list containing the first n prime numbers.

    Raises:
        ValueError: If n is negative.
        TypeError: If n is not an integer.
    """
    if not isinstance(n, int):
        raise TypeError("The input must be an integer.")
    if n < 0:
        raise ValueError("The number of primes requested must be non-negative.")

    primes: List[int] = []
    i = 2
    while len(primes) < n:
        if is_prime(i):
            primes.append(i)
        i += 1
    return primes


def main():
    """
    Prints the first 100 prime numbers and their count.
    """
    n = 100
    primes = prime_numbers(n)
    print(f"First {n} prime numbers:", primes)
    print(f"Length: {len(primes)}")


if __name__ == "__main__":
    main()
