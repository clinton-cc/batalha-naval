import threading
import random

class BatalhaNaval:
    def __init__(self, tamanho):
        self.tamanho = tamanho
        self.tabuleiro = [['~' for _ in range(tamanho)] for _ in range(tamanho)]
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)
        self.jogo_acabou = False
        self.turno_jogador = 1  # Controla de quem é o turno
        self.embarcacoes_afundadas = {1: 0, 2: 0}
        self.navios = [
            ('Porta-aviões', 5),
            ('Encouraçado', 4),
            ('Cruzador', 3),
            ('Submarino', 3),
            ('Destroier', 2)
        ]
        self.colocar_navios()

    def colocar_navios(self):
        for nome, tamanho in self.navios:
            colocado = False
            tentativas = 0  # Contador de tentativas para evitar loops infinitos
            while not colocado and tentativas < 100:
                tentativas += 1
                orientacao = random.choice(['H', 'V'])
                if orientacao == 'H':
                    x = random.randint(0, self.tamanho - 1)
                    y = random.randint(0, self.tamanho - tamanho)
                    if all(self.tabuleiro[x][y + i] == '~' for i in range(tamanho)):
                        for i in range(tamanho):
                            self.tabuleiro[x][y + i] = nome[0]
                        colocado = True
                else:
                    x = random.randint(0, self.tamanho - tamanho)
                    y = random.randint(0, self.tamanho - 1)
                    if all(self.tabuleiro[x + i][y] == '~' for i in range(tamanho)):
                        for i in range(tamanho):
                            self.tabuleiro[x + i][y] = nome[0]
                        colocado = True
            if not colocado:
                raise ValueError(f"Não foi possível colocar o navio {nome} no tabuleiro.")

    def mostrar_tabuleiro(self):
        print("  " + " ".join(map(str, range(self.tamanho))))
        for idx, linha in enumerate(self.tabuleiro):
            linha_oculta = []
            for celula in linha:
                if celula in ['J1', 'J2', 'O']:
                    linha_oculta.append(celula)  # Mostra apenas acertos ou tiros na água
                else:
                    linha_oculta.append('~')  # Esconde as embarcações
            print(f"{idx} " + ' '.join(linha_oculta))

    def ataque(self, jogador, x, y):
        if self.tabuleiro[x][y] in ['P', 'E', 'C', 'S', 'D']:
            self.tabuleiro[x][y] = f"J{jogador}"
            return True
        elif self.tabuleiro[x][y] == '~':
            self.tabuleiro[x][y] = 'O'
        return False

    def verificar_navio_afundado(self, jogador):
        for nome, tamanho in self.navios:
            posicoes = [(i, j) for i in range(self.tamanho) for j in range(self.tamanho) if self.tabuleiro[i][j] == nome[0]]
            if len(posicoes) > 0 and all(self.tabuleiro[x][y] == f"J{jogador}" for x, y in posicoes):
                self.embarcacoes_afundadas[jogador] += 1
                # Marca todas as posições do navio afundado com um identificador
                for x, y in posicoes:
                    self.tabuleiro[x][y] = f"A{jogador}"

    def verificar_vitoria(self):
        total_navios = len(self.navios)
        for jogador in [1, 2]:
            if self.embarcacoes_afundadas[jogador] == total_navios:
                self.jogo_acabou = True
                return True
        return False

    def esperar_turno(self, jogador):
        with self.condition:
            while self.turno_jogador != jogador and not self.jogo_acabou:
                self.condition.wait()

    def alternar_turno(self):
        with self.condition:
            self.turno_jogador = 2 if self.turno_jogador == 1 else 1
            self.condition.notify_all()

def jogada(jogo:BatalhaNaval, jogador):
    tiros = 5
    while tiros > 0 and not jogo.jogo_acabou:
        jogo.esperar_turno(jogador)

        if jogo.jogo_acabou:
            break

        with jogo.lock:
            print(f"Jogador {jogador}, é a sua vez. Você tem {tiros} tiros restantes.")
            jogo.mostrar_tabuleiro()

            try:
                x = int(input(f"Jogador {jogador}, informe a linha para ataque: "))
                y = int(input(f"Jogador {jogador}, informe a coluna para ataque: "))
            except ValueError:
                print("Entrada inválida. Tente novamente.")
                continue

        if x < 0 or x >= jogo.tamanho or y < 0 or y >= jogo.tamanho:
            with jogo.lock:
                print("Coordenadas inválidas. Tente novamente.")
            continue

        acertou = jogo.ataque(jogador, x, y)
        if acertou:
            with jogo.lock:
                print("Acertou um navio!")
                tiros -= 1
            jogo.verificar_navio_afundado(jogador)
            if jogo.verificar_vitoria():
                with jogo.lock:
                    print(f"Jogador {jogador} venceu o jogo!")
                return
        else:
            with jogo.lock:
                print("Tiro na água.")
            tiros = 5  # Reinicia o número de tiros restantes
            jogo.alternar_turno()  # Passa a vez para o próximo jogador

def thread_jogador(jogo:BatalhaNaval, jogador):
    while not jogo.jogo_acabou:
        jogada(jogo, jogador)

def main():
    tamanho = 5
    jogo = BatalhaNaval(tamanho)

    thread1 = threading.Thread(target=thread_jogador, args=(jogo, 1))
    thread2 = threading.Thread(target=thread_jogador, args=(jogo, 2))

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()

    print(f"Resultado Final: Jogador 1 afundou {jogo.embarcacoes_afundadas[1]} embarcações.")
    print(f"Resultado Final: Jogador 2 afundou {jogo.embarcacoes_afundadas[2]} embarcações.")

    if jogo.embarcacoes_afundadas[1] > jogo.embarcacoes_afundadas[2]:
        print("Jogador 1 venceu a partida!")
    elif jogo.embarcacoes_afundadas[1] < jogo.embarcacoes_afundadas[2]:
        print("Jogador 2 venceu a partida!")
    else:
        print("A partida terminou empatada!")

if __name__ == "__main__":
    main()
