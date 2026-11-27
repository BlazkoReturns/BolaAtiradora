"""Trilha sonora 8 bits do jogo, composta e sintetizada por código.

CONCEITO: música "8 bits" (chiptune)
------------------------------------
Os videogames antigos tinham chips de som muito simples, com poucas "vozes":
algumas ondas quadradas/de pulso (melodia e baixo) e um gerador de ruído (bateria).
É esse som que imitamos aqui, com três camadas tocando juntas:
  - baixo: onda quadrada grave, em colcheias (dá o "motor" da música);
  - melodia: onda de pulso estreita (25%), mais "fina" e brilhante;
  - bateria: bumbo (seno que cai de frequência), caixa e chimbal (ruído).
Andamento rápido (165 batidas por minuto) e escala menor dão a sensação de adrenalina.

CONCEITO: tocar a música em loop
--------------------------------
A trilha é um único pygame.mixer.Sound. Sound.play(loops=-1) toca o som e o repete
para sempre (loops=-1 significa "infinito"), num canal só dele, enquanto os efeitos
sonoros usam os outros canais. Sound.stop() interrompe todas as reproduções do som.
(O pygame também tem pygame.mixer.music, feito para tocar música a partir de
ARQUIVOS .ogg/.mp3; como geramos o som na memória, usamos Sound.)

CONCEITO: acelerar tempo e tom ao mesmo tempo
---------------------------------------------
Tocar as mesmas amostras mais rápido (como um disco girando acelerado) deixa a
música mais curta e mais aguda de uma vez só: é o efeito de "urgência" dos
fliperamas quando o jogador está perto de morrer. Fazemos isso "reamostrando":
montamos uma versão nova pegando as amostras originais com passo maior que 1.
"""

import math
import random
from array import array

import pygame

BPM = 165  # batidas por minuto
VOLUME_MUSICA = 0.45  # volume da trilha (0.0 a 1.0), abaixo dos efeitos

# Urgência estilo fliperama: a cada vida perdida a música fica mais rápida e mais aguda.
# Os fatores são intervalos musicais (2 ** (semitons / 12)), para continuar afinada:
# +2 semitons = ~12% mais rápida; +4 semitons = ~26% mais rápida.
VIDA_NORMAL = 3
FATOR_POR_VIDA = {
    3: 1.0,
    2: 2 ** (2 / 12),
    1: 2 ** (4 / 12),
}

# Duração de uma semicolcheia (1/4 de batida): é a menor unidade de tempo da música.
SEMICOLCHEIA = 60 / BPM / 4

# Notas no padrão MIDI (69 = Lá 440 Hz; cada +1 é um semitom acima, +12 é uma oitava).
LA2, MI2, FA2, SOL2, DO3 = 45, 40, 41, 43, 48

# Acorde (nota do baixo) de cada um dos 8 compassos: Lá menor, Fá, Dó, Sol, ...
# e no fim Mi maior, que cria tensão e "puxa" de volta para o começo do loop.
BAIXO_POR_COMPASSO = [LA2, FA2, DO3, SOL2, LA2, FA2, SOL2, MI2]

# Melodia: (nota MIDI, duração em semicolcheias). Cada compasso soma 16.
MELODIA = [
    # Parte A
    (69, 2), (72, 2), (76, 2), (72, 2), (81, 4), (79, 2), (76, 2),
    (77, 2), (76, 2), (72, 2), (69, 2), (72, 4), (74, 2), (76, 2),
    (79, 2), (76, 2), (72, 2), (76, 2), (79, 4), (81, 2), (79, 2),
    (79, 4), (74, 2), (71, 2), (74, 4), (67, 4),
    # Parte B (mais aguda e agitada)
    (81, 1), (81, 1), (76, 2), (81, 1), (81, 1), (76, 2), (84, 4), (83, 2), (81, 2),
    (77, 2), (81, 2), (84, 4), (81, 2), (77, 2), (76, 4),
    (79, 2), (74, 2), (71, 2), (74, 2), (79, 2), (83, 2), (86, 4),
    (83, 4), (80, 4), (76, 4), (71, 4),
]

# Bateria em cada uma das 16 semicolcheias do compasso.
BUMBO = {0, 6, 8, 10}  # 6 e 10 deixam o ritmo mais "galopante"
CAIXA = {4, 12}  # tempos 2 e 4
CHIMBAL = {0, 2, 4, 6, 8, 10, 12, 14}  # todas as colcheias


def _freq(nota):
    """Converte nota MIDI em frequência (Hz)."""
    return 440 * 2 ** ((nota - 69) / 12)


