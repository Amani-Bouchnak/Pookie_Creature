import math
import os
import pygame

# --- Configuration ---
DEFAULT_USER_NAME = "Amani"
WIDTH, HEIGHT = 560, 560
FPS = 60

# Cozy warm pastel palette
BG_COLOR = (246, 238, 227)            # Warm cream background
TEXT_COLOR = (92, 73, 63)             # Soft dark brown outline color
SHADOW_COLOR = (218, 203, 186)        # Soft warm shadow

BUBBLE_BG = (255, 251, 246)         # Speech bubble fill
BUBBLE_BORDER = (165, 142, 128)

# Livelier bonbon button (berry-coral pastel with depth)
BONBON_BTN_BG = (244, 156, 174)
BONBON_BTN_HOVER = (238, 130, 154)
BONBON_BTN_BORDER = (176, 98, 118)
BONBON_BTN_SHADOW = (214, 168, 178)

# Top-left pastel blue user button
BLUE_BTN_BG = (164, 205, 240)
BLUE_BTN_HOVER = (136, 186, 232)
BLUE_BTN_BORDER = (92, 142, 188)
BLUE_BTN_SHADOW = (175, 196, 214)

# "Wow!" sprout comeback colors
SPARKLE_GOLD = (255, 214, 102)
SPARKLE_PINK = (255, 168, 188)
SPARKLE_MINT = (158, 224, 178)


def load_sprite(filename, scale_size=None):
    path = os.path.join("assets", filename)
    img = pygame.image.load(path).convert_alpha()
    if scale_size:
        img = pygame.transform.smoothscale(img, scale_size)
    return img


def load_sound(filename):
    path = os.path.join("assets", filename)
    if not os.path.exists(path):
        return None
    try:
        return pygame.mixer.Sound(path)
    except pygame.error:
        return None


def pick_font(candidates, size, bold=True):
    available = {name.lower(): name for name in pygame.font.get_fonts()}
    for cand in candidates:
        key = cand.lower().replace(" ", "")
        if key in available:
            return pygame.font.SysFont(available[key], size, bold=bold)
    return pygame.font.SysFont(None, size + 6, bold=bold)


def draw_person_icon(surface, center, color):
    """Draws a crisp 👤-style person icon so it never breaks on any system font."""
    cx, cy = center
    pygame.draw.circle(surface, color, (cx, cy - 7), 6)
    shoulders_rect = pygame.Rect(cx - 11, cy + 1, 22, 13)
    pygame.draw.ellipse(surface, color, shoulders_rect)


def draw_star_sparkle(surface, cx, cy, radius, color):
    """Draws a 4-point sparkle."""
    pts = [
        (cx, cy - radius),
        (cx + radius * 0.28, cy - radius * 0.28),
        (cx + radius, cy),
        (cx + radius * 0.28, cy + radius * 0.28),
        (cx, cy + radius),
        (cx - radius * 0.28, cy + radius * 0.28),
        (cx - radius, cy),
        (cx - radius * 0.28, cy - radius * 0.28),
    ]
    pygame.draw.polygon(surface, color, pts)


