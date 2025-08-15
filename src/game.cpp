#include "game.h"

Game::Game(){
   nDificuldadeBase = 0.6;
   nPontuacao = 0;
   nMultiplicadorVelocidade = 1;
   nNivelDificuldade = 1;
   nTempoUltimoInimigo = 0;
   lGameOver = false;  
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

   if (nTempoAgora - nTempoAumentaVelocidade > 10.00){
      nDificuldadeBase -= 0.05;
      nMultiplicadorVelocidade += 0.1;
      nNivelDificuldade++;
      nTempoAumentaVelocidade = GetTime(); 
   }

   if(nTempoAgora - nTempoUltimoInimigo > nDificuldadeBase) {
      inimigos.push_back(Inimigos(GetRandomValue(1,4),nMultiplicadorVelocidade)); 
      nTempoUltimoInimigo = GetTime();
   }

}

void Game::ProcessamentoComandos(){
   if (IsKeyPressed(KEY_UP)) {
      tiros.push_back(Tiro(1));
   }else if (IsKeyPressed(KEY_DOWN)) {
      tiros.push_back(Tiro(2));
   }else if (IsKeyPressed(KEY_LEFT)){
      tiros.push_back(Tiro(3));
   } else if (IsKeyPressed(KEY_RIGHT)){
      tiros.push_back(Tiro(4));
   }
}

void Game::TelaGameOver(){
   DrawText(TextFormat("Score: %08i", nPontuacao), 10, 10, 20, BLACK);
   DrawText("Game Over",GetScreenWidth()/2-MeasureText("Game Over",50)/2,GetScreenHeight()/2,50,BLACK);
   DrawText("Press any key to try again",GetScreenWidth()/2-MeasureText("Press any key to try again",30)/2,(GetScreenHeight()/2)+60,30,BLACK);
   
   if (GetKeyPressed() != 0){
      
      lGameOver = false;
      nDificuldadeBase = 0.6;
      nMultiplicadorVelocidade = 1;
      nNivelDificuldade = 1;
      nPontuacao = 0;
      nTempoUltimoInimigo = 0;
      
      DesabilitaObjetos(true);
   }
}

void Game::VerificaColisoes(){
   for (auto& inimigo: inimigos){
      if ((inimigo.nDirecao == 1 && inimigo.vPosicaoInimigo.y >= (GetScreenHeight()/2)-50-inimigo.nRaio) || 
          (inimigo.nDirecao == 2 && inimigo.vPosicaoInimigo.y <= (GetScreenHeight()/2)+50+inimigo.nRaio) ||
          (inimigo.nDirecao == 3 && inimigo.vPosicaoInimigo.x >= (GetScreenWidth()/2)-50-inimigo.nRaio)  ||
          (inimigo.nDirecao == 4 && inimigo.vPosicaoInimigo.x <= (GetScreenWidth()/2)+50+inimigo.nRaio)){
            lGameOver = true;
            break;   
      }           
      
      for (auto& tiro: tiros){
         if ((tiro.nDirecao == 1 && inimigo.nDirecao == 1 && (tiro.vPosicaoTiro.y)<=(inimigo.vPosicaoInimigo.y + inimigo.nRaio)) ||
             (tiro.nDirecao == 2 && inimigo.nDirecao == 2 && (tiro.vPosicaoTiro.y+10)>=(inimigo.vPosicaoInimigo.y - inimigo.nRaio)) ||
             (tiro.nDirecao == 3 && inimigo.nDirecao == 3 && (tiro.vPosicaoTiro.x)<=(inimigo.vPosicaoInimigo.x + inimigo.nRaio)) ||
             (tiro.nDirecao == 4 && inimigo.nDirecao == 4 && (tiro.vPosicaoTiro.x+10)>=(inimigo.vPosicaoInimigo.x - inimigo.nRaio))){
                inimigo.lDesenhar = false;
                tiro.lDesenhar = false;
                nPontuacao += nNivelDificuldade;
         }
      }
   }
}



