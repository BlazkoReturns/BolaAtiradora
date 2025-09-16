#include "game.h"
#include <string>
#include <stdlib.h>

Game::Game()
{
   InitWindow(nLadoTela, nLadoTela, "Bola Atiradora");
   SetExitKey(KEY_NULL);
   SetTargetFPS(60);
   InicializarVariaveis();
}

void Game::Atualizar()
{
   for (auto &tiro : tiros)
   {
      tiro.Atualizar();
   }
   for (auto &inimigo : inimigos)
   {
      inimigo.Atualizar();
   }
}

int Game::CarregarRecorde()
{
   int Recorde = 0;

    if (FileExists("highscore.txt"))
    {
        char *scoreText = LoadFileText("highscore.txt");
        if (scoreText != NULL)
        {
            Recorde = atoi(scoreText);
            UnloadFileText(scoreText); // Libera a memória do texto carregado
            TraceLog(LOG_INFO, "High score carregado com sucesso: %i", Recorde);
        }
    }
    
    return Recorde;
}

void Game::DesabilitaObjetos(bool lNovoJogo)
{
   for (auto it = tiros.begin(); it != tiros.end();)
   {
      if (!it->lDesenhar || lNovoJogo)
      {
         it = tiros.erase(it);
      }
      else
      {
         ++it;
      }
   }

   for (auto it = inimigos.begin(); it != inimigos.end();)
   {
      if (!it->lDesenhar || lNovoJogo)
      {
         it = inimigos.erase(it);
      }
      else
      {
         ++it;
      }
   }
}

void Game::Desenhar()
{

   for (auto &tiro : tiros)
   {
      tiro.Desenhar();
   }

   for (auto &inimigo : inimigos)
   {
      inimigo.Desenhar();
   }

   ball.Draw();

   DrawText(TextFormat("Score: %08i", nPontuacao), 10, 10, 20, BLACK);
   DrawText(TextFormat("Dificuldade: %02i", nNivelDificuldade), 10, 30, 20, BLACK);
   DrawText("Modo: ", 10, 50, 20, BLACK);
   DrawText((nModoJogo == 2 ? "Humano" : nModoJogo == 4 ? "Macaco" : "Polvo"), 70, 50, 20, BLACK);
   DrawText(TextFormat("Top Score: %08i", nRecorde), 10, 70, 20, BLACK);
   DrawText(TextFormat("Esc->Menu"), 10, nLadoTela-20, 20, BLACK);
}

void Game::DesenharSetasDiagonais()
{
   DrawTriangleLines({(nLadoTela / 2) + nRaioBola - 10, (nLadoTela / 2) - nRaioBola}, {(nLadoTela / 2) + nRaioBola, (nLadoTela / 2) - nRaioBola + 10}, {(nLadoTela / 2) + nRaioBola, (nLadoTela / 2) - nRaioBola}, BLACK);
   DrawTriangleLines({(nLadoTela / 2) + nRaioBola - 10, (nLadoTela / 2) + nRaioBola}, {(nLadoTela / 2) + nRaioBola, (nLadoTela / 2) + nRaioBola - 10}, {(nLadoTela / 2) + nRaioBola, (nLadoTela / 2) + nRaioBola}, BLACK);
   DrawTriangleLines({(nLadoTela / 2) - nRaioBola + 10, (nLadoTela / 2) + nRaioBola}, {(nLadoTela / 2) - nRaioBola, (nLadoTela / 2) + nRaioBola - 10}, {(nLadoTela / 2) - nRaioBola, (nLadoTela / 2) + nRaioBola}, BLACK);
   DrawTriangleLines({(nLadoTela / 2) - nRaioBola + 10, (nLadoTela / 2) - nRaioBola}, {(nLadoTela / 2) - nRaioBola, (nLadoTela / 2) - nRaioBola + 10}, {(nLadoTela / 2) - nRaioBola, (nLadoTela / 2) - nRaioBola}, BLACK);
}

void Game::DesenharSetasHorizontais()
{
   DrawTriangleLines({(nLadoTela / 2) + nRaioBola + 10, nLadoTela / 2 + 10}, {(nLadoTela / 2) + nRaioBola + 10, (nLadoTela / 2) - 10}, {(nLadoTela / 2) + nRaioBola + 30, nLadoTela / 2}, BLACK);
   DrawTriangleLines({(nLadoTela / 2) - nRaioBola - 10, nLadoTela / 2 + 10}, {(nLadoTela / 2) - nRaioBola - 10, (nLadoTela / 2) - 10}, {(nLadoTela / 2) - nRaioBola - 30, nLadoTela / 2}, BLACK);
}

void Game::DesenharSetasVerticais()
{
   DrawTriangleLines({(nLadoTela / 2) - 10, (nLadoTela / 2) - nRaioBola - 10}, {(nLadoTela / 2) + 10, (nLadoTela / 2) - nRaioBola - 10}, {(nLadoTela / 2), (nLadoTela / 2) - nRaioBola - 30}, BLACK);
   DrawTriangleLines({(nLadoTela / 2) + 10, (nLadoTela / 2) + nRaioBola + 10}, {(nLadoTela / 2) - 10, (nLadoTela / 2) + nRaioBola + 10}, {(nLadoTela / 2), (nLadoTela / 2) + nRaioBola + 30}, BLACK);
}

