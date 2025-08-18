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
       float nLadoTela = 800;
       
    private:
  
       std::vector<Inimigos> inimigos;
       std::vector<Tiro> tiros;
       
       Ball ball;
       
       int nNivelDificuldade;
       int nPontuacao;
       int nRaioInimigo;
       int nRaioBola;
       int nRaioTiro;
       int nVelocidadeInicialInimigo;
   
       double nDificuldadeBase;
       double nIntervaloOrigemInimigo;
       double nFatorAumentoDificuldade;
       double nMultiplicadorVelocidade;
       double nTempoAumentaVelocidade;
       double nTempoUltimoInimigo;       
};