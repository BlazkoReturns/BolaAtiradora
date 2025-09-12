#pragma once

#include <vector>
#include "ball.h"
#include "inimigos.h"
#include "tiro.h"

class Game{
    public:
       Game();
       
       void Atualizar();
       int CarregarRecorde();
       void DesabilitaObjetos(bool lNovoJogo);
       void Desenhar();
       void DesenharSetasHorizontais();
       void DesenharSetasVerticais();
       void DesenharSetasDiagonais();
       void GeraInimigos();
       void InicializaVariaveis();
       void ProcessamentoComandos();
       void SalvarRecorde(int score);
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
       
       int nModoJogo = 2;
       int nMultiplicadorVelocidade;
       int nNivelDificuldade;
       int nPontuacao;
       int nRaioInimigo;
       int nRaioBola;
       int nRaioTiro;
       int nRecorde;
       int nVelocidadeInicialInimigo;
       int nVelocidadeTiro;

       double nIntervaloGeraInimigo;     
       double nFatorIntervaloGeraInimigo;
       double nIntervaloAumentaDificuldade;
       double nTempoAumentaVelocidade;
       double nTempoUltimoInimigo;
       double nFatorAumentoMultiplicadorVelocidade;       
};