import pygame

RAIO_BOLINHA = 8
VELOCIDADE_BOLINHA = 8  # pixels por quadro
COR_BOLINHA = (220, 50, 50)


class Bolinha:
    """Pequena bola disparada pela bola central, que anda em linha reta."""

    def __init__(self, centro_bola, raio_bola, direcao):
        # pygame.math.Vector2: vetor 2D (x, y) que aceita contas diretas (somar,
        # multiplicar por número...). normalize() deixa o comprimento igual a 1,
        # para o tiro diagonal (1, 1) não ser ~41% mais rápido.
        direcao = pygame.math.Vector2(direcao).normalize()

        # Nasce no perímetro da bola central, na direção do tiro.
        self.posicao = pygame.math.Vector2(centro_bola) + direcao * raio_bola
        self.velocidade = direcao * VELOCIDADE_BOLINHA

    def atualizar(self):
        self.posicao += self.velocidade

    def desenhar(self, tela):
        pygame.draw.circle(tela, COR_BOLINHA, self.posicao, RAIO_BOLINHA)

    def rect(self):
        # Caixa em volta do círculo, usada nas colisões. Como bolinha e alvo andam
        # na mesma linha reta, essa aproximação basta.
        caixa = pygame.Rect(0, 0, RAIO_BOLINHA * 2, RAIO_BOLINHA * 2)
        caixa.center = self.posicao
        return caixa

    def saiu_da_tela(self, largura, altura):
        # A margem de RAIO_BOLINHA garante que a bolinha inteira já passou da borda.
        x, y = self.posicao
        return (
            x < -RAIO_BOLINHA
            or x > largura + RAIO_BOLINHA
            or y < -RAIO_BOLINHA
            or y > altura + RAIO_BOLINHA
        )
