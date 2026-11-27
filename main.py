import random

import pygame

from bolinha import Bolinha
from quadrado import criar_par_de_quadrados, criar_quadrado_aleatorio
import recordes
from sons import carregar_sons

TAMANHO_JANELA = 600  # largura e altura, em pixels
FPS = 60

# Cores no formato (R, G, B), de 0 a 255.
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
VERMELHO = (200, 30, 30)
VERDE = (40, 170, 60)
AMARELO = (230, 200, 30)
CINZA = (110, 110, 110)

RAIO_CIRCULO = 40

# Quantos danos a bola central aguenta, e a cor dela para cada vida restante.
VIDA_MAXIMA_BOLA = 3
CORES_POR_VIDA = {
    3: VERDE,
    2: AMARELO,
    1: VERMELHO,
}

INTERVALO_QUADRADOS_MS = 650  # intervalo fixo entre o nascimento de quadrados

# pygame.USEREVENT é o primeiro número de evento livre para o próprio jogo usar.
EVENTO_NOVO_QUADRADO = pygame.USEREVENT + 1

# Tecla -> direção do tiro (x, y). No pygame, y positivo aponta para BAIXO.
# pygame.K_* são as constantes que identificam cada tecla (vêm em evento.key).
DIRECOES = {
    pygame.K_UP: (0, -1),
    pygame.K_w: (0, -1),
    pygame.K_DOWN: (0, 1),
    pygame.K_s: (0, 1),
    pygame.K_LEFT: (-1, 0),
    pygame.K_a: (-1, 0),
    pygame.K_RIGHT: (1, 0),
    pygame.K_d: (1, 0),
    # K_KP* são as teclas do teclado numérico (keypad), diferentes de K_8, K_2...
    # Com o Num Lock desligado, o teclado numérico manda setas/Home/PgUp etc.
    pygame.K_KP8: (0, -1),
    pygame.K_KP2: (0, 1),
    pygame.K_KP4: (-1, 0),
    pygame.K_KP6: (1, 0),
    # Diagonais: Q E Z C e 7 9 1 3 do teclado numérico.
    pygame.K_q: (-1, -1),
    pygame.K_KP7: (-1, -1),
    pygame.K_e: (1, -1),
    pygame.K_KP9: (1, -1),
    pygame.K_z: (-1, 1),
    pygame.K_KP1: (-1, 1),
    pygame.K_c: (1, 1),
    pygame.K_KP3: (1, 1),
}

