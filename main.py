import textwrap, os
from abc import ABC, abstractclassmethod, abstractproperty
from datetime import datetime


class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco  # recebe
        self.contas = []  # inicia sem nenhuma conta

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(conta):
        self.contas.append(conta)  # adicionar uma nova conta ao cliente


class PessoaFisica(Cliente):
    def __init__(self, endereco, cpf, nome, data_nascimento):
        super().__init__(endereco)
        self.nome = nome
        self.cpf = cpf
        self.data_nascimento = data_nascimento


class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    def sacar(self, valor):
        saldo = self.saldo
        excedeu_saldo = valor > saldo

        if excedeu_saldo:
            print("Erro na operação! Você não tem saldo suficiente.")

        elif valor > 0:
            self._saldo -= valor
            print(f"Saque de R$ {valor:.2f} realizado com sucesso.")
            return True

        else:
            print("Erro na operação! O valor informado é inválido.")

        return False

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print(f"Depósito de R$ {valor:.2f} realizado com sucesso.")
            return True

        else:
            print("Erro na operação! O valor informado é inválido.")
            return False


class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_saques = limite_saques

    def sacar(self, valor):
        saques_realizados = [
            transacao
            for transacao in self.historico.transacoes
            if transacao["tipo"] == "Saque"
        ]

        numero_saques = len(saques_realizados)

        excedeu_limite = valor > self.limite
        excedeu_saques = numero_saques >= self.limite_saques

        if excedeu_limite:
            print("Erro na operação! O valor do saque ultrapassa o limite.")

        elif excedeu_saques:
            print("Erro na operação! Número máximo de saques ultrapassado.")

        else:  # não deu nenhum erro
            return super().sacar(valor)

    def __str__(self):
        return f"""\
                Agência: \t{self.agencia}
                C/C:\t\t{self.numero}
                Titular:\t{self.cliente.nome}
            """


class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            }
        )


class Transacao(ABC):
    @property
    @abstractproperty
    def valor(self):
        pass

    @abstractclassmethod
    def registrar(self, conta):
        pass


class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


# Função para limpar a tela do terminal
def limpar_tela():
    if os.name == "posix":  # Unix/Linux/MacOS/BSD/etc
        _ = os.system("clear")
    elif os.name == "nt":  # Windows
        _ = os.system("cls")


def mostrar_menu():
    menu = """
    =============MENU BANCÁRIO=============

    Escolha uma opção:
    [1] Depositar
    [2] Sacar
    [3] Extrato
    [4] Novo Cliente
    [5] Nova Conta
    [6] Listar Contas
    [7] Sair

    =======================================
    ===> """
    return input(menu)


def filtrar_cliente(cpf, clientes):
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None


def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("\n Cliente não possui conta vinculada!")
        return

    return cliente.contas[0]


def depositar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\nCliente não encontrado!")
        return

    valor = float(input("Informe o valor do depósito: "))
    transacao = Deposito(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)


def sacar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n Cliente não encontrado!")
        return

    valor = float(input("Informe o valor que deseja sacar: "))
    transacao = Saque(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)


def mostrar_extrato(clientes):
    cpf = input("Informe o cpf do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n Cliente não encontrado!")
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    print("\n=============== EXTRATO ================")
    extrato = ""

    transacoes = conta.historico.transacoes

    if not transacoes:
        extrato = "Não foram realizadas movimentações."

    else:
        for transacao in transacoes:
            tipo_transacao = "(+)" if transacao["tipo"] == "Deposito" else "(-)"
            extrato += f"\n\t\t{tipo_transacao} R${transacao['valor']:.2f}"

    print(extrato)
    print(f"\nSaldo:\n\t\t(=)R$ {conta.saldo:.2f}")
    print("========================================")


def criar_conta(numero_conta, clientes, contas):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\nCliente não encontrado, fluxo de criação de conta encerrado!")
        return

    conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta)
    contas.append(conta)
    cliente.contas.append(conta)
    print("\nConta criada com sucesso!")


def listar_contas(contas):
    if not contas:
        print("Nenhuma conta cadastrada no banco!")
    else:
        for conta in contas:
            print("=" * 100)
            print(textwrap.dedent(str(conta)))


def criar_cliente(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if cliente:
        print("\nJá existe cliente cadastrado neste CPF!")
        return

    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
    endereco = input("Informe o endereço (logradouro, nro - bairro - cidade/estado): ")

    cliente = PessoaFisica(
        endereco=endereco, cpf=cpf, nome=nome, data_nascimento=data_nascimento
    )

    clientes.append(cliente)

    print("\nCliente criado com sucesso!")


def main():
    clientes = []
    contas = []

    while True:
        limpar_tela()
        opcao_escolhida = mostrar_menu()
        limpar_tela()

        if opcao_escolhida == "1":
            depositar(clientes)

        elif opcao_escolhida == "2":
            sacar(clientes)

        elif opcao_escolhida == "3":
            mostrar_extrato(clientes)

        elif opcao_escolhida == "4":
            criar_cliente(clientes)

        elif opcao_escolhida == "5":
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)

        elif opcao_escolhida == "6":
            listar_contas(contas)

        elif opcao_escolhida == "7":
            limpar_tela()
            print("Programa finalizado. Até mais!\n\n")
            break

        else:
            limpar_tela()
            print(
                "Operação inválida, por favor selecione corretamente a operação desejada."
            )

        input("\nPressione Enter para voltar ao menu...")


main()
