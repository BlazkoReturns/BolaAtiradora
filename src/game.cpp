#include "game.h"

Game::Game(){

   InitWindow(nLadoTela, nLadoTela, "Bola Atiradora 0.1");
   SetTargetFPS(60);

   lGameOver = false;
   nPontuacao = 0;
   
   /*Variáveis relacionadas a dificuldade do jogo*/
   nDificuldadeBase = 0.6;
   nIntervaloOrigemInimigo = 10;
   nMultiplicadorVelocidade = 1;
   nNivelDificuldade = 1;
   nTempoUltimoInimigo = 0;
   nVelocidadeInicialInimigo =5;
   
   /*Variáveis de tamanhos dos objetos*/
   nRaioBola = 50;
   nRaioInimigo = 10;
   nRaioTiro = 7;
   ball.nRaioBola = nRaioBola;
   ball.nLadoTela = nLadoTela;

}


void Game::Atualizar(){
   for (auto& tiro: tiros){
      tiro.Atualizar();
   } 
   for (auto& inimigo: inimigos){
      inimigo.Atualizar();
   }
}

void Game::DesabilitaObjetos(bool lNovoJogo){   
   for(auto it = tiros.begin(); it != tiros.end();){
        if(!it -> lDesenhar || lNovoJogo) {
            it = tiros.erase(it);
        } else {
            ++ it;
        }
    }

   for(auto it = inimigos.begin(); it != inimigos.end();){
        if(!it -> lDesenhar || lNovoJogo) {
            it = inimigos.erase(it);
        } else {
            ++ it;
        }
    }
}

void Game::Desenhar(){
   for (auto& tiro: tiros){
      tiro.Desenhar();
   } 

   for (auto& inimigo: inimigos){
      inimigo.Desenhar();
   }

   ball.Draw();
   
   DrawText(TextFormat("Score: %08i", nPontuacao), 10, 10, 20, BLACK);
   DrawText(TextFormat("Dificuldade: %08i", nNivelDificuldade), 10, 30, 20, BLACK);
}

void Game::GeraInimigos(){
   double nTempoAgora = GetTime();

   if (nTempoAgora - nTempoAumentaVelocidade > nIntervaloOrigemInimigo){
      nDificuldadeBase -= 0.05;
      nMultiplicadorVelocidade += 0.1;
      nNivelDificuldade++;
      nTempoAumentaVelocidade = GetTime(); 
   }

   if(nTempoAgora - nTempoUltimoInimigo > nDificuldadeBase) {
      inimigos.push_back(Inimigos(GetRandomValue(1,4),nVelocidadeInicialInimigo,nMultiplicadorVelocidade,nRaioInimigo,nLadoTela)); 
      nTempoUltimoInimigo = GetTime();
   }

}

void Game::ProcessamentoComandos(){
   if (IsKeyPressed(KEY_UP)) {
      tiros.push_back(Tiro(1,nLadoTela,nRaioTiro,nRaioBola));
   }else if (IsKeyPressed(KEY_DOWN)) {
      tiros.push_back(Tiro(2,nLadoTela,nRaioTiro,nRaioBola));
   }else if (IsKeyPressed(KEY_LEFT)){
      tiros.push_back(Tiro(3,nLadoTela,nRaioTiro,nRaioBola));
   } else if (IsKeyPressed(KEY_RIGHT)){
      tiros.push_back(Tiro(4,nLadoTela,nRaioTiro,nRaioBola));
   }
}

void Game::TelaGameOver(){
   DrawText(TextFormat("Score: %08i", nPontuacao), 10, 10, 20, BLACK);
   DrawText("Game Over",nLadoTela/2-MeasureText("Game Over",50)/2,nLadoTela/2,50,BLACK);
   DrawText("Press any key to try again",nLadoTela/2-MeasureText("Press any key to try again",30)/2,(nLadoTela/2)+60,30,BLACK);
   DesabilitaObjetos(true);

   if (GetKeyPressed() != 0){
      lGameOver = false;
      nDificuldadeBase = 0.6;
      nMultiplicadorVelocidade = 1;
      nNivelDificuldade = 1;
      nPontuacao = 0;
      nTempoUltimoInimigo = 0;
   }
}

void Game::VerificaColisoes(){
   for (auto& inimigo: inimigos){
      if (CheckCollisionCircles({nLadoTela/2,nLadoTela/2},50,{inimigo.vPosicaoInimigo.x,inimigo.vPosicaoInimigo.y},inimigo.nRaioInimigo)){
            lGameOver = true;
            break;   
      }           
      
      for (auto& tiro: tiros){
         if (CheckCollisionCircles({tiro.vPosicaoTiro.x,tiro.vPosicaoTiro.y},nRaioTiro,{inimigo.vPosicaoInimigo.x,inimigo.vPosicaoInimigo.y},nRaioInimigo)){
                inimigo.lDesenhar = false;
                tiro.lDesenhar = false;
                nPontuacao += nNivelDificuldade;
         }
      }
   }
}



