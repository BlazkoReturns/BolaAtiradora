#include "inimigos.h"

Inimigos::Inimigos(int xnDirecao, int xnVelocidadeInicialInimigo,int xnMultiVelocidade, int xnRaioInimigo, int xnLadoTela)
{   
    lDesenhar = true;
    nRaioInimigo = xnRaioInimigo;
    
    if (xnDirecao==1){
       vPosicaoInimigo.x = xnLadoTela/2;
       vPosicaoInimigo.y = 0;
       vVelocidadeInimigo.y = xnVelocidadeInicialInimigo * xnMultiVelocidade;
       vVelocidadeInimigo.x = 0;
    } else if (xnDirecao==2){
       vPosicaoInimigo.x = xnLadoTela/2;
       vPosicaoInimigo.y = xnLadoTela;
       vVelocidadeInimigo.y = -xnVelocidadeInicialInimigo * xnMultiVelocidade;
       vVelocidadeInimigo.x = 0;
    } if (xnDirecao==3){
       vPosicaoInimigo.x = 0;
       vPosicaoInimigo.y = xnLadoTela/2;
       vVelocidadeInimigo.x =  xnVelocidadeInicialInimigo * xnMultiVelocidade;
       vVelocidadeInimigo.y = 0;
    }if (xnDirecao==4){
       vPosicaoInimigo.x = xnLadoTela;
       vPosicaoInimigo.y = xnLadoTela/2;
       vVelocidadeInimigo.x = -xnVelocidadeInicialInimigo * xnMultiVelocidade;
       vVelocidadeInimigo.y = 0;
    }

}

void Inimigos::Atualizar(){
    vPosicaoInimigo.x += vVelocidadeInimigo.x;
    vPosicaoInimigo.y += vVelocidadeInimigo.y;
}

void Inimigos::Desenhar(){
    if (lDesenhar){
    DrawCircleLines(vPosicaoInimigo.x,vPosicaoInimigo.y,nRaioInimigo,BLACK);
   }   
}