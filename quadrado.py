import random

import pygame

LADO_QUADRADO = 30  # em pixels
VELOCIDADE_QUADRADO = 2.2  # velocidade inicial, em pixels por quadro (a 60 FPS = 132 px/s)

# Cor do quadrado de acordo com a vida que resta (ataques que ainda aguenta).
# É a mesma ideia da bola central: verde -> amarelo -> vermelho a cada ataque.
CORES_POR_VIDA = {
    3: (40, 170, 60),  # verde
    2: (230, 200, 30),  # amarelo
    1: (200, 30, 30),  # vermelho
}

# Chances de um quadrado nascer mais resistente. O resto (85%) nasce vermelho.
CHANCE_VERDE = 0.05  # 5%: aguenta 3 ataques
CHANCE_AMARELO = 0.10  # 10%: aguenta 2 ataques

# Chance de, no lugar de um quadrado, nascer uma bolinha amiga (não deve ser atingida).
CHANCE_AMIGA = 0.05  # 5%
COR_AMIGA = (30, 100, 220)  # azul, para não confundir com os tiros vermelhos

# Chance de nascer num canto e vir pela diagonal (só quando a diagonal está liberada).
CHANCE_DIAGONAL = 0.15  # 15%


class Quadrado:
    """Inimigo que nasce fora de uma das bordas e anda em linha reta até a bola central."""

    # Atributo de classe: vale para todos os quadrados. A BolinhaAmiga troca para True.
    amiga = False

    def __init__(self, posicao_inicial, direcao, velocidade=VELOCIDADE_QUADRADO, vida=1):
        # Posição do CENTRO do quadrado. Usamos Vector2 (números com casas decimais)
        # para o movimento ficar preciso; o Rect abaixo só aceita números inteiros.
        self.posicao = pygame.math.Vector2(posicao_inicial)
        # normalize() deixa a direção com comprimento 1, para que o inimigo diagonal
        # ande na mesma velocidade que os outros (e não ~41% mais rápido).
        self.velocidade = pygame.math.Vector2(direcao).normalize() * velocidade
        self.vida = vida  # quantos ataques (bolinhas) ainda faltam para destruí-lo

        # pygame.Rect(x, y, largura, altura) representa um retângulo alinhado aos eixos.
        # (x, y) é o canto superior esquerdo. O Rect tem atributos práticos como
        # .center, .top, .left, .width, e métodos de colisão (colliderect, collidepoint...).
        self.rect = pygame.Rect(0, 0, LADO_QUADRADO, LADO_QUADRADO)
        # Atribuir .center move o retângulo para que seu centro fique nesse ponto.
        self.rect.center = self.posicao

    def atualizar(self):
        self.posicao += self.velocidade
        self.rect.center = self.posicao  # mantém o Rect acompanhando a posição

    def desenhar(self, tela):
        # pygame.draw.rect(superfície, cor, rect) desenha um retângulo preenchido.
        # Assim como no círculo, um parâmetro extra de largura desenharia só a borda.
        # A cor é escolhida pela vida atual, então ela muda a cada ataque recebido.
        pygame.draw.rect(tela, CORES_POR_VIDA[self.vida], self.rect)

    def receber_ataque(self):
        """Tira 1 de vida. Retorna True se o quadrado foi destruído."""
        self.vida -= 1
        return self.vida <= 0

    def encostou_na_bola(self, centro_bola, raio_bola):
        # Os quadrados andam em linha reta até o centro, então basta comparar a distância
        # entre os centros com (raio + metade do lado). Na diagonal é uma aproximação
        # (o canto do quadrado encosta um pouco antes), mas fica bom o suficiente.
        # Vector2.distance_to(ponto) calcula a distância em linha reta até o ponto.
        return self.posicao.distance_to(centro_bola) <= raio_bola + LADO_QUADRADO / 2


