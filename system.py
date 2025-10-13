import os
import textwrap

def menu():
    os.system('cls' if os.name == 'nt' else 'clear')
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

def mensagem_final():
    print("=" * 100)
    input("Operação concluída com sucesso! Tecle ENTER para continuar...")
    print("=" * 100)

def criar_usuario(usuarios):
    cpf = input("Informe o CPF (somente números): ")

    # Valida o CPF
    if not validar_cpf(cpf):
        print("CPF inválido! Favor informar um CPF válido para prosseguir com o cadastro.")
        return criar_usuario(usuarios)
    # Verifica se o CPF já existe na base de usuários
    usuario = filtrar_usuario(cpf, usuarios)

    if usuario:
        print("Já existe usuário com esse CPF!")
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
        print("Data de nascimento inválida! Favor informar uma data válida para prosseguir com o cadastro.")
        return criar_usuario(usuarios)

    usuarios.append({"nome": nome, "data_nascimento": data_nascimento, "cpf": cpf})

    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"Usuário '{nome}' criado com sucesso!")
    return mensagem_final()

def listar_usuarios(usuarios):
    if not usuarios:
        print("Nenhum usuário cadastrado.")
        return

    for usuario in usuarios:
        linha = f"""\
            Nome:\t{usuario['nome']}
            CPF:\t{usuario['cpf']}
            Data de Nascimento:\t{usuario['data_nascimento']}
        """
        print("=" * 100)
        print(textwrap.dedent(linha))

def validar_cpf(cpf: str) -> bool:
    ''' Valida um CPF brasileiro.
    Retorna True se o CPF for válido, caso contrário retorna False.

    Inputs:
    cpf: str - CPF a ser validado, pode conter caracteres não numéricos.
    Outputs:
    bool - True se o CPF for válido, False caso contrário.
    '''
    # remove caracteres não numéricos
    if not cpf:
        return False
    cpf_digits = ''.join(filter(str.isdigit, cpf))
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

def filtrar_usuario(cpf, usuarios):
    ''' Filtra um usuário pelo CPF informado. 
    Retorna o usuário se encontrado, caso contrário retorna None. 
    
    Inputs:
    cpf: str - CPF do usuário a ser filtrado.
    usuarios: list - Lista de usuários cadastrados.
    Outputs:
    dict or None - Usuário encontrado ou None se não encontrado.
    '''
    # Valida o CPF
    if not validar_cpf(cpf):
        print("CPF inválido!")
        return None

    # Remove non-digit characters from CPF    
    cpf_digits = ''.join(filter(str.isdigit, cpf))
    usuarios_filtrados = [
        usuario for usuario in usuarios
        if ''.join(filter(str.isdigit, usuario.get("cpf", ""))) == cpf_digits
    ]
    return usuarios_filtrados[0] if usuarios_filtrados else None

def criar_conta(agencia, numero_conta, usuarios):
    cpf = input("Informe o CPF do usuário: ")
    usuario = filtrar_usuario(cpf, usuarios)

    if usuario:
        print(f"=== Conta {numero_conta} criada com sucesso! ===")
        mensagem_final()
        return {"agencia": agencia, "numero_conta": numero_conta, "usuario": usuario}
    
    print("Usuário não encontrado, fluxo de criação de conta encerrado!")
    mensagem_final()

def listar_contas(contas):
    if not contas:
        print("Nenhuma conta cadastrada.")
        return

    for conta in contas:
        linha = f"""\
            Agência:\t{conta['agencia']}
            N° da conta:\t{conta['numero_conta']}
            Titular:\t{conta['usuario']['nome']}
        """
        print("=" * 100)
        print(textwrap.dedent(linha))

def filtrar_conta(numero_conta, contas):
    contas_filtradas = [conta for conta in contas if conta["numero_conta"] == numero_conta]
    return contas_filtradas[0] if contas_filtradas else None

