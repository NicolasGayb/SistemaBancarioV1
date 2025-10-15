import os
import textwrap
import functools
from datetime import datetime
from pathlib import Path


ROOT_PATH = Path(__file__).parent


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def log_transacao(func):
    """Decorador simples que registra chamadas de função/método em log.txt."""

    @functools.wraps(func)
    def envelope(*args, **kwargs):
        resultado = func(*args, **kwargs)
        data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open(ROOT_PATH / "log.txt", "a", encoding="utf-8") as arquivo:
                arquivo.write(
                    f"[{data_hora}] {func.__name__} called with args={args}, kwargs={kwargs} -> {resultado}\n"
                )
        except Exception:
            # não deixar o logging quebrar a execução
            pass

        print(f"{data_hora}: {func.__name__.upper()}")
        return resultado

    return envelope


def finalizador(func):
    return func


@finalizador
def mensagem_final():
    print("=" * 50)
    input("Pressione ENTER para continuar...")
    print("=" * 50)


def validar_cpf(cpf: str) -> bool:
    """Valida um CPF brasileiro (aceita strings com ou sem formatação)."""
    if not cpf:
        return False
    cpf_digits = "".join(filter(str.isdigit, cpf))
    if len(cpf_digits) != 11:
        return False
    if cpf_digits == cpf_digits[0] * 11:
        return False
    nums = [int(d) for d in cpf_digits]
    s1 = sum((10 - i) * nums[i] for i in range(9))
    r1 = s1 % 11
    d1 = 0 if r1 < 2 else 11 - r1
    if nums[9] != d1:
        return False
    s2 = sum((11 - i) * nums[i] for i in range(10))
    r2 = s2 % 11
    d2 = 0 if r2 < 2 else 11 - r2
    if nums[10] != d2:
        return False
    return True


class Usuario:
    def __init__(self, nome: str, cpf: str, data_nascimento: str):
        self.nome = nome
        self.cpf = cpf
        self.data_nascimento = data_nascimento

    def to_dict(self):
        return {"nome": self.nome, "cpf": self.cpf, "data_nascimento": self.data_nascimento}


class Conta:
    def __init__(self, agencia: str, numero_conta: int, usuario: Usuario):
        self.agencia = agencia
        self.numero_conta = numero_conta
        self.usuario = usuario
        self.saldo = 0.0
        self.extrato = ""

    def to_dict(self):
        return {
            "agencia": self.agencia,
            "numero_conta": self.numero_conta,
            "usuario": self.usuario.to_dict(),
            "saldo": self.saldo,
            "extrato": self.extrato,
        }


