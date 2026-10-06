import json
from pathlib import Path
from typing import Any
from utils.functions import safe_cast


# Funções
def ler_json_vendas(caminho_arquivo):
    # with open(caminho_arquivo, 'r') as arquivo:
    #     dados = json.load(arquivo)
    #     return dados['vendas']
    p = Path(caminho_arquivo)

    if not p.is_file():
        raise FileNotFoundError(f"O arquivo '{caminho_arquivo}' não foi encontrado.")

    json_vendas = json.loads(p.read_text(encoding='utf-8'))

    if 'vendas' not in json_vendas:
        raise KeyError("JSON com formato desconhecido: O campo 'vendas' não foi encontrado no arquivo JSON.")

    return json_vendas['vendas']

def ordenar_vendas_por_vendedor(vendas: list[dict[str, Any]]) -> dict[str, list[dict]]:
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


# Resposta do desafio
try:
    # Ler arquivo JSON com as vendas e salvar o campo "vendas" em uma lista

    vendas = ler_json_vendas('Desafio1/vendas.json')
    vendas_ordenadas = ordenar_vendas_por_vendedor(vendas)
    pass


    # Ordenar as vendas por vendedor (No exemplo já está ordenado, mas em casos reais pode não estar)
    #   Criar dict "vendas", cada chave é o nome do vendedor e o valor é uma lista das vendas dele

    # Iterar sobre o dict "vendas" e calcular a comissão de cada vendedor

    # • Vendas abaixo de R$100,00 não gera comissão
    # • Vendas abaixo de R$500,00 gera 1% de comissão
    # • A partir de R$500,00 gera 5% de comissão
except Exception as e:
    print("Não foi possível calcular as comissões. Erro:", str(e))
