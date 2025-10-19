import re

def is_palindrome(text: str) -> bool:
    """Sprawdza, czy tekst jest palindromem."""
    cleaned = ''.join(ch.lower() for ch in text if ch.isalnum())
    return cleaned == cleaned[::-1]


def fibonacci(n: int) -> int:
    """Zwraca n-ty element ciągu Fibonacciego."""
    if n < 0:
        raise ValueError("n musi być nieujemne")
    if n in (0, 1):
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def count_vowels(text: str) -> int:
    """Zlicza samogłoski (w tym polskie)."""
    vowels = "aeiouyąęó"
    return sum(1 for ch in text.lower() if ch in vowels)


def calculate_discount(price: float, discount: float) -> float:
    """Zwraca cenę po uwzględnieniu zniżki."""
    if not (0 <= discount <= 1):
        raise ValueError("Zniżka musi być w zakresie 0–1")
    return price * (1 - discount)


def flatten_list(nested_list: list) -> list:
    """Spłaszcza listę (rekurencyjnie)."""
    result = []
    for item in nested_list:
        if isinstance(item, list):
            result.extend(flatten_list(item))
        else:
            result.append(item)
    return result


def word_frequencies(text: str) -> dict:
    """Zwraca słownik częstości słów (bez interpunkcji, wielkość liter ignorowana)."""
    words = re.findall(r'\b\w+\b', text.lower())
    freq = {}
    for word in words:
        freq[word] = freq.get(word, 0) + 1
    return freq


def is_prime(n: int) -> bool:
    """Sprawdza, czy liczba jest pierwsza."""
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True
