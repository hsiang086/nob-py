#include "raylib.h"
#include <stdlib.h>
#include <math.h>

#define SCREEN_WIDTH 800
#define SCREEN_HEIGHT 600
#define MAX_ORBS     50
#define MAX_PARTICLES 512

typedef struct {
    Vector2 position;
    float radius;
    Color color;
    bool active;
} Orb;

typedef struct {
    Vector2 position;
    Vector2 velocity;
    Color color;
    float life;      // remaining life in seconds
} Particle;

Orb orbs[MAX_ORBS];
Particle particles[MAX_PARTICLES];

// Spawn a new orb at a random x, top of screen
void SpawnOrb(void) {
    for (int i = 0; i < MAX_ORBS; i++) {
        if (!orbs[i].active) {
            orbs[i].active = true;
            orbs[i].radius = 15 + rand() % 10;
            orbs[i].position.x = (float)(orbs[i].radius + rand() % (SCREEN_WIDTH - 2 * (int)orbs[i].radius));
            orbs[i].position.y = -orbs[i].radius;
            orbs[i].color = (Color){ GetRandomValue(50,255), GetRandomValue(50,255), GetRandomValue(50,255), 255 };
            break;
        }
    }
}

// Spawn particles at a position with a base color
void SpawnParticles(Vector2 pos, Color color) {
    for (int i = 0; i < 20; i++) {
        for (int j = 0; j < MAX_PARTICLES; j++) {
            if (particles[j].life <= 0) {
                //particles[j].active = true;
                particles[j].position = pos;
                float angle = GetRandomValue(0, 360) * DEG2RAD;
                float speed = GetRandomValue(50, 200);
                particles[j].velocity = (Vector2){ cosf(angle)*speed, sinf(angle)*speed };
                particles[j].color = color;
                particles[j].life = 0.5f + GetRandomValue(0, 500)/1000.0f;
                break;
            }
        }
    }
}

int main(void) {
    InitWindow(SCREEN_WIDTH, SCREEN_HEIGHT, "Catch the Orbs with Particles");
    SetTargetFPS(60);

    // Initialize orbs
    for (int i = 0; i < MAX_ORBS; i++) orbs[i].active = false;
    // Initialize particles
    for (int i = 0; i < MAX_PARTICLES; i++) particles[i].life = 0;

    float spawnTimer = 0;
    int score = 0;

    while (!WindowShouldClose()) {
        float dt = GetFrameTime();
        spawnTimer += dt;

        // Spawn an orb every 0.7 seconds
        if (spawnTimer >= 0.7f) {
            SpawnOrb();
            spawnTimer = 0;
        }

        // Paddle follows mouse x
        Vector2 paddle = { GetMouseX(), SCREEN_HEIGHT - 20 };

        // Update orbs
        for (int i = 0; i < MAX_ORBS; i++) {
            if (!orbs[i].active) continue;
            orbs[i].position.y += 200 * dt;
            // Check catch
            if (CheckCollisionCircleRec(orbs[i].position, orbs[i].radius,
                (Rectangle){ paddle.x - 60, paddle.y - 10, 120, 20 })) {
                score++;
                SpawnParticles(orbs[i].position, orbs[i].color);
                orbs[i].active = false;
            }
            // Missed
            else if (orbs[i].position.y - orbs[i].radius > SCREEN_HEIGHT) {
                SpawnParticles((Vector2){ orbs[i].position.x, SCREEN_HEIGHT }, orbs[i].color);
                orbs[i].active = false;
            }
        }

        // Update particles
        for (int i = 0; i < MAX_PARTICLES; i++) {
            if (particles[i].life > 0) {
                particles[i].life -= dt;
                particles[i].position.x += particles[i].velocity.x * dt;
                particles[i].position.y += particles[i].velocity.y * dt;
                particles[i].velocity.y += 300 * dt; // gravity
            }
        }

        // Draw
        BeginDrawing();
        ClearBackground(BLACK);

        // Draw paddle
        DrawRectanglePro((Rectangle){ paddle.x - 60, paddle.y - 10, 120, 20 }, (Vector2){0,0}, 0, LIGHTGRAY);

        // Draw orbs
        for (int i = 0; i < MAX_ORBS; i++) {
            if (orbs[i].active) {
                DrawCircleV(orbs[i].position, orbs[i].radius, orbs[i].color);
            }
        }

        // Draw particles
        for (int i = 0; i < MAX_PARTICLES; i++) {
            if (particles[i].life > 0) {
                float t = particles[i].life; // fade out
                Color c = particles[i].color;
                c.a = (unsigned char)(255 * (t / 1.0f));
                DrawPixelV(particles[i].position, c);
            }
        }

        // Draw score
        DrawText(TextFormat("Score: %02i", score), 10, 10, 20, RAYWHITE);

        EndDrawing();
    }

    CloseWindow();
    return 0;
}

