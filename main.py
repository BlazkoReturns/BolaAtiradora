import random

import pygame  # Biblioteca para criar jogos 2D: janelas, desenho, teclado/mouse, sons etc.

from bolinha import Bolinha
from quadrado import VELOCIDADE_QUADRADO, criar_par_de_quadrados, criar_quadrado_aleatorio
import recordes
from musica import Trilha
from sons import carregar_sons

# Configurações da janela (quadrada)
TAMANHO_JANELA = 600  # largura e altura em pixels
FPS = 60  # quadros (frames) por segundo: quantas vezes a tela é redesenhada a cada segundo

# Cores no formato (R, G, B): cada valor vai de 0 a 255 (vermelho, verde, azul)
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
VERMELHO = (200, 30, 30)
VERDE = (40, 170, 60)
AMARELO = (230, 200, 30)
CINZA = (110, 110, 110)  # textos secundários

# Círculo
RAIO_CIRCULO = 40  # em pixels

# Vida da bola central: quantos contatos com quadrados ela aguenta.
VIDA_MAXIMA_BOLA = 3

# Cor da bola central de acordo com a vida que resta.
# Começa verde, fica amarela após 1 contato, vermelha após 2; no 3º é fim de jogo.
CORES_POR_VIDA = {
    3: VERDE,
    2: AMARELO,
    1: VERMELHO,
}

# Dificuldade: a cada PONTOS_POR_NIVEL pontos o jogo sobe de nível.
# A cada nível os quadrados ficam 10% mais rápidos e nascem com 10% menos intervalo.
PONTOS_POR_NIVEL = 10
AUMENTO_VELOCIDADE = 0.10  # 10%
REDUCAO_INTERVALO = 0.10  # 10%

# Trava: a partir desta pontuação a dificuldade para de subir. A velocidade dos
# quadrados para de aumentar e o intervalo de nascimento para de diminuir.
PONTOS_LIMITE_DIFICULDADE = 80
NIVEL_MAXIMO = PONTOS_LIMITE_DIFICULDADE // PONTOS_POR_NIVEL  # 80 // 10 = nível 8

# Intervalo entre o nascimento de quadrados, em milissegundos.
INTERVALO_QUADRADOS_MS = 900  # intervalo inicial (nível 0)
INTERVALO_MINIMO_MS = 300  # limite, para o jogo não virar uma chuva impossível

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
    # Teclado numérico: pygame.K_KP8, K_KP2 etc. são as teclas do "keypad" (KP),
    # diferentes das teclas de número da fileira de cima (pygame.K_8, K_2...).
    # Obs.: com o Num Lock desligado, o teclado numérico manda setas/Home/PgUp etc.
    pygame.K_KP8: (0, -1),
    pygame.K_KP2: (0, 1),
    pygame.K_KP4: (-1, 0),
    pygame.K_KP6: (1, 0),
    # Diagonais: Q E Z C (em volta do W A S D) e 7 9 1 3 do teclado numérico.
    # Aqui o vetor tem comprimento maior que 1 (ex.: (1, 1) mede ~1,41);
    # a Bolinha normaliza a direção para o tiro diagonal não ser mais rápido.
    pygame.K_q: (-1, -1),
    pygame.K_KP7: (-1, -1),
    pygame.K_e: (1, -1),
    pygame.K_KP9: (1, -1),
    pygame.K_z: (-1, 1),
    pygame.K_KP1: (-1, 1),
    pygame.K_c: (1, 1),
    pygame.K_KP3: (1, 1),
}

