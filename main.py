import pygame  # Biblioteca para criar jogos 2D: janelas, desenho, teclado/mouse, sons etc.

from bolinha import Bolinha
from quadrado import criar_quadrado_aleatorio

# Configurações da janela (quadrada)
TAMANHO_JANELA = 600  # largura e altura em pixels
FPS = 60  # quadros (frames) por segundo: quantas vezes a tela é redesenhada a cada segundo

# Cores no formato (R, G, B): cada valor vai de 0 a 255 (vermelho, verde, azul)
BRANCO = (255, 255, 255)
AZUL = (30, 100, 220)
PRETO = (0, 0, 0)
VERMELHO = (200, 30, 30)

# Círculo
RAIO_CIRCULO = 40  # em pixels

# Intervalo entre o nascimento de quadrados, em milissegundos.
INTERVALO_QUADRADOS_MS = 1000

# pygame.USEREVENT é o primeiro número reservado para eventos criados pelo próprio jogo.
# Criamos o nosso tipo de evento "nasce um quadrado" com esse número.
EVENTO_NOVO_QUADRADO = pygame.USEREVENT + 1

# Mapa tecla -> direção do tiro (x, y). Lembre: y positivo aponta para BAIXO.
# pygame.K_UP, pygame.K_w etc. são constantes do pygame que identificam cada tecla
# (setas e letras W, A, S, D). Elas vêm no atributo "key" dos eventos de teclado.
DIRECOES = {
    pygame.K_UP: (0, -1),
    pygame.K_w: (0, -1),
    pygame.K_DOWN: (0, 1),
    pygame.K_s: (0, 1),
    pygame.K_LEFT: (-1, 0),
    pygame.K_a: (-1, 0),
    pygame.K_RIGHT: (1, 0),
    pygame.K_d: (1, 0),
}


