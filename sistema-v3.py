import textwrap
from abc import ABC, abstractmethod
from datetime import datetime


class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf


class Conta(ABC):
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._cliente = cliente
        self._historico = Historico()

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    @abstractmethod
    def sacar(self, valor):
        pass

    @abstractmethod
    def depositar(self, valor):
        pass


class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques

    def sacar(self, valor):
        numero_saques = len(
            [transacao for transacao in self.historico.transacoes if isinstance(transacao, Saque)])

        excedeu_limite = valor > self._limite
        excedeu_saques = numero_saques >= self._limite_saques

        if excedeu_limite:
            print("\n@@@ Operação falhou! O valor do saque excede o limite. @@@")
            return False

        elif excedeu_saques:
            print("\n@@@ Operação falhou! Número máximo de saques excedido. @@@")
            return False

        elif valor > self.saldo:
            print("\n@@@ Operação falhou! Saldo insuficiente. @@@")
            return False

        else:
            self._saldo -= valor
            print("\n=== Saque realizado com sucesso! ===")
            return True

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print("\n=== Depósito realizado com sucesso! ===")
            return True
        else:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
            return False

    def __str__(self):
        return f"""
            Agência: {self.cliente.endereco}
            C/C: {self.numero}
            Titular: {self.cliente.nome}
        """


class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append({
            "tipo": transacao.__class__.__name__,
            "valor": transacao.valor,
            "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        })


class Transacao(ABC):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    @abstractmethod
    def registrar(self, conta):
        pass


class Saque(Transacao):
    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


class Deposito(Transacao):
    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


def menu():
    menu_text = """
    ================ MENU ================
    [d] Depositar
    [s] Sacar
    [e] Extrato
    [nc] Nova conta
    [lc] Listar contas
    [nu] Novo usuário
    [q] Sair
    => """
    return input(textwrap.dedent(menu_text))


def filtrar_cliente(cpf, clientes):
    clientes_filtrados = [
        cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None


def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("\n@@@ Cliente não possui conta! @@@")
        return None

    # FIXME: escolher a conta corretamente
    return cliente.contas[0]


def depositar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    valor = float(input("Informe o valor do depósito: "))
    transacao = Deposito(valor)
    conta = recuperar_conta_cliente(cliente)

    if conta:
        cliente.realizar_transacao(conta, transacao)


def sacar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    valor = float(input("Informe o valor do saque: "))
    transacao = Saque(valor)
    conta = recuperar_conta_cliente(cliente)

    if conta:
        cliente.realizar_transacao(conta, transacao)


def exibir_extrato(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    conta = recuperar_conta_cliente(cliente)

    if conta:
        print("\n================ EXTRATO ================")
        transacoes = conta.historico.transacoes

        if not transacoes:
            print("Não há transações registradas.")
        else:
            for transacao in transacoes:
                print(f"{transacao['tipo']}: R$ {
                      transacao['valor']:.2f} em {transacao['data']}")

        print(f"\nSaldo atual: R$ {conta.saldo:.2f}")
        print("==========================================")


def criar_cliente(clientes):
    cpf = input("Informe o CPF (somente números): ")
    if filtrar_cliente(cpf, clientes):
        print("\n@@@ Já existe cliente com esse CPF! @@@")
        return

    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
    endereco = input("Informe o endereço completo: ")

    cliente = PessoaFisica(nome, data_nascimento, cpf, endereco)
    clientes.append(cliente)
    print("\n=== Cliente criado com sucesso! ===")


def criar_conta(numero_conta, clientes, contas):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado, impossível criar conta! @@@")
        return

    conta = ContaCorrente(numero_conta, cliente)
    contas.append(conta)
    cliente.adicionar_conta(conta)
    print("\n=== Conta criada com sucesso! ===")


def listar_contas(contas):
    if not contas:
        print("\n@@@ Ainda não existem contas registradas! @@@")
        return

    for conta in contas:
        print("\n=========================================")
        print(conta)
        print("=========================================")


def main():
    clientes = []
    contas = []

    while True:
        opcao = menu()

        if opcao == "d":
            depositar(clientes)

        elif opcao == "s":
            sacar(clientes)

        elif opcao == "e":
            exibir_extrato(clientes)

        elif opcao == "nu":
            criar_cliente(clientes)

        elif opcao == "nc":
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)

        elif opcao == "lc":
            listar_contas(contas)

        elif opcao == "q":
            print("\n=== Encerrando o sistema. Obrigado! ===")
            break

        else:
            print(
                "\n@@@ Operação inválida, por favor selecione novamente a operação desejada. @@@")


if __name__ == "__main__":
    main()
