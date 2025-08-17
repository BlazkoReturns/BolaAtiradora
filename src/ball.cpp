#include "ball.h"
#include <raylib.h>

Ball::Ball()  
{
}

void Ball::Draw() const
{
    DrawCircleLines(nLadoTela/2, nLadoTela/2, nRaioBola, BLACK);
}