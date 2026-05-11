import pygame
import re
from constants import *

def draw_rich_text(surface, text, pos, font, default_color=WHITE, max_width=None, align="left"):
    """Dibuja texto con soporte para cambios de color y alineación"""
    start_x, start_y = pos
    color_keywords = {
        "BLUE": BLUE, "RED": RED, "PURPLE": PURPLE, "WHITE": WHITE,
        "YELLOW": YELLOW, "ORANGE": ORANGE, "GREEN": GREEN, "CYAN": CYAN,
        "GOLDEN": GOLD, "GOLD": GOLD, "MAG": BLUE, "NET": RED, "GHOST": GHOST_COLOR,
        "PINK": PINK, "GUM_PINK": GUM_PINK, "GRAY": GRAY
    }
    
    line_height = font.get_linesize()
    
    # Pre-procesamiento para wrap automático si max_width está definido
    processed_text = text
    if max_width:
        words = text.split(' ')
        new_text = ""
        current_line = ""
        for word in words:
            # Limpiar tags para el cálculo del ancho
            clean_word = re.sub(r'\|[A-Z_]+\|', '', word)
            clean_line = re.sub(r'\|[A-Z_]+\|', '', current_line)
            
            if font.size(clean_line + clean_word)[0] < max_width:
                current_line += (word + " ")
            else:
                new_text += current_line.strip() + "\n"
                current_line = word + " "
        new_text += current_line.strip()
        processed_text = new_text

    lines = processed_text.split('\n')
    for i, line in enumerate(lines):
        # Calcular posición X basada en alineación
        if align == "center":
            clean_line = re.sub(r'\|[A-Z_]+\|', '', line)
            line_w = font.size(clean_line)[0]
            curr_x = start_x + (max_width - line_w) // 2 if max_width else start_x - line_w // 2
        else:
            curr_x = start_x
            
        curr_y = start_y + i * line_height
        parts = re.split(r'(\s+|\(|\)|/|\|)', line)
        is_tag = False
        curr_color = default_color
        
        for part in parts:
            if not part: continue
            if part == "|":
                is_tag = not is_tag
                continue
            
            if is_tag and part.upper() in color_keywords:
                curr_color = color_keywords[part.upper()]
                continue
                
            # Si no es un tag, renderizar la palabra
            # Auto-color de palabras clave (v0.6.0 Fix)
            word_color = curr_color
            clean_p = part.upper().strip("(),.¡!¿?")
            if clean_p in ["CROWN", "CORONA"]: word_color = GOLD
            elif clean_p == "ARCADE": word_color = RED

            word_surf = font.render(part, True, word_color)
            surface.blit(word_surf, (curr_x, curr_y))
            curr_x += word_surf.get_width()

def draw_remove_option(game, y, label, is_active, rect, text_rect, active_color=GREEN, is_checkbox=True, offset=0, surface=None):
    if surface is None: surface = game.screen
    lm = game.modifiers_panel_rect.x + 50
    ox = game.modifiers_panel_rect.centerx + 50
    
    # Ajuste de posición basado en el scroll
    draw_y = game.modifiers_panel_rect.y + y - offset
    
    # Dibujar etiqueta (Aumentar ancho de detección a 400 para facilitar colisión)
    text_rect.update(lm, draw_y, 400, 30)
    draw_rich_text(surface, label, (lm, draw_y), game.small_font)
    
    # Dibujar checkbox/toggle (Tamaño original 30x30)
    if is_checkbox:
        rect.update(ox + 25, draw_y - 5, 30, 30)
        pygame.draw.rect(surface, BLACK, rect)
        pygame.draw.rect(surface, WHITE, rect, 2)
        if is_active:
            pygame.draw.rect(surface, active_color, rect.inflate(-10, -10))
    else:
        rect.update(ox + 25, draw_y - 5, 30, 30)
        # Dibujar el cuadrado base (consistente con checkbox)
        pygame.draw.rect(surface, BLACK, rect)
        pygame.draw.rect(surface, WHITE, rect, 2)
        
        # Flecha de acordeón tipo "V" con líneas
        cx, cy = rect.centerx, rect.centery
        if not is_active:
            # Cerrado: Flecha apuntando a la derecha (>)
            pygame.draw.lines(surface, WHITE, False, [(cx - 5, cy - 8), (cx + 3, cy), (cx - 5, cy + 8)], 3)
        else:
            # Abierto: Flecha apuntando abajo (V)
            pygame.draw.lines(surface, WHITE, False, [(cx - 8, cy - 5), (cx, cy + 3), (cx + 8, cy - 5)], 3)

def draw_tooltip(game, lines, surface=None):
    if not lines: return
    if surface is None: surface = game.screen
    
    m_pos = pygame.mouse.get_pos()
    padding = 10
    line_height = 25
    
    tw = max(game.tiny_font.render(l, True, WHITE).get_width() for l in lines) + padding * 2
    th = len(lines) * line_height + padding * 2
    
    tx = m_pos[0] + 15
    ty = m_pos[1] + 15
    
    # Evitar que salga de la pantalla
    if tx + tw > SCREEN_WIDTH: tx = m_pos[0] - tw - 5
    if ty + th > SCREEN_HEIGHT: ty = m_pos[1] - th - 5
    
    rect = pygame.Rect(tx, ty, tw, th)
    pygame.draw.rect(surface, (30, 30, 30), rect)
    pygame.draw.rect(surface, WHITE, rect, 1)
    
    for i, line in enumerate(lines):
        surface.blit(game.tiny_font.render(line, True, WHITE), (tx + padding, ty + padding + i*line_height))

def draw_crown(surface, x, y, size=1.0):
    """Dibuja una corona pixel-art detallada (v0.6.0 New Design)"""
    b = max(1, int(5 * size)) # Escala del píxel
    
    # Matriz de la corona (15x10)
    # 0: Transparente, 1: Negro, 2: Oro, 3: Oro Oscuro, 4: Blanco
    grid = [
        [0,0,0,0,1,0,0,0,0,0,1,0,0,0,0],
        [0,0,0,1,1,1,0,0,0,1,1,1,0,0,0],
        [0,1,0,1,3,1,0,1,0,1,3,1,0,1,0],
        [1,2,1,3,3,3,1,2,1,3,3,3,1,2,1],
        [1,2,2,1,3,1,2,2,2,1,3,1,2,2,1],
        [1,2,2,2,2,2,4,4,2,2,2,2,2,2,1],
        [1,2,4,2,2,2,2,4,2,2,2,2,2,2,1],
        [1,2,4,2,2,2,2,2,2,2,2,2,2,2,1],
        [1,2,4,4,4,2,2,2,2,2,2,2,2,2,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
    ]
    
    colors = {
        1: (0, 0, 0),         # Negro
        2: (255, 200, 0),     # Oro
        3: (130, 100, 0),     # Oro Oscuro
        4: (255, 255, 255)    # Blanco
    }
    
    start_x = x - (len(grid[0]) * b) // 2
    start_y = y - (len(grid) * b)
    
    for r, row in enumerate(grid):
        for c, val in enumerate(row):
            if val in colors:
                pygame.draw.rect(surface, colors[val], (start_x + c*b, start_y + r*b, b, b))
