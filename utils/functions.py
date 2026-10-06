# Funções compartilhadas entre os desafios

from typing import Any, Type, TypeVar


T = TypeVar('T')


def safe_cast(value: Any, target_type: Type[T]) -> T:
    """
    Casts a value to the target type only if it's not already an instance of that type.

    Args:
        value: The value to potentially cast.
        target_type: The type to cast to.

    Returns:
        The value as the target type, either cast or unchanged.

    Raises:
        TypeError: If the value cannot be cast to the target type.
        ValueError: If the value is incompatible with the target type.
    """
    if isinstance(value, target_type):
        return value
    return target_type(value)