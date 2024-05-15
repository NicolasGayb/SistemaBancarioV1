menu = """

[d] Depositar
[s] Sacar
[e] Extrato
[q] Sair

=> """

saldo = 0
limite = 500
extrato = ""
numero_saques = 0
LIMITE_SAQUES = 3

while True:

    opcao = input(menu)

    if opcao == "d":
        valor = float(input("Informe o valor que deseja depositar: "))

        if valor > 0:
            saldo += valor
            extrato += f"Depósito: R$ {valor:.2f}\n"

            print(f"O valor de {valor} foi depositado em sua conta!")
        
        else:
            print("O valor informado para depósito é inválido, favor informar um valor positivo para prosseguir com a operação.")


    elif opcao == "s":
        valor = float(input("Informe o valor que deseja sacar: "))

        sem_saldo = valor > saldo
        excede_limite = valor > limite
        excede_saques = numero_saques => LIMITE_SAQUES

        if sem_saldo:
            print("Você não possui saldo suficiente para esta transação. Favor informar um valor válido para sacar.")

        elif excede_limite:
            print("Você excedeu o limite de valor para saques. Tente novamente utilizando um valor válido para a operação.")

        elif excede_saques:
            print("Você excedeu o limite de saques diários. Favor aguardar 24 horas para realizar novas transações.")

        elif valor > 0:
            saldo -= valor
            extrato += f"Saque: {valor:.2f}\n"
            numero_saques += 1

        else:
            print("Operação falhou! Insira um valor válido para a transação.")

    elif opcao == "e":
        print("\n==============EXTRATO==============")
        print("Não foram realizadas movimentações hoje." if not extrato else extrato)
        print(f"\nSaldo: R${saldo:.2f}")
        print("===================================")


    elif opcao == "q":
        break

    else:
        print("Operação inválida, por favor selecione novamente uma opção válida para a operação desejada.")