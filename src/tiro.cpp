#include "tiro.h"

Tiro::Tiro(int xnDirecao, int xnLadoTela, int  xnRaioTiro, int xnVelocidadeTiro,int xnRaioBola)   
{

   nLadoTela = xnLadoTela;
   nRaioTiro = xnRaioTiro;
   lDesenhar = true;


   if (xnDirecao == 1 ){ /*Cima*/
      vVelocidadeTiro.y = -xnVelocidadeTiro;
      vVelocidadeTiro.x =0 ;
      vPosicaoTiro.x = (nLadoTela/2);
      vPosicaoTiro.y = (nLadoTela/2)-(nRaioTiro/2)-xnRaioBola;
   } else if (xnDirecao == 2){ /*Baixo*/
      vVelocidadeTiro.y = +xnVelocidadeTiro;
      vVelocidadeTiro.x =0 ;
      vPosicaoTiro.x = (nLadoTela/2);
      vPosicaoTiro.y = (nLadoTela/2)+(nRaioTiro/2)+xnRaioBola; 
   } else if (xnDirecao == 3){/*Esqueda*/
      vVelocidadeTiro.x = -xnVelocidadeTiro;
      vVelocidadeTiro.y = 0 ;
      vPosicaoTiro.x = (nLadoTela/2)-(nRaioTiro/2)-xnRaioBola;
      vPosicaoTiro.y = (nLadoTela/2);
   } else if (xnDirecao == 4){/*Direita*/
      vVelocidadeTiro.x = +xnVelocidadeTiro;
      vVelocidadeTiro.y = 0;
      vPosicaoTiro.x = (nLadoTela/2)+(nRaioTiro/2)+xnRaioBola;
      vPosicaoTiro.y = (nLadoTela/2);
   };  
}

void Tiro::Atualizar(){
    vPosicaoTiro.x += vVelocidadeTiro.x;
    vPosicaoTiro.y += vVelocidadeTiro.y;

    if (vPosicaoTiro.x >= nLadoTela || vPosicaoTiro.y >= nLadoTela || vPosicaoTiro.x <= 0 || vPosicaoTiro.y <=0){
      lDesenhar = false;
    }
}

void Tiro::Desenhar(){
    DrawCircleLines(vPosicaoTiro.x, vPosicaoTiro.y, nRaioTiro ,BLACK);
}

