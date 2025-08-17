#pragma once
#include "raylib.h"

class Tiro{
    public:
      Tiro(int xnDirecao, int xnLadoTela, int  xnRaioTiro, int xnRaioBola);
      
      void Atualizar();
      void Desenhar();
      
      bool lDesenhar;
      
      int nRaioTiro;
      int nLadoTela;
      
      Vector2 vPosicaoTiro;
      Vector2 vVelocidadeTiro;
};