def main():
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pookie - Pocket Creature")
    clock = pygame.time.Clock()

    # Load your two sound effects from assets/
    bonbon_fly_sfx = load_sound("bonbonflying.wav")
    chewing_sfx = load_sound("sound-effect-of-chewing-food.wav")
    chewing_channel = None

    def play_fly_sound():
        if bonbon_fly_sfx:
            bonbon_fly_sfx.play()

    def start_chewing_sound():
        nonlocal chewing_channel
        if chewing_sfx:
            chewing_channel = chewing_sfx.play(loops=-1)

    def stop_chewing_sound():
        nonlocal chewing_channel
        if chewing_channel:
            chewing_channel.stop()
            chewing_channel = None
        elif chewing_sfx:
            chewing_sfx.stop()

    # Fonts
    title_font = pick_font(["Comic Sans MS", "Trebuchet MS", "Segoe Print", "Arial"], 50, bold=True)
    bubble_font = pick_font(["Comic Sans MS", "Trebuchet MS", "Arial"], 21, bold=True)
    input_font = pick_font(["Trebuchet MS", "Arial"], 20, bold=True)
    small_font = pick_font(["Trebuchet MS", "Arial"], 15, bold=True)

    # Load sprites
    body_img = load_sprite("pookie_body.png", (210, 175))
    head_open_img = load_sprite("pookie_head_open.png", (175, 165))
    head_closed_img = load_sprite("pookie_head_closed.png", (175, 165))
    head_eating_img = load_sprite("pookie_head_eating.png", (175, 140))
    heart_img = load_sprite("heart.png", (38, 35))
    bonbon_img = load_sprite("bonbon.png", (68, 44))
    flying_bonbon_img = load_sprite("bonbon.png", (52, 34))

    # Base positions
    base_x = WIDTH // 2 - 15
    base_y = 345  # Anchor point for Pookie's body

    # Top-left blue button with 👤 icon
    user_btn_rect = pygame.Rect(18, 18, 50, 50)

    # Pink button in the lower right containing the bonbon
    bonbon_btn_rect = pygame.Rect(WIDTH - 115, HEIGHT - 108, 92, 84)

    # Username & inline editor state
    user_name = DEFAULT_USER_NAME
    editing_name = False
    name_draft = user_name
    save_btn_rect = pygame.Rect(WIDTH // 2 - 45, HEIGHT // 2 + 24, 90, 34)

    # State machine: "GREETING", "IDLE", "PETTED", "TRAVELING_BONBON", "EATING"
    state = "GREETING"
    state_timer = 2.4
    elapsed_time = 0.0

    # Bonbon flight progress (0.0 -> 1.0)
    bonbon_flight_t = 0.0
    bonbon_flight_duration = 0.55

    # "Wow!" sprout reappearance effect timer
    wow_timer = 0.0
    wow_duration = 1.15

    # Floating hearts list: [x, y, timer]
    hearts = []

    def trigger_greeting(duration=2.2):
        nonlocal state, state_timer
        stop_chewing_sound()
        state = "GREETING"
        state_timer = duration

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        elapsed_time += dt

        if wow_timer > 0:
            wow_timer = max(0.0, wow_timer - dt)

        # 1. Handle Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if editing_name:
                    if event.key == pygame.K_RETURN:
                        cleaned = name_draft.strip()
                        if cleaned:
                            user_name = cleaned[:18]
                        editing_name = False
                        trigger_greeting(2.4)
                    elif event.key == pygame.K_ESCAPE:
                        editing_name = False
                        name_draft = user_name
                    elif event.key == pygame.K_BACKSPACE:
                        name_draft = name_draft[:-1]
                    else:
                        if event.unicode and event.unicode.isprintable() and len(name_draft) < 18:
                            name_draft += event.unicode
                else:
                    if event.key == pygame.K_g:
                        trigger_greeting(2.2)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos

                if editing_name:
                    if save_btn_rect.collidepoint(mouse_pos):
                        cleaned = name_draft.strip()
                        if cleaned:
                            user_name = cleaned[:18]
                        editing_name = False
                        trigger_greeting(2.4)
                    continue

                # Top-left blue 👤 button
                if user_btn_rect.collidepoint(mouse_pos):
                    stop_chewing_sound()
                    editing_name = True
                    name_draft = user_name
                    continue

                # Lower-right bonbon button -> send bonbon flying to Pookie's mouth
                if bonbon_btn_rect.collidepoint(mouse_pos):
                    if state != "TRAVELING_BONBON":
                        stop_chewing_sound()
                        state = "TRAVELING_BONBON"
                        bonbon_flight_t = 0.0
                        play_fly_sound()

                # Check if Pookie was clicked
                elif pookie_hitbox.collidepoint(mouse_pos):
                    stop_chewing_sound()
                    state = "PETTED"
                    state_timer = 1.6
                    hearts.append([base_x - 85, base_y - 145, 1.5])

        # 2. Update Timers & Movement Offsets
        if state == "TRAVELING_BONBON":
            bonbon_flight_t += dt / bonbon_flight_duration
            if bonbon_flight_t >= 1.0:
                bonbon_flight_t = 1.0
                state = "EATING"
                state_timer = 2.0  # Sprout disappears while eating
                start_chewing_sound()

        elif state != "IDLE":
            state_timer -= dt
            if state_timer <= 0:
                if state == "EATING":
                    stop_chewing_sound()
                    wow_timer = wow_duration  # Trigger "wow!" sprout comeback
                state = "IDLE"

        jump_offset_y = 0.0
        head_sway_x = 0.0

        if state == "GREETING":
            jump_offset_y = -abs(math.sin(elapsed_time * 9.0)) * 30
            head_sway_x = math.sin(elapsed_time * 3.0) * 1.5
        elif state == "IDLE":
            # Gentle head sway
            head_sway_x = math.sin(elapsed_time * 2.2) * 2.5
        elif state == "PETTED":
            head_sway_x = math.sin(elapsed_time * 4.5) * 2.0
        elif state == "TRAVELING_BONBON":
            head_sway_x = math.sin(elapsed_time * 4.0) * 1.5
        elif state == "EATING":
            head_sway_x = math.sin(elapsed_time * 13.0) * 2.0

        if wow_timer > 0:
            wow_progress = 1.0 - (wow_timer / wow_duration)
            jump_offset_y += -abs(math.sin(wow_progress * math.pi * 2.0)) * 12 * (1.0 - wow_progress * 0.5)

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

        # Bigger, rounder Top Title: "Pookie"
        title_shadow = title_font.render("Pookie", True, SHADOW_COLOR)
        title_surf = title_font.render("Pookie", True, TEXT_COLOR)
        title_rect = title_surf.get_rect(center=(WIDTH // 2, 50))
        screen.blit(title_shadow, title_rect.move(2, 3))
        screen.blit(title_surf, title_rect)

        # "Wow!" aura & sparkles when sprout reappears after eating
        if wow_timer > 0:
            wow_progress = 1.0 - (wow_timer / wow_duration)
            alpha = int(255 * (1.0 - wow_progress))
            glow_radius = int(66 + wow_progress * 44)
            glow_surf = pygame.Surface((glow_radius * 2 + 12, glow_radius * 2 + 12), pygame.SRCALPHA)
            pygame.draw.circle(
                glow_surf,
                (*SPARKLE_GOLD, max(0, min(140, alpha // 2))),
                (glow_radius + 6, glow_radius + 6),
                glow_radius,
                width=5,
            )
            screen.blit(
                glow_surf,
                glow_surf.get_rect(center=(head_rect.centerx, head_rect.top + 28)),
            )

            sparkle_colors = [SPARKLE_GOLD, SPARKLE_PINK, SPARKLE_MINT, SPARKLE_GOLD]
            for i in range(6):
                angle = (i / 6.0) * math.tau + wow_progress * 2.2
                dist = 50 + wow_progress * 32
                sx = head_rect.centerx + math.cos(angle) * dist
                sy = (head_rect.top + 24) + math.sin(angle) * (dist * 0.75)
                s_rad = max(4, int(13 * (1.0 - wow_progress * 0.65)))
                draw_star_sparkle(screen, sx, sy, s_rad, sparkle_colors[i % len(sparkle_colors)])

        # Draw Body FIRST, then Head SECOND so the full head stays in front
        screen.blit(body_img, body_rect)
        screen.blit(current_head, head_rect)

        # Bonbon flying from button to Pookie's mouth
        if state == "TRAVELING_BONBON":
            t = bonbon_flight_t
            ease_t = t * t * (3 - 2 * t)
            start_x, start_y = bonbon_btn_rect.center
            mouth_x = head_rect.centerx
            mouth_y = head_rect.centery + 10
            arc_lift = -math.sin(t * math.pi) * 90

            cur_x = start_x + (mouth_x - start_x) * ease_t
            cur_y = start_y + (mouth_y - start_y) * ease_t + arc_lift
            fly_rect = flying_bonbon_img.get_rect(center=(cur_x, cur_y))
            screen.blit(flying_bonbon_img, fly_rect)

        # Greeting speech bubble
        if state == "GREETING":
            msg = f"Hello, {user_name}!"
            msg_surf = bubble_font.render(msg, True, TEXT_COLOR)
            bubble_rect = msg_surf.get_rect(center=(WIDTH // 2, 114))
            padding_rect = bubble_rect.inflate(28, 14)
            pygame.draw.rect(screen, BUBBLE_BG, padding_rect, border_radius=14)
            pygame.draw.rect(screen, BUBBLE_BORDER, padding_rect, width=2, border_radius=14)
            screen.blit(msg_surf, bubble_rect)

        # Draw floating hearts
        for hx, hy, _ in hearts:
            screen.blit(heart_img, (hx, hy))

        # Top-left Blue Button with 👤 icon
        user_hovered = not editing_name and user_btn_rect.collidepoint(pygame.mouse.get_pos())
        draw_user_rect = user_btn_rect.copy()
        if user_hovered:
            draw_user_rect.y -= 2

        pygame.draw.rect(screen, BLUE_BTN_SHADOW, draw_user_rect.move(0, 3), border_radius=14)
        pygame.draw.rect(
            screen,
            BLUE_BTN_HOVER if user_hovered else BLUE_BTN_BG,
            draw_user_rect,
            border_radius=14,
        )
        pygame.draw.rect(screen, BLUE_BTN_BORDER, draw_user_rect, width=2, border_radius=14)
        draw_person_icon(screen, draw_user_rect.center, TEXT_COLOR)

        # Livelier Pink/Berry Button in the lower right with the bonbon inside
        is_hovered = not editing_name and bonbon_btn_rect.collidepoint(pygame.mouse.get_pos())
        draw_btn_rect = bonbon_btn_rect.copy()
        if is_hovered:
            draw_btn_rect.y -= 3

        pygame.draw.rect(screen, BONBON_BTN_SHADOW, draw_btn_rect.move(0, 4), border_radius=18)
        btn_fill = BONBON_BTN_HOVER if is_hovered else BONBON_BTN_BG
        pygame.draw.rect(screen, btn_fill, draw_btn_rect, border_radius=18)
        pygame.draw.rect(screen, BONBON_BTN_BORDER, draw_btn_rect, width=2, border_radius=18)

        gloss_rect = pygame.Rect(draw_btn_rect.x + 10, draw_btn_rect.y + 8, 26, 6)
        pygame.draw.rect(screen, (255, 232, 238), gloss_rect, border_radius=3)

        bonbon_inside_rect = bonbon_img.get_rect(center=draw_btn_rect.center)
        screen.blit(bonbon_img, bonbon_inside_rect)

        # Inline Username Editor Modal
        if editing_name:
            dim = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            dim.fill((60, 46, 38, 95))
            screen.blit(dim, (0, 0))

            modal_rect = pygame.Rect(WIDTH // 2 - 160, HEIGHT // 2 - 75, 320, 145)
            pygame.draw.rect(screen, BUBBLE_BG, modal_rect, border_radius=18)
            pygame.draw.rect(screen, BUBBLE_BORDER, modal_rect, width=2, border_radius=18)

            prompt_surf = small_font.render("Change your name:", True, TEXT_COLOR)
            screen.blit(prompt_surf, prompt_surf.get_rect(center=(WIDTH // 2, modal_rect.y + 26)))

            box_rect = pygame.Rect(WIDTH // 2 - 120, modal_rect.y + 44, 240, 36)
            pygame.draw.rect(screen, (255, 255, 255), box_rect, border_radius=10)
            pygame.draw.rect(screen, BLUE_BTN_BORDER, box_rect, width=2, border_radius=10)

            cursor = "|" if int(elapsed_time * 2.5) % 2 == 0 else ""
            typed_surf = input_font.render(name_draft + cursor, True, TEXT_COLOR)
            screen.blit(typed_surf, typed_surf.get_rect(midleft=(box_rect.x + 12, box_rect.centery)))

            pygame.draw.rect(screen, BLUE_BTN_BG, save_btn_rect, border_radius=10)
            pygame.draw.rect(screen, BLUE_BTN_BORDER, save_btn_rect, width=2, border_radius=10)
            save_surf = small_font.render("Save", True, TEXT_COLOR)
            screen.blit(save_surf, save_surf.get_rect(center=save_btn_rect.center))

        pygame.display.flip()

    stop_chewing_sound()
    pygame.quit()


if __name__ == "__main__":
    main()