# Tela inicial: a bola fica abaixo do título e, ao apertar ENTER, desliza até o
# centro crescendo até o tamanho normal. Só então a partida (e a música) começa.
POSICAO_BOLA_INICIO = (TAMANHO_JANELA // 2, 190)
RAIO_BOLA_INICIO = 25
DURACAO_TRANSICAO_MS = 1200

# A partir desta pontuação, inimigos também podem vir pelas diagonais.
PONTOS_PARA_DIAGONAL = 50

# A partir desta pontuação, às vezes nascem dois quadrados juntos (mesma cor,
# direções diferentes) no lugar de um só.
PONTOS_PARA_DUPLO = 80
CHANCE_DUPLO = 0.20  # 20%

# Modo de depuração: com True, a tecla ESPAÇO soma PONTOS_DEBUG pontos (para testar
# os níveis altos rapidamente). Troque para False antes de "entregar" o jogo.
DEBUG = True
PONTOS_DEBUG = 10


def intervalo_do_nivel(nivel):
    """Intervalo (ms) entre quadrados no nível dado: 900, 810, 729, 656... até a trava."""
    # Trava: acima do NIVEL_MAXIMO o intervalo fica igual ao dele (~387 ms).
    nivel = min(nivel, NIVEL_MAXIMO)
    intervalo = INTERVALO_QUADRADOS_MS * (1 - REDUCAO_INTERVALO) ** nivel
    # set_timer só aceita milissegundos inteiros, por isso o int().
    return max(INTERVALO_MINIMO_MS, int(intervalo))


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


def desenhar_ranking(tela, fonte, lista, y, destaque=None):
    """Desenha a tabela de recordes a partir da altura y. destaque = posição a realçar."""
    if not lista:
        desenhar_texto_centralizado(tela, fonte, "Nenhum recorde ainda", CINZA, y)
        return
    for posicao, recorde in enumerate(lista):
        cor = VERMELHO if posicao == destaque else PRETO
        # :<3 alinha o nome à esquerda em 3 espaços; :>5 alinha os pontos à direita.
        linha = f"{posicao + 1}.  {recorde['nome']:<3}   {recorde['pontos']:>5}"
        desenhar_texto_centralizado(tela, fonte, linha, cor, y + posicao * 32)


def desenhar_veu(tela):
    """Cobre a tela com um branco semitransparente, para o texto ficar legível por cima.

    CONCEITO: transparência (canal alfa). Além de R, G e B, uma cor pode ter um 4º
    valor, o "alfa": 0 = totalmente transparente, 255 = totalmente opaco.
    """
    # pygame.Surface((largura, altura), pygame.SRCALPHA) cria uma superfície nova,
    # em branco, que guarda alfa por pixel (sem SRCALPHA o alfa seria ignorado).
    veu = pygame.Surface((TAMANHO_JANELA, TAMANHO_JANELA), pygame.SRCALPHA)
    veu.fill((255, 255, 255, 210))  # branco com alfa 210: quase opaco
    # Ao fazer blit de uma superfície com alfa, o pygame mistura as cores com o
    # que já está desenhado embaixo, e o jogo "congelado" aparece esmaecido.
    tela.blit(veu, (0, 0))


def piscando():
    """True e False alternando a cada meio segundo, para textos que piscam."""
    # pygame.time.get_ticks() = milissegundos desde o pygame.init().
    return (pygame.time.get_ticks() // 500) % 2 == 0


def main():
    # pygame.mixer.pre_init(frequência, formato, canais, buffer) escolhe as
    # configurações de áudio ANTES de o pygame.init() abrir o mixer:
    # 44100 amostras/s (qualidade de CD), -16 = amostras de 16 bits com sinal
    # (o formato que o sons.py gera), 2 = estéreo, e buffer de 512 amostras.
    # Buffer pequeno = menos atraso entre apertar a tecla e ouvir o som.
    pygame.mixer.pre_init(44100, -16, 2, 512)

    # pygame.init() inicializa todos os módulos do pygame (vídeo, fontes, som...).
    # Deve ser chamado antes de usar qualquer outra função do pygame.
    pygame.init()

    # Dicionário com os efeitos sonoros: sons["tiro"].play() toca o som do tiro.
    # Sound.play() toca o som uma vez, num canal livre, sem pausar o jogo.
    sons = carregar_sons()

    # Trilha sonora 8 bits em loop. Ela acelera (tempo e tom) a cada vida perdida.
    # Só começa a tocar quando a partida começa (a tela inicial é silenciosa).
    trilha = Trilha()

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

    fonte_media = pygame.font.Font(None, 44)

    # Recordes salvos em disco (lista de {"nome", "pontos"}, do maior para o menor).
    lista_recordes = recordes.carregar()

    # Estados (telas) do jogo. Cada um muda o que as teclas fazem e o que é desenhado:
    #   "inicio"    -> tela inicial: só o título e a bola, em silêncio
    #   "transicao" -> a bola desliza até o centro (depois de apertar ENTER)
    #   "jogando"   -> a partida em si
    #   "iniciais" -> fez recorde: digitando as iniciais
    #   "fim"      -> fim de jogo, com a tabela de recordes
    estado = "inicio"
    inicio_transicao_ms = 0  # quando a animação da bola começou (pygame.time.get_ticks)

    # Estado da partida. Os valores reais são definidos ao começar cada partida.
    bolinhas = []  # bolinhas voando na tela
    quadrados = []  # quadrados (inimigos) na tela
    pontos = 0  # quadrados destruídos
    vida_bola = VIDA_MAXIMA_BOLA  # contatos que a bola central ainda aguenta
    nivel = 0  # sobe 1 a cada PONTOS_POR_NIVEL pontos
    usou_debug = False  # se usou o atalho de debug, a partida não vale recorde
    iniciais = ""  # letras digitadas na tela de recorde
    posicao_recorde = None  # posição do recorde novo na tabela (para destacar)

    # Loop principal do jogo ("game loop"): a cada volta ele
    # 1) lê os eventos, 2) atualiza o estado do jogo e 3) desenha a tela.
    rodando = True
    while rodando:
        comecar_partida = False  # marcado pelos eventos; a partida é montada logo abaixo

        # ---------- 1) EVENTOS ----------
        # pygame.event.get() retorna a lista de eventos que aconteceram desde a
        # última chamada (teclas, cliques, mover o mouse, fechar a janela...).
        # Precisa ser chamado todo quadro, senão a janela "trava" para o Windows.
        for evento in pygame.event.get():
            # pygame.QUIT é o evento gerado quando o usuário clica no X da janela.
            if evento.type == pygame.QUIT:
                rodando = False

            # pygame.KEYDOWN é gerado UMA vez no momento em que uma tecla é pressionada
            # (segurar a tecla não gera novos KEYDOWN). evento.key diz qual tecla foi.
            elif estado == "inicio":
                # pygame.K_RETURN é o ENTER principal; pygame.K_KP_ENTER, o do teclado
                # numérico. pygame.K_ESCAPE é a tecla ESC.
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
                    # pygame.K_BACKSPACE é a tecla de apagar.
                    elif evento.key == pygame.K_BACKSPACE:
                        iniciais = iniciais[:-1]
                    # evento.unicode é o caractere que a tecla produz ("a", "B", "7"...),
                    # já levando em conta Shift e o layout do teclado. Aceitamos só
                    # letras A-Z e guardamos em maiúsculas, como nos fliperamas.
                    elif (
                        len(iniciais) < recordes.TAMANHO_NOME
                        and evento.unicode.isascii()
                        and evento.unicode.isalpha()
                    ):
                        iniciais += evento.unicode.upper()

            elif estado == "fim":
                # R reinicia a partida (pygame.K_r é a tecla R); ESC volta ao início.
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_r:
                        comecar_partida = True
                    elif evento.key == pygame.K_ESCAPE:
                        estado = "inicio"  # a música já parou no fim de jogo

            # A partir daqui, estado == "jogando".

            # Atalho de debug. pygame.K_SPACE é a constante da barra de espaço.
            # O nível é recalculado logo abaixo, na atualização, a partir dos pontos.
            elif DEBUG and evento.type == pygame.KEYDOWN and evento.key == pygame.K_SPACE:
                pontos += PONTOS_DEBUG
                usou_debug = True

            # Cada toque numa tecla de direção dispara exatamente uma bolinha.
            elif evento.type == pygame.KEYDOWN and evento.key in DIRECOES:
                direcao = DIRECOES[evento.key]
                bolinhas.append(Bolinha(centro, RAIO_CIRCULO, direcao))
                sons["tiro"].play()

            # Nosso evento de timer: a cada intervalo (que encurta por nível) nasce um quadrado.
            elif evento.type == EVENTO_NOVO_QUADRADO:
                # Cada nível multiplica a velocidade por 1.10, então o aumento é
                # acumulativo: nível 1 = 110%, nível 2 = 121%, nível 3 = 133,1%...
                # min() aplica a trava: o nível usado na velocidade nunca passa do
                # NIVEL_MAXIMO (nível 8, ou ~214% da velocidade inicial).
                nivel_velocidade = min(nivel, NIVEL_MAXIMO)
                velocidade = (
                    VELOCIDADE_QUADRADO * (1 + AUMENTO_VELOCIDADE) ** nivel_velocidade
                )
                diagonal_liberada = pontos >= PONTOS_PARA_DIAGONAL
                if pontos >= PONTOS_PARA_DUPLO and random.random() < CHANCE_DUPLO:
                    # extend() adiciona os dois quadrados do par à lista de uma vez.
                    quadrados.extend(
                        criar_par_de_quadrados(TAMANHO_JANELA, velocidade, diagonal_liberada)
                    )
                else:
                    quadrados.append(
                        criar_quadrado_aleatorio(TAMANHO_JANELA, velocidade, diagonal_liberada)
                    )

        # Progresso da animação da tela inicial: 0.0 (começo) a 1.0 (bola no centro).
        progresso = 0.0
        if estado == "transicao":
            progresso = (pygame.time.get_ticks() - inicio_transicao_ms) / DURACAO_TRANSICAO_MS
            if progresso >= 1.0:
                progresso = 1.0
                comecar_partida = True  # a bola chegou: começa a partida e a música

        # Monta uma partida nova (fim da animação inicial ou R no fim de jogo).
        if comecar_partida:
            bolinhas = []
            quadrados = []
            pontos = 0
            vida_bola = VIDA_MAXIMA_BOLA
            nivel = 0
            usou_debug = False
            iniciais = ""
            posicao_recorde = None
            estado = "jogando"
            # pygame.time.set_timer(evento, milissegundos) faz o pygame colocar esse
            # evento na fila automaticamente, repetidamente, a cada intervalo.
            # Chamar de novo para o MESMO evento substitui o timer anterior, então
            # isto também "zera" o relógio: o 1º quadrado nasce após um intervalo cheio.
            pygame.time.set_timer(EVENTO_NOVO_QUADRADO, intervalo_do_nivel(0))
            trilha.tocar()  # a música recomeça do início, na velocidade normal

        # ---------- 2) ATUALIZAÇÃO ----------
        # Só durante a partida as coisas se mexem; nas outras telas a cena fica parada.
        if estado == "jogando":
            # Guardamos a vida do início do quadro: no fim comparamos para saber se o
            # núcleo levou dano (por qualquer motivo) e tocar o som uma vez só.
            vida_antes = vida_bola

            # Atualiza a posição de cada bolinha...
            for bolinha in bolinhas:
                bolinha.atualizar()

            # ...e remove as que já saíram da tela (senão a lista cresceria para sempre).
            # Bolinha que sai da tela é um tiro errado: custa 1 de vida da bola central.
            # Isso pune quem fica apertando as teclas sem parar ("spam" de tiros).
            # O fim de jogo por vida zerada é verificado mais abaixo.
            errados = [b for b in bolinhas if b.saiu_da_tela(TAMANHO_JANELA, TAMANHO_JANELA)]
            vida_bola -= len(errados)
            bolinhas = [b for b in bolinhas if b not in errados]

            # Move os quadrados em direção à bola central.
            for quadrado in quadrados:
                quadrado.atualizar()

            # Colisão bolinha x quadrado: a bolinha sempre some e o quadrado perde 1 de vida.
            # Só quando a vida do quadrado acaba ele é destruído e vale ponto.
            # Se o alvo for uma bolinha amiga, é fogo amigo: as duas somem e o núcleo
            # perde 1 de vida, sem ganhar ponto.
            # Rect.colliderect(outro_rect) retorna True se os dois retângulos se sobrepõem.
            for quadrado in quadrados[:]:  # [:] percorre uma cópia, pois vamos remover itens
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
                            sons["acerto"].play()  # perdeu vida, mas continua vivo
                        break  # uma bolinha por quadrado por quadro; passa para o próximo

            # O nível sobe a cada 10 pontos (0-9 = nível 0, 10-19 = nível 1...).
            novo_nivel = pontos // PONTOS_POR_NIVEL
            if novo_nivel != nivel:
                nivel = novo_nivel
                sons["nivel"].play()
                # Substitui o timer antigo pelo novo intervalo (não cria um segundo timer).
                pygame.time.set_timer(EVENTO_NOVO_QUADRADO, intervalo_do_nivel(nivel))

            # Quadrado que chega na bola central some e tira 1 de vida dela.
            # Bolinha amiga que chega só some (ela "voltou para casa"), sem dano.
            # Quando a vida chega a zero, o jogo acaba.
            for quadrado in quadrados[:]:
                if quadrado.encostou_na_bola(centro, RAIO_CIRCULO):
                    quadrados.remove(quadrado)
                    if not quadrado.amiga:
                        vida_bola -= 1
            if vida_bola <= 0:
                vida_bola = 0
                trilha.parar()  # para a música, deixando o som de fim sozinho
                sons["fim"].play()
                # Passando 0 como intervalo, pygame.time.set_timer DESLIGA o timer:
                # fora da partida não precisamos de quadrados nascendo.
                pygame.time.set_timer(EVENTO_NOVO_QUADRADO, 0)
                # Fez pontos para entrar na tabela? Então pede as iniciais.
                # Partidas com o atalho de debug não contam.
                if not usou_debug and recordes.entra_no_ranking(lista_recordes, pontos):
                    estado = "iniciais"
                else:
                    estado = "fim"
            elif vida_bola < vida_antes:
                sons["dano"].play()
                trilha.ajustar(vida_bola)  # mais rápida e aguda: sensação de urgência

        # ---------- 3) DESENHO ----------
        # Surface.fill(cor) pinta a superfície inteira com uma cor.
        # Usamos para "apagar" o quadro anterior antes de desenhar o novo.
        tela.fill(BRANCO)

        if estado in ("inicio", "transicao"):
            # "Suavização" (easing): em vez de andar em velocidade constante, a bola
            # acelera no começo e freia no fim. Esta fórmula (smoothstep) transforma
            # o progresso linear 0..1 numa curva em "S", também de 0 a 1.
            suave = progresso * progresso * (3 - 2 * progresso)

            # Título: some aos poucos durante a animação.
            titulo = fonte_grande.render("BOLA ATIRADORA", True, PRETO)
            # Surface.set_alpha(0 a 255) define a transparência da superfície inteira:
            # 255 = opaca, 0 = invisível. Assim o título "desbota" até sumir.
            titulo.set_alpha(int(255 * (1 - suave)))
            tela.blit(titulo, titulo.get_rect(center=(TAMANHO_JANELA // 2, 90)))

            # Bola: sai da posição da tela inicial e vai até o centro, crescendo.
            # Vector2.lerp(destino, t) ("interpolação linear") devolve o ponto que fica
            # a fração t do caminho entre o vetor e o destino (t=0 início, t=1 destino).
            posicao_bola = pygame.math.Vector2(POSICAO_BOLA_INICIO).lerp(centro, suave)
            raio_bola = RAIO_BOLA_INICIO + (RAIO_CIRCULO - RAIO_BOLA_INICIO) * suave
            pygame.draw.circle(tela, VERDE, posicao_bola, raio_bola)

        else:
            # Cena da partida. Em "iniciais" e "fim" ela aparece congelada, ao fundo.

            # pygame.draw.circle(superfície, cor, centro, raio) desenha um círculo preenchido.
            # Um 5º parâmetro opcional (largura) desenharia só o contorno, ex.: largura=3.
            # A cor depende da vida restante. No fim de jogo (vida 0) mantemos o vermelho.
            cor_bola = CORES_POR_VIDA.get(vida_bola, VERMELHO)
            pygame.draw.circle(tela, cor_bola, centro, RAIO_CIRCULO)

            # Desenhamos as bolinhas depois da bola central, então elas ficam "por cima"
            # dela: no pygame, o que é desenhado por último aparece na frente.
            for bolinha in bolinhas:
                bolinha.desenhar(tela)

            for quadrado in quadrados:
                quadrado.desenhar(tela)

            # Placar no canto superior esquerdo. Aqui blit recebe uma tupla (x, y),
            # que é a posição do canto superior esquerdo do texto.
            tela.blit(fonte_pequena.render(f"Pontos: {pontos}", True, PRETO), (10, 10))

            # Recorde no canto superior direito. get_rect(topright=...) posiciona o
            # texto pelo canto superior DIREITO, para ele ficar colado na borda.
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
            # Mostra as letras digitadas e "_" nas que faltam: "AB_".
            # O "_" da próxima letra pisca, como um cursor.
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
