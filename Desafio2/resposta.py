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

    def __init__(self, caminho_db_original: str):
        """Inicializa o estoque usando um arquivo JSON como banco original.

        Cria `database.json` e `movimentacoes.json` no diretório do arquivo
        original caso esses arquivos ainda não existam.

        Args:
            caminho_db_original: Caminho para o arquivo JSON original do estoque.

        Raises:
            FileNotFoundError: Se o arquivo original não existir.
            OSError: Se não for possível ler ou criar os arquivos do estoque.
            json.JSONDecodeError: Se o arquivo original contiver JSON inválido.
        """
        # "Conectar" com banco de dados mock original
        self.caminho_db_original = Path(caminho_db_original)

        if not self.caminho_db_original.exists():
            raise FileNotFoundError(f"Banco de dados não encontrado: '{self.caminho_db_original}'")

        # Gerar arquivo database.json no mesmo diretório do banco de dados original (se já não existir)
        self.caminho_db = Path(self.caminho_db_original.parent / "database.json")

        if not self.caminho_db.exists():
            # Copiar banco original para database.json
            with open(self.caminho_db_original, "r", encoding="utf-8") as f:
                dados = json.load(f)
            self._gravar_json(self.caminho_db, dados)

        # Gerar arquivo de log de movimentações no mesmo diretório do banco de dados
        self.caminho_log = self.caminho_db_original.parent / "movimentacoes.json"

        if not self.caminho_log.exists():
            self._gravar_json(self.caminho_log, [])

    # ---------------------- API Pública ----------------------

    def imprimir_produtos(self):
        """Imprime os dados de todos os produtos cadastrados."""
        banco = self._ler_json(self.caminho_db)
        for prod in banco["estoque"]:
                print(prod)

    def buscar_produto(self, codigo_produto: int):
        """Busca e retorna um produto pelo código.

        Args:
            codigo_produto: Código do produto que será buscado.

        Returns:
            Dicionário com os dados do produto encontrado.

        Raises:
            ProdutoNaoEncontradoError: Se não houver produto com o código informado.
            OSError: Se não for possível ler o arquivo do estoque.
            json.JSONDecodeError: Se o arquivo do estoque contiver JSON inválido.
        """
        banco = self._ler_json(self.caminho_db)
        produto = self._buscar_produto(banco, codigo_produto)
        return produto

    def entrada(self, codigo_produto: int, quantidade: int):
        """Adiciona unidades ao estoque de um produto.

        Args:
            codigo_produto: Código do produto que receberá as unidades.
            quantidade: Número de unidades a adicionar; deve ser maior que zero.

        Returns:
            A nova quantidade do produto em estoque.

        Raises:
            ValueError: Se a quantidade não for um inteiro positivo.
            ProdutoNaoEncontradoError: Se o produto não estiver cadastrado.
            OSError: Se não for possível ler ou gravar os arquivos do estoque.
        """
        return self._movimentar(TipoMovimentacao.ENTRADA, codigo_produto, quantidade)

    def saida(self, codigo_produto: int, quantidade: int):
        """Remove unidades do estoque de um produto.

        Args:
            codigo_produto: Código do produto do qual as unidades serão removidas.
            quantidade: Número de unidades a remover; deve ser maior que zero.

        Returns:
            A nova quantidade do produto em estoque.

        Raises:
            ValueError: Se a quantidade não for um inteiro positivo.
            EstoqueError: Se não houver unidades suficientes em estoque.
            ProdutoNaoEncontradoError: Se o produto não estiver cadastrado.
            OSError: Se não for possível ler ou gravar os arquivos do estoque.
        """
        return self._movimentar(TipoMovimentacao.SAIDA, codigo_produto, quantidade)

    # ---------------------- API interna ----------------------

    def _movimentar(self, tipo: TipoMovimentacao, codigo_produto: int, quantidade: int):
        """Aplica uma movimentação e registra seus dados no log.

        Args:
            tipo: Tipo da movimentação, entrada ou saída.
            codigo_produto: Código do produto movimentado.
            quantidade: Número de unidades movimentadas; deve ser maior que zero.

        Returns:
            A quantidade do produto em estoque após a movimentação.

        Raises:
            ValueError: Se a quantidade não for um inteiro positivo.
            EstoqueError: Se o tipo for inválido ou a saída exceder o estoque.
            ProdutoNaoEncontradoError: Se o produto não estiver cadastrado.
            OSError: Se não for possível ler ou gravar os arquivos do estoque.
        """
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
        """Localiza um produto no conteúdo carregado do banco.

        Args:
            banco: Dados do banco, contendo a lista de produtos em `estoque`.
            codigo_produto: Código do produto que será localizado.

        Returns:
            Dicionário com os dados do produto encontrado.

        Raises:
            ProdutoNaoEncontradoError: Se não houver produto com o código informado.
        """
        for produto in banco["estoque"]:
            if produto["codigoProduto"] == codigo_produto:
                return produto
        raise ProdutoNaoEncontradoError(f"Produto {codigo_produto} não encontrado.")

    def _registrar_log(self, tipo, codigo_produto, quantidade):
        """Acrescenta uma movimentação ao arquivo de log.

        Args:
            tipo: Tipo da movimentação registrada.
            codigo_produto: Código do produto movimentado.
            quantidade: Número de unidades movimentadas.

        Raises:
            OSError: Se não for possível ler ou gravar o arquivo de log.
            json.JSONDecodeError: Se o arquivo de log contiver JSON inválido.
        """
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
        """Carrega e decodifica um arquivo JSON.

        Args:
            caminho: Caminho do arquivo JSON a ser lido.

        Returns:
            O valor Python correspondente ao conteúdo JSON do arquivo.

        Raises:
            OSError: Se não for possível abrir ou ler o arquivo.
            json.JSONDecodeError: Se o conteúdo do arquivo não for JSON válido.
        """
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)

    def _gravar_json(self, caminho, dados):
        """Grava dados JSON usando um arquivo temporário antes da substituição.

        Args:
            caminho: Caminho do arquivo JSON de destino.
            dados: Valor Python serializável que será gravado.

        Raises:
            OSError: Se não for possível gravar o arquivo temporário ou substituir
                o arquivo de destino.
            TypeError: Se `dados` não puder ser serializado como JSON.
            ValueError: Se `dados` contiver um valor numérico fora do padrão JSON.
        """
        # Grava em arquivo temporário e troca no final, para que uma falha
        # no meio da escrita não corrompa o arquivo original.
        caminho_tmp = Path(str(caminho) + ".tmp")
        with open(caminho_tmp, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
        os.replace(caminho_tmp, caminho)


# ========================== Exemplos ==========================

if __name__ == "__main__":
    # Instanciar banco de dados mock
    estoque = Estoque(
        "Desafio2/database_original.json"  # Será gerado um arquivo database.json com base no banco original.
    )

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
