from pgzero.actor import Actor
from pygame.rect import Rect
from pgzero.builtins import music, sounds
import random
import pgzrun

# ===============================
# CONFIGURAÇÕES GERAIS
# ===============================
WIDTH = 1000
HEIGHT = 800
TITLE = "Jump & Dash"

GROUND_Y = 680  # altura do chão

TOP_ENEMY_X = 730
TOP_ENEMY_Y = 170
TOP_ENEMY_PLATFORM_LEFT = 700
TOP_ENEMY_PLATFORM_RIGHT = 850

# ===============================
# ESTADOS DO JOGO
# ===============================
game_state = "menu"
sound_on = True
music_on = True

# ===============================
# BOTÕES DO MENU
# ===============================
play_button = Rect(350, 180, 300, 70)
sound_button = Rect(350, 270, 300, 70)
exit_button = Rect(350, 360, 300, 70)

# ===============================
# VARIÁVEIS PRINCIPAIS
# ===============================
player = None
background = None
platforms = []
enemies = []
player_direction = "right"
enemy_respawns = []

# ===============================
# ANIMAÇÃO DE CORRIDA
# ===============================
run_frame = 1
frame_counter = 0
idle_frame = 1
idle_counter = 0

# ===============================
# FUNÇÕES AUXILIARES
# ===============================
def create_enemy(image_name, x, y, direction, is_top_enemy=False):
    return {
        'actor': Actor(image_name, (x, y)),
        'direction': direction,
        'damage': False,
        'animation_counter': 0,
        'animation_frame': 1,
        'type_image': image_name.rstrip('1'), 
        'is_top_enemy': is_top_enemy
    }

# ===============================
# INICIAR O JOGO
# ===============================
def start_game():
    global player, background, run_frame, frame_counter, platforms, player_direction, enemies, idle_frame, idle_counter, enemy_respawns

    # PLAYER
    player = Actor('idle1')
    player.x = 100
    player.y = GROUND_Y
    player.vy = 0
    player.on_ground = True
    player.direction = "right"
    player.damaged = False
    player.damage_timer = 0
    player.stunned_frame = 1
    player.health = 3  # vida do player

    # BACKGROUND
    background = Actor('background')
    background.width = WIDTH
    background.height = HEIGHT

    # ANIMAÇÃO
    run_frame = 1
    frame_counter = 0
    idle_frame = 1
    idle_counter = 0

    # PLATAFORMAS
    platforms.clear()
    platforms_positions = [
        (400, 550),(430, 550),(460, 550),(490, 550),(520, 550),(550, 550),
        (700, 200),(730, 200),(760, 200),(790, 200),(820, 200),(850, 200),
        (640, 600),(670, 600),(700, 600),(730, 600),
        (60, 400),(90, 400),(120, 400),(150, 400),(180, 400),
        (270, 450),(300, 450),(330, 450),
        (300, 230),(330, 230),(360, 230),(390, 230),(420, 230),(450, 230),
        (480, 230),(510, 230),(540, 230),(570, 230)
    ]
    for pos in platforms_positions:
        platforms.append(Actor('plataforma1', pos))

    # INIMIGOS
    enemies.clear()
    enemy_respawns.clear()
    enemies.append(create_enemy('inimigoe1', 700, GROUND_Y - 50, -1))
    enemies.append(create_enemy('inimigoe1', 850, GROUND_Y - 50, -1))
    enemies.append(create_enemy('inimigoe1', 950, GROUND_Y - 50, -1))
    enemies.append(create_enemy('inimigoidle1', TOP_ENEMY_X, TOP_ENEMY_Y, 1, is_top_enemy=True))

