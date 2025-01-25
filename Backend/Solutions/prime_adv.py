# refactored_sieve_complete.py

from typing import List
import math


def estimate_upper_bound(n: int) -> int:
    """
    Estimate an upper bound for the nth prime number using the Prime Number Theorem.

    Args:
        n (int): The position of the prime number to estimate.

    Returns:
        int: The estimated upper bound.
    """
    if n < 6:
        return 15
    return int(n * (math.log(n) + math.log(math.log(n))))


def sieve_of_eratosthenes(limit: int) -> List[int]:
    """
    Generate all prime numbers up to a specified limit using the Sieve of Eratosthenes algorithm.

    Args:
        limit (int): The upper bound of numbers to check for primality.

    Returns:
        List[int]: A list of prime numbers up to the limit.
    """
    sieve = [True] * (limit + 1)
    sieve[0], sieve[1] = False, False  # 0 and 1 are not primes

    for number in range(2, int(math.sqrt(limit)) + 1):
        if sieve[number]:
            for multiple in range(number * number, limit + 1, number):
                sieve[multiple] = False

    primes = [num for num, is_prime in enumerate(sieve) if is_prime]
    return primes


def get_first_n_primes(n: int) -> List[int]:
    """
    Retrieve the first n prime numbers.

    Args:
        n (int): The number of prime numbers to retrieve.

    Returns:
        List[int]: A list containing the first n prime numbers.
    """
    upper_bound = estimate_upper_bound(n)
    primes = sieve_of_eratosthenes(upper_bound)
    if len(primes) >= n:
        return primes[:n]
    else:
        # If the estimate was too low, recursively try with a higher bound
        return get_first_n_primes(n * 2)


def main():
    """
    Main function to retrieve and print the first 100 prime numbers.
    """
    n = 100
    first_n_primes = get_first_n_primes(n)
    print(f"The first {n} prime numbers are:")
    print(first_n_primes)


if __name__ == "__main__":
    main()
