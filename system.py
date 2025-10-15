import os
import textwrap
import functools
import inspect
from datetime import datetime
from pathlib import Path

ROOT_PATH = Path(__file__).parent


def menu():
    """Exibe o menu e retorna a opção escolhida pelo usuário.
    Outputs:
    str - Opção escolhida pelo usuário.
    """
    os.system("cls" if os.name == "nt" else "clear")
    menu = """
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
    return input(textwrap.dedent(menu))


def log_transacao(func):
    """Decorador que registra transações em um arquivo de log.
    Logs a data, hora, nome da função, argumentos e valor retornado.
    Outputs:
    resultado - Valor retornado pela função decorada.
    """

    def envelope(*args, **kwargs):
        resultado = func(*args, **kwargs)
        data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(ROOT_PATH / "log.txt", "a") as arquivo:
            arquivo.write(
                f"[{data_hora}] Função '{func.__name__}' chamada com args: {args}, kwargs: {kwargs}. "
                f"Retornou {resultado}\n"
            )

        print(f"{data_hora}: {func.__name__.upper()}")
        return resultado

    return envelope


def finalizador(func):
    """Decorador marcador; por enquanto não altera comportamento da função.
    Mantém a compatibilidade com chamadas existentes que usam @finalizador.
    """
    return func


@finalizador
def mensagem_final():
    """Mensagem final padrão após operações."""
    print("=" * 50)
    input("Pressione ENTER para continuar...")
    print("=" * 50)


def listar_usuarios(usuarios):
    """Lista todos os usuários cadastrados.

    Inputs:
    usuarios: list - Lista de usuários existentes.
    """
    if not usuarios:
        print("Nenhum usuário cadastrado.")
        return

    for usuario in usuarios:
        linha = f"""\
            Nome:\t{usuario['nome']}
            CPF:\t{usuario['cpf']}
            Data de Nascimento:\t{usuario['data_nascimento']}
        """
        print("=" * 50)
        print(textwrap.dedent(linha))


def validar_cpf(cpf: str) -> bool:
    """Valida um CPF brasileiro.
    Retorna True se o CPF for válido, caso contrário retorna False.

    Inputs:
    cpf: str - CPF a ser validado, pode conter caracteres não numéricos.
    Outputs:
    bool - True se o CPF for válido, False caso contrário.
    """
    # remove caracteres não numéricos
    if not cpf:
        return False
    cpf_digits = "".join(filter(str.isdigit, cpf))
    if len(cpf_digits) != 11:
        return False
    # rejeita CPFs com todos os dígitos iguais (ex: 11111111111)
    if cpf_digits == cpf_digits[0] * 11:
        return False

    nums = [int(d) for d in cpf_digits]

    # calcula primeiro dígito verificador
    s1 = sum((10 - i) * nums[i] for i in range(9))
    r1 = s1 % 11
    d1 = 0 if r1 < 2 else 11 - r1
    if nums[9] != d1:
        return False

    # calcula segundo dígito verificador
    s2 = sum((11 - i) * nums[i] for i in range(10))
    r2 = s2 % 11
    d2 = 0 if r2 < 2 else 11 - r2
    if nums[10] != d2:
        return False

    return True


def require_valid_cpf(arg_name: str = "cpf"):
    """Decorador que valida o CPF passado como argumento para a função decorada.
    Inputs:
    arg_name: str - Nome do argumento que contém o CPF.
    Outputs:
    bool - True se o CPF for válido, False caso contrário.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cpf_val = kwargs.get(arg_name)
            if cpf_val is None:
                try:
                    sig = inspect.signature(func)
                    bound = sig.bind_partial(*args, **kwargs)
                    cpf_val = bound.arguments.get(arg_name)
                except Exception:
                    cpf_val = None

            if not cpf_val:
                print("CPF não fornecido para validação.")
                return None

            if not validar_cpf(cpf_val):
                print("CPF inválido! Operação cancelada.")
                return None

            return func(*args, **kwargs)

        return wrapper

    return decorator


