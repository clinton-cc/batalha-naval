import threading
import random

class BatalhaNaval:
    def __init__(self, tamanho=10):
        self.tamanho = tamanho
        self.tabuleiro_jogo = [['~' for _ in range(tamanho)] for _ in range(tamanho)]
        self.lock = threading.Lock()
        self.jogo_acabou = False
        self.navios = [
            ('Porta-aviões', 5),
            ('Encouraçado', 4),
            ('Cruzador', 3),
            ('Submarino', 3),
            ('Destroier', 2)
        ]
        self.colocar_navios(self.tabuleiro_jogo)

    def colocar_navios(self, tabuleiro):
        for nome, tamanho in self.navios:
            colocado = False
            while not colocado:
                orientacao = random.choice(['H', 'V'])
                if orientacao == 'H':
                    x = random.randint(0, self.tamanho - 1)
                    y = random.randint(0, self.tamanho - tamanho)
                    if all(tabuleiro[x][y + i] == '~' for i in range(tamanho)):
                        for i in range(tamanho):
                            tabuleiro[x][y + i] = nome[0]
                        colocado = True
                else:
                    x = random.randint(0, self.tamanho - tamanho)
                    y = random.randint(0, self.tamanho - 1)
                    if all(tabuleiro[x + i][y] == '~' for i in range(tamanho)):
                        for i in range(tamanho):
                            tabuleiro[x + i][y] = nome[0]
                        colocado = True

    def mostrar_tabuleiro(self, tabuleiro, jogador,modo_ataque=False):
        print(f"Afunde um navio!, Jogador {jogador}:")
        print("  " + " ".join(map(str, range(self.tamanho))))
        for idx, linha in enumerate(tabuleiro):
            if modo_ataque:
                linha_mostrada=['~' if cell not in ['X', 'O'] else cell for cell in linha]
                print(f"{idx}"+' '.join (linha_mostrada))
            else:
                print(f"{idx} " + ' '.join(linha))
        print()

    def ataque(self, tabuleiro, x, y):
        with self.lock:
            if tabuleiro[x][y] in ['P', 'E', 'C', 'S', 'D']:
                tabuleiro[x][y] = 'X'
                return True
            elif tabuleiro[x][y] == '~':
                tabuleiro[x][y] = 'O'
            return False

    def verificar_vitoria(self, tabuleiro):
        for linha in tabuleiro:
            if any(c in linha for c in ['P', 'E', 'C', 'S', 'D']):
                return False
        return True

def jogada(jogo, tabuleiro, jogador):
    tiros = 3
    while tiros > 0 and not jogo.jogo_acabou:
        print(f"Jogador {jogador}, você tem {tiros} tiros restantes.")
        print(f"======================")
        jogo.mostrar_tabuleiro(tabuleiro, jogador)
        x = int(input("Informe a linha para ataque: "))
        y = int(input("Informe a coluna para ataque: "))
        if x < 0 or x >= jogo.tamanho or y < 0 or y >= jogo.tamanho:
            print("Coordenadas inválidas. Tente novamente.")
            continue
        if jogo.ataque(tabuleiro, x, y):
            print("Acertou um navio!")
            if jogo.verificar_vitoria(tabuleiro):
                print(f"Jogador {jogador} venceu!")
                jogo.jogo_acabou = True
                return True
        else:
            print("Tiro na água.")
        tiros -= 1
    return False

def thread_jogador(jogo, tabuleiro, jogador):
    while not jogo.jogo_acabou:
        if jogada(jogo, tabuleiro, jogador):
            break

def main():
    tamanho = 10
    jogo = BatalhaNaval(tamanho)
    rodada = 0

    thread1 = threading.Thread(target=thread_jogador, args=(jogo, jogo.tabuleiro_jogo))

    thread1.start()

    thread1.join()

    while not jogo.jogo_acabou:
        print(f"Rodada {rodada + 1}")
        if jogada(jogo, jogo.tabuleiro_jogo, 1):
            break
        if jogada(jogo, jogo.tabuleiro_jogo, 2):
            break
        rodada += 1

if __name__ == "__main__":
    main()
