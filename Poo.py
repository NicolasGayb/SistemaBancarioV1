# RoboNomeador 3000 - Núcleo em Python (POO)

class Robo:
    def __init__(self, modelo1: str, modelo2: str):
        self.modelo1 = modelo1
        self.modelo2 = modelo2

    def nome_completo(self) -> str:
        return f"{self.modelo1}-{self.modelo2}"

# Lê a entrada padrão e separa em dois modelos usando espaço como separador
entrada = input().strip()
modelos = entrada.split()

if len(modelos) != 2:
    print("Entrada invalida: devem ser dois modelos separados por espaço.")
else:
    modelo1, modelo2 = modelos

robo = Robo(modelo1, modelo2)
print(robo.nome_completo())

    # TODO: Crie um objeto da classe Robo com os modelos e imprima o nome completo
    # Dica: utilize o método nome_completo para compor o nome

    # Exemplo de uso (apague na implementação final):
    # robo = Robo(modelo1, modelo2)
    # print(robo.nome_completo())