# ===============================
# DESENHO
# ===============================
def draw():
    screen.clear()
    if game_state == "menu":
        screen.fill((30, 30, 60))
        screen.draw.text("JUMP & DASH", center=(WIDTH//2, 100), fontsize=60, color="white")
        screen.draw.filled_rect(play_button, (0, 200, 0))
        screen.draw.text("Jogar", center=play_button.center, fontsize=40, color="white")
        screen.draw.filled_rect(sound_button, (0, 150, 0) if sound_on else (150, 0, 0))
        screen.draw.text(f"Som: {'Ligar' if sound_on else 'Desligar'}", center=sound_button.center, fontsize=30, color="white")
        screen.draw.filled_rect(exit_button, (200, 0, 0))
        screen.draw.text("Sair", center=exit_button.center, fontsize=40, color="white")
    elif game_state == "game" and player:
        if background:
            background.draw()
        for plat in platforms:
            plat.draw()
        player.draw()
        for enemy in enemies:
            enemy['actor'].draw()
        screen.draw.text("Pressione ESC para voltar ao menu", center=(WIDTH//2, 30), fontsize=25, color="yellow")

# ===============================
# UPDATE
# ===============================
def update():
    global run_frame, frame_counter, player_direction, idle_frame, idle_counter

    if game_state != "game" or not player:
        return

    # --- GRAVIDADE ---
    player.vy += 0.5
    player.y += player.vy
    player.on_ground = False

    # COLISÃO COM PLATAFORMAS
    if player.vy >= 0:
        platforms_below = [
            plat for plat in platforms
            if player.bottom <= plat.top + 10 and player.right > plat.left + 5 and player.left < plat.right - 5
        ]
        if platforms_below:
            closest_platform = min(platforms_below, key=lambda p: p.top - player.bottom)
            if player.bottom + player.vy >= closest_platform.top:
                player.bottom = closest_platform.top
                player.vy = 0
                player.on_ground = True
    if player.y >= GROUND_Y:
        player.y = GROUND_Y
        player.vy = 0
        player.on_ground = True

    # --- PULO ---
    if keyboard.up and player.on_ground and not player.damaged:
        player.vy = -13
        player.on_ground = False
        if sound_on:
            sounds.pulo.play()

    # --- MOVIMENTO HORIZONTAL E ANIMAÇÃO ---
    moving = False
    if not player.damaged:
        if keyboard.left:
            player.x -= 5
            moving = True
            player_direction = "left"
        if keyboard.right:
            player.x += 5
            moving = True
            player_direction = "right"
        player.x = max(player.width//2, min(WIDTH - player.width//2, player.x))

    # ANIMAÇÃO
    if player.damaged:
        player.damage_timer -= 1
        if player.damage_timer % 10 == 0:
            player.stunned_frame = 2 if player.stunned_frame == 1 else 1
        player.image = f'atordoadod{player.stunned_frame}'
        if player.damage_timer <= 0:
            player.damaged = False
    else:
        if player.on_ground:
            if moving:
                frame_counter += 1
                if frame_counter % 5 == 0:
                    run_frame = (run_frame % 4) + 1
                player.image = f'correndo{run_frame}' if player_direction == "right" else f'correndoinv{run_frame}'
            else:
                idle_counter += 1
                if idle_counter % 15 == 0:
                    idle_frame = 2 if idle_frame == 1 else 1
                player.image = f'idle{idle_frame}' if player_direction == "right" else f'idleinv{idle_frame}'
        else:
            player.image = 'pulando' if player_direction == "right" else 'pulandoinv'

    # COLISÃO COM INIMIGOS
    for enemy in enemies[:]:
        actor = enemy['actor']
        if player.vy > 0 and player.colliderect(actor) and player.bottom >= actor.top and player.bottom <= actor.top + 10:
            player.vy = -10
            enemy_respawns.append({'type_image': enemy['type_image'], 'timer': 180, 'is_top_enemy': enemy['is_top_enemy']})
            enemies.remove(enemy)
            if sound_on:
                sounds.mortemonstro.play()
            continue
        elif not player.damaged and player.colliderect(actor):
            player.health -= 1
            player.damaged = True
            player.damage_timer = 30
            player.stunned_frame = 1

    # MOVIMENTO INIMIGOS
    for enemy in enemies:
        actor = enemy['actor']
        move_speed = 1 if enemy['type_image'] == 'inimigoidle' else 2
        actor.x += enemy['direction'] * move_speed

        if enemy['is_top_enemy']:
            if actor.x <= TOP_ENEMY_PLATFORM_LEFT:
                actor.x = TOP_ENEMY_PLATFORM_LEFT
                enemy['direction'] = 1
            elif actor.x >= TOP_ENEMY_PLATFORM_RIGHT:
                actor.x = TOP_ENEMY_PLATFORM_RIGHT
                enemy['direction'] = -1
            enemy['animation_counter'] += 1
            if enemy['animation_counter'] % 20 == 0:
                enemy['animation_frame'] = 2 if enemy['animation_frame'] == 1 else 1
            actor.image = f'inimigoidle{enemy["animation_frame"]}' if enemy['direction'] == 1 else f'inimigoidleinv{enemy["animation_frame"]}'
        else:
            if actor.x <= actor.width // 2:
                actor.x = actor.width // 2
                enemy['direction'] = 1
            elif actor.x >= WIDTH - actor.width // 2:
                actor.x = WIDTH - actor.width // 2
                enemy['direction'] = -1
            actor.image = 'inimigoe1' if enemy['direction'] == -1 and not enemy['damage'] else \
                          'inimigofe1' if enemy['direction'] == -1 else \
                          'inimigod1' if not enemy['damage'] else 'inimigofd1'

    # RESPAWN DE INIMIGOS
    for respawn in enemy_respawns[:]:
        respawn['timer'] -= 1
        if respawn['timer'] <= 0:
            new_direction = random.choice([-1, 1])
            if respawn['is_top_enemy']:
                new_enemy = create_enemy(f'{respawn["type_image"]}1', TOP_ENEMY_X, TOP_ENEMY_Y, new_direction, is_top_enemy=True)
            else:
                possible_platforms = [plat for plat in platforms if plat.y < GROUND_Y - 300]
                if possible_platforms:
                    plat = random.choice(possible_platforms)
                    new_enemy = create_enemy(f'{respawn["type_image"]}1', plat.x, plat.y - 30, new_direction)
                else:
                    new_enemy = create_enemy(f'{respawn["type_image"]}1', random.randint(100, WIDTH - 100), GROUND_Y - 50, new_direction)
            enemies.append(new_enemy)
            enemy_respawns.remove(respawn)

# ===============================
# MOUSE
# ===============================
def on_mouse_down(pos):
    global game_state, sound_on
    if game_state == "menu":
        button_clicked = False
        if play_button.collidepoint(pos):
            start_game()
            game_state = "game"
            button_clicked = True
        elif sound_button.collidepoint(pos):
            sound_on = not sound_on
            button_clicked = True
            if sound_on:
                music.play("theme")
            else:
                music.stop()
        elif exit_button.collidepoint(pos):
            exit()

        if button_clicked and sound_on:
            sounds.click.play()

# ===============================
# TECLADO
# ===============================
def on_key_down(key):
    global game_state
    if key == keys.ESCAPE and game_state == "game":
        game_state = "menu"

# ===============================
# Toca a música ao iniciar o jogo
# ===============================
if music_on:
    try:
        music.play("theme")
    except Exception:
        pass

# INICIA O JOGO
pgzrun.go()