class BolinhaAmiga(Quadrado):
    """Bolinha aliada que vem até a bola central. Acertá-la é "fogo amigo": custa 1 vida.

    Herda de Quadrado (nasce, anda e colide do mesmo jeito); só muda o desenho
    e a marcação amiga = True, que o main.py usa para tratar a colisão diferente.
    """

    amiga = True

    def desenhar(self, tela):
        # Desenhada como círculo azul do mesmo tamanho do quadrado.
        # pygame.draw.circle(superfície, cor, centro, raio): o centro é o do Rect.
        pygame.draw.circle(tela, COR_AMIGA, self.rect.center, LADO_QUADRADO // 2)


def _sortear_trajetoria(tamanho_janela, diagonal):
    """Sorteia (posição inicial, direção) logo fora de uma borda ou, às vezes, de um canto."""
    meio = tamanho_janela / 2
    fora = -LADO_QUADRADO / 2  # nasce com o corpo inteiro fora da tela, e vai entrando
    longe = tamanho_janela - fora

    # Cada opção: (posição inicial do centro, direção do movimento).
    # A direção é sempre o sentido oposto à borda onde ele nasce.
    opcoes = [
        ((meio, fora), (0, 1)),  # nasce em cima e desce
        ((meio, longe), (0, -1)),  # nasce embaixo e sobe
        ((fora, meio), (1, 0)),  # nasce à esquerda e vai para a direita
        ((longe, meio), (-1, 0)),  # nasce à direita e vai para a esquerda
    ]
    # Cantos: nasce fora de um canto e anda na diagonal até o centro.
    opcoes_diagonais = [
        ((fora, fora), (1, 1)),  # canto superior esquerdo
        ((longe, fora), (-1, 1)),  # canto superior direito
        ((fora, longe), (1, -1)),  # canto inferior esquerdo
        ((longe, longe), (-1, -1)),  # canto inferior direito
    ]

    # Com a diagonal liberada, 15% das vezes o inimigo vem de um canto.
    if diagonal and random.random() < CHANCE_DIAGONAL:
        return random.choice(opcoes_diagonais)
    return random.choice(opcoes)


def _sortear_vida():
    """Sorteia a resistência: 5% verde (3), 10% amarelo (2), 85% vermelho (1)."""
    # random.random() devolve um número entre 0 e 1: abaixo de 0.05 (5% das vezes)
    # é verde; entre 0.05 e 0.15 (10%) é amarelo; o resto (85%) é vermelho.
    sorteio = random.random()
    if sorteio < CHANCE_VERDE:
        return 3
    if sorteio < CHANCE_VERDE + CHANCE_AMARELO:
        return 2
    return 1


def criar_quadrado_aleatorio(tamanho_janela, velocidade=VELOCIDADE_QUADRADO, diagonal=False):
    """Cria um quadrado (ou, às vezes, uma bolinha amiga) logo fora de uma borda sorteada."""
    posicao, direcao = _sortear_trajetoria(tamanho_janela, diagonal)

    # 5% das vezes nasce uma bolinha amiga no lugar do quadrado.
    if random.random() < CHANCE_AMIGA:
        return BolinhaAmiga(posicao, direcao, velocidade)

    return Quadrado(posicao, direcao, velocidade, _sortear_vida())


def criar_par_de_quadrados(tamanho_janela, velocidade=VELOCIDADE_QUADRADO, diagonal=False):
    """Cria dois quadrados ao mesmo tempo, com a MESMA vida (mesma cor), em direções diferentes."""
    vida = _sortear_vida()  # sorteada uma vez só e usada nos dois

    primeira = _sortear_trajetoria(tamanho_janela, diagonal)
    # Sorteia de novo até cair numa trajetória diferente da primeira.
    segunda = _sortear_trajetoria(tamanho_janela, diagonal)
    while segunda == primeira:
        segunda = _sortear_trajetoria(tamanho_janela, diagonal)

    return [
        Quadrado(posicao, direcao, velocidade, vida)
        for posicao, direcao in (primeira, segunda)
    ]
