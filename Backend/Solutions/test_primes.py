import unittest
from prime import is_prime, prime_numbers


class TestPrimeFunctions(unittest.TestCase):
    """Unit tests for prime number functions."""

    # Tests for is_prime function
    def test_is_prime_with_prime_numbers(self):
        """Test is_prime with known prime numbers."""
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
        for num in primes:
            with self.subTest(num=num):
                self.assertTrue(is_prime(num), f"{num} should be prime.")

    def test_is_prime_with_non_prime_numbers(self):
        """Test is_prime with known non-prime numbers."""
        non_primes = [0, 1, 4, 6, 8, 9, 10, 12, 14, 15]
        for num in non_primes:
            with self.subTest(num=num):
                self.assertFalse(is_prime(num), f"{num} should not be prime.")

    def test_is_prime_with_negative_numbers(self):
        """Test is_prime with negative numbers."""
        negative_numbers = [-10, -3, -1]
        for num in negative_numbers:
            with self.subTest(num=num):
                self.assertFalse(is_prime(num), f"{num} should not be prime.")

    def test_is_prime_with_non_integer_input(self):
        """Test is_prime with non-integer inputs."""
        non_integers = [2.5, "3", None, [5], {7}]
        for num in non_integers:
            with self.subTest(num=num):
                with self.assertRaises(TypeError):
                    is_prime(num)

    # Tests for prime_numbers function
    def test_prime_numbers_zero(self):
        """Test prime_numbers with n=0."""
        self.assertEqual(prime_numbers(0), [], "Should return an empty list for n=0.")

    def test_prime_numbers_one(self):
        """Test prime_numbers with n=1."""
        self.assertEqual(prime_numbers(1), [2], "Should return [2] for n=1.")

    def test_prime_numbers_ten(self):
        """Test prime_numbers with n=10."""
        expected_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
        self.assertEqual(
            prime_numbers(10), expected_primes, "Should return the first 10 primes."
        )

    def test_prime_numbers_hundred(self):
        """Test prime_numbers with n=100."""
        primes = prime_numbers(100)
        self.assertEqual(len(primes), 100, "Should return 100 prime numbers.")
        self.assertEqual(primes[-1], 541, "The 100th prime should be 541.")

    def test_prime_numbers_negative(self):
        """Test prime_numbers with negative n."""
        with self.assertRaises(ValueError):
            prime_numbers(-5)

    def test_prime_numbers_with_non_integer_input(self):
        """Test prime_numbers with non-integer inputs."""
        non_integers = [10.5, "20", None, [30], {40}]
        for n in non_integers:
            with self.subTest(n=n):
                with self.assertRaises(TypeError):
                    prime_numbers(n)


if __name__ == "__main__":
    unittest.main()
