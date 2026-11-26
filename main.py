import math
import os
import pygame

# --- Configuration ---
USER_NAME = "Amani"
WIDTH, HEIGHT = 560, 560
FPS = 60

# Matching warm pastel palette
BG_COLOR = (246, 238, 227)          # Warm cream background
TEXT_COLOR = (92, 73, 63)           # Soft dark brown outline color
BUBBLE_BG = (255, 251, 246)         # Speech bubble fill
BUBBLE_BORDER = (165, 142, 128)
PINK_BTN_BG = (248, 205, 212)       # Soft pink button fill
PINK_BTN_HOVER = (243, 185, 196)    # Slightly deeper pink on hover
PINK_BTN_BORDER = (196, 136, 148)


def load_sprite(filename, scale_size=None):
    path = os.path.join("assets", filename)
    img = pygame.image.load(path).convert_alpha()
    if scale_size:
        img = pygame.transform.smoothscale(img, scale_size)
    return img


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pookie - Pocket Creature")
    clock = pygame.time.Clock()

    # Fonts
    title_font = pygame.font.SysFont("arial", 36, bold=True)
    bubble_font = pygame.font.SysFont("arial", 20, bold=True)

    # Load sprites
    body_img = load_sprite("pookie_body.png", (210, 175))
    head_open_img = load_sprite("pookie_head_open.png", (175, 165))
    head_closed_img = load_sprite("pookie_head_closed.png", (175, 165))
    head_eating_img = load_sprite("pookie_head_eating.png", (175, 140))
    heart_img = load_sprite("heart.png", (38, 35))
    bonbon_img = load_sprite("bonbon.png", (68, 44))

    # Base positions
    base_x = WIDTH // 2 - 15
    base_y = 345  # Anchor point for Pookie's body

    # Pink button in the lower right containing the bonbon
    bonbon_btn_rect = pygame.Rect(WIDTH - 115, HEIGHT - 108, 92, 84)

    # State machine: "GREETING", "IDLE", "PETTED", "EATING"
    state = "GREETING"
    state_timer = 2.4
    elapsed_time = 0.0

    # Floating hearts list: [x, y, timer]
    hearts = []

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        elapsed_time += dt

        # 1. Handle Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos

                # Check if pink bonbon button was clicked
                if bonbon_btn_rect.collidepoint(mouse_pos):
                    state = "EATING"
                    state_timer = 2.0  # Sprout disappears for 2 seconds while eating

                # Check if Pookie was clicked
                elif pookie_hitbox.collidepoint(mouse_pos):
                    state = "PETTED"
                    state_timer = 1.6
                    hearts.append([base_x - 85, base_y - 145, 1.5])

        # 2. Update Timers & Movement Offsets
        if state != "IDLE":
            state_timer -= dt
            if state_timer <= 0:
                state = "IDLE"

        jump_offset_y = 0
        head_sway_x = 0

        if state == "GREETING":
            jump_offset_y = -abs(math.sin(elapsed_time * 9.0)) * 32
        elif state == "IDLE":
            # Only the head moves gently left and right
            head_sway_x = math.sin(elapsed_time * 2.6) * 7
        elif state == "PETTED":
            head_sway_x = math.sin(elapsed_time * 5.0) * 4
        elif state == "EATING":
            head_sway_x = math.sin(elapsed_time * 12.0) * 3

        # Choose head sprite
        if state == "PETTED":
            current_head = head_closed_img
        elif state == "EATING":
            current_head = head_eating_img  # Sprout disappears while eating
        else:
            current_head = head_open_img    # Sprout visible

        # Compute rects
        body_rect = body_img.get_rect(center=(base_x, base_y + jump_offset_y))
        head_bottom_y = body_rect.top + 90
        head_rect = current_head.get_rect(
            midbottom=(base_x + head_sway_x, head_bottom_y)
        )

        pookie_hitbox = body_rect.union(head_rect)

        # Update floating hearts
        for h in hearts[:]:
            h[1] -= 38 * dt
            h[2] -= dt
            if h[2] <= 0:
                hearts.remove(h)

        # 3. Draw Everything
        screen.fill(BG_COLOR)

        # Top Title: "Pookie"
        title_surf = title_font.render("Pookie", True, TEXT_COLOR)
        title_rect = title_surf.get_rect(center=(WIDTH // 2, 48))
        screen.blit(title_surf, title_rect)

        # Draw Body FIRST, then Head SECOND so the full head stays in front
        screen.blit(body_img, body_rect)
        screen.blit(current_head, head_rect)

        # Greeting speech bubble at startup
        if state == "GREETING":
            msg = f"Hello, {USER_NAME}!"
            msg_surf = bubble_font.render(msg, True, TEXT_COLOR)
            bubble_rect = msg_surf.get_rect(center=(WIDTH // 2, 108))
            padding_rect = bubble_rect.inflate(28, 14)
            pygame.draw.rect(screen, BUBBLE_BG, padding_rect, border_radius=14)
            pygame.draw.rect(screen, BUBBLE_BORDER, padding_rect, width=2, border_radius=14)
            screen.blit(msg_surf, bubble_rect)

        # Draw floating hearts
        for hx, hy, _ in hearts:
            screen.blit(heart_img, (hx, hy))

        # Draw Pink Button in the lower right with the bonbon inside
        is_hovered = bonbon_btn_rect.collidepoint(pygame.mouse.get_pos())
        draw_btn_rect = bonbon_btn_rect.copy()
        if is_hovered:
            draw_btn_rect.y -= 3

        btn_fill = PINK_BTN_HOVER if is_hovered else PINK_BTN_BG
        pygame.draw.rect(screen, btn_fill, draw_btn_rect, border_radius=18)
        pygame.draw.rect(screen, PINK_BTN_BORDER, draw_btn_rect, width=2, border_radius=18)

        bonbon_inside_rect = bonbon_img.get_rect(center=draw_btn_rect.center)
        screen.blit(bonbon_img, bonbon_inside_rect)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()