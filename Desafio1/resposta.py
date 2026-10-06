import json
from pathlib import Path
from typing import Any
from pprint import pprint
from decimal import Decimal, ROUND_DOWN
from utils.functions import safe_cast


# Funções
def ler_json_vendas(caminho_arquivo):
    """Carrega as vendas de um arquivo JSON.

    Args:
        caminho_arquivo: Caminho do arquivo JSON que contém as vendas.

    Returns:
        Lista de vendas encontrada no campo `vendas` do arquivo JSON.

    Raises:
        FileNotFoundError: Se o arquivo não existir.
        KeyError: Se o campo `vendas` não estiver presente no JSON.
        json.JSONDecodeError: Se o conteúdo do arquivo não for um JSON válido.
    """
    p = Path(caminho_arquivo)

    if not p.is_file():
        raise FileNotFoundError(f"O arquivo '{caminho_arquivo}' não foi encontrado.")

    json_vendas = json.loads(p.read_text(encoding='utf-8'))

    if 'vendas' not in json_vendas:
        raise KeyError("JSON com formato desconhecido: O campo 'vendas' não foi encontrado no arquivo JSON.")

    return json_vendas['vendas']

def ordenar_vendas_por_vendedor(vendas: list[dict[str, Any]]) -> dict[str, list[dict]]:
    """Agrupa os valores das vendas pelo nome normalizado do vendedor.

    Args:
        vendas: Lista de vendas, cada uma com os campos `vendedor` e `valor`.

    Returns:
        Dicionário que associa cada vendedor à lista de valores de suas vendas.

    Raises:
        KeyError: Se uma venda não contiver `vendedor` ou `valor`.
        ValueError: Se o nome do vendedor estiver vazio ou o valor não for positivo.
        TypeError: Se o tipo do valor da venda não puder ser convertido para número.
        ValueError: Se o conteúdo do valor da venda não for numérico.
    """
    vendas_por_vendedor = {}
    for venda in vendas:
        # Validar formato do dict
        if 'vendedor' not in venda or 'valor' not in venda:
            raise KeyError("Formato de venda inválido: Cada venda deve conter os campos 'vendedor' e 'valor'.")

        # Normalizar valores
        vendedor = venda['vendedor'].upper().strip()

        if not vendedor:
            raise ValueError("O campo 'vendedor' não pode estar vazio.")

        valor = safe_cast(venda['valor'], float)

        if valor <= 0:
            raise ValueError(f"Valor da venda inválido: '{valor}'.")

        # Ordenar vendas
        if vendedor not in vendas_por_vendedor:
            vendas_por_vendedor[vendedor] = []

        vendas_por_vendedor[vendedor].append(valor)

    return vendas_por_vendedor


def calcular_comissao_vendas(vendas: dict[str, list[dict]]):
    """Calcula as comissões de cada vendedor e de cada venda.

    Vendas abaixo de R$ 100,00 não geram comissão; valores de R$ 100,00 a
    R$ 499,99 geram 1%, e valores a partir de R$ 500,00 geram 5%. Os valores
    são arredondados para baixo em duas casas decimais.

    Args:
        vendas: Dicionário que associa cada vendedor à lista de valores vendidos.

    Returns:
        Dicionário com a comissão total e a comissão individual de cada venda,
        organizadas por vendedor.

    Raises:
        TypeError: Se o tipo de algum valor de venda não puder ser convertido para número.
        ValueError: Se o conteúdo de algum valor de venda não for numérico.
    """
    comissao_vendas = {}
    for vendedor, v in vendas.items():
        # Venda é elegível para comissão se:
        # • Vendas abaixo de R$100,00 não gera comissão
        # • Vendas abaixo de R$500,00 gera 1% de comissão
        # • A partir de R$500,00 gera 5% de comissão
        comissao_vendas[vendedor] = {
            "COMISSAO_TOTAL": 0,  # Evitar erro de null pointer
            "COMISSAO_POR_VENDA": []
        }
        for valor in v:
            valor = safe_cast(valor, float)
            if valor < 100:
                comissao = 0
            elif valor < 500:
                # Geralmente, o valor da comissão é parametrizado ou é definido em um banco de dados, mas para fins de simplicidade, vamos definir diretamente no código.
                comissao = valor * 0.01
            else:
                comissao = valor * 0.05

            # No enunciado da questão não foi especificado como tratar o arredondamento da comissão,
            # então vamos arredondar para baixo.
            comissao = float(Decimal(comissao).quantize(Decimal('0.01'), rounding=ROUND_DOWN))

            comissao_vendas[vendedor]["COMISSAO_TOTAL"] += comissao
            comissao_vendas[vendedor]["COMISSAO_POR_VENDA"].append(comissao)

        # Arredondar o valor total da comissão para baixo fora do loop para evitar processamentos desnecessários.
        comissao_vendas[vendedor]["COMISSAO_TOTAL"] = float(Decimal(comissao_vendas[vendedor]["COMISSAO_TOTAL"]).quantize(Decimal('0.01'), rounding=ROUND_DOWN))

    return comissao_vendas


# Resposta do desafio
try:
    # Ler arquivo JSON com as vendas e salvar o campo "vendas" em uma lista
    vendas = ler_json_vendas('Desafio1/vendas.json')

    # Ordenar as vendas por vendedor (No exemplo já está ordenado, mas em casos reais pode não estar)
    vendas_ordenadas = ordenar_vendas_por_vendedor(vendas)

    # Calcular comissão.
    vendas_comissao = calcular_comissao_vendas(vendas_ordenadas)

    # Imprimir resultado final no console
    pprint(vendas_comissao)
except Exception as e:
    print("Não foi possível calcular as comissões. Erro:", str(e))
