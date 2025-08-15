#include "inimigos.h"

Inimigos::Inimigos(int nDirecao, int nMultiVelocidade)
    :nVelocidadex(0),
    nVelocidadey(0),
    nRaio(10.0f)  
{   
    lDesenhar = true;
    this -> nDirecao = nDirecao;

    if (nDirecao==1){
       vPosicaoInimigo.x = 400;
       vPosicaoInimigo.y = 0;
       nVelocidadey = 5*nMultiVelocidade;
    } else if (nDirecao==2){
       vPosicaoInimigo.x = 400;
       vPosicaoInimigo.y = 600;
       nVelocidadey = -5*nMultiVelocidade;
    } if (nDirecao==3){
       vPosicaoInimigo.x = 0;
       vPosicaoInimigo.y = 300;
       nVelocidadex = 5*nMultiVelocidade;
    }if (nDirecao==4){
       vPosicaoInimigo.x = 800;
       vPosicaoInimigo.y = 300;
       nVelocidadex = -5*nMultiVelocidade;
    }

}

void Inimigos::Atualizar(){
    vPosicaoInimigo.x += nVelocidadex;
    vPosicaoInimigo.y += nVelocidadey;
}

void Inimigos::Desenhar(){
    if (lDesenhar){
    DrawCircleLines(vPosicaoInimigo.x,vPosicaoInimigo.y,nRaio,BLACK);
   }   
}