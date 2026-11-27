import pygame

RAIO_BOLINHA = 8  # em pixels
VELOCIDADE_BOLINHA = 8  # pixels por quadro (a 60 FPS = 480 pixels por segundo)
COR_BOLINHA = (220, 50, 50)  # vermelho


class Bolinha:
    """Pequena bola disparada pela bola central, que anda em linha reta."""

    def __init__(self, centro_bola, raio_bola, direcao):
        # pygame.math.Vector2(x, y) é um vetor 2D do pygame. Ele guarda um par (x, y)
        # e permite fazer contas diretamente: somar vetores, multiplicar por um número,
        # normalizar etc. É muito usado para posições e velocidades.
        # Vector2.normalize() devolve um vetor com a mesma direção, mas comprimento 1.
        # Sem isso, o tiro diagonal (1, 1) teria comprimento ~1,41 e seria mais rápido.
        direcao = pygame.math.Vector2(direcao).normalize()

        # Nascimento: o centro da bolinha fica no perímetro da bola central.
        # Partimos do centro da bola e andamos "raio_bola" pixels na direção do tiro.
        # (direcao tem comprimento 1, então direcao * raio_bola tem comprimento raio_bola.)
        self.posicao = pygame.math.Vector2(centro_bola) + direcao * raio_bola

        # Velocidade: quanto a posição muda a cada quadro.
        self.velocidade = direcao * VELOCIDADE_BOLINHA

    def atualizar(self):
        # Somar dois Vector2 soma x com x e y com y: a bolinha anda um "passo".
        self.posicao += self.velocidade

    def desenhar(self, tela):
        # pygame.draw.circle aceita um Vector2 como centro (ele usa o x e o y do vetor).
        pygame.draw.circle(tela, COR_BOLINHA, self.posicao, RAIO_BOLINHA)

    def rect(self):
        # Retângulo (pygame.Rect) que envolve a bolinha, usado para testar colisões.
        # Como bolinha e alvo andam na mesma linha reta (horizontal, vertical ou
        # diagonal), essa aproximação "caixa em volta do círculo" é suficiente.
        caixa = pygame.Rect(0, 0, RAIO_BOLINHA * 2, RAIO_BOLINHA * 2)
        caixa.center = self.posicao
        return caixa

    def saiu_da_tela(self, largura, altura):
        # Consideramos que saiu quando a bolinha inteira passou da borda
        # (por isso a margem de RAIO_BOLINHA).
        x, y = self.posicao
        return (
            x < -RAIO_BOLINHA
            or x > largura + RAIO_BOLINHA
            or y < -RAIO_BOLINHA
            or y > altura + RAIO_BOLINHA
        )
