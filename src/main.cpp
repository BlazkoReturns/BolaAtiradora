#include <raylib.h>
#include "game.h"


int main() 
{
    constexpr int screenWidth = 800;
    constexpr int screenHeight = 600;
      
    InitWindow(screenWidth, screenHeight, "Bola Atiradora");
    SetTargetFPS(60);
    Game game;

    while (!WindowShouldClose())
    {    
        BeginDrawing();
        ClearBackground(WHITE);
        
        if (!game.lGameOver){
           game.Atualizar();
           game.Desenhar();
           game.GeraInimigos();
           game.ProcessamentoComandos();
           game.VerificaColisoes();
           game.DesabilitaObjetos(false);
        } else {
           game.TelaGameOver();
        }
        EndDrawing();
    }
    CloseWindow();
}