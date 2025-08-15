#include "ball.h"
#include <raylib.h>

Ball::Ball() 
    :radius(50) 
{
}

void Ball::Draw() const
{
    DrawCircleLines(GetScreenWidth()/2, GetScreenHeight()/2, radius, BLACK);
}