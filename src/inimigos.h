#pragma once
#include <raylib.h>

class Inimigos{
public:
    Inimigos(int nDirecao, int nMultiVelocidade);

    void Atualizar();
    void Desenhar();
    
    bool lDesenhar;
    double nVelocidadex;
    double nVelocidadey;
    int nDirecao;
    float nRaio;
    Vector2 vPosicaoInimigo;    
};