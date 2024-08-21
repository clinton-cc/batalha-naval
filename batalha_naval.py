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
        self.navios_posicionados = {}  # Para rastrear as posições de cada navio
        self.total_navios = len(self.navios)
        self.colocar_navios()

    def colocar_navios(self): # Posiciona os navios no tabuleiro
        for nome, tamanho in self.navios:
            colocado = False
            tentativas = 0
            while not colocado and tentativas < 100: # Faz até 100 tentativas de posicionar todos os barcos no tabuleiro
                tentativas += 1
                orientacao = random.choice(['H', 'V'])
                if orientacao == 'H':
                    x = random.randint(0, self.tamanho - 1)
                    y = random.randint(0, self.tamanho - tamanho)
                    if all(self.tabuleiro[x][y + i] == '~' for i in range(tamanho)):
                        for i in range(tamanho):
                            self.tabuleiro[x][y + i] = nome[0]
                        self.navios_posicionados[nome[0]] = [(x, y + i) for i in range(tamanho)]
                        colocado = True
                else:
                    x = random.randint(0, self.tamanho - tamanho)
                    y = random.randint(0, self.tamanho - 1)
                    if all(self.tabuleiro[x + i][y] == '~' for i in range(tamanho)):
                        for i in range(tamanho):
                            self.tabuleiro[x + i][y] = nome[0]
                        self.navios_posicionados[nome[0]] = [(x + i, y) for i in range(tamanho)]
                        colocado = True
            if not colocado:
                raise ValueError(f"Não foi possível colocar o navio {nome} no tabuleiro.")

    def mostrar_tabuleiro(self): #Saída do tabuleiro
        print("  " + " ".join(map(str, range(self.tamanho))))
        for idx, linha in enumerate(self.tabuleiro):
            linha_oculta = []
            for celula in linha:
                if celula in ['J1', 'J2', 'O']:
                    linha_oculta.append(celula)  # Mostra apenas acertos ou tiros na água
                else:
                    linha_oculta.append('~')  # Esconde as embarcações
            print(f"{idx} " + ' '.join(linha_oculta))

    def ataque(self, jogador, x, y): # Define caso o ataque for bem sucedido ou não
        if self.tabuleiro[x][y] in ['P', 'E', 'C', 'S', 'D']:
            self.tabuleiro[x][y] = f"J{jogador}"
            return True
        elif self.tabuleiro[x][y] == '~':
            self.tabuleiro[x][y] = 'O'
        return False

    def verificar_navio_afundado(self, jogador):
        for simbolo, posicoes in self.navios_posicionados.items():
            if all(self.tabuleiro[x][y] == f"J{jogador}" for x, y in posicoes):
                # Verifica se o navio já foi afundado
                if any(self.tabuleiro[x][y] == simbolo for x, y in posicoes):
                    continue  # O navio já foi afundado, passa para o próximo

                # Incrementa o número de navios afundados do jogador
                self.embarcacoes_afundadas[jogador] += 1
                
                # Decrementa o total de navios restantes
                self.total_navios -= 1
                
                print(f"Jogador {jogador} afundou o navio '{simbolo}'!")

        # Verifica se todos os navios foram afundados
        if self.total_navios == 0:
            self.jogo_acabou = True
            self.verificar_vencedor()

    def verificar_vencedor(self):
        #Verifica quem afundou mais navios e declara o vencedor.
        if self.embarcacoes_afundadas[1] > self.embarcacoes_afundadas[2]:
            print("Jogador 1 venceu a partida com mais navios afundados!")
        elif self.embarcacoes_afundadas[2] > self.embarcacoes_afundadas[1]:
            print("Jogador 2 venceu a partida com mais navios afundados!")
        else:
            print("O jogo terminou empatado!")

    def alternar_turno(self):
        #Alterna o turno após verificar se o jogo acabou.
        with self.condition:
            if not self.jogo_acabou:
                self.turno_jogador = 2 if self.turno_jogador == 1 else 1
                self.condition.notify_all()

    def esperar_turno(self, jogador):
        #Espera até que seja o turno do jogador atual.
        with self.condition:
            while self.turno_jogador != jogador and not self.jogo_acabou:
                self.condition.wait()

def jogada(jogo: BatalhaNaval, jogador): 
    #Organiza a ordem dos processos 
    tiros = 5 #Número total de disparos disponíveis
    while tiros > 0 and not jogo.jogo_acabou:
        jogo.esperar_turno(jogador) #

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
                tiros -= 1 # Decrementa o valor total de disparos

            # Verifica se o navio foi afundado após o acerto
            jogo.verificar_navio_afundado(jogador)
        else:
            with jogo.lock:
                print("Tiro na água.")
            tiros = 5  # Reinicia o número de tiros restantes
            jogo.alternar_turno()  # Passa a vez para o próximo jogador

def thread_jogador(jogo: BatalhaNaval, jogador):
    while not jogo.jogo_acabou:
        jogada(jogo, jogador)

def main():
    tamanho = 10
    jogo = BatalhaNaval(tamanho)

    thread1 = threading.Thread(target=thread_jogador, args=(jogo, 1))
    thread2 = threading.Thread(target=thread_jogador, args=(jogo, 2))

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()

    print(f"Resultado Final: Jogador 1 afundou {jogo.embarcacoes_afundadas[1]} embarcações.")
    print(f"Resultado Final: Jogador 2 afundou {jogo.embarcacoes_afundadas[2]} embarcações.")

if __name__ == "__main__":
    main()
