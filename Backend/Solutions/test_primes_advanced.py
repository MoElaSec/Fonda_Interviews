import pytest
from prime import prime_numbers, is_prime


@pytest.mark.parametrize(
    "num,expected",
    [
        (2, True),
        (3, True),
        (4, False),
        (5, True),
        (9, False),
        (11, True),
        (15, False),
        (17, True),
        (19, True),
        (21, False),
        (23, True),
        (25, False),
        (29, True),
        (31, True),
        (37, True),
        (41, True),
        (43, True),
        (47, True),
        (53, True),
        (59, True),
        (61, True),
        (67, True),
        (71, True),
        (73, True),
        (79, True),
        (83, True),
        (89, True),
        (97, True),
    ],
)
def test_is_prime_parametrized(num, expected):
    """
    Parametrized tests: allow you to run the same test function with different input values,
    enhancing test coverage without redundant code.
    """
    assert is_prime(num) == expected, f"Failed for num={num}"


# ?Fixtures: in pytest provide a way to set up preconditions before tests and clean up after tests,
# promoting code reuse and modularity.
@pytest.fixture
def sample_prime_list():
    """Fixture that provides a sample list of prime numbers."""
    return [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]


def test_prime_numbers_zero(sample_prime_list):
    """Test prime_numbers with n=0."""
    assert prime_numbers(0) == [], "Should return an empty list for n=0."


def test_prime_numbers_one(sample_prime_list):
    """Test prime_numbers with n=1."""
    assert prime_numbers(1) == [2], "Should return [2] for n=1."


def test_prime_numbers_ten(sample_prime_list):
    """Test prime_numbers with n=10."""
    expected_primes = sample_prime_list
    assert prime_numbers(10) == expected_primes, "Should return the first 10 primes."
