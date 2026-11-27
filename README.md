# Bola Atiradora

Jogo de reflexo em 2D feito com [pygame](https://www.pygame.org/), criado como projeto de
estudo. Uma bola fica no centro da tela e atira em oito direções para destruir os inimigos
que vêm das bordas antes que eles a alcancem.

## Como rodar

```
pip install pygame
python main.py
```

Todos os sons são gerados por código, então não há arquivos de áudio para baixar.
Sem placa de som, o jogo roda normalmente, só que em silêncio.

## Controles

| Tecla | Ação |
|---|---|
| `↑` `W` `8`* | Atira para cima |
| `↓` `S` `2`* | Atira para baixo |
| `←` `A` `4`* | Atira para a esquerda |
| `→` `D` `6`* | Atira para a direita |
| `Q` `7`* | Atira na diagonal superior esquerda |
| `E` `9`* | Atira na diagonal superior direita |
| `Z` `1`* | Atira na diagonal inferior esquerda |
| `C` `3`* | Atira na diagonal inferior direita |
| `ENTER` | Começa a partida (tela inicial) / confirma as iniciais (novo recorde) |
| `R` | Joga de novo (tela de fim de jogo) |
| `ESC` | Sai do jogo (tela inicial) / volta à tela inicial (fim de jogo) |
| `ESPAÇO` | +10 pontos, só com `DEBUG = True` (ver [Modo de depuração](#modo-de-depuração)) |

\* Teclado numérico, com o Num Lock ligado.

Cada toque numa tecla dispara exatamente um tiro: segurar a tecla não repete.

---

## Mecânicas

### A bola central (o jogador)

- Fica parada no centro da tela e tem **3 vidas**.
- A cor mostra a vida que resta: **verde** (3) → **amarelo** (2) → **vermelho** (1).
- Com 0 vidas, a partida acaba.

**O que tira 1 vida da bola central:**

| Situação | Por quê |
|---|---|
| Um quadrado encosta nela | É o objetivo do inimigo |
| Um tiro sai da tela sem acertar nada | Pune quem atira sem parar ("spam" de tiros) |
| Um tiro acerta uma bolinha amiga | Fogo amigo |

Vários danos no mesmo quadro tiram várias vidas, mas o som de dano toca uma vez só.

### Tiros

- Saem da borda da bola central e andam em linha reta a 8 px por quadro (480 px/s).
- O tiro diagonal anda na mesma velocidade que o reto, porque a direção é normalizada.
- Um tiro sempre some ao acertar algo.

### Inimigos (quadrados)

Nascem logo fora do meio de uma das quatro bordas e andam em linha reta até o centro.
A resistência deles é sorteada ao nascer e aparece na cor:

| Cor | Chance | Tiros para destruir |
|---|---|---|
| Vermelho | 85% | 1 |
| Amarelo | 10% | 2 |
| Verde | 5% | 3 |

A cada tiro recebido o quadrado perde 1 de vida e muda de cor (verde → amarelo → vermelho).
Só o tiro que o destrói vale ponto.

### Bolinha amiga (azul)

Em 5% dos nascimentos, no lugar do quadrado vem uma **bolinha azul**. Ela faz o mesmo
caminho dos inimigos, mas **não deve ser atingida**:

- Se chegar à bola central, some sem causar dano.
- Se for atingida, some e a bola central perde 1 vida, sem ganhar ponto.

### Pontuação

**1 ponto por quadrado destruído.** Acertos que só tiram vida de um quadrado e bolinhas
amigas não dão ponto.

---

## Escalamento de dificuldade

A velocidade dos inimigos e o ritmo de nascimento são **fixos** durante toda a partida.
A dificuldade sobe por **novos padrões de ataque**, liberados por pontuação:

| A partir de | O que muda |
|---|---|
| 0 pontos | Base: um inimigo a cada **650 ms**, a **3,3 px por quadro** (~200 px/s), vindo só pelas 4 bordas |
| **50 pontos** | Inimigos também vêm pelas **diagonais**: 15% dos nascimentos saem de um dos 4 cantos |
| **80 pontos** | **Ataques duplos**: 20% dos nascimentos trazem **dois quadrados ao mesmo tempo**, com a mesma cor e trajetórias diferentes |

Detalhes:

- As regras se somam: a partir de 80 pontos, os ataques duplos também podem vir pelas diagonais.
- Um ataque duplo traz sempre dois quadrados, nunca uma bolinha amiga.
- As chances de cor (85/10/5%) e de bolinha amiga (5%) são as mesmas a partida toda.

### Onde ajustar

| Constante | Arquivo | Valor |
|---|---|---|
| `VELOCIDADE_QUADRADO` | [quadrado.py](quadrado.py) | 3,3 px por quadro |
| `INTERVALO_QUADRADOS_MS` | [main.py](main.py) | 650 ms |
| `PONTOS_PARA_DIAGONAL` | [main.py](main.py) | 50 |
| `CHANCE_DIAGONAL` | [quadrado.py](quadrado.py) | 15% |
| `PONTOS_PARA_DUPLO` / `CHANCE_DUPLO` | [main.py](main.py) | 80 / 20% |
| `CHANCE_VERDE` / `CHANCE_AMARELO` | [quadrado.py](quadrado.py) | 5% / 10% |
| `CHANCE_AMIGA` | [quadrado.py](quadrado.py) | 5% |
| `VIDA_MAXIMA_BOLA` | [main.py](main.py) | 3 |
| `VELOCIDADE_BOLINHA` | [bolinha.py](bolinha.py) | 8 px por quadro |

---

## Telas

```
inicio ──ENTER──► transicao ──1,2 s──► jogando ──vida 0──► iniciais ──ENTER──► fim
                                                    └──── (sem recorde) ─────► fim

fim ──R──► jogando        fim ──ESC──► inicio
```

| Tela | O que acontece |
|---|---|
| `inicio` | Título e a bola. |
| `transicao` | A bola desliza até o centro, crescendo, e o título desbota. As teclas ficam ignoradas. No fim, a partida começa. |
| `jogando` | A partida em si. |
| `iniciais` | Só aparece se a pontuação entrou no ranking. O jogador digita 3 letras (A-Z). |
| `fim` | Pontuação final e tabela de recordes, por cima da partida congelada. |

## Recordes

- A tabela guarda as **5 melhores** pontuações, cada uma com **3 iniciais**.
- Para entrar, é preciso fazer mais de 0 pontos e **superar** o 5º colocado. Num empate,
  quem chegou antes fica na frente.
- Ficam salvos em `recordes.json`, na pasta do jogo (fora do git). Se o arquivo sumir ou
  estiver corrompido, a tabela começa vazia.
- Durante a partida, o canto superior direito mostra o maior valor entre o 1º recorde e a
  pontuação atual.

## Modo de depuração

Com `DEBUG = True` em [main.py](main.py), cada `ESPAÇO` soma 10 pontos, para testar
rapidamente as regras de 50 e 80 pontos. **Uma partida em que o atalho foi usado não entra
no ranking.** Troque para `DEBUG = False` antes de distribuir o jogo.

## Sons

| Som | Quando toca |
|---|---|
| `tiro` | A cada disparo |
| `acerto` | Um quadrado perdeu vida, mas continua vivo |
| `destruido` | Um quadrado foi destruído |
| `dano` | A bola central perdeu vida |
| `fim` | Fim de jogo |

`sons.py` também gera um som `nivel` (duas notas subindo), que hoje não é usado.

---

## Estrutura do código

```
Bola Atiradora/
├── main.py      → janela, game loop, telas, colisões, vidas, pontuação e dificuldade
├── bolinha.py   → classe Bolinha (o tiro)
├── quadrado.py  → classes Quadrado e BolinhaAmiga, e o sorteio de onde e como nascem
├── recordes.py  → carregar/salvar o ranking em JSON
└── sons.py      → efeitos sonoros sintetizados
```

`main.py` importa e usa os outros módulos, que não se conhecem entre si.

### O game loop

Todo jogo em pygame gira em torno de um `while` que roda 60 vezes por segundo. Cada volta
produz um quadro e faz três coisas, nesta ordem:

1. **Eventos** (`pygame.event.get()`): teclas, fechar a janela e o timer
   `EVENTO_NOVO_QUADRADO`, que o `pygame.time.set_timer()` dispara a cada 650 ms.
2. **Atualização** (só na tela `jogando`): move tiros e quadrados, descarta tiros que saíram
   da tela, testa colisões, aplica dano e verifica o fim de jogo.
3. **Desenho**: `tela.fill()` apaga o quadro anterior, desenha tudo de novo e
   `pygame.display.flip()` mostra o resultado. O que é desenhado por último fica na frente.

No fim de cada volta, `relogio.tick(60)` segura o loop em 60 quadros por segundo. Como as
velocidades são em "pixels por quadro", o jogo roda na mesma velocidade em qualquer computador.

### Colisões

| Situação | Técnica |
|---|---|
| Tiro × quadrado | `Rect.colliderect()`: sobreposição de retângulos (o tiro usa uma caixa em volta do círculo) |
| Quadrado × bola central | `Vector2.distance_to()`: distância entre os centros ≤ raio + metade do lado |

A posição dos objetos fica num `pygame.math.Vector2`, que aceita casas decimais. O
`pygame.Rect` só guarda inteiros, então ele apenas acompanha a posição e serve para colisões
e desenho.

### Áudio

- `sons.py` gera as amostras com matemática (ondas quadradas, senoides e ruído) e cria os
  sons com `pygame.mixer.Sound(buffer=...)`.
- Cada `Sound.play()` usa um canal livre do mixer, então um som não corta o outro.

### Recursos do pygame usados

| Recurso | Para que |
|---|---|
| `pygame.init()` / `pygame.quit()` | Ligar e desligar o pygame |
| `pygame.display.set_mode()` / `set_caption()` / `flip()` | Janela, título e exibição do quadro |
| `pygame.time.Clock()` / `.tick()` | Limitar o FPS |
| `pygame.time.set_timer()` / `get_ticks()` | Evento periódico e tempo decorrido |
| `pygame.event.get()`, `QUIT`, `KEYDOWN`, `USEREVENT`, `K_*` | Eventos e teclas |
| `pygame.Surface`, `SRCALPHA`, `.fill()`, `.blit()`, `.get_rect()`, `.set_alpha()` | Superfícies e transparência |
| `pygame.draw.circle()` / `pygame.draw.rect()` | Desenhar formas |
| `pygame.font.Font()` / `.render()` | Textos |
| `pygame.Rect` / `.colliderect()` | Retângulos e colisão |
| `pygame.math.Vector2` (`normalize`, `distance_to`, `lerp`) | Posição, direção e animação |
| `pygame.mixer` (`pre_init`, `Sound`) | Áudio |
