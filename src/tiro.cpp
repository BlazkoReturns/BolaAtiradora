#include "tiro.h"

Tiro::Tiro(int direcao)
   :nLargura(10)
   ,nAltura(10)
   ,nVelocidadex(0)
   ,nVelocidadey(0)   
{

   nDirecao = direcao;
   lDesenhar = true;

   if (direcao == 1 ){
      nVelocidadey = -5;
      vPosicaoTiro.x = 400-nLargura/2;
      vPosicaoTiro.y = 250-nAltura;
   } else if (direcao == 2){
      nVelocidadey = +5;
      vPosicaoTiro.x = 400-nLargura/2;
      vPosicaoTiro.y = 350; 
   } else if (direcao == 3){
      nVelocidadex = -5;
      vPosicaoTiro.x = 350-nLargura;
      vPosicaoTiro.y = 300-nAltura/2;
   } else if (direcao == 4){
      nVelocidadex = +5;
      vPosicaoTiro.x = 450;
      vPosicaoTiro.y = 300-nAltura/2;
   };  
}

void Tiro::Atualizar(){
    vPosicaoTiro.x += nVelocidadex;
    vPosicaoTiro.y += nVelocidadey;

    if (vPosicaoTiro.x >= 800 || vPosicaoTiro.y >= 600 || vPosicaoTiro.x <= 0 || vPosicaoTiro.y <=0){
      lDesenhar = false;
    }
}

void Tiro::Desenhar(){
    DrawRectangleLines(vPosicaoTiro.x, vPosicaoTiro.y, nLargura, nAltura ,BLACK);
}