# Animação da tela inicial: a bola sai daqui e desliza até o centro, crescendo.
POSICAO_BOLA_INICIO = (TAMANHO_JANELA // 2, 190)
RAIO_BOLA_INICIO = 25
DURACAO_TRANSICAO_MS = 1200

PONTOS_PARA_DIAGONAL = 50  # a partir daqui, inimigos também vêm pelas diagonais

# A partir daqui, às vezes nascem dois quadrados juntos (mesma cor, direções diferentes).
PONTOS_PARA_DUPLO = 80
CHANCE_DUPLO = 0.20

# Com True, ESPAÇO soma PONTOS_DEBUG pontos (para testar níveis altos).
# Troque para False antes de "entregar" o jogo.
DEBUG = True
PONTOS_DEBUG = 10


def desenhar_texto_centralizado(tela, fonte, texto, cor, y):
    # Font.render(texto, antialias, cor) NÃO desenha na tela: cria uma nova Surface
    # (uma "imagem") com o texto. antialias=True suaviza as bordas das letras.
    imagem = fonte.render(texto, True, cor)

    # Surface.get_rect() devolve um Rect do tamanho da imagem; center= já o posiciona.
    retangulo = imagem.get_rect(center=(TAMANHO_JANELA // 2, y))

    # Surface.blit(imagem, posição) "carimba" uma Surface sobre outra. Com um Rect
    # como posição, o pygame usa o canto superior esquerdo dele.
    tela.blit(imagem, retangulo)


def desenhar_ranking(tela, fonte, lista, y, destaque=None):
    """Desenha a tabela de recordes a partir da altura y. destaque = posição a realçar."""
    if not lista:
        desenhar_texto_centralizado(tela, fonte, "Nenhum recorde ainda", CINZA, y)
        return
    for posicao, recorde in enumerate(lista):
        cor = VERMELHO if posicao == destaque else PRETO
        linha = f"{posicao + 1}.  {recorde['nome']:<3}   {recorde['pontos']:>5}"
        desenhar_texto_centralizado(tela, fonte, linha, cor, y + posicao * 32)


def desenhar_veu(tela):
    """Cobre a tela com um branco semitransparente, para o texto ficar legível por cima.

    CONCEITO: transparência (canal alfa). Além de R, G e B, uma cor pode ter um 4º
    valor, o "alfa": 0 = totalmente transparente, 255 = totalmente opaco.
    """
    # pygame.SRCALPHA faz a Surface guardar alfa por pixel (sem ele, o alfa é ignorado).
    veu = pygame.Surface((TAMANHO_JANELA, TAMANHO_JANELA), pygame.SRCALPHA)
    veu.fill((255, 255, 255, 210))
    # No blit, o pygame mistura as cores do véu com o que já está desenhado embaixo.
    tela.blit(veu, (0, 0))


def piscando():
    """True e False alternando a cada meio segundo, para textos que piscam."""
    # pygame.time.get_ticks() = milissegundos desde o pygame.init().
    return (pygame.time.get_ticks() // 500) % 2 == 0


def main():
    # pygame.mixer.pre_init(frequência, formato, canais, buffer) configura o áudio
    # ANTES de o pygame.init() abrir o mixer: 44100 Hz, -16 = 16 bits com sinal
    # (o formato que sons.py gera), estéreo e buffer pequeno (menos atraso no som).
    pygame.mixer.pre_init(44100, -16, 2, 512)

    # pygame.init() inicializa todos os módulos do pygame (vídeo, fontes, som...).
    pygame.init()

    sons = carregar_sons()

    # pygame.display.set_mode((largura, altura)) cria a janela e devolve a Surface
    # onde tudo é desenhado.
    tela = pygame.display.set_mode((TAMANHO_JANELA, TAMANHO_JANELA))
    pygame.display.set_caption("Bola Atiradora")  # título da janela

    # pygame.time.Clock() controla a velocidade do loop (ver relogio.tick no fim).
    relogio = pygame.time.Clock()

    # pygame.font.Font(arquivo, tamanho); None usa a fonte padrão embutida.
    fonte_grande = pygame.font.Font(None, 72)
    fonte_pequena = pygame.font.Font(None, 32)
    fonte_media = pygame.font.Font(None, 44)

    # (0, 0) é o canto SUPERIOR ESQUERDO; x cresce para a direita e y para BAIXO.
    centro = (TAMANHO_JANELA // 2, TAMANHO_JANELA // 2)

    lista_recordes = recordes.carregar()

    # Telas do jogo:
    #   "inicio"    -> título e a bola
    #   "transicao" -> a bola desliza até o centro (depois de apertar ENTER)
    #   "jogando"   -> a partida em si
    #   "iniciais"  -> fez recorde: digitando as iniciais
    #   "fim"       -> fim de jogo, com a tabela de recordes
    estado = "inicio"
    inicio_transicao_ms = 0

    # Estado da partida; os valores reais são definidos ao começar cada partida.
    bolinhas = []
    quadrados = []
    pontos = 0
    vida_bola = VIDA_MAXIMA_BOLA
    usou_debug = False  # partida com debug não vale recorde
    iniciais = ""
    posicao_recorde = None  # posição do recorde novo na tabela, para destacar

    # Game loop: a cada volta, 1) lê os eventos, 2) atualiza o jogo e 3) desenha.
    rodando = True
    while rodando:
        comecar_partida = False

        # ---------- 1) EVENTOS ----------
        # pygame.event.get() devolve os eventos desde a última chamada (teclas,
        # mouse, fechar a janela...). Precisa rodar todo quadro, senão a janela trava.
        for evento in pygame.event.get():
            # pygame.QUIT: o usuário clicou no X da janela.
            if evento.type == pygame.QUIT:
                rodando = False

            # pygame.KEYDOWN é gerado uma vez quando a tecla é pressionada (segurar
            # não repete). K_RETURN = ENTER, K_KP_ENTER = ENTER do teclado numérico.
            elif estado == "inicio":
                if evento.type == pygame.KEYDOWN:
                    if evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        estado = "transicao"
                        inicio_transicao_ms = pygame.time.get_ticks()
                    elif evento.key == pygame.K_ESCAPE:
                        rodando = False

            elif estado == "transicao":
                pass  # durante a animação as teclas são ignoradas

            elif estado == "iniciais":
                if evento.type == pygame.KEYDOWN:
                    if evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER) and iniciais:
                        posicao_recorde = recordes.adicionar(lista_recordes, iniciais, pontos)
                        recordes.salvar(lista_recordes)
                        estado = "fim"
                    elif evento.key == pygame.K_BACKSPACE:
                        iniciais = iniciais[:-1]
                    # evento.unicode é o caractere que a tecla produz, já considerando
                    # Shift e o layout do teclado. Aceitamos só letras A-Z.
                    elif (
                        len(iniciais) < recordes.TAMANHO_NOME
                        and evento.unicode.isascii()
                        and evento.unicode.isalpha()
                    ):
                        iniciais += evento.unicode.upper()

            elif estado == "fim":
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_r:
                        comecar_partida = True
                    elif evento.key == pygame.K_ESCAPE:
                        estado = "inicio"

            # A partir daqui, estado == "jogando".

            elif DEBUG and evento.type == pygame.KEYDOWN and evento.key == pygame.K_SPACE:
                pontos += PONTOS_DEBUG
                usou_debug = True

            elif evento.type == pygame.KEYDOWN and evento.key in DIRECOES:
                direcao = DIRECOES[evento.key]
                bolinhas.append(Bolinha(centro, RAIO_CIRCULO, direcao))
                sons["tiro"].play()

            elif evento.type == EVENTO_NOVO_QUADRADO:
                diagonal_liberada = pontos >= PONTOS_PARA_DIAGONAL
                if pontos >= PONTOS_PARA_DUPLO and random.random() < CHANCE_DUPLO:
                    quadrados.extend(
                        criar_par_de_quadrados(TAMANHO_JANELA, diagonal=diagonal_liberada)
                    )
                else:
                    quadrados.append(
                        criar_quadrado_aleatorio(TAMANHO_JANELA, diagonal=diagonal_liberada)
                    )

        # Progresso da animação inicial: 0.0 (começo) a 1.0 (bola no centro).
        progresso = 0.0
        if estado == "transicao":
            progresso = (pygame.time.get_ticks() - inicio_transicao_ms) / DURACAO_TRANSICAO_MS
            if progresso >= 1.0:
                progresso = 1.0
                comecar_partida = True

        if comecar_partida:
            bolinhas = []
            quadrados = []
            pontos = 0
            vida_bola = VIDA_MAXIMA_BOLA
            usou_debug = False
            iniciais = ""
            posicao_recorde = None
            estado = "jogando"
            # pygame.time.set_timer(evento, ms) coloca o evento na fila a cada intervalo.
            # Chamar de novo para o mesmo evento substitui o timer anterior.
            pygame.time.set_timer(EVENTO_NOVO_QUADRADO, INTERVALO_QUADRADOS_MS)

        # ---------- 2) ATUALIZAÇÃO ----------
        if estado == "jogando":
            # Comparado no fim do quadro, para tocar o som de dano uma vez só.
            vida_antes = vida_bola

            for bolinha in bolinhas:
                bolinha.atualizar()

            # Tiro que sai da tela é um tiro errado e custa 1 de vida (pune o "spam").
            errados = [b for b in bolinhas if b.saiu_da_tela(TAMANHO_JANELA, TAMANHO_JANELA)]
            vida_bola -= len(errados)
            bolinhas = [b for b in bolinhas if b not in errados]

            for quadrado in quadrados:
                quadrado.atualizar()

            # Bolinha que acerta sempre some. Quadrado perde 1 de vida (e vale ponto se
            # for destruído); bolinha amiga atingida é fogo amigo e custa 1 de vida.
            # Rect.colliderect(outro) retorna True se os dois retângulos se sobrepõem.
            for quadrado in quadrados[:]:  # cópia, pois removemos itens durante o laço
                for bolinha in bolinhas:
                    if quadrado.rect.colliderect(bolinha.rect()):
                        bolinhas.remove(bolinha)
                        if quadrado.amiga:
                            quadrados.remove(quadrado)
                            vida_bola -= 1
                        elif quadrado.receber_ataque():
                            quadrados.remove(quadrado)
                            pontos += 1
                            sons["destruido"].play()
                        else:
                            sons["acerto"].play()
                        break  # uma bolinha por quadrado por quadro

            # Quadrado que chega na bola tira 1 de vida; bolinha amiga só some.
            for quadrado in quadrados[:]:
                if quadrado.encostou_na_bola(centro, RAIO_CIRCULO):
                    quadrados.remove(quadrado)
                    if not quadrado.amiga:
                        vida_bola -= 1
            if vida_bola <= 0:
                vida_bola = 0
                sons["fim"].play()
                # Intervalo 0 desliga o timer.
                pygame.time.set_timer(EVENTO_NOVO_QUADRADO, 0)
                if not usou_debug and recordes.entra_no_ranking(lista_recordes, pontos):
                    estado = "iniciais"
                else:
                    estado = "fim"
            elif vida_bola < vida_antes:
                sons["dano"].play()

        # ---------- 3) DESENHO ----------
        # Surface.fill(cor) pinta a superfície inteira, apagando o quadro anterior.
        tela.fill(BRANCO)

        if estado in ("inicio", "transicao"):
            # Easing (smoothstep): transforma o progresso linear numa curva em "S",
            # para a bola acelerar no começo e frear no fim.
            suave = progresso * progresso * (3 - 2 * progresso)

            titulo = fonte_grande.render("BOLA ATIRADORA", True, PRETO)
            # Surface.set_alpha(0 a 255): transparência da superfície inteira, para o
            # título desbotar durante a animação.
            titulo.set_alpha(int(255 * (1 - suave)))
            tela.blit(titulo, titulo.get_rect(center=(TAMANHO_JANELA // 2, 90)))

            # Vector2.lerp(destino, t) devolve o ponto a uma fração t do caminho até o destino.
            posicao_bola = pygame.math.Vector2(POSICAO_BOLA_INICIO).lerp(centro, suave)
            raio_bola = RAIO_BOLA_INICIO + (RAIO_CIRCULO - RAIO_BOLA_INICIO) * suave
            # pygame.draw.circle(superfície, cor, centro, raio) desenha um círculo preenchido.
            pygame.draw.circle(tela, VERDE, posicao_bola, raio_bola)

        else:
            # Cena da partida; em "iniciais" e "fim" ela aparece congelada, ao fundo.
            # No fim de jogo (vida 0) mantemos o vermelho.
            cor_bola = CORES_POR_VIDA.get(vida_bola, VERMELHO)
            pygame.draw.circle(tela, cor_bola, centro, RAIO_CIRCULO)

            # O que é desenhado por último aparece na frente.
            for bolinha in bolinhas:
                bolinha.desenhar(tela)

            for quadrado in quadrados:
                quadrado.desenhar(tela)

            tela.blit(fonte_pequena.render(f"Pontos: {pontos}", True, PRETO), (10, 10))

            # topright= posiciona o texto pelo canto superior direito, colado na borda.
            texto_recorde = fonte_pequena.render(
                f"Recorde: {max(recordes.melhor(lista_recordes), pontos)}", True, CINZA
            )
            tela.blit(texto_recorde, texto_recorde.get_rect(topright=(TAMANHO_JANELA - 10, 10)))

        if estado == "iniciais":
            desenhar_veu(tela)
            desenhar_texto_centralizado(tela, fonte_grande, "NOVO RECORDE!", VERMELHO, 150)
            desenhar_texto_centralizado(tela, fonte_media, f"{pontos} pontos", PRETO, 220)
            desenhar_texto_centralizado(
                tela, fonte_pequena, "Digite suas iniciais:", PRETO, 300
            )
            # Letras digitadas e "_" nas que faltam ("AB_"); o da próxima letra pisca.
            faltam = recordes.TAMANHO_NOME - len(iniciais)
            cursor = "_" if piscando() else " "
            campo = iniciais + (cursor + "_" * (faltam - 1) if faltam else "")
            desenhar_texto_centralizado(tela, fonte_grande, " ".join(campo), PRETO, 370)
            desenhar_texto_centralizado(
                tela, fonte_pequena, "ENTER para confirmar", CINZA, 450
            )

        elif estado == "fim":
            desenhar_veu(tela)
            desenhar_texto_centralizado(tela, fonte_grande, "FIM DE JOGO", VERMELHO, 110)
            desenhar_texto_centralizado(tela, fonte_media, f"{pontos} pontos", PRETO, 170)
            if usou_debug:
                desenhar_texto_centralizado(
                    tela, fonte_pequena, "(debug usado: não vale recorde)", CINZA, 205
                )
            desenhar_texto_centralizado(tela, fonte_media, "RECORDES", PRETO, 260)
            desenhar_ranking(tela, fonte_pequena, lista_recordes, 300, posicao_recorde)
            desenhar_texto_centralizado(
                tela, fonte_pequena, "R: jogar de novo    ESC: tela inicial", PRETO, 500
            )

        # pygame.display.flip() mostra na janela tudo o que foi desenhado em memória.
        pygame.display.flip()

        # Clock.tick(FPS) espera o necessário para o loop não passar de FPS voltas por
        # segundo, deixando a velocidade igual em qualquer computador.
        relogio.tick(FPS)

    # pygame.quit() finaliza os módulos do pygame e fecha a janela.
    pygame.quit()


if __name__ == "__main__":
    main()
