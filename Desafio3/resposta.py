import re
from datetime import date, datetime
from decimal import Decimal, ROUND_DOWN
from math import isfinite

# Constantes
_PADRAO_DATA = re.compile(r"^\d{2}/\d{2}/\d{4}$")
_DATA_MINIMA = date(2000, 1, 1)


# Funções
def _validar_numero_positivo(valor, nome):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise TypeError(f"{nome} deve ser um número (int ou float).")
    if not isfinite(valor) or valor <= 0:
        raise ValueError(f"{nome} deve ser um número finito maior que 0.")


def calcular_juros(data_vencimento: str, valor_base: float, multa_percentual: float) -> float:
    """
    Calcula o total de juros de um pagamento em atraso.

    juros = valor_base * (multa_percentual / 100) * dias_em_atraso

    Retorna float com 2 casas decimais, arredondado para baixo.
    Retorna 0.0 se o pagamento ainda não venceu.
    """
    # 1. Validação da data
    if not isinstance(data_vencimento, str) or not _PADRAO_DATA.match(data_vencimento):
        raise ValueError("data_vencimento deve estar no formato DD/MM/AAAA.")
    try:
        vencimento = datetime.strptime(data_vencimento, "%d/%m/%Y").date()
    except ValueError:
        raise ValueError(f"data_vencimento '{data_vencimento}' não é uma data válida.")

    # Tomei a liberdade de adicionar uma validação para datas anteriores a 01/01/2000
    if vencimento < _DATA_MINIMA:
        raise ValueError("data_vencimento deve ser igual ou posterior a 01/01/2000.")

    # 2. Validação dos valores
    _validar_numero_positivo(valor_base, "valor_base")
    _validar_numero_positivo(multa_percentual, "multa_percentual")

    # 3. Dias em atraso
    dias_atraso = (date.today() - vencimento).days
    if dias_atraso <= 0:
        return 0.0

    # 4. Cálculo dos juros
    base = Decimal(str(valor_base))
    taxa = Decimal(str(multa_percentual)) / Decimal(100)
    juros = base * taxa * dias_atraso

    # 5. Arredonda para baixo, 2 casas
    return float(juros.quantize(Decimal("0.01"), rounding=ROUND_DOWN))

# =============================== Exemplos ===============================

# Data dentro do prazo
print("Data dentro do prazo\n")
test_cases1 =[
    ["12/12/2026", 150.4, 2.5],
    ["01/12/2026", 90.75, 2.5],
    ["29/10/2026", 40, 2.5],
]

for data, valor, multa in test_cases1:
    print(
        f"Data: {data}, Valor: {valor}, Multa: {multa} => Juros: {calcular_juros(data, valor, multa)} => Total: {valor + calcular_juros(data, valor, multa)}"
    )

print("\n\n")

# Data vencida
print("Data vencida\n")
test_cases2 = [
    ["05/10/2026", 100, 2.5],
    ["04/10/2026", 100, 2.5],
    ["03/10/2026", 100, 2.5],
    ["02/10/2026", 120.4, 2.5],
]

for data, valor, multa in test_cases2:
    print(
        f"Data: {data}, Valor: {valor}, Multa: {multa} => Juros: {calcular_juros(data, valor, multa)} => Total: {valor + calcular_juros(data, valor, multa)}"
    )

print("\n\n")

# Data vencida, multa de 5%
print("Data vencida, multa de 5%\n")
test_cases3 = [
    ["05/10/2026", 100, 5.0],
    ["04/10/2026", 100, 5.0],
    ["03/10/2026", 100, 5.0],
    ["02/10/2026", 120.4, 5.0],
]

for data, valor, multa in test_cases3:
    print(
        f"Data: {data}, Valor: {valor}, Multa: {multa} => Juros: {calcular_juros(data, valor, multa)} => Total: {valor + calcular_juros(data, valor, multa)}"
    )

print("\n\n")

# Argumentos inválidos
print("Argumentos inválidos\n")
test_cases4 = [
    ["32/10/2026", 100, 2.5], # Data não existe
    ["31/09/2026", 100, 2.5], # Data não existe
    ["31/09/2026", 0, 2.5],   # Valor base inválido
    ["31/09/2026", -100, 2.5], # Valor base inválido
    ["31/09/2026", 100, 0],    # Multa inválida
    ["31/09/2026", 100, -2.5], # Multa inválida
    ["31-09-2026", 100, 2.5],  # Formato de data inválido
    ["13/09/1999", 100, 2.5],  # Data anterior a 01/01/2000
]

for data, valor, multa in test_cases4:
    try:
        print(
            f"Data: {data}, Valor: {valor}, Multa: {multa} => Juros: {calcular_juros(data, valor, multa)} => Total: {valor + calcular_juros(data, valor, multa)}"
        )
    except Exception as e:
        print(f"Erro capturado com sucesso: {e}")