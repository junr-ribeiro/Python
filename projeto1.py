import argparse
import random
import tkinter as tk


COLUNAS = 4
PARES = 8
SIMBOLOS = ["A", "B", "C", "D", "E", "F", "G", "H"]

FUNDO = "#10172a"
PAINEL = "#18233b"
CARTA = "#202e4d"
CARTA_HOVER = "#2a3c60"
DESTAQUE = "#7c9cff"
TEXTO = "#eef3ff"
TEXTO_SUAVE = "#9eacc8"
VERDE = "#52d6a0"


def mostrar_tabuleiro(cartas, encontradas, reveladas):
    for inicio in range(0, len(cartas), COLUNAS):
        linha = []
        for posicao in range(inicio, inicio + COLUNAS):
            if posicao in encontradas or reveladas[posicao]:
                valor = cartas[posicao]
            else:
                valor = f"{posicao + 1:02d}"
            linha.append(f"[{valor}]")
        print(" ".join(linha))


def pedir_posicao(mensagem, indisponiveis, total_cartas):
    while True:
        resposta = input(mensagem).strip().lower()
        if resposta in {"sair", "q"}:
            return None

        try:
            posicao = int(resposta) - 1
        except ValueError:
            print("Digite o número de uma posição ou 'sair' para encerrar.")
            continue

        if not 0 <= posicao < total_cartas:
            print(f"Escolha uma posição entre 1 e {total_cartas}.")
        elif posicao in indisponiveis:
            print("Essa posição já está descoberta ou foi escolhida nesta jogada.")
        else:
            return posicao


def jogar():
    cartas = SIMBOLOS * 2
    random.shuffle(cartas)

    encontradas = set()
    reveladas = [False] * len(cartas)
    tentativas = 0

    print("=== Jogo da memória ===")
    print("Encontre os pares. Digite 'sair' a qualquer momento para encerrar.")

    while len(encontradas) < len(cartas):
        mostrar_tabuleiro(cartas, encontradas, reveladas)

        primeira = pedir_posicao(
            "Escolha a primeira posição: ", encontradas, len(cartas)
        )
        if primeira is None:
            break
        reveladas[primeira] = True
        mostrar_tabuleiro(cartas, encontradas, reveladas)

        segunda = pedir_posicao(
            "Escolha a segunda posição: ",
            encontradas | {primeira},
            len(cartas),
        )
        if segunda is None:
            reveladas[primeira] = False
            break
        reveladas[segunda] = True
        mostrar_tabuleiro(cartas, encontradas, reveladas)
        tentativas += 1

        if cartas[primeira] == cartas[segunda]:
            encontradas.update({primeira, segunda})
            print("Par encontrado!")
        else:
            print("Não formam um par.")
            input("Pressione Enter para continuar...")
            reveladas[primeira] = False
            reveladas[segunda] = False

    if len(encontradas) == len(cartas):
        print(f"Parabéns! Você encontrou todos os pares em {tentativas} tentativas.")
    else:
        print("Jogo encerrado. Tente novamente quando quiser!")


