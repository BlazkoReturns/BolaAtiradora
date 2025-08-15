#pragma once

#include <vector>
#include "ball.h"
#include "inimigos.h"
#include "tiro.h"

class Game{
    public:
       Game();
       
       void Atualizar();
       void DesabilitaObjetos(bool lNovoJogo);
       void Desenhar();
       void GeraInimigos();
       void ProcessamentoComandos();
       void TelaGameOver();
       void VerificaColisoes();
                     
       bool lGameOver;

    private:
       Ball ball;
    
       std::vector<Inimigos> inimigos;
       std::vector<Tiro> tiros;
       
       int nMultiplicadorVelocidade;
       int nNivelDificuldade;
       int nPontuacao;
       
       double nDificuldadeBase;
       double nTempoAumentaVelocidade;
       double nTempoUltimoInimigo;       
};