"""Efeitos sonoros do jogo, gerados por código (sem arquivos de áudio).

CONCEITO: como o som digital funciona
-------------------------------------
Um som é uma vibração do ar. No computador ele é guardado como uma lista de números
("amostras"), cada um dizendo a posição do alto-falante num instante. Tocando
44100 amostras por segundo (a "taxa de amostragem"), o alto-falante reproduz a
onda. Quanto mais rápido a onda sobe e desce (frequência, em Hz), mais agudo o som;
quanto maiores os números (amplitude), mais alto o volume.

Aqui criamos essas amostras com matemática (ondas quadradas, senoides e ruído) e
entregamos ao pygame. Assim o projeto não depende de baixar arquivos .wav/.ogg.
Para usar arquivos prontos, bastaria trocar por pygame.mixer.Sound("arquivo.wav").

CONCEITO: o módulo pygame.mixer
-------------------------------
pygame.mixer é a parte do pygame que toca áudio. Ele mistura ("mixa") vários sons
ao mesmo tempo em "canais": cada Sound.play() usa um canal livre, por isso um tiro
não corta o som de uma explosão que já estava tocando.
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
    # foi aberto. Precisamos gerar as amostras exatamente nesse formato.
    taxa, formato, canais = pygame.mixer.get_init()

    total = int(taxa * duracao)  # quantas amostras cabem na duração
    maximo = 32767 * volume * VOLUME_GERAL  # 32767 = maior valor de um inteiro de 16 bits

    # array("h") é uma lista compacta de inteiros de 16 bits com sinal ("h" = short),
    # exatamente o formato de amostra que pedimos ao mixer (-16 = 16 bits com sinal).
    amostras = array("h")
    fase = 0.0
    for i in range(total):
        progresso = i / total  # vai de 0 (início) a 1 (fim do som)

        # Frequência que desliza linearmente: dá o efeito "piu" (cai) ou "plim" (sobe).
        freq = freq_inicio + (freq_fim - freq_inicio) * progresso
        # A fase avança proporcional à frequência; uma volta completa = 1.0.
        fase = (fase + freq / taxa) % 1.0

        if forma == "quadrada":
            valor = 1.0 if fase < 0.5 else -1.0
        elif forma == "seno":
            valor = math.sin(2 * math.pi * fase)
        else:  # "ruido"
            valor = random.uniform(-1.0, 1.0)

        # Envelope: o volume cai até zero ao longo do som, para ele não terminar
        # num "clique" seco. (1 - progresso) ** 2 cai rápido no começo e suave no fim.
        envelope = (1 - progresso) ** 2

        amostra = int(valor * envelope * maximo)
        # Em som estéreo (2 canais), cada instante tem uma amostra por canal
        # (esquerdo, direito), intercaladas. Repetimos o mesmo valor em todos.
        amostras.extend([amostra] * canais)

    # pygame.mixer.Sound(buffer=bytes) cria um som a partir de amostras brutas na
    # memória (em vez de ler um arquivo). .tobytes() converte o array em bytes.
    return pygame.mixer.Sound(buffer=amostras.tobytes())


def _concatenar(*sons):
    """Junta vários Sound em sequência, um depois do outro, num Sound só."""
    # Sound.get_raw() devolve os bytes das amostras do som; colando os bytes,
    # temos um som que toca as partes em sequência.
    return pygame.mixer.Sound(buffer=b"".join(s.get_raw() for s in sons))


def carregar_sons():
    """Prepara todos os efeitos e devolve um dicionário nome -> som.

    Deve ser chamada depois de pygame.init(). Se não houver dispositivo de áudio,
    devolve sons "mudos" para o jogo funcionar normalmente, só que em silêncio.
    """
    nomes = ["tiro", "acerto", "destruido", "dano", "nivel", "fim"]

    # pygame.mixer.get_init() devolve None quando o mixer não conseguiu abrir
    # (ex.: computador sem saída de som). pygame.error é a exceção do pygame.
    if not pygame.mixer.get_init():
        try:
            pygame.mixer.init()
        except pygame.error:
            return {nome: SomMudo() for nome in nomes}

    return {
        # Tiro: bipe curto e agudo que cai rápido ("piu").
        "tiro": _gerar_som(0.08, 900, 400, "quadrada", 0.5),
        # Acerto sem destruir (quadrado amarelo/verde perdeu vida): "tic" seco.
        "acerto": _gerar_som(0.06, 300, 250, "quadrada", 0.6),
        # Quadrado destruído: estouro de ruído curto.
        "destruido": _gerar_som(0.18, 0, 0, "ruido", 0.6),
        # Núcleo perdeu vida (quadrado encostou, tiro errado ou fogo amigo): som grave.
        "dano": _gerar_som(0.30, 220, 60, "quadrada", 0.9),
        # Subiu de nível: duas notas subindo ("plim-plim").
        "nivel": _concatenar(
            _gerar_som(0.09, 660, 660, "seno", 0.8),
            _gerar_som(0.15, 990, 990, "seno", 0.8),
        ),
        # Fim de jogo: descida longa e grave.
        "fim": _gerar_som(1.0, 400, 50, "quadrada", 1.0),
    }
