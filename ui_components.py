import pygame
import re
from constants import *

def draw_rich_text(surface, text, pos, font, default_color=WHITE):
    """Dibuja texto con soporte para cambios de color persistentes"""
    parts = re.split(r'(\s+|\(|\)|/|\|)', text)
    curr_x, curr_y = pos
    curr_color = default_color
    color_keywords = {
        "BLUE": BLUE, "RED": RED, "PURPLE": PURPLE, "WHITE": WHITE,
        "YELLOW": YELLOW, "ORANGE": ORANGE, "GREEN": GREEN, "CYAN": CYAN,
        "GOLDEN": GOLD, "GOLD": GOLD, "MAG": BLUE, "NET": RED
    }
    is_tag = False
    for part in parts:
        if not part: continue
        if part == "|":
            is_tag = not is_tag
            continue
        
        if is_tag and part.upper() in color_keywords:
            curr_color = color_keywords[part.upper()]
            continue
            
        # Si no es un tag, renderizar la palabra
        word_surf = font.render(part, True, curr_color)
        surface.blit(word_surf, (curr_x, curr_y))
        curr_x += word_surf.get_width()

def draw_remove_option(game, y, label, is_active, rect, text_rect, active_color=GREEN, is_checkbox=True, offset=0, surface=None):
    if surface is None: surface = game.screen
    lm = game.modifiers_panel_rect.x + 50
    ox = game.modifiers_panel_rect.centerx + 50
    
    # Ajuste de posición basado en el scroll
    draw_y = game.modifiers_panel_rect.y + y - offset
    
    # Dibujar etiqueta
    text_rect.update(lm, draw_y, 250, 25)
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