def depositar(saldo, extrato, usuarios, contas):
    cpf = input("Informe o CPF do usuário para depósito (somente números): ")
    
    # Validar usuario
    usuario = filtrar_usuario(cpf, usuarios)
    if not usuario:
        print("Operação falhou! CPF não corresponde a um usuário cadastrado.")
        return saldo, extrato

    # Normaliza o CPF e busca a conta
    cpf_digits = ''.join(filter(str.isdigit, cpf))
    contas_usuario = [
        conta for conta in contas
        if ''.join(filter(str.isdigit, conta['usuario'].get("cpf", ""))) == cpf_digits
        ]
    
    if not contas_usuario:
        print("Operação falhou! Nenhuma conta encontrada para o CPF informado.")
        return saldo, extrato

    # Se houver múltiplas contas, solicitar o número da conta
    if len(contas_usuario) > 1:
        numero_conta = contas_usuario[0]['numero_conta']
    else:
        print("Contas encontradas para o CPF informado:")
        for conta in contas_usuario:
            print(f" - Conta: {conta['numero_conta']} (Agência: {conta['agencia']})")
        numero_conta = input("Informe o número da conta para depósito: ")
        # Validar se o número da conta é válido
        if not any(str(conta['numero_conta']) == str(numero_conta) for conta in contas_usuario):
            print("Operação falhou! Conta não encontrada para o CPF informado.")
            return saldo, extrato
    
    valor_str = input("Informe o valor do depósito: ")

    try:
        valor_deposito = float(valor_str.replace(',', '.'))
    except ValueError:
        print("Operação falhou! O valor informado é inválido.")
        return saldo, extrato

    if valor_deposito <= 0:
        print("Operação falhou! O valor informado é inválido.")
        return saldo, extrato

    saldo += valor_deposito
    extrato += f"Depósito:\tR$ {valor_deposito:.2f} - CPF: {cpf} - Conta: {numero_conta}\n"

    print("=============== DEPÓSITO ===============")
    print(f"Depósito de R$ {valor_deposito:.2f} realizado com sucesso para a conta {numero_conta}!")
    print(f"Novo saldo: R$ {saldo:.2f}")
    print("=======================================")

    return saldo, extrato

def sacar(*, saldo, valor, extrato, limite, numero_saques, limite_saques):
    cpf = input("Informe o CPF do usuário para saque (somente números): ")
    numero_conta = input("Informe o número da conta para saque: ")

    # Validação de CPF e conta
    usuario = filtrar_usuario(cpf, usuarios) if usuarios is not None else None
    conta = filtrar_conta(int(numero_conta), contas) if contas is not None and numero_conta.isdigit() else None

    if not usuario:
        print("Operação falhou! CPF não corresponde a um usuário cadastrado.")
        return saldo, extrato

    if not conta:
        print("Operação falhou! Conta não encontrada.")
        return saldo, extrato

    os.system('cls' if os.name == 'nt' else 'clear')
    print("=============== SAQUE ===============")
    print(f"Saque de R$ {valor:.2f} solicitado para a conta {numero_conta} - CPF: {cpf}")
    print("=======================================")

    if valor > saldo:
        print("Operação falhou! Você não tem saldo suficiente.")
    
    elif valor > limite:
        print("Operação falhou! O valor do saque excede o limite.")

    elif numero_saques >= limite_saques:
        print("Operação falhou! Número máximo de saques diários excedido.")

    elif valor > 0:
        saldo -= valor
        extrato += f"Saque:\tR$ {valor:.2f}\n"
        numero_saques += 1
        print("Saque realizado com sucesso!")

    else:
        print("Operação falhou! O valor informado é inválido.")
    
    return saldo, extrato

def exibir_extrato(saldo, /, *, extrato):
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=============== EXTRATO ===============")
    print("Não foram realizadas movimentações." if not extrato else extrato)
    print(f"\nSaldo:\tR$ {saldo:.2f}")
    print("=======================================")

def main():
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
            saldo, extrato = depositar(saldo, extrato, usuarios, contas)

        elif opcao == "s":
            valor = float(input("Informe o valor do saque: "))
            
            saldo, extrato = sacar(
                saldo=saldo,
                valor=valor,
                extrato=extrato,
                limite=limite,
                numero_saques=numero_saques,
                limite_saques=LIMITE_SAQUES,
                usuarios=usuarios,
                contas=contas
            )

        elif opcao == "e":
            exibir_extrato(saldo, extrato=extrato)

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
                print("=" * 100)
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
                    C/C:\t{conta['numero_conta']}
                    Titular:\t{conta['usuario']['nome']}
                """
                print("=" * 100)
                print(textwrap.dedent(linha))
            else:
                print("Conta não encontrada.")
            input("Pressione ENTER para continuar...")

        elif opcao == "q":
            break

        else:
            print("Operação inválida, por favor selecione novamente a operação desejada.")

    print("Obrigado por utilizar nossos serviços!")

if __name__ == "__main__":
    main()