def resolve_user_account(prompt_account: bool = True):
    """Decorador que solicita CPF, valida, filtra usuário e conta,
    e injeta conta_obj, usuario_obj e cpf na função decorada.

    Inputs:
    prompt_account: bool - Se True, solicita o número da conta se houver múltiplas contas para o usuário.
    Outputs:
    conta_obj: dict - Conta selecionada do usuário.
    usuario_obj: dict - Usuário correspondente ao CPF.
    cpf: str - CPF informado.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            usuarios = kwargs.get("usuarios")
            contas = kwargs.get("contas")
            try:
                sig = inspect.signature(func)
                bound = sig.bind_partial(*args, **kwargs)
                if usuarios is None and "usuarios" in bound.arguments:
                    usuarios = bound.arguments.get("usuarios")
                if contas is None and "contas" in bound.arguments:
                    contas = bound.arguments.get("contas")
            except Exception:
                pass

            cpf = input("Informe o CPF (somente números): ")
            if not validar_cpf(cpf):
                print("CPF inválido! Operação cancelada.")
                mensagem_final()
                return None

            usuario = filtrar_usuario(cpf, usuarios or [])
            if not usuario:
                print("Usuário não encontrado.")
                mensagem_final()
                return None

            cpf_digits = "".join(filter(str.isdigit, cpf))
            contas_usuario = [
                c
                for c in (contas or [])
                if "".join(filter(str.isdigit, c["usuario"].get("cpf", "")))
                == cpf_digits
            ]
            if not contas_usuario:
                print("Nenhuma conta encontrada para este usuário.")
                mensagem_final()
                return None

            if len(contas_usuario) == 1:
                conta_obj = contas_usuario[0]
            else:
                print("Contas encontradas para o usuário:")
                for conta in contas_usuario:
                    print(
                        f" - Conta: {conta['numero_conta']} | Agência: {conta['agencia']}"
                    )
                numero_conta = input("Informe o número da conta: ")
                matching = [
                    c
                    for c in contas_usuario
                    if str(c["numero_conta"]) == str(numero_conta)
                ]
                if not matching:
                    print("Conta inválida para este usuário.")
                    mensagem_final()
                    return None
                conta_obj = matching[0]

            kwargs.update(
                {
                    "conta_obj": conta_obj,
                    "usuario_obj": usuario,
                    "cpf": cpf,
                }
            )

            return func(*args, **kwargs)

        return wrapper

    return decorator


@log_transacao
def criar_usuario(usuarios):
    """Cria um novo usuário interativamente e o adiciona à lista de usuários.
    Verifica se o CPF é válido e se já existe na base de usuários.

    Inputs:
    usuarios: list - Lista de usuários existentes.
    """
    cpf = input("Informe o CPF (somente números): ")

    # Valida o CPF
    if not validar_cpf(cpf):
        print(
            "CPF inválido! Favor informar um CPF válido para prosseguir com o cadastro."
        )
        return criar_usuario(usuarios)
    # Verifica se o CPF já existe na base de usuários
    usuario = filtrar_usuario(cpf, usuarios)

    if usuario:
        print("Já existe usuário com esse CPF!")
        mensagem_final()
        return

    nome = input("Informe o nome: ").title()
    sobrenome = input("Informe o sobrenome: ").title()
    nome = f"{nome} {sobrenome}"

    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
    # Valida a data de nascimento
    try:
        dia, mes, ano = map(int, data_nascimento.split("-"))
        assert 1 <= dia <= 31
        assert 1 <= mes <= 12
        assert 1900 <= ano <= 2024
    except (ValueError, AssertionError):
        print(
            "Data de nascimento inválida! Favor informar uma data válida para prosseguir com o cadastro."
        )
        return criar_usuario(usuarios)

    usuarios.append({"nome": nome, "data_nascimento": data_nascimento, "cpf": cpf})

    os.system("cls" if os.name == "nt" else "clear")
    print(f"Usuário '{nome}' criado com sucesso!")
    return mensagem_final()


@log_transacao
@require_valid_cpf("cpf")
def filtrar_usuario(cpf, usuarios):
    """Filtra um usuário pelo CPF informado. Retorna o usuário ou None.

    Inputs:
    cpf: str - CPF do usuário a ser filtrado.
    Outputs:
    dict - Usuário correspondente ao CPF ou None.
    """
    cpf_digits = "".join(filter(str.isdigit, cpf))
    usuarios_filtrados = [
        usuario
        for usuario in usuarios
        if "".join(filter(str.isdigit, usuario.get("cpf", ""))) == cpf_digits
    ]
    return usuarios_filtrados[0] if usuarios_filtrados else None


@log_transacao
def criar_conta(agencia, numero_conta, usuarios):
    """Cria uma nova conta associada a um usuário existente.

    Inputs:
    agencia: str - Número da agência.
    numero_conta: int - Número da conta.
    usuarios: list - Lista de usuários existentes.
    Outputs:
    dict - Conta criada ou None se falhar.
    """
    cpf = input("Informe o CPF do usuário: ")
    usuario = filtrar_usuario(cpf, usuarios)

    if usuario:
        print(f"=== Conta {numero_conta} criada com sucesso! ===")
        mensagem_final()
        # inicializa saldo e extrato por conta
        return {
            "agencia": agencia,
            "numero_conta": numero_conta,
            "usuario": usuario,
            "saldo": 0.0,
            "extrato": "",
        }

    print("Usuário não encontrado, fluxo de criação de conta encerrado!")
    mensagem_final()


@log_transacao
def listar_contas(contas):
    """Lista todas as contas cadastradas.

    Inputs:
    contas: list - Lista de contas existentes.
    """
    if not contas:
        print("Nenhuma conta cadastrada.")
        return

    for conta in contas:
        linha = f"""\
            Agência:\t{conta['agencia']}
            N° da conta:\t{conta['numero_conta']}
            Titular:\t{conta['usuario']['nome']}
        """
        print("=" * 50)
        print(textwrap.dedent(linha))


@log_transacao
@require_valid_cpf("cpf")
def filtrar_conta(numero_conta, contas):
    """Filtra uma conta pelo número da conta. Retorna a conta ou None.

    Inputs:
    numero_conta: int - Número da conta a ser filtrada.
    Outputs:
    dict - Conta correspondente ao número ou None.
    """
    contas_filtradas = [
        conta for conta in contas if conta["numero_conta"] == numero_conta
    ]
    return contas_filtradas[0] if contas_filtradas else None


@log_transacao
@resolve_user_account()
def depositar(
    saldo, extrato, usuarios, contas, *, conta_obj=None, usuario_obj=None, cpf=None
):
    """Depósito interativo que recebe `conta_obj` injetada pelo decorator.

    Inputs:
    saldo: float - Saldo atual da conta.
    Outputs:
    tuple - Saldo e extrato atualizados.
    """
    numero_conta = conta_obj["numero_conta"]
    valor_str = input("Informe o valor do depósito: ")

    try:
        valor_deposito = float(valor_str.replace(",", "."))
    except ValueError:
        print("Operação falhou! O valor informado é inválido.")
        mensagem_final()
        return saldo, extrato

    if valor_deposito <= 0:
        print("Operação falhou! O valor informado é inválido.")
        mensagem_final()
        return saldo, extrato

    # Atualiza apenas a conta selecionada
    conta_obj["saldo"] = conta_obj.get("saldo", 0.0) + valor_deposito
    conta_obj["extrato"] = (
        conta_obj.get("extrato", "")
        + f"Depósito:\tR$ {valor_deposito:.2f} - CPF: {cpf} - Conta: {numero_conta}\n"
    )

    # Atualiza valores retornados para compatibilidade com main
    saldo = conta_obj["saldo"]
    extrato = conta_obj["extrato"]

    print("=============== DEPÓSITO ===============")
    print(
        f"Depósito de R$ {valor_deposito:.2f} realizado com sucesso para a conta {numero_conta}!"
    )
    print(f"Saldo da conta {numero_conta}: R$ {conta_obj['saldo']:.2f}")
    print("=======================================")
    mensagem_final()

    return saldo, extrato


@log_transacao
@resolve_user_account()
def sacar(
    *,
    saldo,
    extrato,
    limite,
    numero_saques,
    limite_saques,
    usuarios=None,
    contas=None,
    conta_obj=None,
    usuario_obj=None,
    cpf=None,
):
    """Realiza um saque na conta, atualizando o saldo e o extrato.
    Retorna o saldo e o extrato atualizados.

    Inputs:
    saldo: float - Saldo atual da conta.
    valor: float - Valor do saque.
    extrato: str - Extrato atual da conta.
    limite: float - Limite máximo para cada saque.
    numero_saques: int - Número de saques realizados no dia.
    limite_saques: int - Limite máximo de saques permitidos por dia.
    Outputs:
    tuple - Saldo e extrato atualizados.
    """

    # conta_obj, usuario_obj e cpf são injetados pelo decorator
    numero_conta = conta_obj["numero_conta"]

    valor_str = input("Informe o valor do saque: ")
    try:
        valor = float(valor_str.replace(",", "."))
    except ValueError:
        print("Operação falhou! O valor informado é inválido.")
        mensagem_final()
        return saldo, extrato, numero_saques

    print("=" * 23 + "SAQUE" + "=" * 23)
    print(
        f"Saque de R$ {valor:.2f} solicitado para a conta {numero_conta} - CPF: {cpf}"
    )
    print("=" * 50)

    # utiliza o saldo da conta selecionada
    conta_saldo = conta_obj.get("saldo", 0.0)

    if valor > conta_saldo:
        print("Operação falhou! Você não tem saldo suficiente.")
        mensagem_final()

    elif valor > limite:
        print("Operação falhou! O valor do saque excede o limite.")
        mensagem_final()

    elif numero_saques >= limite_saques:
        print("Operação falhou! Número máximo de saques diários excedido.")
        mensagem_final()

    elif valor > 0:
        conta_obj["saldo"] = conta_saldo - valor
        conta_obj["extrato"] = (
            conta_obj.get("extrato", "") + f"Saque:\tR$ {valor:.2f}\n"
        )
        numero_saques += 1
        print("Saque realizado com sucesso!")
        print(f"Novo saldo: R$ {conta_obj['saldo']:.2f}")
        mensagem_final()

    else:
        print("Operação falhou! O valor informado é inválido.")
        mensagem_final()

    # retorna o saldo/extrato da conta selecionada para compatibilidade com main
    saldo = conta_obj.get("saldo", 0.0)
    extrato = conta_obj.get("extrato", "")
    return saldo, extrato, numero_saques


@log_transacao
@resolve_user_account()
def exibir_extrato(
    *, usuarios=None, contas=None, conta_obj=None, usuario_obj=None, cpf=None
):
    """Exibe o extrato da conta selecionada.
    Inputs:
    usuarios: list - Lista de usuários existentes.
    contas: list - Lista de contas existentes.
    """
    os.system("cls" if os.name == "nt" else "clear")
    print("=" * 23 + "EXTRATO" + "=" * 23)
    extrato = conta_obj.get("extrato", "")
    saldo = conta_obj.get("saldo", 0.0)
    print("Não foram realizadas movimentações." if not extrato else extrato)
    print(f"\nSaldo:\tR$ {saldo:.2f}")
    print("=" * 50)
    mensagem_final()


def main():
    """Função principal que executa o sistema bancário."""
    LIMITE_SAQUES = 3
    AGENCIA = "0001"
    limite = 500
    saldo = 0
    extrato = ""
    numero_saques = 0
    usuarios = []
    contas = []

    while True:

        opcao = menu()
        if opcao == "d":
            res = depositar(saldo, extrato, usuarios, contas)
            if res is None:
                # operação cancelada ou falhou; mantém estado
                continue
            saldo, extrato = res

        elif opcao == "s":
            res = sacar(
                saldo=saldo,
                extrato=extrato,
                limite=limite,
                numero_saques=numero_saques,
                limite_saques=LIMITE_SAQUES,
                usuarios=usuarios,
                contas=contas,
            )
            if res is None:
                continue
            saldo, extrato, numero_saques = res

        elif opcao == "e":
            # exibir_extrato agora pede CPF/conta via decorator
            exibir_extrato(usuarios=usuarios, contas=contas)

        elif opcao == "nu":
            criar_usuario(usuarios)

        elif opcao == "lu":
            listar_usuarios(usuarios)
            input("Pressione ENTER para continuar...")

        elif opcao == "fu":
            cpf = input("Informe o CPF do usuário: ")
            usuario = filtrar_usuario(cpf, usuarios)

            if usuario:
                linha = f"""\
                    Nome:\t{usuario['nome']}
                    CPF:\t{usuario['cpf']}
                    Data de Nascimento:\t{usuario['data_nascimento']}
                """
                print("=" * 50)
                print(textwrap.dedent(linha))
            else:
                print("Usuário não encontrado.")
            input("Pressione ENTER para continuar...")

        elif opcao == "nc":
            numero_conta = len(contas) + 1
            conta = criar_conta(AGENCIA, numero_conta, usuarios)

            if conta:
                contas.append(conta)
                print("Conta criada com sucesso!")

        elif opcao == "lc":
            listar_contas(contas)
            input("Pressione ENTER para continuar...")

        elif opcao == "fc":
            numero_conta = int(input("Informe o número da conta: "))
            conta = filtrar_conta(numero_conta, contas)

            if conta:
                linha = f"""\
                    Agência:\t{conta['agencia']}
                    N° da conta:\t{conta['numero_conta']}
                    Titular:\t{conta['usuario']['nome']}
                """
                print("=" * 50)
                print(textwrap.dedent(linha))
            else:
                print("Conta não encontrada.")
            input("Pressione ENTER para continuar...")

        elif opcao == "q":
            break

        else:
            print(
                "Operação inválida, por favor selecione novamente a operação desejada."
            )

    print("Obrigado por utilizar nossos serviços!")


if __name__ == "__main__":
    main()