class SistemaBancario:
    def __init__(self):
        self.LIMITE_SAQUES = 3
        self.AGENCIA = "0001"
        self.limite = 500.0
        self.saldo = 0.0
        self.extrato = ""
        self.numero_saques = 0
        self.usuarios: list[Usuario] = []
        self.contas: list[Conta] = []

    def menu(self) -> str:
        clear_screen()
        menu_text = """
        ================= MENU ================
        [d]\tDepositar
        [s]\tSacar
        [e]\tExtrato
        [nu]\tNovo Usuário
        [lu]\tListar Usuários
        [fu]\tFiltrar Usuário
        [nc]\tNova Conta
        [lc]\tListar Contas
        [fc]\tFiltrar Conta
        [q]\tSair
        =======================================
        => """
        return input(textwrap.dedent(menu_text))

    @log_transacao
    def criar_usuario(self):
        while True:
            cpf = input("Informe o CPF (somente números): ")
            if not validar_cpf(cpf):
                print("CPF inválido! Tente novamente.")
                continue
            if self.filtrar_usuario(cpf) is not None:
                print("Já existe usuário com esse CPF!")
                mensagem_final()
                return
            nome = input("Informe o nome: ").title()
            sobrenome = input("Informe o sobrenome: ").title()
            full_name = f"{nome} {sobrenome}"
            data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
            try:
                dia, mes, ano = map(int, data_nascimento.split("-"))
                assert 1 <= dia <= 31 and 1 <= mes <= 12 and 1900 <= ano <= 9999
            except Exception:
                print("Data de nascimento inválida! Tente novamente.")
                continue
            usuario = Usuario(full_name, cpf, data_nascimento)
            self.usuarios.append(usuario)
            clear_screen()
            print(f"Usuário '{full_name}' criado com sucesso!")
            return mensagem_final()

    def listar_usuarios(self):
        if not self.usuarios:
            print("Nenhum usuário cadastrado.")
            return
        for usuario in self.usuarios:
            linha = f"""\
            Nome:\t{usuario.nome}
            CPF:\t{usuario.cpf}
            Data de Nascimento:\t{usuario.data_nascimento}
        """
            print("=" * 50)
            print(textwrap.dedent(linha))

    def filtrar_usuario(self, cpf: str):
        if not cpf or not validar_cpf(cpf):
            return None
        cpf_digits = "".join(filter(str.isdigit, cpf))
        for u in self.usuarios:
            if "".join(filter(str.isdigit, u.cpf)) == cpf_digits:
                return u
        return None

    @log_transacao
    def criar_conta(self):
        cpf = input("Informe o CPF do usuário: ")
        usuario = self.filtrar_usuario(cpf)
        if not usuario:
            print("Usuário não encontrado, fluxo de criação de conta encerrado!")
            mensagem_final()
            return
        numero_conta = len(self.contas) + 1
        conta = Conta(self.AGENCIA, numero_conta, usuario)
        self.contas.append(conta)
        print(f"=== Conta {numero_conta} criada com sucesso! ===")
        mensagem_final()

    def listar_contas(self):
        if not self.contas:
            print("Nenhuma conta cadastrada.")
            return
        for conta in self.contas:
            linha = f"""\
            Agência:\t{conta.agencia}
            N° da conta:\t{conta.numero_conta}
            Titular:\t{conta.usuario.nome}
        """
            print("=" * 50)
            print(textwrap.dedent(linha))

    def filtrar_conta(self, numero_conta: int):
        for conta in self.contas:
            if conta.numero_conta == numero_conta:
                return conta
        return None

    def _selecionar_conta_por_cpf(self, prompt_account: bool = True):
        cpf = input("Informe o CPF (somente números): ")
        if not validar_cpf(cpf):
            print("CPF inválido! Operação cancelada.")
            mensagem_final()
            return None, None, None
        usuario = self.filtrar_usuario(cpf)
        if not usuario:
            print("Usuário não encontrado.")
            mensagem_final()
            return None, None, None
        cpf_digits = "".join(filter(str.isdigit, cpf))
        contas_usuario = [c for c in self.contas if "".join(filter(str.isdigit, c.usuario.cpf)) == cpf_digits]
        if not contas_usuario:
            print("Nenhuma conta encontrada para este usuário.")
            mensagem_final()
            return None, None, None
        if len(contas_usuario) == 1 or not prompt_account:
            conta = contas_usuario[0]
        else:
            print("Contas encontradas para o usuário:")
            for c in contas_usuario:
                print(f" - Conta: {c.numero_conta} | Agência: {c.agencia}")
            numero_conta = input("Informe o número da conta: ")
            matching = [c for c in contas_usuario if str(c.numero_conta) == str(numero_conta)]
            if not matching:
                print("Conta inválida para este usuário.")
                mensagem_final()
                return None, None, None
            conta = matching[0]
        return conta, usuario, cpf

    @log_transacao
    def depositar(self):
        conta, usuario, cpf = self._selecionar_conta_por_cpf()
        if not conta:
            return
        valor_str = input("Informe o valor do depósito: ")
        try:
            valor = float(valor_str.replace(",", "."))
        except ValueError:
            print("Operação falhou! O valor informado é inválido.")
            mensagem_final()
            return
        if valor <= 0:
            print("Operação falhou! O valor informado é inválido.")
            mensagem_final()
            return
        conta.saldo += valor
        conta.extrato += f"Depósito:\tR$ {valor:.2f} - CPF: {cpf} - Conta: {conta.numero_conta}\n"
        print("=============== DEPÓSITO ===============")
        print(f"Depósito de R$ {valor:.2f} realizado com sucesso para a conta {conta.numero_conta}!")
        print(f"Saldo da conta {conta.numero_conta}: R$ {conta.saldo:.2f}")
        print("=======================================")
        mensagem_final()

    @log_transacao
    def sacar(self):
        conta, usuario, cpf = self._selecionar_conta_por_cpf()
        if not conta:
            return
        valor_str = input("Informe o valor do saque: ")
        try:
            valor = float(valor_str.replace(",", "."))
        except ValueError:
            print("Operação falhou! O valor informado é inválido.")
            mensagem_final()
            return
        print("=" * 23 + "SAQUE" + "=" * 23)
        print(f"Saque de R$ {valor:.2f} solicitado para a conta {conta.numero_conta} - CPF: {cpf}")
        print("=" * 50)
        if valor > conta.saldo:
            print("Operação falhou! Você não tem saldo suficiente.")
            mensagem_final()
        elif valor > self.limite:
            print("Operação falhou! O valor do saque excede o limite.")
            mensagem_final()
        elif self.numero_saques >= self.LIMITE_SAQUES:
            print("Operação falhou! Número máximo de saques diários excedido.")
            mensagem_final()
        elif valor > 0:
            conta.saldo -= valor
            conta.extrato += f"Saque:\tR$ {valor:.2f}\n"
            self.numero_saques += 1
            print("Saque realizado com sucesso!")
            print(f"Novo saldo: R$ {conta.saldo:.2f}")
            mensagem_final()
        else:
            print("Operação falhou! O valor informado é inválido.")
            mensagem_final()

    @log_transacao
    def exibir_extrato(self):
        conta, usuario, cpf = self._selecionar_conta_por_cpf(prompt_account=False)
        if not conta:
            return
        clear_screen()
        print("=" * 23 + "EXTRATO" + "=" * 23)
        extrato = conta.extrato
        saldo = conta.saldo
        print("Não foram realizadas movimentações." if not extrato else extrato)
        print(f"\nSaldo:\tR$ {saldo:.2f}")
        print("=" * 50)
        mensagem_final()

    def run(self):
        while True:
            opcao = self.menu()
            if opcao == "d":
                self.depositar()
            elif opcao == "s":
                self.sacar()
            elif opcao == "e":
                self.exibir_extrato()
            elif opcao == "nu":
                self.criar_usuario()
            elif opcao == "lu":
                self.listar_usuarios()
                input("Pressione ENTER para continuar...")
            elif opcao == "fu":
                cpf = input("Informe o CPF do usuário: ")
                usuario = self.filtrar_usuario(cpf)
                if usuario:
                    linha = f"""\
                    Nome:\t{usuario.nome}
                    CPF:\t{usuario.cpf}
                    Data de Nascimento:\t{usuario.data_nascimento}
                """
                    print("=" * 50)
                    print(textwrap.dedent(linha))
                else:
                    print("Usuário não encontrado.")
                input("Pressione ENTER para continuar...")
            elif opcao == "nc":
                self.criar_conta()
            elif opcao == "lc":
                self.listar_contas()
                input("Pressione ENTER para continuar...")
            elif opcao == "fc":
                try:
                    numero_conta = int(input("Informe o número da conta: "))
                except ValueError:
                    print("Número de conta inválido.")
                    input("Pressione ENTER para continuar...")
                    continue
                conta = self.filtrar_conta(numero_conta)
                if conta:
                    linha = f"""\
                    Agência:\t{conta.agencia}
                    N° da conta:\t{conta.numero_conta}
                    Titular:\t{conta.usuario.nome}
                """
                    print("=" * 50)
                    print(textwrap.dedent(linha))
                else:
                    print("Conta não encontrada.")
                input("Pressione ENTER para continuar...")
            elif opcao == "q":
                break
            else:
                print("Operação inválida, por favor selecione novamente a operação desejada.")
        print("Obrigado por utilizar nossos serviços!")


def main():
    sistema = SistemaBancario()
    sistema.run()


if __name__ == "__main__":
    main()
