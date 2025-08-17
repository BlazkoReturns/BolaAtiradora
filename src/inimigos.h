#pragma once
#include <raylib.h>

class Inimigos{
public:
    Inimigos(int xnDirecao, int xnVelocidadeInicialInimigo, int xnMultiVelocidade, int xnRaioInimigo, int xnLadoTela);

    void Atualizar();
    void Desenhar();
    
    bool lDesenhar;

    int nRaioInimigo;
    
    Vector2 vPosicaoInimigo;
    Vector2 vVelocidadeInimigo;    
};