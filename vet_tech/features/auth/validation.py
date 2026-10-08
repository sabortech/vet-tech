def normalize_cpf(value: str) -> str:
    if any(character not in "0123456789. -" for character in value):
        return ""
    return "".join(character for character in value if character in "0123456789")


def is_valid_cpf(value: str) -> bool:
    cpf = normalize_cpf(value)
    if len(cpf) != 11 or len(set(cpf)) == 1:
        return False

    digits = [int(character) for character in cpf]
    first_digit = (sum(digit * weight for digit, weight in zip(digits[:9], range(10, 1, -1))) * 10) % 11
    if first_digit == 10:
        first_digit = 0
    if first_digit != digits[9]:
        return False

    second_digit = (sum(digit * weight for digit, weight in zip(digits[:10], range(11, 1, -1))) * 10) % 11
    if second_digit == 10:
        second_digit = 0
    return second_digit == digits[10]