def _tom(taxa, duracao, freq, ciclo, volume):
    """Amostras (floats de -1 a 1) de uma nota de onda de pulso.

    ciclo = fração da onda que fica "em cima": 0.5 é quadrada, 0.25 é mais fina.
    """
    total = int(taxa * duracao)
    amostras = []
    fase = 0.0
    for i in range(total):
        fase = (fase + freq / taxa) % 1.0
        valor = 1.0 if fase < ciclo else -1.0
        progresso = i / total
        # Envelope: cai um pouco ao longo da nota e some nos últimos 15%,
        # para as notas não grudarem umas nas outras (cliques).
        envelope = 1 - 0.4 * progresso
        if progresso > 0.85:
            envelope *= (1 - progresso) / 0.15
        amostras.append(valor * envelope * volume)
    return amostras


def _bumbo(taxa, volume):
    """Seno que despenca de 150 Hz para 40 Hz: o 'tum' do bumbo."""
    total = int(taxa * 0.12)
    amostras = []
    fase = 0.0
    for i in range(total):
        progresso = i / total
        fase += (150 - 110 * progresso) / taxa
        amostras.append(math.sin(2 * math.pi * fase) * (1 - progresso) ** 2 * volume)
    return amostras


def _ruido(taxa, duracao, volume):
    """Chiado que some rápido: caixa (mais longo) ou chimbal (bem curto)."""
    total = int(taxa * duracao)
    return [random.uniform(-1, 1) * (1 - i / total) ** 3 * volume for i in range(total)]


def _somar(mix, inicio, amostras):
    """Mistura (soma) as amostras no buffer da música a partir da posição inicio."""
    for i, valor in enumerate(amostras):
        if inicio + i < len(mix):
            mix[inicio + i] += valor


def _compor(taxa):
    """Compõe a música e devolve o buffer mono (lista de floats) com o loop inteiro."""
    passo = int(taxa * SEMICOLCHEIA)  # amostras por semicolcheia
    compassos = len(BAIXO_POR_COMPASSO)
    mix = [0.0] * (passo * 16 * compassos)  # buffer mono com a música inteira

    # Sons de bateria gerados uma vez e reaproveitados em todo o loop.
    bumbo = _bumbo(taxa, 0.9)
    caixa = _ruido(taxa, 0.10, 0.45)
    chimbal = _ruido(taxa, 0.025, 0.2)

    for compasso, nota_baixo in enumerate(BAIXO_POR_COMPASSO):
        inicio_compasso = compasso * 16 * passo

        # Baixo: colcheias alternando a nota e sua oitava (padrão clássico de chiptune).
        for colcheia in range(8):
            nota = nota_baixo + (12 if colcheia % 2 else 0)
            tom = _tom(taxa, SEMICOLCHEIA * 2, _freq(nota), 0.5, 0.28)
            _somar(mix, inicio_compasso + colcheia * 2 * passo, tom)

        # Bateria.
        for s in range(16):
            posicao = inicio_compasso + s * passo
            if s in BUMBO:
                _somar(mix, posicao, bumbo)
            if s in CAIXA:
                _somar(mix, posicao, caixa)
            if s in CHIMBAL:
                _somar(mix, posicao, chimbal)

    # Melodia por cima de tudo.
    posicao = 0
    for nota, duracao in MELODIA:
        _somar(mix, posicao, _tom(taxa, SEMICOLCHEIA * duracao, _freq(nota), 0.25, 0.22))
        posicao += duracao * passo

    return mix


def _acelerar(mix, fator):
    """Devolve a música tocada 'fator' vezes mais rápida: mais curta E mais aguda.

    É o mesmo efeito de girar um disco de vinil mais rápido. A nova amostra j
    corresponde ao ponto j * fator da original; como esse ponto quase sempre cai
    entre duas amostras, fazemos uma média ponderada das duas vizinhas
    (interpolação linear), o que evita chiados.
    """
    if fator == 1.0:
        return mix
    total = int(len(mix) / fator)
    ultimo = len(mix) - 1
    novo = []
    for j in range(total):
        origem = j * fator
        i = int(origem)
        frac = origem - i
        proximo = mix[i + 1] if i < ultimo else mix[0]  # no fim, emenda com o começo
        novo.append(mix[i] * (1 - frac) + proximo * frac)
    return novo