void Game::GeraInimigos()
{
   double nTempoAgora = GetTime();

   if ((nTempoAgora - nTempoAumentaVelocidade > nIntervaloAumentaDificuldade) && nNivelDificuldade <=19)
   {
      nIntervaloGeraInimigo -= nFatorIntervaloGeraInimigo;
      //nMultiplicadorVelocidade += nFatorAumentoMultiplicadorVelocidade;
      nNivelDificuldade++;
      nTempoAumentaVelocidade = GetTime();
   }

   if (nTempoAgora - nTempoUltimoInimigo > nIntervaloGeraInimigo)
   {
      inimigos.push_back(Inimigos(GetRandomValue(1, nModoJogo), nVelocidadeInicialInimigo, nMultiplicadorVelocidade, nRaioInimigo, nLadoTela));
      nTempoUltimoInimigo = GetTime();
   }
}

void Game::InicializarVariaveis()
{

   lGameOver = false;

   nRaioBola = 80;
   nRaioInimigo = 10;
   nRaioTiro = 5;
   ball.nRaioBola = nRaioBola;
   ball.nLadoTela = nLadoTela;

   /*Variáveis referentes a textos de tela*/
   nPontuacao = 0;
   nRecorde = CarregarRecorde();
   nNivelDificuldade = 1;

   /*Variáveis relacionadas a dificuldade do jogo*/
   nTempoAumentaVelocidade = GetTime();
   nTempoUltimoInimigo = GetTime();
   nIntervaloAumentaDificuldade = 6.00;
   nIntervaloGeraInimigo = 0.80;

   nFatorAumentoMultiplicadorVelocidade = 0.1;
   nFatorIntervaloGeraInimigo = 0.035;

   nVelocidadeInicialInimigo = 5;
   nVelocidadeTiro = 15;

   nMultiplicadorVelocidade = 1;
   
}

void Game::ProcessamentoComandos()
{

   int nDirecaoTiro = 0;

   if (IsKeyPressed(KEY_ESCAPE)){
      lIniciarJogo = false;
      DesabilitaObjetos(true);
      InicializarVariaveis();
   }

   if (IsKeyPressed(KEY_LEFT) || IsKeyPressed(KEY_KP_4))
   { /*Cima*/
      nDirecaoTiro = 3;
   }

   if (IsKeyPressed(KEY_RIGHT) || IsKeyPressed(KEY_KP_6))
   { /*Baixo*/
      nDirecaoTiro = 4;
   }

   if (nModoJogo == 4 || nModoJogo == 8)
   {
      if (IsKeyPressed(KEY_UP) || IsKeyPressed(KEY_KP_8))
      { /*Esquerda*/
         nDirecaoTiro = 1;
      }

      if (IsKeyPressed(KEY_DOWN) || IsKeyPressed(KEY_KP_2))
      { /*Direita*/
         nDirecaoTiro = 2;
      }
   }

   if (nModoJogo == 8)
   {
      if (IsKeyPressed(KEY_KP_7))
      { /*Esquerda superior*/
         nDirecaoTiro = 5;
      }

      if (IsKeyPressed(KEY_KP_9))
      { /*Direita superior*/
         nDirecaoTiro = 6;
      }

      if (IsKeyPressed(KEY_KP_1))
      { /*Esquerda inferior*/
         nDirecaoTiro = 7;
      }

      if (IsKeyPressed(KEY_KP_3))
      { /*Direita inferior*/
         nDirecaoTiro = 8;
      }
   }
   if (nDirecaoTiro != 0)
   {
      tiros.push_back(Tiro(nDirecaoTiro, nLadoTela, nRaioTiro, nVelocidadeTiro, nRaioBola));
   }
   
}

void Game::SalvarRecorde(int score)
{
    std::string scoreText = std::to_string(score);
    SaveFileText("highscore.txt", (char*)scoreText.c_str());
}

void Game::TelaGameOver()
{
   DrawText(TextFormat("Score: %08i", nPontuacao), 10, 10, 20, BLACK);
   DrawText("Game Over", nLadoTela / 2 - MeasureText("Game Over", 50) / 2, nLadoTela / 2, 50, BLACK);
   DrawText("Press any key to try again", nLadoTela / 2 - MeasureText("Press any key to try again", 30) / 2, (nLadoTela / 2) + 60, 30, BLACK);
   DesabilitaObjetos(true);

   if (GetKeyPressed() != 0)
   {
      InicializarVariaveis();
   }
}

