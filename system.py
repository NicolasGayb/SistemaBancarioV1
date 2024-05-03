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
deposito = float

while True:

    opcao = input(menu)

    if opcao == "d":
        valor = float(input("Insira o valor que deseja depositar: "))
        if valor > 0:
            print(f"O valor de {valor} foi depositado em sua conta!")
        
        else:
            print("O valor informado para depósito é inválido, favor informar um valor maior que 0 para prosseguir com a operação.")

    elif opcao == "s":
        print("Saque")

    elif opcao == "e":
        print("Extrato")
    
    elif opcao == "q":
        break

    else:
        print("Operação inválida, por favor selecione novamente a operação desejada.")