def _para_bytes(mix, canais):
    """Converte o buffer de floats em bytes de 16 bits com sinal, no formato do mixer."""
    # Converte para inteiros de 16 bits (array "h"), limitando a -1..1 para não
    # "estourar" (distorcer) onde as camadas somadas passam do máximo.
    amostras = array("h")
    for valor in mix:
        # 0.75 abaixa a mistura toda um pouco, para quase nunca chegar ao limite.
        valor = max(-1.0, min(1.0, valor * 0.75))
        # Em estéreo, cada instante tem uma amostra por canal, intercaladas.
        amostras.extend([int(valor * 32767)] * canais)
    return amostras.tobytes()


class Trilha:
    """Toca a trilha em loop e acelera (tempo + tom) conforme o núcleo perde vida.

    Uso: tocar() no início da partida, ajustar(vida) quando a vida mudar,
    parar() no fim de jogo. Sem placa de som, todos os métodos não fazem nada.
    """

    def __init__(self):
        # pygame.mixer.get_init() devolve (frequência, formato, canais) do mixer
        # aberto, ou None se não há áudio: nesse caso a trilha fica muda.
        config = pygame.mixer.get_init()
        self.ativa = config is not None
        if not self.ativa:
            return
        self.taxa, _formato, self.canais = config
        self.bytes_por_quadro = 2 * self.canais  # 2 bytes (16 bits) por canal

        # pygame.mixer.set_reserved(1) reserva o canal 0 só para nós: os efeitos
        # sonoros (Sound.play) nunca vão usá-lo, então a música não é cortada.
        # pygame.mixer.Channel(0) dá acesso direto a esse canal.
        pygame.mixer.set_reserved(1)
        self.canal = pygame.mixer.Channel(0)

        # Pré-gera uma versão da música para cada vida (leva ~1 s ao abrir o jogo),
        # para a troca durante a partida ser instantânea.
        mix = _compor(self.taxa)
        self.duracao_base = len(mix) / self.taxa  # duração da versão normal, em segundos
        self.versoes = {
            vida: _para_bytes(_acelerar(mix, fator), self.canais)
            for vida, fator in FATOR_POR_VIDA.items()
        }

        self.fator = 1.0
        self.posicao = 0.0  # onde a música está, em segundos da versão normal
        self.inicio_ms = 0  # instante (pygame.time.get_ticks) em que posicao foi medida

    def tocar(self):
        """Começa a música do início, na velocidade normal."""
        if self.ativa:
            self._tocar_de(VIDA_NORMAL, 0.0)

    def ajustar(self, vida):
        """Troca para a versão da vida atual, continuando do mesmo ponto da música."""
        if not self.ativa:
            return
        # Garante que a vida está entre a menor e a maior que têm versão (1 a 3).
        vida = min(max(vida, min(FATOR_POR_VIDA)), max(FATOR_POR_VIDA))
        if FATOR_POR_VIDA[vida] == self.fator:
            return
        # pygame.time.get_ticks() = milissegundos desde o pygame.init(). O tempo que
        # passou desde a última medição, vezes a velocidade em que estava tocando,
        # diz quanto a música avançou (em segundos da versão normal).
        agora = pygame.time.get_ticks()
        avancou = (agora - self.inicio_ms) / 1000 * self.fator
        posicao = (self.posicao + avancou) % self.duracao_base
        self._tocar_de(vida, posicao)

    def parar(self):
        if self.ativa:
            # Channel.stop() interrompe o que estiver tocando neste canal.
            self.canal.stop()

    def _tocar_de(self, vida, posicao):
        fator = FATOR_POR_VIDA[vida]
        dados = self.versoes[vida]

        # Na versão acelerada, o mesmo ponto da música fica em posicao / fator segundos.
        # Convertemos para bytes, alinhado ao tamanho de um quadro de áudio
        # (senão trocaríamos esquerdo/direito ou cortaríamos uma amostra ao meio).
        quadro = int(posicao / fator * self.taxa)
        corte = quadro * self.bytes_por_quadro
        if corte >= len(dados):
            corte = 0

        # "Gira" o loop para ele começar no ponto atual: [daqui até o fim] + [começo].
        # Assim o loop infinito continua a música sem voltar ao início.
        girado = dados[corte:] + dados[:corte]
        # pygame.mixer.Sound(buffer=bytes) cria o som a partir das amostras na memória.
        # Sound.set_volume(v) define o volume deste som (0.0 a 1.0).
        som = pygame.mixer.Sound(buffer=girado)
        som.set_volume(VOLUME_MUSICA)
        # Channel.play(som, loops=-1) toca neste canal e repete para sempre,
        # substituindo o que estava tocando nele.
        self.canal.play(som, loops=-1)

        self.fator = fator
        self.posicao = posicao
        self.inicio_ms = pygame.time.get_ticks()
