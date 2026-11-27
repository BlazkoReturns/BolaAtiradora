"""Efeitos sonoros do jogo, gerados por código (sem arquivos de áudio).

CONCEITO: som digital
---------------------
O som é guardado como uma sequência de números ("amostras"), cada um dizendo a
posição do alto-falante num instante; tocando 44100 por segundo (taxa de amostragem),
o alto-falante reproduz a onda. Frequência maior = mais agudo; amplitude maior = mais alto.
Para usar arquivos prontos, bastaria trocar por pygame.mixer.Sound("arquivo.wav").

CONCEITO: pygame.mixer
----------------------
É o módulo de áudio do pygame. Ele mistura vários sons ao mesmo tempo em "canais":
cada Sound.play() usa um canal livre, então um tiro não corta uma explosão.
"""

import math
import random
from array import array

import pygame

VOLUME_GERAL = 0.35  # de 0.0 (mudo) a 1.0 (máximo)


class SomMudo:
    """Substituto usado quando não há placa de som: tem play(), mas não faz nada."""

    def play(self, loops=0):
        pass

    def stop(self):
        pass


def _gerar_som(duracao, freq_inicio, freq_fim, forma="quadrada", volume=1.0):
    """Cria um pygame.mixer.Sound com um "bipe" que desliza de freq_inicio a freq_fim.

    duracao em segundos; forma: "quadrada" (som de videogame antigo),
    "seno" (som suave) ou "ruido" (chiado, bom para explosões).
    """
    # pygame.mixer.get_init() devolve (frequência, formato, canais) com que o mixer
    # foi aberto; as amostras precisam ser geradas nesse formato.
    taxa, formato, canais = pygame.mixer.get_init()

    total = int(taxa * duracao)
    maximo = 32767 * volume * VOLUME_GERAL  # 32767 = maior inteiro de 16 bits com sinal

    # array("h") = inteiros de 16 bits com sinal, o formato pedido ao mixer.
    amostras = array("h")
    fase = 0.0
    for i in range(total):
        progresso = i / total
        freq = freq_inicio + (freq_fim - freq_inicio) * progresso
        fase = (fase + freq / taxa) % 1.0  # uma volta completa da onda = 1.0

        if forma == "quadrada":
            valor = 1.0 if fase < 0.5 else -1.0
        elif forma == "seno":
            valor = math.sin(2 * math.pi * fase)
        else:  # "ruido"
            valor = random.uniform(-1.0, 1.0)

        # Envelope: o volume cai até zero, para o som não terminar num "clique".
        envelope = (1 - progresso) ** 2

        amostra = int(valor * envelope * maximo)
        # Em estéreo, cada instante tem uma amostra por canal, intercaladas.
        amostras.extend([amostra] * canais)

    # pygame.mixer.Sound(buffer=bytes) cria um som a partir de amostras na memória.
    return pygame.mixer.Sound(buffer=amostras.tobytes())


def _concatenar(*sons):
    """Junta vários Sound em sequência, um depois do outro, num Sound só."""
    # Sound.get_raw() devolve os bytes das amostras do som.
    return pygame.mixer.Sound(buffer=b"".join(s.get_raw() for s in sons))


def carregar_sons():
    """Prepara todos os efeitos e devolve um dicionário nome -> som.

    Deve ser chamada depois de pygame.init(). Se não houver dispositivo de áudio,
    devolve sons "mudos" para o jogo funcionar normalmente, só que em silêncio.
    """
    nomes = ["tiro", "acerto", "destruido", "dano", "nivel", "fim"]

    # get_init() devolve None se o mixer não abriu; pygame.error é a exceção do pygame.
    if not pygame.mixer.get_init():
        try:
            pygame.mixer.init()
        except pygame.error:
            return {nome: SomMudo() for nome in nomes}

    return {
        "tiro": _gerar_som(0.08, 900, 400, "quadrada", 0.5),
        "acerto": _gerar_som(0.06, 300, 250, "quadrada", 0.6),
        "destruido": _gerar_som(0.18, 0, 0, "ruido", 0.6),
        "dano": _gerar_som(0.30, 220, 60, "quadrada", 0.9),
        "nivel": _concatenar(
            _gerar_som(0.09, 660, 660, "seno", 0.8),
            _gerar_som(0.15, 990, 990, "seno", 0.8),
        ),
        "fim": _gerar_som(1.0, 400, 50, "quadrada", 1.0),
    }