class JogoMemoria:
    LARGURA_CARTA = 132
    ALTURA_CARTA = 112

    def __init__(self, raiz):
        self.raiz = raiz
        self.raiz.title("Jogo da memória")
        self.raiz.configure(bg=FUNDO)
        self.raiz.minsize(700, 690)
        self.raiz.resizable(False, False)

        self.partida_id = 0
        self.cartas = []
        self.reveladas = []
        self.encontradas = set()
        self.tentativas = 0
        self.primeira = None
        self.segunda = None
        self.animando = False
        self.widgets_cartas = []

        self._montar_interface()
        self.novo_jogo()

    def _montar_interface(self):
        principal = tk.Frame(self.raiz, bg=FUNDO, padx=34, pady=26)
        principal.pack(fill="both", expand=True)

        topo = tk.Frame(principal, bg=FUNDO)
        topo.pack(fill="x", pady=(0, 20))
        textos = tk.Frame(topo, bg=FUNDO)
        textos.pack(side="left")
        tk.Label(
            textos,
            text="Jogo da memória",
            font=("Segoe UI", 25, "bold"),
            fg=TEXTO,
            bg=FUNDO,
        ).pack(anchor="w")
        tk.Label(
            textos,
            text="Encontre os pares. Você consegue lembrar de todos?",
            font=("Segoe UI", 10),
            fg=TEXTO_SUAVE,
            bg=FUNDO,
        ).pack(anchor="w", pady=(3, 0))

        tk.Button(
            topo,
            text="Novo jogo",
            command=self.novo_jogo,
            font=("Segoe UI", 10, "bold"),
            fg=TEXTO,
            bg="#30446b",
            activebackground="#405a89",
            activeforeground=TEXTO,
            relief="flat",
            padx=16,
            pady=9,
            cursor="hand2",
        ).pack(side="right", pady=6)

        indicadores = tk.Frame(principal, bg=FUNDO)
        indicadores.pack(fill="x", pady=(0, 14))
        self.tentativas_label = self._criar_indicador(
            indicadores, "TENTATIVAS", "0"
        )
        self.pares_label = self._criar_indicador(indicadores, "PARES", "0 / 8")

        self.status_label = tk.Label(
            principal,
            text="Escolha uma carta para começar.",
            font=("Segoe UI", 10),
            fg=TEXTO_SUAVE,
            bg=FUNDO,
            anchor="w",
        )
        self.status_label.pack(fill="x", pady=(0, 12))

        tabuleiro = tk.Frame(principal, bg=FUNDO)
        tabuleiro.pack()
        for linha in range(4):
            for coluna in range(COLUNAS):
                posicao = linha * COLUNAS + coluna
                carta = tk.Canvas(
                    tabuleiro,
                    width=self.LARGURA_CARTA,
                    height=self.ALTURA_CARTA,
                    bg=FUNDO,
                    highlightthickness=0,
                    cursor="hand2",
                )
                carta.grid(row=linha, column=coluna, padx=6, pady=6)
                carta.bind("<Button-1>", lambda evento, p=posicao: self._clicar(p))
                carta.bind(
                    "<Enter>", lambda evento, p=posicao: self._passar_mouse(p, True)
                )
                carta.bind(
                    "<Leave>", lambda evento, p=posicao: self._passar_mouse(p, False)
                )
                self.widgets_cartas.append(carta)

        rodape = tk.Label(
            principal,
            text="Clique em duas cartas para revelar um par.",
            font=("Segoe UI", 9),
            fg=TEXTO_SUAVE,
            bg=FUNDO,
        )
        rodape.pack(pady=(15, 0))

    @staticmethod
    def _criar_indicador(pai, titulo, valor_inicial):
        caixa = tk.Frame(pai, bg=PAINEL, padx=16, pady=9)
        caixa.pack(side="left", padx=(0, 10))
        tk.Label(
            caixa,
            text=titulo,
            font=("Segoe UI", 8, "bold"),
            fg=TEXTO_SUAVE,
            bg=PAINEL,
        ).pack(anchor="w")
        valor = tk.Label(
            caixa,
            text=valor_inicial,
            font=("Segoe UI", 15, "bold"),
            fg=TEXTO,
            bg=PAINEL,
        )
        valor.pack(anchor="w", pady=(1, 0))
        return valor

    @staticmethod
    def _cartao_arredondado(canvas, x1, y1, x2, y2, raio, cor):
        raio = min(raio, (x2 - x1) / 2, (y2 - y1) / 2)
        pontos = [
            x1 + raio,
            y1,
            x2 - raio,
            y1,
            x2,
            y1,
            x2,
            y1 + raio,
            x2,
            y2 - raio,
            x2,
            y2,
            x2 - raio,
            y2,
            x1 + raio,
            y2,
            x1,
            y2,
            x1,
            y2 - raio,
            x1,
            y1 + raio,
            x1,
            y1,
        ]
        return canvas.create_polygon(
            pontos, smooth=True, splinesteps=12, fill=cor, outline=""
        )

    def _desenhar_carta(self, posicao, largura=None, hover=False, face=None):
        canvas = self.widgets_cartas[posicao]
        canvas.delete("all")
        largura = largura or self.LARGURA_CARTA - 12
        centro_x = self.LARGURA_CARTA / 2
        centro_y = self.ALTURA_CARTA / 2
        metade = max(largura / 2, 1)

        if posicao in self.encontradas:
            cor = "#183e3b"
        elif hover and not self.animando:
            cor = CARTA_HOVER
        else:
            cor = CARTA

        self._cartao_arredondado(
            canvas,
            centro_x - metade,
            7,
            centro_x + metade,
            self.ALTURA_CARTA - 7,
            13,
            cor,
        )

        mostrar = self.reveladas[posicao] if face is None else face
        if largura < 42:
            return
        if mostrar or posicao in self.encontradas:
            simbolo = self.cartas[posicao]
            canvas.create_text(
                centro_x,
                centro_y,
                text=simbolo,
                font=("Segoe UI", 25, "bold"),
                fill=VERDE if posicao in self.encontradas else TEXTO,
            )
        else:
            canvas.create_text(
                centro_x,
                centro_y - 4,
                text="?",
                font=("Segoe UI", 25, "bold"),
                fill=DESTAQUE,
            )
            canvas.create_text(
                centro_x,
                self.ALTURA_CARTA - 24,
                text=f"{posicao + 1:02d}",
                font=("Segoe UI", 8, "bold"),
                fill=TEXTO_SUAVE,
            )

    def _passar_mouse(self, posicao, entrou):
        if not self.animando and posicao not in self.encontradas:
            self._desenhar_carta(posicao, hover=entrou)

    def _animar_carta(self, posicao, revelar, ao_terminar, passo=0, partida=None):
        partida = self.partida_id if partida is None else partida
        if partida != self.partida_id:
            return

        meio = 5
        if passo == meio:
            self.reveladas[posicao] = revelar

        largura = max(
            2,
            (self.LARGURA_CARTA - 12) * abs(meio - passo) / meio,
        )
        face = self.reveladas[posicao] if passo <= meio else revelar
        self._desenhar_carta(posicao, largura=largura, face=face)

        if passo < meio * 2:
            self.raiz.after(
                16,
                lambda: self._animar_carta(
                    posicao, revelar, ao_terminar, passo + 1, partida
                ),
            )
        else:
            ao_terminar()

    def _clicar(self, posicao):
        if (
            self.animando
            or posicao in self.encontradas
            or self.reveladas[posicao]
        ):
            return

        self.animando = True
        if self.primeira is None:
            self._animar_carta(
                posicao, True, lambda: self._primeira_revelada(posicao)
            )
        else:
            self.segunda = posicao
            self._animar_carta(
                posicao, True, lambda: self._segunda_revelada(posicao)
            )

    def _primeira_revelada(self, posicao):
        self.primeira = posicao
        self.animando = False
        self.status_label.config(text="Agora escolha outra carta.")

    def _segunda_revelada(self, posicao):
        self.tentativas += 1
        self.tentativas_label.config(text=str(self.tentativas))

        if self.cartas[self.primeira] == self.cartas[posicao]:
            self.encontradas.update({self.primeira, posicao})
            self.pares_label.config(text=f"{len(self.encontradas) // 2} / {PARES}")
            self.status_label.config(text="Par encontrado! Muito bem.")
            self.primeira = None
            self.segunda = None
            self.animando = False
            if len(self.encontradas) == len(self.cartas):
                self.status_label.config(
                    text=f"Você venceu em {self.tentativas} tentativas! 🎉"
                )
            for encontrada in self.encontradas:
                self._desenhar_carta(encontrada)
            return

        self.status_label.config(text="Não formam um par. Tente novamente!")
        partida = self.partida_id
        self.raiz.after(750, lambda: self._esconder_nao_encontradas(partida))

    def _esconder_nao_encontradas(self, partida):
        if partida != self.partida_id:
            return
        primeira, segunda = self.primeira, self.segunda
        self._animar_carta(
            primeira,
            False,
            lambda: self._animar_carta(
                segunda, False, lambda: self._fim_da_jogada(primeira, segunda)
            ),
            partida=partida,
        )

    def _fim_da_jogada(self, primeira, segunda):
        self.primeira = None
        self.segunda = None
        self.animando = False
        self.status_label.config(text="Escolha duas cartas para encontrar o próximo par.")
        self._desenhar_carta(primeira)
        self._desenhar_carta(segunda)

    def novo_jogo(self):
        self.partida_id += 1
        self.cartas = SIMBOLOS * 2
        random.shuffle(self.cartas)
        self.reveladas = [False] * len(self.cartas)
        self.encontradas = set()
        self.tentativas = 0
        self.primeira = None
        self.segunda = None
        self.animando = False
        self.tentativas_label.config(text="0")
        self.pares_label.config(text=f"0 / {PARES}")
        self.status_label.config(text="Escolha uma carta para começar.")
        for posicao in range(len(self.cartas)):
            self._desenhar_carta(posicao)


def iniciar_interface():
    raiz = tk.Tk()
    JogoMemoria(raiz)
    raiz.mainloop()


def main():
    parser = argparse.ArgumentParser(description="Jogo da memória")
    parser.add_argument(
        "--terminal",
        action="store_true",
        help="joga no terminal em vez de abrir a interface gráfica",
    )
    argumentos = parser.parse_args()
    if argumentos.terminal:
        jogar()
    else:
        iniciar_interface()


if __name__ == "__main__":
    main()
