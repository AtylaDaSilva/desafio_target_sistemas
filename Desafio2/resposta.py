import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from enum import StrEnum

# Exceptions

class EstoqueError(Exception):
    pass

class ProdutoNaoEncontradoError(EstoqueError):
    pass

# Enums

class TipoMovimentacao(StrEnum):
    ENTRADA = "entrada"
    SAIDA = "saída"

# Classes

class Estoque:

    def __init__(self, caminho_db):
        # "Conectar" com banco de dados mock
        self.caminho_db = Path(caminho_db)

        if not self.caminho_db.exists():
            raise FileNotFoundError(f"Banco de dados não encontrado: '{self.caminho_db}'")

        # Gerar arquivo de log de movimentações no mesmo diretório do banco de dados
        self.caminho_log = self.caminho_db.parent / "movimentacoes.json"

        if not self.caminho_log.exists():
            self._gravar_json(self.caminho_log, [])

    # ---------------------- API Pública ----------------------

    def imprimir_produtos(self):
        banco = self._ler_json(self.caminho_db)
        for prod in banco["estoque"]:
                print(prod)

    def buscar_produto(self, codigo_produto: int):
        banco = self._ler_json(self.caminho_db)
        produto = self._buscar_produto(banco, codigo_produto)
        return produto

    def entrada(self, codigo_produto: int, quantidade: int):
        return self._movimentar(TipoMovimentacao.ENTRADA, codigo_produto, quantidade)

    def saida(self, codigo_produto: int, quantidade: int):
        return self._movimentar(TipoMovimentacao.SAIDA, codigo_produto, quantidade)

    # ---------------------- API interna ----------------------

    def _movimentar(self, tipo: TipoMovimentacao, codigo_produto: int, quantidade: int):
        # Validar quantidade
        if not isinstance(quantidade, int) or quantidade <= 0:
            raise ValueError("A quantidade deve ser um inteiro maior que zero.")

        # Lê o banco direto do arquivo
        banco = self._ler_json(self.caminho_db)
        produto = self._buscar_produto(banco, codigo_produto)

        if tipo == TipoMovimentacao.ENTRADA:
            produto["estoque"] += quantidade
        elif tipo == TipoMovimentacao.SAIDA:
            if produto["estoque"] < quantidade:
                raise EstoqueError(
                    f"Estoque insuficiente para o produto {codigo_produto}: "
                    f"disponível {produto['estoque']}, solicitado {quantidade}."
                )
            produto["estoque"] -= quantidade
        else:
            raise EstoqueError(f"Tipo de movimentação inválido: {tipo}")

        # Grava o banco e registra o log
        self._gravar_json(self.caminho_db, banco)
        self._registrar_log(tipo, codigo_produto, quantidade)

        return produto["estoque"]

    def _buscar_produto(self, banco, codigo_produto):
        for produto in banco["estoque"]:
            if produto["codigoProduto"] == codigo_produto:
                return produto
        raise ProdutoNaoEncontradoError(f"Produto {codigo_produto} não encontrado.")

    def _registrar_log(self, tipo, codigo_produto, quantidade):
        movimentacoes = self._ler_json(self.caminho_log)
        movimentacoes.append(
            {
                "id": str(uuid.uuid4()),
                "tipo": tipo,
                "timestamp": datetime.now().isoformat(),
                "codigoProduto": codigo_produto,
                "quantidade": quantidade,
            }
        )
        self._gravar_json(self.caminho_log, movimentacoes)

    def _ler_json(self, caminho):
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)

    def _gravar_json(self, caminho, dados):
        # Grava em arquivo temporário e troca no final, para que uma falha
        # no meio da escrita não corrompa o arquivo original.
        caminho_tmp = Path(str(caminho) + ".tmp")
        with open(caminho_tmp, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
        os.replace(caminho_tmp, caminho)


# ========================== Exemplos ==========================

if __name__ == "__main__":
    # Instanciar banco de dados mock
    estoque = Estoque("Desafio2/database.json")

    # Imprimir estoque inicial
    print("------------------ Estoque inicial ------------------\n")
    estoque.imprimir_produtos()

    print("\n------------------ Entradas ------------------")

    entradas = [
        (101, 2),
        (102, 5),
        (103, 3),
        (104, 10),
        (105, 18),
    ]

    for codigo, qtd in entradas:
        prod = estoque.buscar_produto(codigo)
        cod = prod["codigoProduto"]
        descr = prod["descricaoProduto"]
        estoque_atual = prod["estoque"]
        print(f"\nEntrada de {qtd} unidade(s) do produto {descr} (Cód.: {cod}). Estoque atual: {estoque_atual}")
        nova_qtd = estoque.entrada(codigo, qtd)
        print(f"Nova quantidade em estoque: {nova_qtd}")

    print("\n------------------ Saídas ------------------")
    
    saidas = [
        (101, 10),
        (102, 15),
        (103, 18),
        (104, 20),
        (105, 22),
    ]

    for codigo, qtd in saidas:
        prod = estoque.buscar_produto(codigo)
        cod = prod["codigoProduto"]
        descr = prod["descricaoProduto"]
        estoque_atual = prod["estoque"]
        print(f"\nSaída de {qtd} unidade(s) do produto {descr} (Cód.: {cod}). Estoque atual: {estoque_atual}")
        nova_qtd = estoque.saida(codigo, qtd)
        print(f"Nova quantidade em estoque: {nova_qtd}")

    print("\n------------------ Edge cases ------------------\n")

    # Teste de saída maior que o estoque
    try:
        print("Teste de saída maior que o estoque")
        estoque.saida(101, 1000)
    except EstoqueError as e:
        print(f"Erro capturado com sucesso: {e}\n")

    # Movimentação de produto inexistente
    try:
        print("Movimentação de produto inexistente")
        estoque.entrada(999, 10)
    except ProdutoNaoEncontradoError as e:
        print(f"Erro capturado com sucesso: {e}\n")

    # Movimentação com quantidade inválida
    try:
        print("Movimentação com quantidade inválida")
        estoque.entrada(101, -5)
    except ValueError as e:
        print(f"Erro capturado com sucesso: {e}\n")