void Game::TelaInicial()
{

   float nLarguraBotao = 200;
   float nAlturaBotao = 100;
   float nOffSet = (nLadoTela - 3 * nLarguraBotao) / 4; /*Espaço entre as bordas-botões e botões-botões*/

   float nPosicaoY = nLadoTela / 2 + 200;
   float nPosicaoXHumano = nOffSet;                        /*Um offset*/
   float nPosicaoXMacaco = 2 * nOffSet + nLarguraBotao;    /*dois offsets e a largura de um botão*/
   float nPosicaoXPolvo = 3 * nOffSet + 2 * nLarguraBotao; /*3 offsets e a largura de 2 botões*/

   Color cCorBotaoHumano = BLACK;
   Color cCorBotaoMacaco = BLACK;
   Color cCorBotaoPolvo = BLACK;

   int nFonteTextoBotao = 30;
   int nFonteTitulo = 80;
   int nFonteAutor = 20;
   int nOffSetHumano = (nLarguraBotao - MeasureText("Humano", nFonteTextoBotao)) / 2;
   int nOffSetMacaco = (nLarguraBotao - MeasureText("Macaco", nFonteTextoBotao)) / 2;
   int nOffSetPolvo = (nLarguraBotao - MeasureText("Polvo", nFonteTextoBotao)) / 2;

   /*Colisão entre mouse e botões*/
   if (CheckCollisionPointRec(GetMousePosition(), {nPosicaoXHumano, nPosicaoY, nLarguraBotao, nAlturaBotao}))
   {
      cCorBotaoHumano = RED; // Estado: MOUSE SOBRE (HOVER)
      DesenharSetasHorizontais();
      if (IsMouseButtonDown(MOUSE_BUTTON_LEFT))
      {
         lIniciarJogo = true;
         nModoJogo = 2;
      }
   }

   if (CheckCollisionPointRec(GetMousePosition(), {nPosicaoXMacaco, nPosicaoY, nLarguraBotao, nAlturaBotao}))
   {
      cCorBotaoMacaco = RED; // Estado: MOUSE SOBRE (HOVER)
      DesenharSetasHorizontais();
      DesenharSetasVerticais();
      if (IsMouseButtonDown(MOUSE_BUTTON_LEFT))
      {
         lIniciarJogo = true;
         nModoJogo = 4;
      }
   }

   if (CheckCollisionPointRec(GetMousePosition(), {nPosicaoXPolvo, nPosicaoY, nLarguraBotao, nAlturaBotao}))
   {
      cCorBotaoPolvo = RED; // Estado: MOUSE SOBRE (HOVER)
      DesenharSetasHorizontais();
      DesenharSetasVerticais();
      DesenharSetasDiagonais();
      if (IsMouseButtonDown(MOUSE_BUTTON_LEFT))
      {
         lIniciarJogo = true;
         nModoJogo = 8;
      }
   }

   /*Botões*/
   DrawRectangleLines(nPosicaoXHumano, nPosicaoY, nLarguraBotao, nAlturaBotao, cCorBotaoHumano);
   DrawRectangleLines(nPosicaoXMacaco, nPosicaoY, nLarguraBotao, nAlturaBotao, cCorBotaoMacaco);
   DrawRectangleLines(nPosicaoXPolvo, nPosicaoY, nLarguraBotao, nAlturaBotao, cCorBotaoPolvo);

   /*Textos dos Botões*/
   DrawText("Humano", nPosicaoXHumano + nOffSetHumano, nPosicaoY + nFonteTextoBotao, nFonteTextoBotao, BLACK);
   DrawText("Macaco", nPosicaoXMacaco + nOffSetMacaco, nPosicaoY + nFonteTextoBotao, nFonteTextoBotao, BLACK);
   DrawText("Polvo", nPosicaoXPolvo + nOffSetPolvo, nPosicaoY + nFonteTextoBotao, nFonteTextoBotao, BLACK);

   /*Textos*/
   DrawText("Bola Atiradora", nLadoTela / 2 - MeasureText("Bola Atiradora", nFonteTitulo) / 2, nLadoTela / 10, nFonteTitulo, BLACK);
   DrawText("Jogo desenvolvido por Blazko", nLadoTela / 2 - MeasureText("Jogo desenvolvido por Blazko", nFonteAutor) / 2, nLadoTela - 20, nFonteAutor, BLACK);

   ball.Draw();
}

void Game::VerificaColisoes()
{
   for (auto &inimigo : inimigos)
   {
      if (CheckCollisionCircles({nLadoTela / 2, nLadoTela / 2}, nRaioBola, {inimigo.vPosicaoInimigo.x, inimigo.vPosicaoInimigo.y}, inimigo.nRaioInimigo))
      {
         lGameOver = true;
         SalvarRecorde(nPontuacao);
         break;
      }

      for (auto &tiro : tiros)
      {
         if (CheckCollisionCircles({tiro.vPosicaoTiro.x, tiro.vPosicaoTiro.y}, nRaioTiro, {inimigo.vPosicaoInimigo.x, inimigo.vPosicaoInimigo.y}, nRaioInimigo)) 
         {
            inimigo.lDesenhar = false;
            tiro.lDesenhar = false;
            nPontuacao += (nNivelDificuldade+nModoJogo);
         }

         if (tiro.vPosicaoTiro.x >= nLadoTela || tiro.vPosicaoTiro.x <= 0 || tiro.vPosicaoTiro.y >= nLadoTela || tiro.vPosicaoTiro.y <= 0)
         {
            lGameOver = true;
            SalvarRecorde(nPontuacao);
            break;
         }

      }
   }
}
