#pragma once
#include "raylib.h"

class Tiro{
    public:
      Tiro(int direcao);
      void Atualizar();
      void Desenhar();
      int nDirecao;
      Vector2 vPosicaoTiro;
      bool lDesenhar;
      
    private:
    int nLargura;
    int nAltura;
    int nVelocidadex;
    int nVelocidadey;
};