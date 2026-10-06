# Funções compartilhadas entre os desafios

from typing import Any, Type, TypeVar


T = TypeVar('T')


def safe_cast(value: Any, target_type: Type[T]) -> T:
    """Converte um valor para o tipo de destino, se necessário.

    Args:
        value: Valor a ser convertido.
        target_type: Tipo para o qual o valor deve ser convertido.

    Returns:
        Valor convertido para o tipo de destino ou inalterado se já for desse tipo.

    Raises:
        TypeError: Se o tipo de destino não puder ser aplicado ao valor.
        ValueError: Se o valor for incompatível com o tipo de destino.
    """
    if isinstance(value, target_type):
        return value
    return target_type(value)