import random

import pygame

LADO_QUADRADO = 30  # em pixels
VELOCIDADE_QUADRADO = 2  # pixels por quadro (a 60 FPS = 120 pixels por segundo)
COR_QUADRADO = (40, 40, 40)  # cinza escuro


class Quadrado:
    """Inimigo que nasce fora de uma das bordas e anda em linha reta até a bola central."""

    def __init__(self, posicao_inicial, direcao):
        # Posição do CENTRO do quadrado. Usamos Vector2 (números com casas decimais)
        # para o movimento ficar preciso; o Rect abaixo só aceita números inteiros.
        self.posicao = pygame.math.Vector2(posicao_inicial)
        self.velocidade = pygame.math.Vector2(direcao) * VELOCIDADE_QUADRADO

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
        pygame.draw.rect(tela, COR_QUADRADO, self.rect)

    def encostou_na_bola(self, centro_bola, raio_bola):
        # Os quadrados andam só na horizontal ou na vertical em direção ao centro,
        # então basta comparar a distância entre os centros com (raio + metade do lado).
        # Vector2.distance_to(ponto) calcula a distância em linha reta até o ponto.
        return self.posicao.distance_to(centro_bola) <= raio_bola + LADO_QUADRADO / 2


def criar_quadrado_aleatorio(tamanho_janela):
    """Cria um quadrado logo fora de uma borda sorteada, andando em direção ao centro."""
    meio = tamanho_janela / 2
    fora = -LADO_QUADRADO / 2  # nasce com o corpo inteiro fora da tela, e vai entrando

    # Cada opção: (posição inicial do centro, direção do movimento).
    # A direção é sempre o sentido oposto à borda onde ele nasce.
    opcoes = [
        ((meio, fora), (0, 1)),  # nasce em cima e desce
        ((meio, tamanho_janela - fora), (0, -1)),  # nasce embaixo e sobe
        ((fora, meio), (1, 0)),  # nasce à esquerda e vai para a direita
        ((tamanho_janela - fora, meio), (-1, 0)),  # nasce à direita e vai para a esquerda
    ]
    posicao, direcao = random.choice(opcoes)
    return Quadrado(posicao, direcao)