def desenhar_texto_centralizado(tela, fonte, texto, cor, y):
    # Font.render(texto, antialias, cor) NÃO desenha na tela: ele cria uma nova
    # Surface (uma "imagem") contendo o texto. antialias=True suaviza as bordas das letras.
    imagem = fonte.render(texto, True, cor)

    # Surface.get_rect() devolve um Rect do tamanho da imagem. Ajustamos o centro
    # dele para posicionar o texto centralizado horizontalmente na altura y.
    retangulo = imagem.get_rect(center=(TAMANHO_JANELA // 2, y))

    # Surface.blit(imagem, posição) "carimba" uma Surface sobre outra.
    # A posição pode ser um Rect: o pygame usa o canto superior esquerdo dele.
    tela.blit(imagem, retangulo)


def main():
    # pygame.init() inicializa todos os módulos do pygame (vídeo, fontes, som...).
    # Deve ser chamado antes de usar qualquer outra função do pygame.
    pygame.init()

    # pygame.display.set_mode((largura, altura)) cria a janela do jogo e retorna
    # uma "Surface": a superfície (tela) onde tudo será desenhado.
    tela = pygame.display.set_mode((TAMANHO_JANELA, TAMANHO_JANELA))

    # pygame.display.set_caption(texto) define o título que aparece na barra da janela.
    pygame.display.set_caption("Bola Atiradora")

    # pygame.time.Clock() cria um relógio usado para controlar a velocidade do jogo
    # (limitar o número de quadros por segundo).
    relogio = pygame.time.Clock()

    # pygame.font.Font(arquivo, tamanho) carrega uma fonte para escrever textos.
    # Passando None como arquivo, o pygame usa sua fonte padrão embutida.
    fonte_grande = pygame.font.Font(None, 72)
    fonte_pequena = pygame.font.Font(None, 32)

    # Coordenadas no pygame: (0, 0) é o canto SUPERIOR ESQUERDO da janela.
    # x cresce para a direita e y cresce para BAIXO.
    centro = (TAMANHO_JANELA // 2, TAMANHO_JANELA // 2)

    # Estado da partida. Ficam aqui para podermos reiniciar facilmente.
    bolinhas = []  # bolinhas voando na tela
    quadrados = []  # quadrados (inimigos) na tela
    pontos = 0  # quadrados destruídos
    fim_de_jogo = False

    # pygame.time.set_timer(evento, milissegundos) faz o pygame colocar esse evento
    # na fila automaticamente, repetidamente, a cada intervalo. Nós o recebemos
    # no pygame.event.get() como qualquer outro evento.
    pygame.time.set_timer(EVENTO_NOVO_QUADRADO, INTERVALO_QUADRADOS_MS)

    # Loop principal do jogo ("game loop"): a cada volta ele
    # 1) lê os eventos, 2) atualiza o estado do jogo e 3) desenha a tela.
    rodando = True
    while rodando:
        # ---------- 1) EVENTOS ----------
        # pygame.event.get() retorna a lista de eventos que aconteceram desde a
        # última chamada (teclas, cliques, mover o mouse, fechar a janela...).
        # Precisa ser chamado todo quadro, senão a janela "trava" para o Windows.
        for evento in pygame.event.get():
            # pygame.QUIT é o evento gerado quando o usuário clica no X da janela.
            if evento.type == pygame.QUIT:
                rodando = False

            elif fim_de_jogo:
                # Na tela de fim de jogo, só a tecla R importa: reinicia a partida.
                # pygame.K_r é a constante da tecla R.
                if evento.type == pygame.KEYDOWN and evento.key == pygame.K_r:
                    bolinhas = []
                    quadrados = []
                    pontos = 0
                    fim_de_jogo = False

            # pygame.KEYDOWN é gerado UMA vez no momento em que uma tecla é pressionada
            # (segurar a tecla não gera novos KEYDOWN). evento.key diz qual tecla foi.
            # Assim, cada toque dispara exatamente uma bolinha.
            elif evento.type == pygame.KEYDOWN and evento.key in DIRECOES:
                direcao = DIRECOES[evento.key]
                bolinhas.append(Bolinha(centro, RAIO_CIRCULO, direcao))

            # Nosso evento de timer: a cada 1 segundo nasce um quadrado numa borda sorteada.
            elif evento.type == EVENTO_NOVO_QUADRADO:
                quadrados.append(criar_quadrado_aleatorio(TAMANHO_JANELA))

        # ---------- 2) ATUALIZAÇÃO ----------
        # Com o jogo encerrado, nada se mexe: a tela fica "congelada".
        if not fim_de_jogo:
            # Atualiza a posição de cada bolinha...
            for bolinha in bolinhas:
                bolinha.atualizar()

            # ...e remove as que já saíram da tela (senão a lista cresceria para sempre).
            bolinhas = [
                b for b in bolinhas if not b.saiu_da_tela(TAMANHO_JANELA, TAMANHO_JANELA)
            ]

            # Move os quadrados em direção à bola central.
            for quadrado in quadrados:
                quadrado.atualizar()

            # Colisão bolinha x quadrado: quando se tocam, os dois são destruídos.
            # Rect.colliderect(outro_rect) retorna True se os dois retângulos se sobrepõem.
            for quadrado in quadrados[:]:  # [:] percorre uma cópia, pois vamos remover itens
                for bolinha in bolinhas:
                    if quadrado.rect.colliderect(bolinha.rect()):
                        quadrados.remove(quadrado)
                        bolinhas.remove(bolinha)
                        pontos += 1
                        break  # este quadrado já morreu; passa para o próximo

            # Se algum quadrado chegou na bola central, o jogo acaba.
            if any(q.encostou_na_bola(centro, RAIO_CIRCULO) for q in quadrados):
                fim_de_jogo = True

        # ---------- 3) DESENHO ----------
        # Surface.fill(cor) pinta a superfície inteira com uma cor.
        # Usamos para "apagar" o quadro anterior antes de desenhar o novo.
        tela.fill(BRANCO)

        # pygame.draw.circle(superfície, cor, centro, raio) desenha um círculo preenchido.
        # Um 5º parâmetro opcional (largura) desenharia só o contorno, ex.: largura=3.
        pygame.draw.circle(tela, AZUL, centro, RAIO_CIRCULO)

        # Desenhamos as bolinhas depois da bola central, então elas ficam "por cima"
        # dela: no pygame, o que é desenhado por último aparece na frente.
        for bolinha in bolinhas:
            bolinha.desenhar(tela)

        for quadrado in quadrados:
            quadrado.desenhar(tela)

        # Placar no canto superior esquerdo. Aqui blit recebe uma tupla (x, y),
        # que é a posição do canto superior esquerdo do texto.
        tela.blit(fonte_pequena.render(f"Pontos: {pontos}", True, PRETO), (10, 10))

        # Mensagem de fim de jogo por cima de tudo (desenhada por último).
        if fim_de_jogo:
            desenhar_texto_centralizado(tela, fonte_grande, "FIM DE JOGO", VERMELHO, 200)
            desenhar_texto_centralizado(
                tela, fonte_pequena, "Pressione R para jogar de novo", PRETO, 400
            )

        # pygame.display.flip() mostra na janela tudo o que foi desenhado neste quadro.
        # Os desenhos são feitos "em memória" e só aparecem depois do flip.
        pygame.display.flip()

        # Clock.tick(FPS) pausa o tempo necessário para o loop não passar de FPS
        # voltas por segundo, deixando a velocidade do jogo igual em qualquer computador.
        relogio.tick(FPS)

    # pygame.quit() finaliza os módulos do pygame e fecha a janela corretamente.
    pygame.quit()


# Executa main() apenas quando este arquivo é rodado diretamente (python main.py),
# e não quando é importado por outro arquivo.
if __name__ == "__main__":
    main()
