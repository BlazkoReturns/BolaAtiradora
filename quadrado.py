import random

import pygame

LADO_QUADRADO = 30
VELOCIDADE_QUADRADO = 3.3  # pixels por quadro (a 60 FPS, ~200 px/s)

# Cor do quadrado de acordo com quantos ataques ele ainda aguenta.
CORES_POR_VIDA = {
    3: (40, 170, 60),  # verde
    2: (230, 200, 30),  # amarelo
    1: (200, 30, 30),  # vermelho
}

# Chances de nascer mais resistente; o resto (85%) nasce vermelho.
CHANCE_VERDE = 0.05
CHANCE_AMARELO = 0.10

# Chance de nascer uma bolinha amiga (não deve ser atingida) no lugar do quadrado.
CHANCE_AMIGA = 0.05
COR_AMIGA = (30, 100, 220)

# Chance de vir de um canto, pela diagonal (só quando a diagonal está liberada).
CHANCE_DIAGONAL = 0.15


class Quadrado:
    """Inimigo que nasce fora de uma das bordas e anda em linha reta até a bola central."""

    amiga = False

    def __init__(self, posicao_inicial, direcao, velocidade=VELOCIDADE_QUADRADO, vida=1):
        # A posição fica num Vector2 (aceita decimais) porque o Rect só guarda inteiros,
        # o que deixaria o movimento impreciso.
        self.posicao = pygame.math.Vector2(posicao_inicial)
        self.velocidade = pygame.math.Vector2(direcao).normalize() * velocidade
        self.vida = vida

        # pygame.Rect(x, y, largura, altura): retângulo alinhado aos eixos, com (x, y)
        # no canto superior esquerdo. Tem atributos como .center/.top/.left e métodos
        # de colisão (colliderect, collidepoint...). Atribuir .center move o retângulo.
        self.rect = pygame.Rect(0, 0, LADO_QUADRADO, LADO_QUADRADO)
        self.rect.center = self.posicao

    def atualizar(self):
        self.posicao += self.velocidade
        self.rect.center = self.posicao

    def desenhar(self, tela):
        # pygame.draw.rect(superfície, cor, rect) desenha um retângulo preenchido.
        pygame.draw.rect(tela, CORES_POR_VIDA[self.vida], self.rect)

    def receber_ataque(self):
        """Tira 1 de vida. Retorna True se o quadrado foi destruído."""
        self.vida -= 1
        return self.vida <= 0

    def encostou_na_bola(self, centro_bola, raio_bola):
        # Compara a distância entre os centros com (raio + metade do lado). Na diagonal
        # é uma aproximação, mas suficiente. Vector2.distance_to() mede a distância.
        return self.posicao.distance_to(centro_bola) <= raio_bola + LADO_QUADRADO / 2


class BolinhaAmiga(Quadrado):
    """Bolinha aliada que vem até a bola central. Acertá-la é "fogo amigo": custa 1 vida.

    Herda de Quadrado; só muda o desenho e a marcação amiga = True.
    """

    amiga = True

    def desenhar(self, tela):
        pygame.draw.circle(tela, COR_AMIGA, self.rect.center, LADO_QUADRADO // 2)


def _sortear_trajetoria(tamanho_janela, diagonal):
    """Sorteia (posição inicial, direção) logo fora de uma borda ou, às vezes, de um canto."""
    meio = tamanho_janela / 2
    fora = -LADO_QUADRADO / 2  # nasce com o corpo inteiro fora da tela
    longe = tamanho_janela - fora

    opcoes = [
        ((meio, fora), (0, 1)),  # em cima, desce
        ((meio, longe), (0, -1)),  # embaixo, sobe
        ((fora, meio), (1, 0)),  # à esquerda, vai para a direita
        ((longe, meio), (-1, 0)),  # à direita, vai para a esquerda
    ]
    opcoes_diagonais = [
        ((fora, fora), (1, 1)),
        ((longe, fora), (-1, 1)),
        ((fora, longe), (1, -1)),
        ((longe, longe), (-1, -1)),
    ]

    if diagonal and random.random() < CHANCE_DIAGONAL:
        return random.choice(opcoes_diagonais)
    return random.choice(opcoes)


def _sortear_vida():
    """Sorteia a resistência: 5% verde (3), 10% amarelo (2), 85% vermelho (1)."""
    sorteio = random.random()
    if sorteio < CHANCE_VERDE:
        return 3
    if sorteio < CHANCE_VERDE + CHANCE_AMARELO:
        return 2
    return 1


def criar_quadrado_aleatorio(tamanho_janela, velocidade=VELOCIDADE_QUADRADO, diagonal=False):
    """Cria um quadrado (ou, às vezes, uma bolinha amiga) logo fora de uma borda sorteada."""
    posicao, direcao = _sortear_trajetoria(tamanho_janela, diagonal)

    if random.random() < CHANCE_AMIGA:
        return BolinhaAmiga(posicao, direcao, velocidade)

    return Quadrado(posicao, direcao, velocidade, _sortear_vida())


def criar_par_de_quadrados(tamanho_janela, velocidade=VELOCIDADE_QUADRADO, diagonal=False):
    """Cria dois quadrados ao mesmo tempo, com a MESMA vida (mesma cor), em direções diferentes."""
    vida = _sortear_vida()

    primeira = _sortear_trajetoria(tamanho_janela, diagonal)
    segunda = _sortear_trajetoria(tamanho_janela, diagonal)
    while segunda == primeira:
        segunda = _sortear_trajetoria(tamanho_janela, diagonal)

    return [
        Quadrado(posicao, direcao, velocidade, vida)
        for posicao, direcao in (primeira, segunda)
    ]
