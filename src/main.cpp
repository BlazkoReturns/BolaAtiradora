#include <raylib.h>
#include "game.h"

int main() 
{    
    
    Game game;
    
    while (!WindowShouldClose())
    {    
        BeginDrawing();
        ClearBackground(WHITE);
    
        if (!game.lIniciarJogo){
           game.TelaInicial();
        } else {
           if (!game.lGameOver){
              game.Atualizar();
              game.Desenhar();
              game.GeraInimigos();
              game.ProcessamentoComandos();
              game.VerificaColisoes();
              game.VerificaTiroErrado();
              game.DesabilitaObjetos(false);
            } else {
              game.TelaGameOver();
            }
        }

        EndDrawing();
    }
    CloseWindow();
}