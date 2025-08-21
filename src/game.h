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
       void InicializaVariaveis();
       void ProcessamentoComandos();
       void TelaGameOver();
       void TelaInicial();
       void VerificaColisoes();
                     
       bool lGameOver;
       bool lIniciarJogo = false;
       float nLadoTela = 900;
       
    private:
  
       std::vector<Inimigos> inimigos;
       std::vector<Tiro> tiros;
       
       Ball ball;
       
       int nMultiplicadorVelocidade;
       int nNivelDificuldade;
       int nPontuacao;
       int nRaioInimigo;
       int nRaioBola;
       int nRaioTiro;
       int nVelocidadeInicialInimigo;
       int nVelocidadeTiro;

       double nIntervaloGeraInimigo;     
       double nFatorIntervaloGeraInimigo;
       double nIntervaloAumentaDificuldade;
       double nTempoAumentaVelocidade;
       double nTempoUltimoInimigo;
       double nFatorAumentoMultiplicadorVelocidade;       
};