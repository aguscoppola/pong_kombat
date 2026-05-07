import pygame
import random
import math
import os
import sys
from constants import *
from entities import Ball, Paddle, Particle
from ui_components import draw_rich_text, draw_remove_option, draw_tooltip
from audio_manager import AudioManager
from vfx_manager import VFXManager
import assets

class Game:
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pong Kombat v0.5.0")
        
        self.clock = pygame.time.Clock()
        self.audio = AudioManager()
        self.vfx = VFXManager()
        self.init_fonts()
        self.init_entities()
        self.init_game_state()
        self.init_modifier_variables()

    def init_fonts(self):
        self.font = pygame.font.SysFont("Arial", 36, bold=True)
        self.medium_font = pygame.font.SysFont("Arial", 30, bold=True)
        self.large_font = pygame.font.SysFont("Arial", 50, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 24, bold=True)
        self.tiny_font = pygame.font.SysFont("Arial", 16, bold=False)

    def init_entities(self):
        # PADDLE_OFFSET se define como 30 para mantener la consistencia
        offset = 30
        self.paddle1 = Paddle(offset, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2)
        self.paddle2 = Paddle(SCREEN_WIDTH - offset - PADDLE_WIDTH, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2)
        self.balls = [Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]

    def init_game_state(self):
        self.score1 = 0
        self.score2 = 0
        self.state = STATE_MAIN_MENU
        self.serve_timer = 0
        self.serve_direction = 1
        self.winner_text = ""
        self.global_hits = 0
        self.revolver_item_active = False
        self.revolver_item_rect = None
        self.revolver_angle = 0.0
        self.revolver_orbit_radius = 180
        self.hourglass_rect = None
        self.hourglass_type = 0
        self.zone_type = 0
        self.slow_zone_owner = 0
        self.last_hitter = 0
        self.wall_sound_cooldown = 0
        self.ai_mode = False # Nuevo para v0.4.0
        self.language = "EN" # "EN" o "ES"
        self.vfx_enabled = True
        self.sfx_enabled = True
        self.last_hovered_rect = None # Para sonidos de hover
        
        # Screen Shake
        self.shake_amount = 0
        self.shake_timer = 0

    def init_modifier_variables(self):
        # Botones Principales (v0.4.0 - Restaurado a 3 botones grandes)
        self.btn_play_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 100, 300, 70)
        self.btn_modifiers_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 15, 300, 70)
        self.btn_settings_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 70, 300, 70)
        
        panel_w, panel_h = 700, 450
        self.modifiers_panel_rect = pygame.Rect(SCREEN_WIDTH//2 - panel_w//2, SCREEN_HEIGHT//2 - panel_h//2, panel_w, panel_h)
        self.back_btn_rect = pygame.Rect(self.modifiers_panel_rect.right - 90, self.modifiers_panel_rect.y + 10, 80, 40)
        self.score_btn_rect = pygame.Rect(0,0,0,0)
        self.ball_speed_btn_rect = pygame.Rect(0,0,0,0)
        
        # Scroll
        self.scroll_y = 0
        self.max_scroll = 150
        self.is_dragging_scrollbar = True # Placeholder logic
        self.scrollbar_rect = pygame.Rect(self.modifiers_panel_rect.right - 20, self.modifiers_panel_rect.y + 60, 10, self.modifiers_panel_rect.height - 70)
        self.scrollbar_thumb_height = 50
        self.scrollbar_thumb_rect = pygame.Rect(self.scrollbar_rect.x, self.scrollbar_rect.y, 10, self.scrollbar_thumb_height)
        self.is_dragging_scrollbar = False
        self.scroll_offset_y = 0

        # Pestañas
        self.modifiers_tab = "ALL"
        self.tab_all_rect = pygame.Rect(0, 0, 100, 45)
        self.tab_extras_rect = pygame.Rect(0, 0, 120, 45)
        self.tab_skins_rect = pygame.Rect(0, 0, 130, 45)

        # Modificadores de Juego
        self.max_score = 6
        self.ball_speed_multiplier_options = [1.01, 1.025, 1.05, 1.075]
        self.ball_speed_multiplier_names = ["Low", "Default", "Original", "Fast"]
        self.ball_speed_multiplier_idx = 1
        self.ball_speed_btn_rect = pygame.Rect(0,0,130,40)
        self.match_point_enabled = False
        self.match_point_rect = pygame.Rect(0,0,30,30)
        self.match_point_text_rect = pygame.Rect(0,0,0,0)
        self.golden_goal_anim_enabled = True
        self.golden_goal_anim_rect = pygame.Rect(0,0,30,30)
        self.golden_goal_anim_text_rect = pygame.Rect(0,0,0,0)
        self.show_golden_goal_anim = False
        
        # Opciones de Settings (v0.4.0)
        self.lang_rect = pygame.Rect(0,0,130,40)
        self.vfx_enabled = True
        self.vfx_rect = pygame.Rect(0,0,30,30)
        self.sfx_volume = 0.5 # 50% por defecto
        self.volume_bar_rect = pygame.Rect(0,0,200,10)
        self.volume_handle_rect = pygame.Rect(0,0,15,30)
        self.is_dragging_volume = False
        self.shake_enabled = True
        self.shake_rect = pygame.Rect(0,0,30,30)
        self.settings_back_btn_rect = pygame.Rect(0,0,80,40)
        self.settings_apply_btn_rect = pygame.Rect(0,0,130,45)
        self.golden_goal_anim_timer = 0
        self.is_golden_goal_round = False
        self.show_match_point_anim = False
        self.match_point_anim_timer = 0.0

        self.reroll_enabled = True
        self.reroll_rect = pygame.Rect(0,0,30,30)
        self.reroll_text_rect = pygame.Rect(0,0,0,0)
        self.all_reroll_enabled = False
        self.all_reroll_rect = pygame.Rect(0,0,30,30)
        self.all_reroll_text_rect = pygame.Rect(0,0,0,0)

        self.equal_watches_enabled = False
        self.equal_watches_rect = pygame.Rect(0,0,30,30)
        self.equal_watches_text_rect = pygame.Rect(0,0,0,0)
        self.equal_powers_enabled = False
        self.equal_powers_rect = pygame.Rect(0,0,30,30)
        self.equal_powers_text_rect = pygame.Rect(0,0,0,0)
        self.watches_kept_enabled = False
        self.watches_kept_rect = pygame.Rect(0,0,30,30)
        self.watches_kept_text_rect = pygame.Rect(0,0,0,0)

        # Relojes y Poderes
        self.watch_spawn_hits_options = [3, 5, 10, 15]
        self.watch_spawn_hits_idx = 2
        self.watch_spawn_hits_rect = pygame.Rect(0,0,80,40)
        self.watch_spawn_hits_text_rect = pygame.Rect(0,0,0,0)
        self.power_auto_grant_hits_options = [3, 5, 7, 10, 12]
        self.power_auto_grant_hits_idx = 2
        self.power_auto_grant_hits_rect = pygame.Rect(0,0,80,40)
        self.power_auto_grant_hits_text_rect = pygame.Rect(0,0,0,0)
        self.start_with_power_enabled = True
        self.start_with_power_rect = pygame.Rect(0,0,30,30)
        self.start_with_power_text_rect = pygame.Rect(0,0,0,0)

        # Secciones colapsables
        self.remove_watches_expanded = False
        self.remove_watches_toggle_rect = pygame.Rect(0,0,30,30)
        self.remove_watches_toggle_text_rect = pygame.Rect(0,0,0,0)
        self.remove_blue = self.remove_red = self.remove_purple = self.remove_white = self.remove_yellow = False
        self.remove_blue_rect = pygame.Rect(0,0,30,30)
        self.remove_red_rect = pygame.Rect(0,0,30,30)
        self.remove_purple_rect = pygame.Rect(0,0,30,30)
        self.remove_white_rect = pygame.Rect(0,0,30,30)
        self.remove_yellow_rect = pygame.Rect(0,0,30,30)
        self.remove_blue_text_rect = self.remove_red_text_rect = self.remove_purple_text_rect = self.remove_white_text_rect = self.remove_yellow_text_rect = pygame.Rect(0,0,0,0)

        self.remove_power_expanded = False
        self.remove_power_toggle_rect = pygame.Rect(0,0,30,30)
        self.remove_power_toggle_text_rect = pygame.Rect(0,0,0,0)
        self.remove_power_red = self.remove_power_green = self.remove_power_yellow = self.remove_power_orange = False
        self.remove_power_red_rect = pygame.Rect(0,0,30,30)
        self.remove_power_green_rect = pygame.Rect(0,0,30,30)
        self.remove_power_yellow_rect = pygame.Rect(0,0,30,30)
        self.remove_power_orange_rect = pygame.Rect(0,0,30,30)
        self.remove_power_red_text_rect = self.remove_power_green_text_rect = self.remove_power_yellow_text_rect = self.remove_power_orange_text_rect = pygame.Rect(0,0,0,0)

        self.experimental_expanded = False
        self.experimental_toggle_rect = pygame.Rect(0,0,30,30)
        self.experimental_toggle_text_rect = pygame.Rect(0,0,0,0)
        self.orange_watch_enabled = False
        self.orange_watch_rect = pygame.Rect(0,0,30,30)
        self.orange_watch_text_rect = pygame.Rect(0,0,0,0)
        self.magnet_power_enabled = True
        self.magnet_power_rect = pygame.Rect(0,0,30,30)
        self.magnet_power_text_rect = pygame.Rect(0,0,0,0)
        self.ghost_power_enabled = True
        self.ghost_power_rect = pygame.Rect(0,0,30,30)
        self.ghost_power_text_rect = pygame.Rect(0,0,0,0)
        self.ghost_identical_enabled = False # Nuevo sub-modificador
        self.ghost_identical_rect = pygame.Rect(0,0,30,30)
        self.ghost_identical_text_rect = pygame.Rect(0,0,0,0)
        self.gum_power_enabled = False # Nuevo en EXTRAS
        self.gum_power_rect = pygame.Rect(0,0,30,30)
        self.gum_power_text_rect = pygame.Rect(0,0,0,0)
        
        self.gum_projectiles = []
        self.experimental_golden_goal = False
        self.experimental_golden_goal_rect = pygame.Rect(0,0,30,30)
        self.experimental_golden_goal_text_rect = pygame.Rect(0,0,0,0)
        self.floating_planets_enabled = False
        self.floating_planets_rect = pygame.Rect(0,0,30,30)
        self.floating_planets_text_rect = pygame.Rect(0,0,0,0)
        self.ghost_power_enabled = False
        self.ghost_power_rect = pygame.Rect(0,0,30,30)
        self.ghost_power_text_rect = pygame.Rect(0,0,0,0)
        
        self.portals_enabled = False
        self.portals_rect = pygame.Rect(0,0,30,30)
        self.portals_text_rect = pygame.Rect(0,0,0,0)
        
        self.portal_size_options = [25, 50, 75, 125, 200]
        self.portal_size_names = ["Minion", "Short", "Default", "Big", "Giant"]
        self.portal_size_idx = 2
        self.portal_size_rect = pygame.Rect(0,0,130,40)
        self.portal_size_text_rect = pygame.Rect(0,0,0,0)
        
        self.portals_vertical = False
        self.portals_vertical_rect = pygame.Rect(0,0,30,30)
        self.portals_vertical_text_rect = pygame.Rect(0,0,0,0)
        
        self.more_portals_enabled = False
        self.more_portals_rect = pygame.Rect(0,0,30,30)
        self.more_portals_text_rect = pygame.Rect(0,0,0,0)
        
        self.revolver_enabled = False
        self.revolver_rect = pygame.Rect(0,0,30,30)
        self.revolver_text_rect = pygame.Rect(0,0,0,0)
        
        self.portal_red_rect = pygame.Rect(0,0,0,0)
        self.portal_green_rect = pygame.Rect(0,0,0,0)
        
        self._update_portal_rects()

        # Planetas
        self.planet1_pos = (SCREEN_WIDTH // 2, 80)
        self.planet2_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80)
        self.planet_radius = 22
        self.gravity_radius_options = [100, 180, 250, 350]
        self.gravity_radius_names = ["Moon", "Planet", "Gas Giant", "Star"]
        self.gravity_radius_idx = 1
        self.gravity_radius_rect = pygame.Rect(0,0,80,40)
        self.gravity_force_options = [5.0, 10.0, 15.0, 20.0]
        self.gravity_force_names = ["Moon", "Planet", "Gas Giant", "Star"]
        self.gravity_force_idx = 1
        self.gravity_force_rect = pygame.Rect(0,0,80,40)
        self.destructible_planets_enabled = False
        self.destructible_planets_rect = pygame.Rect(0,0,30,30)
        self.destructible_planets_text_rect = pygame.Rect(0,0,0,0)
        self.planet1_hits = self.planet2_hits = 0
        self.planet1_alive = self.planet2_alive = True
        self.planet_resistance_options = [5, 7, 10, 13]
        self.planet_resistance_names = ["Moon", "Planet", "Gas Giant", "Star"]
        self.planet_resistance_idx = 2
        
        # Selección de Modo
        self.is_ai_mode = False
        # Botones gigantes (350x400)
        bw, bh = 300, 350
        self.btn_multi_rect = pygame.Rect(SCREEN_WIDTH//4 - bw//2, SCREEN_HEIGHT//2 - bh//2 + 30, bw, bh)
        self.btn_solo_rect = pygame.Rect(SCREEN_WIDTH*3//4 - bw//2, SCREEN_HEIGHT//2 - bh//2 + 30, bw, bh)
        self.planet_resistance_rect = pygame.Rect(0,0,130,40)

        # Skins y X2
        self.orange_skin_options = ["Default", "Hadouken"]
        self.orange_skin_idx = 0
        self.orange_skin_rect = pygame.Rect(0,0,130,40)
        self.yellow_watch_skin_options = ["Default", "CROSS"]
        self.yellow_watch_skin_idx = 0
        self.yellow_watch_skin_rect = pygame.Rect(0,0,130,40)
        self.start_x2_enabled = False
        self.start_x2_rect = pygame.Rect(0,0,30,30)
        self.start_x2_text_rect = pygame.Rect(0,0,0,0)
        self.is_x2_item_active = False
        
        self.ball_skin_options = ["Default", "CHEESE", "Tennis"]
        self.ball_skin_idx = 0
        self.ball_skin_rect = pygame.Rect(0,0,130,40)
        self.pending_x2_spawn = False
        self.ball_is_x2 = False
        self.x2_item_rect = pygame.Rect(SCREEN_WIDTH//2 - 20, SCREEN_HEIGHT//2 - 20, 40, 40)
        
        self.initial_ball_speed_options = [0.75, 1.0, 1.25, 1.5, 2.0]
        self.initial_ball_speed_names = ["Low", "Default", "Mid", "Fast", "FLASH"]
        self.initial_ball_speed_idx = 1
        self.initial_ball_speed_rect = pygame.Rect(0,0,130,40)
        
        self.yellow_speed_up_options = [0.25, 0.5, 0.75, 1.0]
        self.yellow_speed_up_names = ["Low", "Default", "Big", "Giant"]
        self.yellow_speed_up_idx = 1
        self.yellow_speed_up_rect = pygame.Rect(0,0,130,40)
        
        self.encapsulate_powers_enabled = False
        self.encapsulate_powers_rect = pygame.Rect(0,0,30,30)
        self.encapsulate_powers_text_rect = pygame.Rect(0,0,250,25)
        
        self.add_mouse_enabled = False
        self.mouse = None
        self.mouse_hits_counter = 0
        self.add_mouse_rect = pygame.Rect(0,0,30,30)
        self.add_mouse_text_rect = pygame.Rect(0,0,250,25)
        self.add_mouse_expanded = False # Para el acordeón
        
        self.mouse_speed_options = [0.1, 0.25, 0.5, 1.0]
        self.mouse_speed_names = ["Slow", "Normal", "Default", "Fast"]
        self.mouse_speed_idx = 2
        self.mouse_speed_rect = pygame.Rect(0,0,130,40)
        
        self.mouse_appear_options = [1, 2, 3, 5]
        self.mouse_appear_names = ["1st hit", "2nd hit", "3rd hit", "5th hit"]
        self.mouse_appear_idx = 1
        self.mouse_appear_rect = pygame.Rect(0,0,180,40)
        
        self.p1_zone_type = 0
        self.p2_zone_type = 0

    def _update_portal_rects(self):
        size = self.portal_size_options[self.portal_size_idx]
        thick = PADDLE_WIDTH
        
        # Posiciones base
        if self.portals_vertical:
            # Postes
            self.portal_blue_rect = pygame.Rect(200, 0, thick, size)
            self.portal_orange_rect = pygame.Rect(SCREEN_WIDTH - 200 - thick, SCREEN_HEIGHT - size, thick, size)
            if self.more_portals_enabled:
                self.portal_red_rect = pygame.Rect(200, SCREEN_HEIGHT - size, thick, size)
                self.portal_green_rect = pygame.Rect(SCREEN_WIDTH - 200 - thick, 0, thick, size)
        else:
            # Acostados
            self.portal_blue_rect = pygame.Rect(150, 0, size, thick)
            self.portal_orange_rect = pygame.Rect(SCREEN_WIDTH - 150 - size, SCREEN_HEIGHT - thick, size, thick)
            if self.more_portals_enabled:
                self.portal_red_rect = pygame.Rect(150, SCREEN_HEIGHT - thick, size, thick)
                self.portal_green_rect = pygame.Rect(SCREEN_WIDTH - 150 - size, 0, size, thick)

        # Botones de Game Over
        self.btn_gameover_restart = pygame.Rect(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 20, 300, 60)
        self.btn_gameover_menu = pygame.Rect(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 100, 300, 60)
        self.golden_goal_active = False


    def reset_game(self):
        self.score1 = 0
        self.score2 = 0
        self.global_hits = 0
        self.hourglass_rect = None
        self.hourglass_type = 0
        self.zone_type = 0
        self.slow_zone_owner = 0
        self.last_hitter = 0
        self.ball_is_x2 = False
        self.is_x2_item_active = False
        self.pending_x2_spawn = False
        
        self.paddle1.reset()
        self.paddle2.reset()
        self.paddle1.y_float = float(self.paddle1.rect.y)
        self.paddle2.y_float = float(self.paddle2.rect.y)
        self.is_golden_goal_round = False
        self.show_golden_goal_anim = False
        self.golden_goal_active = False # Limpieza por si acaso
        self.golden_goal_active = False

        if self.start_with_power_enabled:
            self.paddle1.grant_random_power(self)
            self.paddle2.grant_random_power(self)
        
        # Resetear RATÓN
        self.mouse = None
        self.mouse_hits_counter = 0
        
        self.state = STATE_SERVE
        self.serve_timer = 2.0
        self.serve_direction = random.choice([1, -1])
        self.balls = [Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        self.balls[0].serve(self.serve_direction, 300 * self.initial_ball_speed_options[self.initial_ball_speed_idx])
        
        # Tirada inicial para reglas especiales
        if self.experimental_golden_goal and random.random() < 0.10: 
            self.is_golden_goal_round = True
            self.pending_x2_spawn = False
        elif self.start_x2_enabled and random.random() < 0.50: 
            self.pending_x2_spawn = True
            self.is_golden_goal_round = False
            
        self._check_for_announcements()

    def handle_input(self, dt):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_mouse_click(event)
            
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.is_dragging_scrollbar = False
                    self.is_dragging_volume = False
                    
            if event.type == pygame.MOUSEMOTION:
                self._handle_mouse_motion(event)
            
            if event.type == pygame.KEYDOWN:
                self._handle_keydown(event)
                
            if event.type == pygame.MOUSEWHEEL:
                if self.state == STATE_MODIFIERS:
                    self.scroll_y = max(0, min(self.scroll_y - event.y * 30, self.max_scroll))

        self._handle_continuous_input(dt)

    def _handle_mouse_click(self, event):
        if event.button != 1: return
        
        if self.state == STATE_MAIN_MENU:
            if self.btn_play_rect.collidepoint(event.pos):
                self.audio.play('hit')
                self.state = STATE_MODE_SELECTION
            elif self.btn_modifiers_rect.collidepoint(event.pos):
                self.audio.play('hit')
                self.state = STATE_MODIFIERS
            elif self.btn_settings_rect.collidepoint(event.pos):
                self.audio.play('hit')
                self.state = STATE_SETTINGS
                # Crear backup para poder cancelar cambios con BACK
                self.settings_backup = {
                    "lang": self.language,
                    "vfx": self.vfx_enabled,
                    "vol": self.sfx_volume,
                    "shake": self.shake_enabled
                }
        
        elif self.state == STATE_MODIFIERS:
            if self.scrollbar_thumb_rect.collidepoint(event.pos):
                self.is_dragging_scrollbar = True
                self.scroll_offset_y = event.pos[1] - self.scrollbar_thumb_rect.y
            elif self.back_btn_rect.collidepoint(event.pos):
                self.audio.play('hit'); self.state = STATE_MAIN_MENU; self.scroll_y = 0
                self.mouse = None # Limpiar ratón al salir
                self.scrollbar_thumb_rect.y = self.scrollbar_rect.y
                self.remove_watches_expanded = False
            
            # Pestañas
            elif self.tab_all_rect.collidepoint(event.pos):
                if self.modifiers_tab != "ALL": self.audio.play('hit'); self.modifiers_tab = "ALL"; self.scroll_y = 0
            elif self.tab_extras_rect.collidepoint(event.pos):
                if self.modifiers_tab != "EXTRAS": self.audio.play('hit'); self.modifiers_tab = "EXTRAS"; self.scroll_y = 0
            elif self.tab_skins_rect.collidepoint(event.pos):
                if self.modifiers_tab != "SKINS": self.audio.play('hit'); self.modifiers_tab = "SKINS"; self.scroll_y = 0
            
            # Contenido del panel
            elif self.modifiers_panel_rect.collidepoint(event.pos):
                if self.modifiers_tab == "ALL":
                    if event.pos[1] > self.modifiers_panel_rect.top + 60:
                        self._handle_modifier_clicks(event)
                        # Recalcular max_scroll tras abrir/cerrar acordeones
                        self.max_scroll = max(0, self.max_y_rendered + 60 - 330)
                        self.scroll_y = min(self.scroll_y, self.max_scroll)
                else:
                    # Tanto SKINS como EXTRAS usan este método para sus clics
                    self._handle_modifier_clicks(event)

        elif self.state == STATE_MODE_SELECTION:
            if self.btn_multi_rect.collidepoint(event.pos):
                self.audio.play('hit')
                self.is_ai_mode = False
                self.state = STATE_PRESS_TO_START
            elif self.btn_solo_rect.collidepoint(event.pos):
                self.audio.play('hit')
                self.is_ai_mode = True
                self.state = STATE_PRESS_TO_START
            elif self.back_btn_rect.collidepoint(event.pos):
                self.audio.play('hit')
                self.state = STATE_MAIN_MENU
        
        elif self.state == STATE_SETTINGS:
            if self.settings_back_btn_rect.collidepoint(event.pos):
                self.audio.play('hit')
                # Restaurar backup (Descartar cambios)
                self.language = self.settings_backup["lang"]
                self.vfx_enabled = self.settings_backup["vfx"]
                self.sfx_volume = self.settings_backup["vol"]
                self.audio.master_volume = self.sfx_volume
                self.shake_enabled = self.settings_backup["shake"]
                self.state = STATE_MAIN_MENU
            elif self.lang_rect.collidepoint(event.pos):
                self.audio.play('hit'); self.language = "EN" if self.language == "ES" else "ES"
            elif self.vfx_rect.collidepoint(event.pos):
                self.audio.play('hit'); self.vfx_enabled = not self.vfx_enabled
            elif self.volume_bar_rect.collidepoint(event.pos) or self.volume_handle_rect.collidepoint(event.pos):
                self.is_dragging_volume = True
                # Actualizar posición inmediata
                rel_x = max(0, min(event.pos[0] - self.volume_bar_rect.x, self.volume_bar_rect.width))
                self.sfx_volume = rel_x / self.volume_bar_rect.width
                self.audio.master_volume = self.sfx_volume
            elif self.shake_rect.collidepoint(event.pos):
                self.audio.play('hit'); self.shake_enabled = not self.shake_enabled
            elif self.settings_apply_btn_rect.collidepoint(event.pos):
                self.audio.play('hit'); self.state = STATE_MAIN_MENU

        elif self.state == STATE_GAME_OVER:
            if self.btn_gameover_restart.collidepoint(event.pos):
                self.audio.play('hit'); self.reset_game()
            elif self.btn_gameover_menu.collidepoint(event.pos):
                self.audio.play('hit'); self.reset_game(); self.state = STATE_MAIN_MENU

    def _handle_modifier_clicks(self, event):
        if self.modifiers_tab == "SKINS":
            if self.orange_skin_rect.collidepoint(event.pos):
                self.audio.play('hit'); self.orange_skin_idx = (self.orange_skin_idx + 1) % len(self.orange_skin_options)
            elif self.yellow_watch_skin_rect.collidepoint(event.pos):
                self.audio.play('hit'); self.yellow_watch_skin_idx = (self.yellow_watch_skin_idx + 1) % len(self.yellow_watch_skin_options)
            elif self.ball_skin_rect.collidepoint(event.pos):
                self.audio.play('hit'); self.ball_skin_idx = (self.ball_skin_idx + 1) % len(self.ball_skin_options)
        
        elif self.modifiers_tab == "ALL":
            if self.score_btn_rect.collidepoint(event.pos):
                self.audio.play('hit')
                self.max_score = 6 if self.max_score == 3 else (9 if self.max_score == 6 else 3)
            elif self.ball_speed_btn_rect.collidepoint(event.pos):
                self.audio.play('pop'); self.ball_speed_multiplier_idx = (self.ball_speed_multiplier_idx + 1) % len(self.ball_speed_multiplier_options)
            elif self.initial_ball_speed_rect.collidepoint(event.pos):
                self.audio.play('pop'); self.initial_ball_speed_idx = (self.initial_ball_speed_idx + 1) % len(self.initial_ball_speed_options)
            elif self.yellow_speed_up_rect.collidepoint(event.pos):
                self.audio.play('pop'); self.yellow_speed_up_idx = (self.yellow_speed_up_idx + 1) % len(self.yellow_speed_up_options)
            elif self.encapsulate_powers_rect.collidepoint(event.pos) or self.encapsulate_powers_text_rect.collidepoint(event.pos):
                self.audio.play('pop'); self.encapsulate_powers_enabled = not self.encapsulate_powers_enabled
            elif self.match_point_rect.collidepoint(event.pos) or self.match_point_text_rect.collidepoint(event.pos):
                self.audio.play('pop'); self.match_point_enabled = not self.match_point_enabled
            elif self.golden_goal_anim_rect.collidepoint(event.pos) or self.golden_goal_anim_text_rect.collidepoint(event.pos):
                self.audio.play('pop'); self.golden_goal_anim_enabled = not self.golden_goal_anim_enabled
            elif self.reroll_rect.collidepoint(event.pos) or self.reroll_text_rect.collidepoint(event.pos):
                self.audio.play('pop'); self.reroll_enabled = not self.reroll_enabled
            elif self.reroll_enabled and (self.all_reroll_rect.collidepoint(event.pos) or self.all_reroll_text_rect.collidepoint(event.pos)):
                self.audio.play('pop'); self.all_reroll_enabled = not self.all_reroll_enabled
            elif self.equal_watches_rect.collidepoint(event.pos) or self.equal_watches_text_rect.collidepoint(event.pos):
                self.audio.play('pop'); self.equal_watches_enabled = not self.equal_watches_enabled
            elif self.equal_powers_rect.collidepoint(event.pos) or self.equal_powers_text_rect.collidepoint(event.pos):
                self.audio.play('pop'); self.equal_powers_enabled = not self.equal_powers_enabled
            elif self.watches_kept_rect.collidepoint(event.pos) or self.watches_kept_text_rect.collidepoint(event.pos):
                self.audio.play('pop'); self.watches_kept_enabled = not self.watches_kept_enabled
            elif self.watch_spawn_hits_rect.collidepoint(event.pos) or self.watch_spawn_hits_text_rect.collidepoint(event.pos):
                self.audio.play('pop'); self.watch_spawn_hits_idx = (self.watch_spawn_hits_idx + 1) % len(self.watch_spawn_hits_options)
            elif self.power_auto_grant_hits_rect.collidepoint(event.pos) or self.power_auto_grant_hits_text_rect.collidepoint(event.pos):
                self.audio.play('pop'); self.power_auto_grant_hits_idx = (self.power_auto_grant_hits_idx + 1) % len(self.power_auto_grant_hits_options)
            elif self.start_with_power_rect.collidepoint(event.pos) or self.start_with_power_text_rect.collidepoint(event.pos):
                self.audio.play('pop'); self.start_with_power_enabled = not self.start_with_power_enabled
            
            # Acordeones en ALL
            elif self.remove_watches_toggle_rect.collidepoint(event.pos) or self.remove_watches_toggle_text_rect.collidepoint(event.pos):
                self.audio.play('pop'); self.remove_watches_expanded = not self.remove_watches_expanded
            elif self.remove_power_toggle_rect.collidepoint(event.pos) or self.remove_power_toggle_text_rect.collidepoint(event.pos):
                self.audio.play('pop'); self.remove_power_expanded = not self.remove_power_expanded
            
            if self.remove_watches_expanded:
                if self.remove_blue_rect.collidepoint(event.pos) or self.remove_blue_text_rect.collidepoint(event.pos): self.audio.play('pop'); self.remove_blue = not self.remove_blue
                elif self.remove_red_rect.collidepoint(event.pos) or self.remove_red_text_rect.collidepoint(event.pos): self.audio.play('pop'); self.remove_red = not self.remove_red
                elif self.remove_purple_rect.collidepoint(event.pos) or self.remove_purple_text_rect.collidepoint(event.pos): self.audio.play('pop'); self.remove_purple = not self.remove_purple
                elif self.remove_white_rect.collidepoint(event.pos) or self.remove_white_text_rect.collidepoint(event.pos): self.audio.play('pop'); self.remove_white = not self.remove_white
                elif self.remove_yellow_rect.collidepoint(event.pos) or self.remove_yellow_text_rect.collidepoint(event.pos): self.audio.play('pop'); self.remove_yellow = not self.remove_yellow
            
            if self.remove_power_expanded:
                if self.remove_power_red_rect.collidepoint(event.pos) or self.remove_power_red_text_rect.collidepoint(event.pos): self.audio.play('pop'); self.remove_power_red = not self.remove_power_red
                elif self.remove_power_green_rect.collidepoint(event.pos) or self.remove_power_green_text_rect.collidepoint(event.pos): self.audio.play('pop'); self.remove_power_green = not self.remove_power_green
                elif self.remove_power_yellow_rect.collidepoint(event.pos) or self.remove_power_yellow_text_rect.collidepoint(event.pos): self.audio.play('pop'); self.remove_power_yellow = not self.remove_power_yellow
                elif self.remove_power_orange_rect.collidepoint(event.pos) or self.remove_power_orange_text_rect.collidepoint(event.pos): self.audio.play('pop'); self.remove_power_orange = not self.remove_power_orange

        elif self.modifiers_tab == "EXTRAS":
            self._handle_experimental_clicks(event)

    def _handle_experimental_clicks(self, event):
        if self.orange_watch_rect.collidepoint(event.pos) or self.orange_watch_text_rect.collidepoint(event.pos): self.audio.play('pop'); self.orange_watch_enabled = not self.orange_watch_enabled
        elif self.magnet_power_rect.collidepoint(event.pos) or self.magnet_power_text_rect.collidepoint(event.pos): self.audio.play('pop'); self.magnet_power_enabled = not self.magnet_power_enabled
        elif self.experimental_golden_goal_rect.collidepoint(event.pos) or self.experimental_golden_goal_text_rect.collidepoint(event.pos): self.audio.play('pop'); self.experimental_golden_goal = not self.experimental_golden_goal
        elif self.floating_planets_rect.collidepoint(event.pos) or self.floating_planets_text_rect.collidepoint(event.pos): self.audio.play('pop'); self.floating_planets_enabled = not self.floating_planets_enabled
        elif self.start_x2_rect.collidepoint(event.pos) or self.start_x2_text_rect.collidepoint(event.pos): self.audio.play('pop'); self.start_x2_enabled = not self.start_x2_enabled
        elif self.ghost_power_rect.collidepoint(event.pos) or self.ghost_power_text_rect.collidepoint(event.pos): self.audio.play('pop'); self.ghost_power_enabled = not self.ghost_power_enabled
        elif self.ghost_power_enabled and (self.ghost_identical_rect.collidepoint(event.pos) or self.ghost_identical_text_rect.collidepoint(event.pos)): self.audio.play('pop'); self.ghost_identical_enabled = not self.ghost_identical_enabled
        elif self.gum_power_rect.collidepoint(event.pos) or self.gum_power_text_rect.collidepoint(event.pos): self.audio.play('pop'); self.gum_power_enabled = not self.gum_power_enabled
        elif self.portals_rect.collidepoint(event.pos) or self.portals_text_rect.collidepoint(event.pos): self.audio.play('pop'); self.portals_enabled = not self.portals_enabled
        elif self.portals_enabled and self.portal_size_rect.collidepoint(event.pos):
            self.audio.play('pop'); self.portal_size_idx = (self.portal_size_idx + 1) % len(self.portal_size_options)
            self._update_portal_rects()
        elif self.portals_enabled and (self.portals_vertical_rect.collidepoint(event.pos) or self.portals_vertical_text_rect.collidepoint(event.pos)):
            self.audio.play('pop'); self.portals_vertical = not self.portals_vertical
            self._update_portal_rects()
        elif self.portals_enabled and (self.more_portals_rect.collidepoint(event.pos) or self.more_portals_text_rect.collidepoint(event.pos)):
            self.audio.play('pop'); self.more_portals_enabled = not self.more_portals_enabled
            self._update_portal_rects()
        elif self.add_mouse_rect.collidepoint(event.pos) or self.add_mouse_text_rect.collidepoint(event.pos): 
            self.audio.play('pop'); self.add_mouse_enabled = not self.add_mouse_enabled
        elif self.revolver_rect.collidepoint(event.pos) or self.revolver_text_rect.collidepoint(event.pos):
            self.audio.play('pop'); self.revolver_enabled = not self.revolver_enabled
        
        if self.add_mouse_enabled:
            if self.mouse_speed_rect.collidepoint(event.pos):
                self.audio.play('pop'); self.mouse_speed_idx = (self.mouse_speed_idx + 1) % len(self.mouse_speed_options)
            elif self.mouse_appear_rect.collidepoint(event.pos):
                self.audio.play('pop'); self.mouse_appear_idx = (self.mouse_appear_idx + 1) % len(self.mouse_appear_options)
        
        if self.floating_planets_enabled:
            if self.gravity_force_rect.collidepoint(event.pos): self.audio.play('pop'); self.gravity_force_idx = (self.gravity_force_idx + 1) % len(self.gravity_force_options)
            elif self.gravity_radius_rect.collidepoint(event.pos): self.audio.play('pop'); self.gravity_radius_idx = (self.gravity_radius_idx + 1) % len(self.gravity_radius_options)
            elif self.destructible_planets_rect.collidepoint(event.pos) or self.destructible_planets_text_rect.collidepoint(event.pos): self.audio.play('pop'); self.destructible_planets_enabled = not self.destructible_planets_enabled
            elif self.destructible_planets_enabled and self.planet_resistance_rect.collidepoint(event.pos): self.audio.play('pop'); self.planet_resistance_idx = (self.planet_resistance_idx + 1) % len(self.planet_resistance_options)

    def _handle_mouse_motion(self, event):
        mpos = event.pos
        current_hover = None
        
        # 1. Detectar sobre qué botón estamos según el estado
        if self.state == STATE_MAIN_MENU:
            for r in [self.btn_play_rect, self.btn_modifiers_rect, self.btn_settings_rect]:
                if r.collidepoint(mpos): current_hover = r
        elif self.state == STATE_MODIFIERS:
            if self.back_btn_rect.collidepoint(mpos): current_hover = self.back_btn_rect
        elif self.state == STATE_SETTINGS:
            # Solo detectamos hover para el botón de volver en settings si queremos, 
            # pero el usuario pidió silenciar los botones DENTRO de settings.
            pass
                
        # 2. Si entramos en un botón nuevo, sonar 'pop'
        if current_hover and current_hover != self.last_hovered_rect:
            self.audio.play('pop')
        
        self.last_hovered_rect = current_hover

        # Scroll original
        if self.state == STATE_MODIFIERS and self.is_dragging_scrollbar:
            new_y = event.pos[1] - self.scroll_offset_y
            limit_bottom = self.scrollbar_rect.bottom - self.scrollbar_thumb_height
            self.scrollbar_thumb_rect.y = max(self.scrollbar_rect.top, min(new_y, limit_bottom))
            
            scroll_fraction = (self.scrollbar_thumb_rect.y - self.scrollbar_rect.top) / (self.scrollbar_rect.height - self.scrollbar_thumb_height)
            self.scroll_y = scroll_fraction * self.max_scroll
            
        # Arrastre de Volumen
        if self.state == STATE_SETTINGS and self.is_dragging_volume:
            rel_x = max(0, min(event.pos[0] - self.volume_bar_rect.x, self.volume_bar_rect.width))
            new_vol = rel_x / self.volume_bar_rect.width
            if int(new_vol * 100) != int(self.sfx_volume * 100):
                self.sfx_volume = new_vol
                self.audio.master_volume = self.sfx_volume
                # Sonar un pequeño pop de prueba para que se note el cambio
                if random.random() < 0.1: # No saturar, solo de vez en cuando
                    self.audio.play('pop')

    def _handle_keydown(self, event):
        if self.state == STATE_PRESS_TO_START and event.key == pygame.K_SPACE:
            self.audio.play('hit')
            self.reset_game()
        elif self.state == STATE_PLAYING:
            if event.key == pygame.K_d: self.activate_paddle_power(self.paddle1, 1)
            if event.key == pygame.K_RIGHT: self.activate_paddle_power(self.paddle2, 2)

    def _handle_continuous_input(self, dt):
        keys = pygame.key.get_pressed()
        if self.state in [STATE_PLAYING, STATE_SERVE]:
            p_speed = 400 # PADDLE_SPEED
            if keys[pygame.K_w]: self.paddle1.move(-1, dt, p_speed)
            if keys[pygame.K_s]: self.paddle1.move(1, dt, p_speed)
            if keys[pygame.K_UP]: self.paddle2.move(-1, dt, p_speed)
            if keys[pygame.K_DOWN]: self.paddle2.move(1, dt, p_speed)

    def check_ball_collisions(self, ball):
        is_main = (ball == self.balls[0])
        # 1. Planetas
        if self.floating_planets_enabled:
            self._check_planet_collisions(ball)
            
        # 2. Paredes
        if ball.rect.top <= 0:
            ball.rect.top = 0; ball.y_float = float(ball.rect.y); ball.vy = abs(ball.vy)
            if self.wall_sound_cooldown <= 0: self.audio.play('hit'); self.wall_sound_cooldown = 0.25
        elif ball.rect.bottom >= SCREEN_HEIGHT:
            ball.rect.bottom = SCREEN_HEIGHT; ball.y_float = float(ball.rect.y); ball.vy = -abs(ball.vy)
            if self.wall_sound_cooldown <= 0: self.audio.play('hit'); self.wall_sound_cooldown = 0.25

        # 3. Multiplicador X2 (Solo principal)
        if is_main and self.is_x2_item_active and ball.rect.colliderect(self.x2_item_rect):
            self.is_x2_item_active = False; self.ball_is_x2 = True; ball.color = GOLD; self.audio.play('x2')
            self.vfx.burst(self.x2_item_rect.centerx, self.x2_item_rect.centery, GOLD)

        # 4. Relojes (Solo principal)
        if is_main and self.hourglass_rect and ball.rect.colliderect(self.hourglass_rect):
            self._handle_watch_capture()

        # 5. Goles
        if ball.rect.right < 0:
            if ball.is_bullet:
                if ball in self.balls: self.balls.remove(ball)
            elif ball.is_ghost:
                if ball.ghost_owner == 2: self.goal_scored(2)
                if ball in self.balls: self.balls.remove(ball)
            elif ball.is_orange: self._handle_orange_bounce(True, ball)
            elif self.paddle1.has_extra_life: self._handle_extra_life_save(True, ball)
            else: self.goal_scored(2)
        elif ball.rect.left > SCREEN_WIDTH:
            if ball.is_bullet:
                if ball in self.balls: self.balls.remove(ball)
            elif ball.is_ghost:
                if ball.ghost_owner == 1: self.goal_scored(1)
                if ball in self.balls: self.balls.remove(ball)
            elif ball.is_orange: self._handle_orange_bounce(False, ball)
            elif self.paddle2.has_extra_life: self._handle_extra_life_save(False, ball)
            else: self.goal_scored(1)

        # 6. Paletas
        if ball.is_bullet and ball.bullet_immunity <= 0:
            if ball.rect.colliderect(self.paddle1.rect):
                self.handle_paddle_collision(self.paddle1, 1, ball)
                return
            if ball.rect.colliderect(self.paddle2.rect):
                self.handle_paddle_collision(self.paddle2, -1, ball)
                return

        if ball.vx < 0 and ball.rect.colliderect(self.paddle1.rect):
            if ball.is_ghost:
                if ball.ghost_owner == 2: # Atrapado por el rival
                    self.audio.play('hit'); self.balls.remove(ball)
            else: self.handle_paddle_collision(self.paddle1, 1, ball)
        elif ball.vx > 0 and ball.rect.colliderect(self.paddle2.rect):
            if ball.is_ghost:
                if ball.ghost_owner == 1: # Atrapado por el rival
                    self.audio.play('hit'); self.balls.remove(ball)
            else: self.handle_paddle_collision(self.paddle2, -1, ball)

    def _check_planet_collisions(self, ball):
        for p_idx, planet_pos in enumerate([self.planet1_pos, self.planet2_pos]):
            is_alive = self.planet1_alive if p_idx == 0 else self.planet2_alive
            if not is_alive: continue
            dx, dy = ball.rect.centerx - planet_pos[0], ball.rect.centery - planet_pos[1]
            dist = math.sqrt(dx**2 + dy**2)
            if dist < self.planet_radius + ball.rect.width / 2:
                nx, ny = dx/dist, dy/dist
                dot = ball.vx * nx + ball.vy * ny
                ball.vx -= 2 * dot * nx; ball.vy -= 2 * dot * ny
                overlap = (self.planet_radius + ball.rect.width / 2) - dist
                ball.rect.centerx += nx * (overlap + 2); ball.rect.centery += ny * (overlap + 2)
                ball.x_float = float(ball.rect.x); self.audio.play('pop')
                if self.destructible_planets_enabled:
                    self._handle_planet_damage(p_idx, planet_pos)

    def _handle_planet_damage(self, p_idx, planet_pos):
        if p_idx == 0: self.planet1_hits += 1
        else: self.planet2_hits += 1
        hits = self.planet1_hits if p_idx == 0 else self.planet2_hits
        max_hits = self.planet_resistance_options[self.planet_resistance_idx]
        if hits >= max_hits:
            if p_idx == 0: self.planet1_alive = False
            else: self.planet2_alive = False
            self.audio.play('explosion')
            # Color de explosión según el tipo de planeta
            p_name = self.gravity_force_names[self.gravity_force_idx]
            exp_color = CYAN
            if p_name == "Moon": exp_color = (180, 180, 180)
            elif p_name == "Planet":
                # Diferenciar Tierra (arriba) de Marte (abajo)
                exp_color = (50, 100, 255) if p_idx == 0 else (220, 80, 50)
            elif p_name == "Gas Giant":
                # Diferenciar Júpiter (arriba) de Saturno (abajo)
                exp_color = (230, 180, 140) if p_idx == 0 else (255, 220, 150)
            elif p_name == "Star": exp_color = YELLOW
            
            self.vfx.explosion(planet_pos[0], planet_pos[1], exp_color)
            self.trigger_shake(12, 0.5) # Sacudida fuerte

    def t(self, en, es):
        return en if self.language == "EN" else es

    def _handle_watch_capture(self):
        sounds = {1: 'item_get', 2: 'error', 3: 'bell', 4: 'divine', 5: 'life'}
        if self.hourglass_type in sounds: self.audio.play(sounds[self.hourglass_type])
        
        self.is_x2_item_active = False
        if self.hourglass_type == 5:
            if self.last_hitter == 1: self.paddle1.has_extra_life = True
            elif self.last_hitter == 2: self.paddle2.has_extra_life = True
        elif self.hourglass_type == 6:
            if self.orange_skin_idx == 1: self.audio.play('hadouken')
            else: self.audio.play('uuui')
            self.balls[0].is_orange = True; self.balls[0].color = ORANGE; self.balls[0].rect.width = self.balls[0].rect.height = BALL_SIZE * 2; self.balls[0].speed *= 1.5
        else:
            h_type = self.hourglass_type
            if self.watches_kept_enabled:
                if self.last_hitter == 1: self.p1_zone_type = h_type
                else: self.p2_zone_type = h_type
            else:
                self.zone_type = h_type; self.slow_zone_owner = self.last_hitter
            if h_type == 3:
                if self.last_hitter == 1: self.paddle1.hits = 0
                else: self.paddle2.hits = 0
            if h_type == 4:
                p = self.paddle1 if self.last_hitter == 1 else self.paddle2
                p.reset(); p.white_activation_timer = 0.05
        
        self.hourglass_rect = None; self.global_hits = 0

    def _handle_orange_bounce(self, is_left, ball):
        ball.rect.width = ball.rect.height = BALL_SIZE
        if is_left: ball.rect.left = 0
        else: ball.rect.right = SCREEN_WIDTH
        ball.vx *= -1; ball.speed /= 1.5; ball.is_orange = False; ball.color = WHITE; self.audio.play('hit')
        ball.x_float = float(ball.rect.x)

    def _handle_extra_life_save(self, is_left, ball):
        p = self.paddle1 if is_left else self.paddle2
        if is_left: ball.rect.left = 0
        else: ball.rect.right = SCREEN_WIDTH
        ball.vx *= -1; p.has_extra_life = False; self.audio.play('hit')
        ball.x_float = float(ball.rect.x)

    def handle_paddle_collision(self, paddle, direction_x, ball):
        if ball.is_bullet:
            self.audio.play('explosion')
            self.vfx.burst(paddle.rect.centerx, paddle.rect.centery, YELLOW)
            self.trigger_shake(12, 0.5)
            # Destruir paleta visualmente como el poder naranja
            if self.orange_skin_idx == 1:
                paddle.is_destroyed = True
                self.vfx.explosion(paddle.rect.centerx, paddle.rect.centery, BROWN)
            
            # Quitar bala y dar punto
            if ball in self.balls: self.balls.remove(ball)
            self.goal_scored(2 if paddle == self.paddle1 else 1)
            return

        if ball.is_orange:
            # Si tiene escudo, el escudo protege de la naranja
            if paddle.power_active == POWER_SHIELD:
                ball.reset_orange(BALL_SIZE)
                self.audio.play('hit')
                paddle.shield_hits_left -= 1
                if paddle.shield_hits_left <= 0: paddle.shield_shrink_timer = 0.1
                # Rebote normal tras perder el "fuego" naranja
                self._calculate_bounce_physics(paddle, direction_x, ball)
                return
                
            ball.reset_orange(BALL_SIZE); self.audio.play('pop')
            if self.orange_skin_idx == 1:
                paddle.is_destroyed = True
                self.vfx.explosion(paddle.rect.centerx, paddle.rect.centery, BROWN)
                self.trigger_shake(15, 0.6) # Gran impacto
            self.goal_scored(2 if paddle == self.paddle1 else 1); return
            
        self.audio.play('pop'); self.last_hitter = 1 if paddle == self.paddle1 else 2
        self.mouse_hits_counter += 1
        if ball.is_fireball:
            ball.is_fireball = False; self.reset_ball_visuals(ball); ball.speed /= 2; self.audio.fadeout('fire', 500)

        ball.speed *= self.ball_speed_multiplier_options[self.ball_speed_multiplier_idx]
        
        if not (paddle.power_active == POWER_SHIELD or paddle.white_zone_hits_left > 0):
            paddle.hits += 1
            if self.reroll_enabled:
                if paddle.power_stored == POWER_SPEED:
                    paddle.yellow_power_hits += 1
                    if paddle.yellow_power_hits >= 2: paddle.grant_random_power(self); paddle.yellow_power_hits = 0
                elif paddle.power_stored == POWER_ORANGE:
                    paddle.orange_power_hits += 1
                    if paddle.orange_power_hits >= 2: paddle.grant_random_power(self); paddle.orange_power_hits = 0

            req = self.power_auto_grant_hits_options[self.power_auto_grant_hits_idx]
            if paddle.hits >= req: paddle.grant_random_power(self); paddle.hits = 0

        self._process_active_powers(paddle, ball)
        self._calculate_bounce_physics(paddle, direction_x, ball)
        self._check_watch_spawn()

    def _process_active_powers(self, paddle, ball):
        if paddle.power_active == POWER_FIREBALL:
            paddle.power_active = POWER_NONE; paddle.color = WHITE; ball.is_fireball = True; ball.color = RED; ball.speed *= 2; self.audio.play('fire', loops=-1)
        elif paddle.power_active == POWER_ORANGE:
            paddle.power_active = POWER_NONE; paddle.color = WHITE; ball.is_orange = True
            if self.orange_skin_idx == 1: self.audio.play('hadouken')
            else: self.audio.play('uuui')
            ball.color = ORANGE if self.orange_skin_idx == 0 else (0, 150, 255)
            ball.rect.width = ball.rect.height = BALL_SIZE * 2; ball.speed *= 1.5
        elif paddle.power_active == POWER_SHIELD:
            paddle.shield_hits_left -= 1
            if paddle.shield_hits_left <= 0: paddle.shield_shrink_timer = 0.1
        elif paddle.power_active == POWER_MAGNET:
            paddle.magnet_hits_left -= 1
            if paddle.magnet_hits_left <= 0: paddle.power_active = POWER_NONE; paddle.color = WHITE
        elif paddle.power_active == POWER_GUM and paddle.gum_charges > 0:
            paddle.is_stuck = True
            paddle.stuck_ball = ball
            self.audio.play('nom') # Sonido de "atrapado"
            return # No calcular rebote si está pegado
        
        # Zona Blanca (Defensiva) - Decrementar golpes
        if paddle.white_zone_hits_left > 0:
            paddle.white_zone_hits_left -= 1
            if paddle.white_zone_hits_left <= 0:
                paddle.white_zone_shrink_timer = 0.005 # ~1 frame de cooldown
                # Limpiar zona en el engine de inmediato pero dejar que la paleta se encoja sola
                if paddle == self.paddle1: self.p1_zone_type = 0
                else: self.p2_zone_type = 0
                if paddle == self.paddle1: self.p1_zone_type = 0
                else: self.p2_zone_type = 0
                if self.slow_zone_owner == (1 if paddle == self.paddle1 else 2) and self.zone_type == 4:
                    self.zone_type = 0; self.slow_zone_owner = 0

    def _calculate_bounce_physics(self, paddle, direction_x, ball):
        rel_y = (paddle.rect.y + (paddle.rect.height / 2)) - ball.rect.centery
        norm_y = rel_y / (paddle.rect.height / 2)
        # MAX_BOUNCE_ANGLE se usa como constante o valor fijo
        angle = norm_y * math.radians(60) * -1
        ball.vx = ball.speed * math.cos(angle) * direction_x
        ball.vy = ball.speed * math.sin(angle)
        if direction_x == 1: ball.rect.left = paddle.rect.right
        else: ball.rect.right = paddle.rect.left
        ball.x_float = float(ball.rect.x)

    def _check_watch_spawn(self):
        if not (self.zone_type == 4 or self.p1_zone_type == 4 or self.p2_zone_type == 4):
            self.global_hits += 1
            if self.pending_x2_spawn: self.is_x2_item_active = True; self.pending_x2_spawn = False
            if self.global_hits >= self.watch_spawn_hits_options[self.watch_spawn_hits_idx]:
                self.global_hits = 0
                self.spawn_random_watch()
                # 25% de chance de Revólver al salir un reloj
                if self.revolver_enabled and not self.revolver_item_active and random.random() < 0.25:
                    self.revolver_item_active = True
                    self.revolver_angle = 0.0

    def reset_ball_visuals(self, ball):
        if ball.is_ghost: ball.color = GHOST_COLOR
        else: ball.color = GOLD if self.ball_is_x2 and ball == self.balls[0] else WHITE

    def spawn_random_watch(self):
        avail = []
        if not self.remove_blue: avail.append((1, 25))
        if not self.remove_red: avail.append((2, 20))
        if not self.remove_purple: avail.append((3, 20))
        if not self.remove_white: avail.append((4, 10))
        if not self.remove_yellow: avail.append((5, 25))
        if self.orange_watch_enabled: avail.append((6, 20))
        if not avail: avail.append((1, 100))
        
        self.hourglass_rect = pygame.Rect(SCREEN_WIDTH//2 - 15, SCREEN_HEIGHT//2 - 20, 30, 40)
        self.is_x2_item_active = False
        if self.equal_watches_enabled: self.hourglass_type = random.choice([w[0] for w in avail])
        else:
            total = sum(w[1] for w in avail)
            r, acc = random.random() * total, 0
            for w, weight in avail:
                acc += weight
                if r <= acc: self.hourglass_type = w; break
    def activate_paddle_power(self, paddle, owner):
        # Si el poder es REVOLVER y no está activo, activarlo
        if paddle.power_stored == POWER_REVOLVER:
            self.audio.play('item_get')
            paddle.power_active = POWER_REVOLVER
            paddle.revolver_shots_left = 3
            paddle.revolver_timer = 10.0
            paddle.power_stored = POWER_NONE
            return

        # Si el poder REVOLVER ya está activo y se vuelve a presionar:
        if paddle.power_active == POWER_REVOLVER and paddle.revolver_shots_left > 0:
            self.audio.play('pium') 
            paddle.revolver_shots_left -= 1
            # Salir del CENTRO de la paleta
            bullet = Ball(paddle.rect.centerx, paddle.rect.centery)
            bullet.is_bullet = True
            bullet.is_kill_ball = True
            bullet.color = YELLOW
            bullet.bullet_immunity = 0.1 # Seguro de 100ms
            # Velocidad 2x, trayectoria RECTA (vy = 0)
            speed = 300 * self.initial_ball_speed_options[self.initial_ball_speed_idx] * 2.0
            bullet.vx = speed * (1 if owner == 1 else -1)
            bullet.vy = 0
            bullet.x_float = float(bullet.rect.x)
            bullet.y_float = float(bullet.rect.y)
            self.balls.append(bullet)
            return

        # Si el poder es GUM y no está activo, activarlo (3 cargas)
        if paddle.power_stored == POWER_GUM:
            self.audio.play('item_get')
            paddle.power_active = POWER_GUM
            paddle.gum_charges = 3
            paddle.power_stored = POWER_NONE
            paddle.color = GUM_PINK
            return

        # Si el poder GUM ya está activo y se vuelve a presionar:
        if paddle.power_active == POWER_GUM:
            if paddle.is_stuck:
                # Soltar pelota
                paddle.is_stuck = False
                # Impulso al soltarse
                paddle.stuck_ball.vx = 500 if paddle.rect.x < SCREEN_WIDTH // 2 else -500
                paddle.stuck_ball.vy = random.uniform(-100, 100)
                paddle.stuck_ball = None
                # No consume carga extra por soltar manualmente (ya consumió tiempo pegada)
            elif paddle.gum_charges > 0:
                # Disparar bola de chicle
                from entities import GumProjectile
                self.audio.play('pop')
                px = paddle.rect.right if owner == 1 else paddle.rect.left
                dir_x = 1 if owner == 1 else -1
                self.gum_projectiles.append(GumProjectile(px, paddle.rect.centery, dir_x))
                paddle.gum_charges -= 1
                if paddle.gum_charges <= 0:
                    paddle.power_active = POWER_NONE
                    paddle.color = WHITE

        elif paddle.power_stored == POWER_GHOST:
            self.audio.play('ghost') # Risa malévola
            ghost = Ball(paddle.rect.centerx, paddle.rect.centery)
            ghost.is_ghost = True
            ghost.ghost_owner = owner
            # Velocidad 50% más lenta que la base
            speed = 300 * self.initial_ball_speed_options[self.initial_ball_speed_idx] * 0.5
            ghost.serve(1 if owner == 1 else -1, speed)
            ghost.color = GHOST_COLOR # Asignar DESPUÉS de serve
            self.balls.append(ghost)
            paddle.power_stored = POWER_NONE
            paddle.color = WHITE
        else:
            paddle.activate_power(self)

    def _reset_round_state(self):
        # Detener sonidos de bucle
        self.audio.fadeout('fire', 500)
        
        # Reset global round variables (relojes, zonas, multiplicadores)
        self.global_hits = 0
        self.hourglass_rect = None
        self.is_x2_item_active = False
        self.pending_x2_spawn = False
        self.zone_type = self.slow_zone_owner = self.p1_zone_type = self.p2_zone_type = self.last_hitter = 0
        self.planet1_alive = self.planet2_alive = True
        self.planet1_hits = self.planet2_hits = 0
        self.paddle1.reset()
        self.paddle2.reset()
        if self.start_with_power_enabled:
            self.paddle1.grant_random_power(self)
            self.paddle2.grant_random_power(self)

    def goal_scored(self, player):
        if self.is_golden_goal_round:
            self.is_golden_goal_round = False
            msg_win = self.t(f"PLAYER {player} WINS!", f"¡EL JUGADOR {player} GANA!")
            msg_reason = self.t(f"(Player {player} won by GOLDEN Goal rule)", f"(El Jugador {player} ganó por Gol de Oro)")
            self.winner_text = f"{msg_win}\n|YELLOW|{msg_reason}"
            if player == 1: self.score1 = self.max_score
            else: self.score2 = self.max_score
            self.state = STATE_GAME_OVER; return

        inc = 2 if self.ball_is_x2 else 1
        self.point_scored(player, inc)

    def point_scored(self, player, increment=1):
        self._reset_round_state()
        
        if player == 1: self.score1 += increment; s_dir = 1
        else: self.score2 += increment; s_dir = -1
        self.ball_is_x2 = False

        # Comprobar Victoria
        if self.score1 >= self.max_score or self.score2 >= self.max_score:
            # Si el Match Point está activado, debe haber una diferencia de 2
            if self.match_point_enabled and abs(self.score1 - self.score2) < 2:
                # Continuamos (Deuce)
                pass
            else:
                winner = 1 if self.score1 >= self.max_score else 2
                msg_win = self.t(f"PLAYER {winner} WINS!", f"¡EL JUGADOR {winner} GANA!")
                self.winner_text = msg_win
                if self.match_point_enabled:
                    msg_reason = self.t(f"(Player {winner} won by MATCH POINT rule)", f"(El Jugador {winner} ganó por Punto de Partido)")
                    self.winner_text += f"\n|YELLOW|{msg_reason}"
                self.state = STATE_GAME_OVER; return

        # Si no hay victoria, preparamos el saque
        self.state = STATE_SERVE
        self.serve_direction = s_dir
        self.balls = [Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        self.balls[0].serve(s_dir, 300 * self.initial_ball_speed_options[self.initial_ball_speed_idx])
        
        # Activar el temporizador de saque y anuncios (Match Point, etc)
        self.serve_timer = 1.75 # Cooldown de seguridad
        self._check_for_announcements()
        
        if self.state == STATE_SERVE:
            if self.experimental_golden_goal and random.random() < 0.10: 
                self.is_golden_goal_round = True
                self.pending_x2_spawn = False
            elif self.start_x2_enabled and random.random() < 0.50: 
                self.pending_x2_spawn = True
                self.is_golden_goal_round = False
            
            # Recalcular anuncios tras las tiradas de azar
            self._check_for_announcements()

        self.mouse = None
        self.mouse_hits_counter = 0

    def _check_for_announcements(self):
        self.show_match_point_anim = self.show_golden_goal_anim = False
        self.serve_timer = 1.0
        
        # Prioridad 1: Golden Goal ALEATORIO (Forzado por el sistema)
        if self.is_golden_goal_round:
            if not self.show_golden_goal_anim: # Solo sonar si no se está mostrando ya
                self.show_golden_goal_anim = True
                self.golden_goal_anim_timer = 2.5
                self.serve_timer = 3.0
                self.audio.play('golden_goal')
            return

        # Prioridad 2: Match Point (Permite Deuce/Diferencia de 2)
        if self.match_point_enabled:
            pts1, pts2 = max(self.max_score, self.score2+2)-self.score1, max(self.max_score, self.score1+2)-self.score2
            if pts1 == 1 or pts2 == 1:
                if not self.show_match_point_anim:
                    self.show_match_point_anim = True
                    self.match_point_anim_timer = 2.5
                    self.serve_timer = 3.0
                    self.audio.play('match_point')
                return
        
        # Prioridad 3: Golden Goal Experimental / Sudden Death Natural
        is_at_final_point = (self.score1 == self.max_score-1 and self.score2 == self.max_score-1)
        if is_at_final_point and (self.experimental_golden_goal or not self.match_point_enabled):
            if not self.show_golden_goal_anim:
                self.is_golden_goal_round = True 
                self.show_golden_goal_anim = True
                self.golden_goal_anim_timer = 2.5
                self.serve_timer = 3.0
                self.audio.play('golden_goal')
            return

    def update(self, dt):
        # Sincronizar estado del VFXManager con el ajuste de Settings
        self.vfx.enabled = self.vfx_enabled
        self.vfx.update(dt)

        # Actualizar Screen Shake
        if self.shake_timer > 0:
            self.shake_timer -= dt
            if self.shake_timer <= 0:
                self.shake_amount = 0

        if self.state == STATE_SERVE:
            self.serve_timer -= dt
            if self.serve_timer <= 0: self.state = STATE_PLAYING; self.paddle1.is_destroyed = self.paddle2.is_destroyed = False
            if self.show_match_point_anim: 
                self.match_point_anim_timer -= dt
                if self.match_point_anim_timer <= 0: self.show_match_point_anim = False
            if self.show_golden_goal_anim: 
                self.golden_goal_anim_timer -= dt
                if self.golden_goal_anim_timer <= 0: self.show_golden_goal_anim = False
                
        elif self.state == STATE_PLAYING:
            if self.wall_sound_cooldown > 0: self.wall_sound_cooldown -= dt
            
            # Lógica de IA para la paleta 2
            if self.is_ai_mode and self.balls:
                # 1. Activar poderes automáticamente
                if self.paddle2.power_stored != POWER_NONE:
                    # 1. Estrategia para GHOST: Lanzar cuando el jugador esté lejos del centro
                    if self.paddle2.power_stored == POWER_GHOST:
                        if abs(self.paddle1.rect.centery - SCREEN_HEIGHT // 2) > 100 or random.random() < 0.01:
                            self.activate_paddle_power(self.paddle2, 2)
                    
                    # 2. Estrategia para MAGNET: NO activar si el jugador tiene el poder NARANJA (explosivo)
                    elif self.paddle2.power_stored == POWER_MAGNET:
                        if self.paddle1.power_active != POWER_ORANGE:
                            self.activate_paddle_power(self.paddle2, 2)
                            
                    # 3. Otros poderes se activan al instante
                    else:
                        self.activate_paddle_power(self.paddle2, 2)
                
                # 2. Lógica de CURVATURA MAGNÉTICA (Si el imán está activo y la pelota se aleja)
                if self.paddle2.power_active == POWER_MAGNET:
                    main_ball = self.balls[0]
                    if main_ball.vx < 0: # La pelota se aleja de la IA hacia el jugador
                        # Decidir hacia dónde curvar
                        target_y = SCREEN_HEIGHT // 2
                        if self.mouse:
                            # Evitar al ratón a toda costa
                            target_y = 100 if self.mouse.rect.centery > SCREEN_HEIGHT // 2 else SCREEN_HEIGHT - 100
                        else:
                            # Atacar: curvar al lado opuesto del jugador
                            target_y = 50 if self.paddle1.rect.centery > SCREEN_HEIGHT // 2 else SCREEN_HEIGHT - 50
                        
                        # Mover paleta para tirar de la pelota
                        if self.paddle2.rect.centery < target_y: self.paddle2.move(1, dt, PADDLE_SPEED)
                        elif self.paddle2.rect.centery > target_y: self.paddle2.move(-1, dt, PADDLE_SPEED)
                        # No retornar, permitir que siga otras lógicas si es necesario
                
                # 3. Lógica específica de CHICLE
                if self.paddle2.power_active == POWER_GUM:
                    if self.paddle2.is_stuck:
                        # PRIORIDAD: Escapar del ratón si está cerca
                        if self.mouse and self.mouse.rect.centerx > SCREEN_WIDTH // 2:
                            target_y = 100 if self.mouse.rect.centery > SCREEN_HEIGHT // 2 else SCREEN_HEIGHT - 100
                        else:
                            # TROLLEAR al jugador (Moverse al lado opuesto de donde está la paleta 1)
                            target_y = 100 if self.paddle1.rect.centery > SCREEN_HEIGHT // 2 else SCREEN_HEIGHT - 100
                        
                        if self.paddle2.rect.centery < target_y - 10:
                            self.paddle2.move(1, dt, PADDLE_SPEED)
                        elif self.paddle2.rect.centery > target_y + 10:
                            self.paddle2.move(-1, dt, PADDLE_SPEED)
                        
                        # Soltar si llegó al objetivo o le queda poca carga
                        if abs(self.paddle2.rect.centery - target_y) < 20 or self.paddle2.gum_charges <= 1:
                            if random.random() < 0.05: # Un poco de azar para soltar
                                self.activate_paddle_power(self.paddle2, 2)
                    else:
                        # Si no está pegada pero tiene cargas: Disparar chicles para confundir
                        if self.paddle2.gum_charges > 0 and random.random() < 0.01:
                            self.activate_paddle_power(self.paddle2, 2)

                # 4. Lógica específica de REVOLVER (Duelo de Vaqueros)
                if self.paddle2.power_active == POWER_REVOLVER:
                    # Apuntar al jugador
                    target_y = self.paddle1.rect.centery
                    if self.paddle2.rect.centery < target_y - 5:
                        self.paddle2.move(1, dt, PADDLE_SPEED)
                    elif self.paddle2.rect.centery > target_y + 5:
                        self.paddle2.move(-1, dt, PADDLE_SPEED)
                    
                    # Disparar si está alineado y no está en cooldown de bala (o azar)
                    if abs(self.paddle2.rect.centery - target_y) < 15:
                        if random.random() < 0.05: # No disparar las 3 balas en 1 frame
                            self.activate_paddle_power(self.paddle2, 2)
                    
                    # Si la pelota está muy cerca de su lado, dejar de apuntar y defender un poco
                    main_ball = self.balls[0]
                    if main_ball.vx > 0 and main_ball.rect.centerx > SCREEN_WIDTH * 0.7:
                        # Prioridad defensa (permitir que siga la lógica de abajo)
                        pass
                    else:
                        # Si está apuntando, terminamos la actualización de IA aquí
                        self._process_ai_movement(dt)
                        return # Salir del frame de actualización de IA

                # 2. Comprobar si hay alguna pelota naranja amenazante (viniendo hacia la IA)
                orange_threats = [b for b in self.balls if b.is_orange and b.vx > 0]
                
                if orange_threats:
                    # ESQUIVAR: Moverse al lado opuesto de la amenaza más cercana
                    danger_ball = min(orange_threats, key=lambda b: abs(b.rect.centerx - self.paddle2.rect.centerx))
                    if danger_ball.rect.centery < SCREEN_HEIGHT // 2:
                        # La pelota está arriba, vamos abajo
                        self.paddle2.move(1, dt, PADDLE_SPEED)
                    else:
                        # La pelota está abajo, vamos arriba
                        self.paddle2.move(-1, dt, PADDLE_SPEED)
                else:
                    # SEGUIR y APUNTAR (Solo si no está pegada)
                    if not self.paddle2.is_stuck:
                        # Filtrar pelotas: Solo seguir la principal o las fantasmas del RIVAL (J1)
                        # Filtrar pelotas: Solo seguir la principal o las fantasmas del RIVAL (J1)
                        valid_balls = [b for b in self.balls if not (b.is_ghost and b.ghost_owner == 2)]
                        if valid_balls:
                            target_ball = min(valid_balls, key=lambda b: abs(b.rect.centerx - self.paddle2.rect.centerx))
                            target_y = target_ball.rect.centery
                            
                            # NUEVO: Anticipación de PORTALES
                            if self.portals_enabled:
                                incoming_to_portal = False
                                exit_y = None
                                portal_pairs = [(self.portal_blue_rect, self.portal_orange_rect), (self.portal_red_rect, self.portal_green_rect) if self.more_portals_enabled else (None, None)]
                                for p1, p2 in portal_pairs:
                                    if p1 and p2:
                                        if p1.inflate(20, 20).colliderect(target_ball.rect): exit_y = p2.centery; incoming_to_portal = True; break
                                        elif p2.inflate(20, 20).colliderect(target_ball.rect): exit_y = p1.centery; incoming_to_portal = True; break
                                if incoming_to_portal and exit_y is not None: target_y = exit_y

                            aim_offset = 0
                            if self.mouse:
                                if self.mouse.rect.centery < target_ball.rect.centery: aim_offset = -self.paddle2.rect.height // 3
                                else: aim_offset = self.paddle2.rect.height // 3
                            elif self.hourglass_rect and self.hourglass_type != 2:
                                if self.hourglass_rect.centery < target_ball.rect.centery: aim_offset = self.paddle2.rect.height // 3
                                else: aim_offset = -self.paddle2.rect.height // 3
                            elif self.score2 < self.score1 and self.is_x2_item_active:
                                if self.x2_item_rect.centery < target_ball.rect.centery: aim_offset = self.paddle2.rect.height // 3
                                else: aim_offset = -self.paddle2.rect.height // 3
                            elif self.portals_enabled and random.random() < 0.20:
                                portals = [self.portal_blue_rect, self.portal_orange_rect]
                                if self.more_portals_enabled: portals.extend([self.portal_red_rect, self.portal_green_rect])
                                target_portal = random.choice(portals)
                                if target_portal.centery < target_ball.rect.centery: aim_offset = self.paddle2.rect.height // 3
                                else: aim_offset = -self.paddle2.rect.height // 3

                            if target_ball.rect.centery < (self.paddle2.rect.centery + aim_offset) - 10: self.paddle2.move(-1, dt, PADDLE_SPEED)
                            elif target_ball.rect.centery > (self.paddle2.rect.centery + aim_offset) + 10: self.paddle2.move(1, dt, PADDLE_SPEED)

            self._process_ai_movement(dt)

    def _process_ai_movement(self, dt):
        for p in [self.paddle1, self.paddle2]:
            p.update(dt, self)
            if p.shield_shrink_timer > 0:
                p.shield_shrink_timer -= dt
                if p.shield_shrink_timer <= 0: p.power_active = POWER_NONE; p.rect.height = PADDLE_HEIGHT; p.color = WHITE
            if p.white_activation_timer > 0:
                p.white_activation_timer -= dt
                if p.white_activation_timer <= 0:
                    p.rect.height = SCREEN_HEIGHT; p.rect.width = SCREEN_WIDTH // 2; p.rect.y = 0; p.y_float = 0.0
                    p.rect.x = 0 if p == self.paddle1 else SCREEN_WIDTH // 2; p.white_zone_hits_left = 5

            # 6. Actualizar Proyectiles de Chicle
            for gp in self.gum_projectiles[:]:
                gp.update(dt)
                if not gp.active:
                    self.gum_projectiles.remove(gp)
                    continue
                # Colisión Chicle - Pelotas
                for ball in self.balls:
                    if gp.rect.colliderect(ball.rect):
                        self.audio.play('explosion')
                        self.vfx.burst(gp.rect.centerx, gp.rect.centery, GUM_PINK)
                        gp.active = False
                        # Rebote de la pelota
                        ball.vx *= -1.2 # Pequeño impulso al chocar con chicle
                        ball.vy += random.uniform(-50, 50)
                        break

            # Lógica del Ratón
            if self.add_mouse_enabled:
                required_hits = self.mouse_appear_options[self.mouse_appear_idx]
                if self.mouse is None and self.mouse_hits_counter >= required_hits:
                    from entities import Mouse
                    self.mouse = Mouse(SCREEN_WIDTH // 2, SCREEN_HEIGHT + 50)
                    self.audio.play('squeak')
                
                if self.mouse and self.balls:
                    m_speed = self.mouse_speed_options[self.mouse_speed_idx]
                    self.mouse.update(dt, self.balls[0], speed_multiplier=m_speed)
                    # Colisión Ratón - Pelota
                    for ball in self.balls[:]:
                        if not ball.is_ghost and self.mouse.rect.colliderect(ball.rect):
                            # CASO ESPECIAL: Pelota NARANJA (Explosión del ratón)
                            if ball.is_orange:
                                self.audio.play('explosion')
                                self.vfx.burst(self.mouse.rect.centerx, self.mouse.rect.centery, ORANGE)
                                self.mouse = None
                                self.mouse_hits_counter = 0
                                # La pelota se purifica y sigue
                                ball.is_orange = False
                                ball.color = WHITE
                                ball.vx *= -1.1
                                return # El juego sigue, el ratón murió
                            
                            self.audio.play('nom')
                            p_responsible = self.last_hitter
                            responsible_paddle = self.paddle1 if p_responsible == 1 else self.paddle2
                            winner_id = 2 if p_responsible == 1 else 1
                            
                            # ¿TIENE ESCUDO EL RESPONSABLE?
                            if responsible_paddle.shield_hits_left > 0:
                                self.audio.play('shield_hit')
                                responsible_paddle.shield_hits_left -= 1
                                # La pelota rebota en lugar de desaparecer
                                ball.vx *= -1.2 
                                ball.vy += random.uniform(-100, 100)
                                self.mouse = None
                                self.mouse_hits_counter = 0
                                return # Continúa el juego sin puntos
                            
                            # Si NO tiene escudo, castigo normal
                            if p_responsible == 1: 
                                if self.score1 > 0: self.score1 -= 1
                            else: 
                                if self.score2 > 0: self.score2 -= 1
                            
                            if ball in self.balls: self.balls.remove(ball)
                            self.mouse = None
                            self.mouse_hits_counter = 0
                            
                            # Usamos goal_scored para que respete Gol de Oro y X2 automáticamente
                            self.goal_scored(winner_id)
                            return 

            for ball in self.balls[:]:
                in_p1 = ball.rect.centerx < SCREEN_WIDTH // 2
                for i, p in enumerate([self.paddle1, self.paddle2]):
                    side = (i == 0 and in_p1) or (i == 1 and not in_p1)
                    if p.power_active == POWER_MAGNET and side:
                        self._apply_magnet_force(p, dt, ball)
                    elif ball.color == (100, 200, 255) and not ball.is_fireball and not ball.is_orange and not ball.is_ghost:
                        self.reset_ball_visuals(ball)

                # Planetas
                if self.floating_planets_enabled:
                    spd = math.sqrt(ball.vx**2 + ball.vy**2)
                    for p_idx, pos in enumerate([self.planet1_pos, self.planet2_pos]):
                        if (p_idx == 0 and self.planet1_alive) or (p_idx == 1 and self.planet2_alive):
                            dx, dy = pos[0]-ball.rect.centerx, pos[1]-ball.rect.centery
                            dist = math.sqrt(dx**2 + dy**2)
                            rad, force = self.gravity_radius_options[self.gravity_radius_idx], self.gravity_force_options[self.gravity_force_idx]
                            if self.planet_radius < dist < rad:
                                f = (1.0 - (dist / rad)) * force
                                ball.vx += (dx/dist)*f*dt*60; ball.vy += (dy/dist)*f*dt*60
                    new_spd = math.sqrt(ball.vx**2 + ball.vy**2)
                    if new_spd > 0: ball.vx = (ball.vx/new_spd)*spd; ball.vy = (ball.vy/new_spd)*spd
                
        # 1. Lógica de Portales (Prioridad sobre rebotes de pared)
        if self.portals_enabled:
            for ball in self.balls:
                colliding_blue = ball.rect.colliderect(self.portal_blue_rect)
                colliding_orange = ball.rect.colliderect(self.portal_orange_rect)
                colliding_red = self.more_portals_enabled and ball.rect.colliderect(self.portal_red_rect)
                colliding_green = self.more_portals_enabled and ball.rect.colliderect(self.portal_green_rect)
                
                if not colliding_blue and not colliding_orange and not colliding_red and not colliding_green:
                    ball.last_portal_id = None 

                if not ball.last_portal_id:
                    target_portal = None
                    if colliding_blue:
                        # Entra por Azul (arriba), sale por Naranja (abajo)
                        if self.portals_vertical:
                            ball.y_float = float(self.portal_orange_rect.y + (ball.y_float - self.portal_blue_rect.y))
                            if self.portal_orange_rect.x < SCREEN_WIDTH // 2: ball.x_float = self.portal_orange_rect.right + 2
                            else: ball.x_float = self.portal_orange_rect.left - ball.rect.width - 2
                        else:
                            ball.y_float = float(self.portal_orange_rect.top - ball.rect.height)
                            ball.x_float = float(self.portal_orange_rect.x + (ball.x_float - self.portal_blue_rect.x))
                        
                        ball.vy = -abs(ball.vy) 
                        ball.last_portal_id = "orange"
                        target_portal = BLUE
                    elif colliding_orange:
                        # Entra por Naranja (abajo), sale por Azul (arriba)
                        if self.portals_vertical:
                            ball.y_float = float(self.portal_blue_rect.y + (ball.y_float - self.portal_orange_rect.y))
                            if self.portal_blue_rect.x < SCREEN_WIDTH // 2: ball.x_float = self.portal_blue_rect.right + 2
                            else: ball.x_float = self.portal_blue_rect.left - ball.rect.width - 2
                        else:
                            ball.y_float = float(self.portal_blue_rect.bottom)
                            ball.x_float = float(self.portal_blue_rect.x + (ball.x_float - self.portal_orange_rect.x))
                        
                        ball.vy = abs(ball.vy) 
                        ball.last_portal_id = "blue"
                        target_portal = ORANGE
                    elif self.more_portals_enabled and ball.rect.colliderect(self.portal_red_rect) and ball.last_portal_id != "red":
                        # Entra por Rojo (abajo, J1), sale por Verde (arriba, J2)
                        if self.portals_vertical:
                            ball.y_float = float(self.portal_green_rect.y + (ball.y_float - self.portal_red_rect.y))
                            if self.portal_green_rect.x < SCREEN_WIDTH // 2: ball.x_float = self.portal_green_rect.right + 2
                            else: ball.x_float = self.portal_green_rect.left - ball.rect.width - 2
                        else:
                            ball.y_float = float(self.portal_green_rect.bottom)
                            ball.x_float = float(self.portal_green_rect.x + (ball.x_float - self.portal_red_rect.x))
                        ball.vy = abs(ball.vy)
                        ball.last_portal_id = "green"
                        target_portal = RED
                    elif self.more_portals_enabled and ball.rect.colliderect(self.portal_green_rect) and ball.last_portal_id != "green":
                        # Entra por Verde (arriba, J2), sale por Rojo (abajo, J1)
                        if self.portals_vertical:
                            ball.y_float = float(self.portal_red_rect.y + (ball.y_float - self.portal_green_rect.y))
                            if self.portal_red_rect.x < SCREEN_WIDTH // 2: ball.x_float = self.portal_red_rect.right + 2
                            else: ball.x_float = self.portal_red_rect.left - ball.rect.width - 2
                        else:
                            ball.y_float = float(self.portal_red_rect.top - ball.rect.height)
                            ball.x_float = float(self.portal_red_rect.x + (ball.x_float - self.portal_green_rect.x))
                        ball.vy = -abs(ball.vy)
                        ball.last_portal_id = "red"
                        target_portal = GREEN

                    if target_portal:
                        # Giro sutil y Aumento de velocidad (0.5%)
                        spd = math.sqrt(ball.vx**2 + ball.vy**2) * 1.005
                        angle = math.atan2(ball.vy, ball.vx) + math.radians(5)
                        ball.vx = spd * math.cos(angle)
                        ball.vy = spd * math.sin(angle)
                        
                        ball.rect.x, ball.rect.y = int(ball.x_float), int(ball.y_float)
                        self.audio.play('ghost'); self.vfx.explosion(ball.rect.centerx, ball.rect.centery, target_portal)

        # 2. Actualización de pelotas y colisiones normales (Solo si no hay cooldown de saque)
        if self.serve_timer > 0:
            self.serve_timer -= dt
        elif self.state == STATE_PLAYING:
            for ball in self.balls:
                ball.update(dt, self._get_zone_multiplier(ball))
                self.check_ball_collisions(ball)
            
        # Actualización de Timers Especiales (Siempre, para que terminen)
        if self.show_match_point_anim: self.match_point_anim_timer -= dt
        if self.show_golden_goal_anim: self.golden_goal_anim_timer -= dt

        # 3. Lógica de Ítem Revólver (Órbita)
        if self.revolver_enabled and self.state == STATE_PLAYING:
            if self.revolver_item_active:
                self.revolver_angle += dt * 1.5 # Velocidad de rotación
                center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
                rx = center_x + math.cos(self.revolver_angle) * self.revolver_orbit_radius
                ry = center_y + math.sin(self.revolver_angle) * self.revolver_orbit_radius
                self.revolver_item_rect = pygame.Rect(rx - 15, ry - 15, 30, 30)
                
                # Colisión con pelota
                for ball in self.balls:
                    if ball.rect.colliderect(self.revolver_item_rect):
                        self.revolver_item_active = False
                        self.revolver_item_rect = None
                        self.audio.play('speed') # Reutilizar sonido o añadir uno nuevo
                        # Dar poder al último que tocó
                        target_p = self.paddle1 if self.last_hitter == 1 else self.paddle2
                        target_p.power_stored = POWER_REVOLVER
                        target_p.color = GUN_METAL
                        self.global_hits += 1 # Evitar re-aparición inmediata
                        break

        # 4. Gestión de Balas Amarillas y Duración
        for p in [self.paddle1, self.paddle2]:
            if p.power_active == POWER_REVOLVER:
                p.revolver_timer -= dt
                if p.revolver_timer <= 0 or p.revolver_shots_left <= 0:
                    p.power_active = POWER_NONE
                    p.revolver_shots_left = 0
                    p.revolver_timer = 0
                    p.color = WHITE

        for ball in self.balls[:]:
            if ball.is_bullet:
                # Si sale de la pantalla, desaparece
                if ball.rect.right < 0 or ball.rect.left > SCREEN_WIDTH:
                    self.balls.remove(ball)
                # Colisión con paletas (Letal)
                for i, p in enumerate([self.paddle1, self.paddle2]):
                    if ball.rect.colliderect(p.rect):
                        # Solo mata al oponente (la bala no mata al que la disparó)
                        p_id = i + 1
                        if (ball.vx > 0 and p_id == 2) or (ball.vx < 0 and p_id == 1):
                            self.audio.play('explosion')
                            self.vfx.burst(p.rect.centerx, p.rect.centery, YELLOW)
                            self.goal_scored(1 if p_id == 2 else 2)
                            if ball in self.balls: self.balls.remove(ball)
                            break

        # Rastro para la bola principal si es naranja
        if self.balls:
            main_ball = self.balls[0]
            if self.state == STATE_PLAYING and main_ball.is_orange and self.orange_skin_idx == 1:
                self.vfx.trail(main_ball.rect.centerx, main_ball.rect.centery, (100, 200, 255))

    def _get_zone_multiplier(self, ball):
        in_p1 = ball.rect.centerx < SCREEN_WIDTH // 2
        z_type = (self.p1_zone_type if in_p1 else self.p2_zone_type) if self.watches_kept_enabled else (self.zone_type if ((self.slow_zone_owner == 1 and in_p1) or (self.slow_zone_owner == 2 and not in_p1)) else 0)
        return 0.5 if z_type == 1 else (1.25 if z_type == 2 else 1.0)


    def _apply_magnet_force(self, p, dt, ball):
        spd = math.sqrt(ball.vx**2 + ball.vy**2)
        incoming = (p == self.paddle1 and ball.vx < 0) or (p == self.paddle2 and ball.vx > 0)
        dx, dy = p.rect.centerx - ball.rect.centerx, p.rect.centery - ball.rect.centery
        dist = math.sqrt(dx**2 + dy**2)
        if dist > 0:
            target_vx, target_vy = (dx/dist)*spd, (dy/dist)*spd
            if incoming: ball.vx += (target_vx - ball.vx)*0.2*dt*60; ball.vy += (target_vy - ball.vy)*0.2*dt*60
            else: ball.vy += (target_vy - ball.vy)*0.1*dt*60
        new_spd = math.sqrt(ball.vx**2 + ball.vy**2)
        if new_spd > 0: ball.vx = (ball.vx/new_spd)*spd; ball.vy = (ball.vy/new_spd)*spd
        
        # Mantener color naranja/hadouken si corresponde, si no, poner azul imán
        if not ball.is_orange:
            ball.color = (100, 200, 255)

    def trigger_shake(self, amount, duration):
        if not self.shake_enabled: return
        self.shake_amount = amount
        self.shake_timer = duration

    def draw(self):
        # Calculamos el desplazamiento del shake
        off_x = 0
        off_y = 0
        if self.shake_timer > 0:
            off_x = random.randint(-self.shake_amount, self.shake_amount)
            off_y = random.randint(-self.shake_amount, self.shake_amount)

        # Superficie temporal
        temp_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        temp_surf.fill(BLACK)
        
        if self.state in [STATE_PLAYING, STATE_SERVE, STATE_PRESS_TO_START, STATE_GAME_OVER, STATE_MAIN_MENU]:
            self._draw_game_field(temp_surf)
            self.paddle1.draw(temp_surf, self); self.paddle2.draw(temp_surf, self)
            if self.state in [STATE_PLAYING, STATE_SERVE]:
                for ball in self.balls:
                    if ball.is_orange and self.orange_skin_idx == 1:
                        pygame.draw.ellipse(temp_surf, (0, 150, 255), ball.rect)
                        pygame.draw.ellipse(temp_surf, WHITE, ball.rect.inflate(-6, -6))
                    else: 
                        if self.add_mouse_enabled and not ball.is_fireball and not ball.is_orange and not ball.is_ghost:
                            ball.color = YELLOW # Queso
                            ball.is_cheese = True
                        else:
                            ball.is_cheese = False
                        m_color = GOLD if self.ball_is_x2 and ball == self.balls[0] else WHITE
                        ball.draw(temp_surf, skin=self.ball_skin_options[self.ball_skin_idx], identical_ghost=self.ghost_identical_enabled, main_color=m_color)
                
                if self.mouse:
                    self.mouse.draw(temp_surf)

                for gp in self.gum_projectiles:
                    gp.draw(temp_surf)
            elif self.state == STATE_PRESS_TO_START:
                t = self.font.render("Presiona ESPACIO para Sacar", True, WHITE)
                temp_surf.blit(t, t.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 100)))
            
            if self.is_x2_item_active: self._draw_x2_icon(temp_surf)
            self._draw_score(temp_surf)
            
        if self.state == STATE_MAIN_MENU: self._draw_main_menu(temp_surf)
        elif self.state == STATE_MODIFIERS: self._draw_modifiers(temp_surf)
        elif self.state == STATE_SETTINGS: self._draw_settings(temp_surf)
        elif self.state == STATE_MODE_SELECTION: self._draw_mode_selection(temp_surf)
        elif self.state == STATE_GAME_OVER: self._draw_game_over(temp_surf)
        
        self.vfx.draw(temp_surf)

        # CAPA FINAL: Animaciones de Anuncio (siempre encima de todo lo demás)
        if self.show_match_point_anim and self.match_point_anim_timer > 0: 
            self._draw_match_point_anim(temp_surf)
        if self.show_golden_goal_anim and self.golden_goal_anim_timer > 0: 
            self._draw_golden_goal_anim(temp_surf)
        
        self.screen.fill(BLACK)
        self.screen.blit(temp_surf, (off_x, off_y))
        pygame.display.flip()

    def _draw_game_field(self, surface):
        def draw_zone(owner, z_type):
            if z_type == 0: return
            colors = {1: (0, 0, 80), 2: (80, 0, 0), 3: VIOLET_ZONE, 4: WHITE}
            r = (0, 0, SCREEN_WIDTH//2, SCREEN_HEIGHT) if owner == 1 else (SCREEN_WIDTH//2, 0, SCREEN_WIDTH//2, SCREEN_HEIGHT)
            pygame.draw.rect(surface, colors[z_type], r)

        if self.watches_kept_enabled: draw_zone(1, self.p1_zone_type); draw_zone(2, self.p2_zone_type)
        elif self.slow_zone_owner != 0: draw_zone(self.slow_zone_owner, self.zone_type)
        self._draw_dashed_line(surface, WHITE, (SCREEN_WIDTH//2, 0), (SCREEN_WIDTH//2, SCREEN_HEIGHT), 2, 15)
        
        # Dibujar Portales
        if self.portals_enabled:
            # Portal Azul (Techo, J1)
            pygame.draw.rect(surface, BLUE, self.portal_blue_rect)
            pygame.draw.rect(surface, WHITE, self.portal_blue_rect, 2)
            # Portal Naranja (Suelo, J2)
            pygame.draw.rect(surface, ORANGE, self.portal_orange_rect)
            pygame.draw.rect(surface, WHITE, self.portal_orange_rect, 2)
            
            if self.more_portals_enabled:
                # Portal Rojo (Suelo, J1)
                pygame.draw.rect(surface, RED, self.portal_red_rect)
                pygame.draw.rect(surface, WHITE, self.portal_red_rect, 2)
                # Portal Verde (Techo, J2)
                pygame.draw.rect(surface, GREEN, self.portal_green_rect)
                pygame.draw.rect(surface, WHITE, self.portal_green_rect, 2)
        
        if self.floating_planets_enabled: self._draw_planets(surface)
        if self.hourglass_rect: self._draw_hourglass(surface)
        if self.revolver_item_active and self.revolver_item_rect: self._draw_revolver(surface)
        if self.paddle1.has_extra_life: pygame.draw.line(surface, YELLOW, (2, 0), (2, SCREEN_HEIGHT), 5)
        if self.paddle2.has_extra_life: pygame.draw.line(surface, YELLOW, (SCREEN_WIDTH-2, 0), (SCREEN_WIDTH-2, SCREEN_HEIGHT), 5)

    def _draw_revolver(self, surface):
        r = self.revolver_item_rect
        # Dibujar un revólver pixelado simple
        # Cañón (Gris)
        pygame.draw.rect(surface, GUN_METAL, (r.x + 5, r.y + 5, 20, 8))
        # Empuñadura (Marrón)
        pygame.draw.rect(surface, LIGHT_BROWN, (r.x + 5, r.y + 13, 8, 12))
        # Tambor
        pygame.draw.rect(surface, GUN_METAL, (r.x + 5, r.y + 10, 10, 6))
        pygame.draw.rect(surface, WHITE, r, 1) # Borde de ítem

    def _draw_dashed_line(self, surface, color, start, end, width, dash):
        x1, y1 = start; x2, y2 = end
        if x1 == x2:
            for y in range(y1, y2, dash*2): pygame.draw.line(surface, color, (x1, y), (x1, min(y+dash, y2)), width)
        else:
            for x in range(x1, x2, dash*2): pygame.draw.line(surface, color, (x, y1), (x+dash, y1), width)

    def _draw_mode_selection(self, surface):
        surface.fill(BLACK)
        # Título
        title = self.large_font.render(self.t("SELECT MODE", "SELECCIONAR MODO"), True, WHITE)
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))

        mpos = pygame.mouse.get_pos()
        
        # Dibujar Botones
        for btn, label, is_solo in [(self.btn_multi_rect, "MULTIPLAYER", False), (self.btn_solo_rect, "SOLO", True)]:
            hover = btn.collidepoint(mpos)
            color = WHITE if hover else GRAY
            pygame.draw.rect(surface, color, btn, 4)
            
            # Texto
            txt = self.medium_font.render(label, True, color)
            surface.blit(txt, (btn.centerx - txt.get_width()//2, btn.top + 30))
            
            # Imagen Retro (Dentro del botón)
            img_rect = pygame.Rect(btn.x + 20, btn.y + 80, btn.width - 40, btn.height - 130)
            pygame.draw.rect(surface, (30, 30, 30), img_rect) # Fondo imagen
            
            # Arte Pong Retro
            # Paleta Izquierda
            pygame.draw.rect(surface, WHITE, (img_rect.x + 20, img_rect.centery - 30, 10, 60))
            # Pelota
            pygame.draw.rect(surface, WHITE, (img_rect.centerx - 5, img_rect.centery - 5, 10, 10))
            
            if not is_solo:
                # Paleta Derecha (Multiplayer)
                pygame.draw.rect(surface, WHITE, (img_rect.right - 30, img_rect.centery - 30, 10, 60))
            else:
                # Computadora IA (Solo)
                # Un monitor retro con "AI" escrito
                monitor_rect = pygame.Rect(img_rect.right - 70, img_rect.centery - 35, 50, 70)
                pygame.draw.rect(surface, WHITE, monitor_rect, 2)
                ai_txt = self.small_font.render("AI", True, WHITE)
                surface.blit(ai_txt, (monitor_rect.centerx - ai_txt.get_width()//2, monitor_rect.centery - ai_txt.get_height()//2))
                # Antena
                pygame.draw.line(surface, WHITE, (monitor_rect.centerx, monitor_rect.top), (monitor_rect.centerx + 10, monitor_rect.top - 15), 2)
                pygame.draw.circle(surface, WHITE, (monitor_rect.centerx + 10, monitor_rect.top - 15), 3)

        # Botón BACK
        pygame.draw.rect(surface, BLACK, self.back_btn_rect)
        pygame.draw.rect(surface, WHITE, self.back_btn_rect, 2)
        back_txt = self.t("BACK", "VOLVER")
        bt = self.small_font.render(back_txt, True, WHITE)
        surface.blit(bt, bt.get_rect(center=self.back_btn_rect.center))

    def _draw_planets(self, surface):
        px_size, g_idx = 5, self.gravity_force_idx
        matrix = assets.PLANET_MATRIX
        for p_idx, pos in enumerate([self.planet1_pos, self.planet2_pos]):
            if (p_idx == 0 and not self.planet1_alive) or (p_idx == 1 and not self.planet2_alive): continue
            sx, sy = pos[0] - 22, pos[1] - 22
            for r in range(9):
                for c in range(9):
                    if matrix[r][c]:
                        color = CYAN
                        if g_idx == 0: color = (180, 180, 180) # Moon
                        elif g_idx == 1: color = (50, 100, 255) if p_idx == 0 else (220, 80, 50) # Terra/Marte
                        elif g_idx == 2:
                            if p_idx == 0: # Júpiter (Beige y Marrón)
                                color = (230, 180, 140) if r in [0,1,4,5,8] else (180, 100, 50)
                            else: # Saturno (Crema/Dorado con "anillo" central)
                                color = (255, 220, 150) if r not in [4] else (210, 180, 120)
                        elif g_idx == 3: color = YELLOW if (r+c)%3!=0 else ORANGE # Star
                        
                        # Añadir sombreado/detalle (cráteres)
                        if (r+c)%3 == 0: color = tuple(max(0, cc-40) for cc in color)
                        pygame.draw.rect(surface, color, (sx + c*px_size, sy + r*px_size, px_size, px_size))

    def _draw_hourglass(self, surface):
        px = 4
        colors = {1: (50, 150, 255), 2: RED, 3: PURPLE, 4: WHITE, 5: YELLOW, 6: ORANGE}
        
        # Elegir matriz y color según la skin del reloj amarillo (tipo 5)
        if self.hourglass_type == 5 and self.yellow_watch_skin_idx == 1:
            matrix = assets.CROSS_MATRIX
            draw_color = BROWN
        else:
            matrix = assets.HOURGLASS_MATRIX
            draw_color = colors[self.hourglass_type]
            
        # Calcular centro dinámicamente según el tamaño de la matriz
        rows = len(matrix)
        cols = len(matrix[0])
        sx = self.hourglass_rect.centerx - (cols * px) // 2
        sy = self.hourglass_rect.centery - (rows * px) // 2
        
        for r in range(rows):
            for c in range(cols):
                if matrix[r][c]: pygame.draw.rect(surface, draw_color, (sx+c*px, sy+r*px, px, px))

    def _draw_x2_icon(self, surface):
        cx, cy, px = *self.x2_item_rect.center, 4
        mx = assets.X2_MATRIX_X
        m2 = assets.X2_MATRIX_2
        for r in range(5):
            for c in range(5):
                if mx[r][c]: pygame.draw.rect(surface, GOLD, (cx-25+c*px, cy-10+r*px, px, px))
                if m2[r][c]: pygame.draw.rect(surface, GOLD, (cx+5+c*px, cy-10+r*px, px, px))

    def _draw_score(self, surface):
        c1 = self.paddle1.encapsulated_color if (self.encapsulate_powers_enabled and self.paddle1.power_encapsulated != POWER_NONE) else (BLACK if (self.zone_type == 4 and self.slow_zone_owner == 1) else WHITE)
        c2 = self.paddle2.encapsulated_color if (self.encapsulate_powers_enabled and self.paddle2.power_encapsulated != POWER_NONE) else (BLACK if (self.zone_type == 4 and self.slow_zone_owner == 2) else WHITE)
        s1, s2 = self.font.render(str(self.score1), True, c1), self.font.render(str(self.score2), True, c2)
        surface.blit(s1, (SCREEN_WIDTH//2-70, 20)); surface.blit(s2, (SCREEN_WIDTH//2+40, 20))

    def _draw_match_point_anim(self, surface):
        t = 2.5 - self.match_point_anim_timer
        txt_m, txt_p = self.large_font.render("MATCH", True, WHITE), self.large_font.render("POINT", True, WHITE)
        off = self.large_font.render("MA", True, WHITE).get_width()
        tw = off + txt_p.get_width()
        if t < 0.8: cx = SCREEN_WIDTH - (SCREEN_WIDTH//2 + tw//2) * (1-(1-t/0.8)**2)
        elif t < 1.7: cx = SCREEN_WIDTH//2 - tw//2
        else:
            t2 = (t-1.7)/0.8
            cx = (SCREEN_WIDTH//2 - tw//2) - (SCREEN_WIDTH//2 + tw)*(t2*t2)
        surface.blit(txt_m, (cx, SCREEN_HEIGHT//2 - txt_m.get_height())); surface.blit(txt_p, (cx + off, SCREEN_HEIGHT//2))

    def _draw_golden_goal_anim(self, surface):
        # Titileo de pantalla amarillo intenso (GOLD)
        if int(pygame.time.get_ticks() / 150) % 2 == 0:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(150); overlay.fill(GOLD); surface.blit(overlay, (0,0))
        
        t1, t2 = self.large_font.render("GOLDEN", True, GOLD), self.large_font.render(" GOAL", True, WHITE)
        tw, sy = t1.get_width() + t2.get_width(), SCREEN_HEIGHT//2 - t1.get_height()//2
        sx = SCREEN_WIDTH//2 - tw//2
        surface.blit(t1, (sx, sy)); surface.blit(t2, (sx + t1.get_width(), sy))

    def _draw_main_menu(self, surface):
        ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)); ov.set_alpha(160); ov.fill(BLACK); surface.blit(ov, (0,0))
        t1, t2 = self.large_font.render("PONG ", True, WHITE), self.large_font.render("KOMBAT", True, RED)
        tw = t1.get_width() + t2.get_width()
        sx, ty = SCREEN_WIDTH//2 - tw//2, SCREEN_HEIGHT//4 - 20
        surface.blit(t1, (sx, ty)); surface.blit(t2, (sx+t1.get_width(), ty))
        
        mpos = pygame.mouse.get_pos()
        buttons = [
            (self.btn_play_rect, self.t("PLAY", "JUGAR"), WHITE),
            (self.btn_modifiers_rect, self.t("MODIFIERS", "MODIFICADORES"), WHITE),
            (self.btn_settings_rect, self.t("SETTINGS", "AJUSTES"), WHITE)
        ]
        
        for r, txt, color in buttons:
            is_hover = r.collidepoint(mpos)
            bg_color = (40, 40, 40) if is_hover else BLACK
            
            pygame.draw.rect(surface, bg_color, r)
            pygame.draw.rect(surface, color, r, 4)
            
            # Auto-encogimiento con escala intermedia
            f_to_use = self.font
            if f_to_use.size(txt)[0] > r.width - 20:
                f_to_use = self.medium_font
                # Si aún así no entra (caso extremo), bajamos a small
                if f_to_use.size(txt)[0] > r.width - 10:
                    f_to_use = self.small_font
                
            st = f_to_use.render(txt, True, WHITE)
            surface.blit(st, st.get_rect(center=r.center))

    def _draw_modifiers(self, surface):
        pygame.draw.rect(surface, BLACK, self.modifiers_panel_rect); pygame.draw.rect(surface, WHITE, self.modifiers_panel_rect, 4)
        title_txt = self.t("MATCH MODIFIERS", "MODIFICADORES DE LA PARTIDA")
        # Auto-encogimiento agresivo para evitar chocar con el botón BACK (umbral 500px)
        f_to_use = self.font
        if f_to_use.size(title_txt)[0] > 500:
            f_to_use = self.medium_font
            if f_to_use.size(title_txt)[0] > 500:
                f_to_use = self.small_font
            
        t = f_to_use.render(title_txt, True, WHITE)
        surface.blit(t, t.get_rect(center=(SCREEN_WIDTH//2, self.modifiers_panel_rect.y+30)))
        pygame.draw.rect(surface, BLACK, self.back_btn_rect); pygame.draw.rect(surface, WHITE, self.back_btn_rect, 2)
        pygame.draw.rect(surface, BLACK, self.back_btn_rect); pygame.draw.rect(surface, WHITE, self.back_btn_rect, 2)
        back_txt = self.t("BACK", "VOLVER")
        # Si el texto es muy ancho para los 80px del botón, usamos tiny_font
        f_to_use = self.tiny_font if self.small_font.size(back_txt)[0] > self.back_btn_rect.width - 10 else self.small_font
        bt = f_to_use.render(back_txt, True, WHITE)
        surface.blit(bt, bt.get_rect(center=self.back_btn_rect.center))
        
        # Tabs
        tab_y = self.modifiers_panel_rect.top - 44
        self.tab_all_rect.topleft = (self.modifiers_panel_rect.left, tab_y)
        self.tab_extras_rect.topleft = (self.tab_all_rect.right + 5, tab_y)
        self.tab_skins_rect.topleft = (self.tab_extras_rect.right + 5, tab_y)
        for r, txt, key in [(self.tab_all_rect, self.t("ALL", "TODO"), "ALL"), (self.tab_extras_rect, self.t("EXTRAS", "EXTRAS"), "EXTRAS"), (self.tab_skins_rect, self.t("SKINS", "ASPECTOS"), "SKINS")]:
            bg = BLACK
            if key == "ALL": bg = (40,40,40) if self.modifiers_tab=="ALL" else BLACK
            elif key == "EXTRAS": bg = (0,80,0) if self.modifiers_tab=="EXTRAS" else (0,40,0)
            elif key == "SKINS": bg = (80,0,80) if self.modifiers_tab=="SKINS" else (40,0,40)
            pygame.draw.rect(surface, bg, r, border_top_left_radius=8, border_top_right_radius=8)
            pygame.draw.rect(surface, WHITE, r, 2, border_top_left_radius=8, border_top_right_radius=8)
            st = self.tiny_font.render(txt, True, WHITE); surface.blit(st, st.get_rect(center=r.center))
            
        old_clip = surface.get_clip(); clip = pygame.Rect(self.modifiers_panel_rect.x+10, self.modifiers_panel_rect.y+60, self.modifiers_panel_rect.width-40, self.modifiers_panel_rect.height-70)
        surface.set_clip(clip)
        self._draw_modifier_content(surface)
        surface.set_clip(old_clip)
        
        # Sincronizar posición del thumb visual con el scroll_y lógico (con clamping de seguridad)
        self.scroll_y = max(0, min(self.scroll_y, self.max_scroll))
        if self.max_scroll > 0:
            fraction = max(0, min(self.scroll_y / self.max_scroll, 1.0))
            self.scrollbar_thumb_rect.y = self.scrollbar_rect.y + fraction * (self.scrollbar_rect.height - self.scrollbar_thumb_height)
        else:
            self.scrollbar_thumb_rect.y = self.scrollbar_rect.y

        pygame.draw.rect(surface, (50,50,50), self.scrollbar_rect)
        pygame.draw.rect(surface, WHITE, self.scrollbar_thumb_rect)
        self._draw_tooltips(clip, surface)

    def _draw_modifier_content(self, surface):
        off, lm, ox = self.scroll_y, self.modifiers_panel_rect.x + 50, self.modifiers_panel_rect.centerx + 50
        self.max_y_rendered = 0
        
        # Reset rects visibility
        for r in [self.match_point_rect, self.golden_goal_anim_rect, self.reroll_rect, self.all_reroll_rect, self.equal_watches_rect, self.equal_powers_rect, self.watches_kept_rect, self.remove_watches_toggle_rect, self.remove_power_toggle_rect, self.experimental_toggle_rect]: r.y = -1000

        if self.modifiers_tab == "ALL":
            curr_y = 100
            # Score
            surface.blit(self.small_font.render(self.t("Score limit:", "Límite de puntos:"), True, WHITE), (lm, self.modifiers_panel_rect.y + curr_y - off))
            self.score_btn_rect.update(ox, self.modifiers_panel_rect.y + curr_y - 5 - off, 80, 40)
            pygame.draw.rect(surface, BLACK, self.score_btn_rect); pygame.draw.rect(surface, WHITE, self.score_btn_rect, 2)
            sv = self.small_font.render(str(self.max_score), True, WHITE); surface.blit(sv, sv.get_rect(center=self.score_btn_rect.center))
            
            inc_val = f"{self.ball_speed_multiplier_options[self.ball_speed_multiplier_idx]-1:g}"
            curr_y += 80; self._draw_sub_selector(curr_y, self.t("Ball speed increase:", "Aumento de velocidad:"), self.ball_speed_multiplier_names[self.ball_speed_multiplier_idx], self.ball_speed_btn_rect, off, ox, lm, surface, sub_val=inc_val)
            
            curr_y += 80
            self._draw_sub_selector(curr_y, self.t("Initial ball speed:", "Velocidad inicial:"), self.initial_ball_speed_names[self.initial_ball_speed_idx], self.initial_ball_speed_rect, off, ox, lm, surface, sub_val=f"x{self.initial_ball_speed_options[self.initial_ball_speed_idx]}")
            
            curr_y += 80
            y_spd = f"{int(self.yellow_speed_up_options[self.yellow_speed_up_idx]*100)}%"
            self._draw_sub_selector(curr_y, self.t("|YELLOW|Yellow |WHITE|Power Speed Up:", "Aumento de velocidad\ndel poder |YELLOW|AMARILLO"), self.yellow_speed_up_names[self.yellow_speed_up_idx], self.yellow_speed_up_rect, off, ox, lm, surface, sub_val=y_spd)
            
            curr_y += 80; draw_remove_option(self, curr_y, self.t("Numbers encapsulating powers", "Los números\nencapsulan poderes"), self.encapsulate_powers_enabled, self.encapsulate_powers_rect, self.encapsulate_powers_text_rect, active_color=CYAN, offset=off, surface=surface)
            
            curr_y += 80; draw_remove_option(self, curr_y, self.t("MATCH POINT:", "PUNTO DE PARTIDA:"), self.match_point_enabled, self.match_point_rect, self.match_point_text_rect, offset=off, surface=surface)
            curr_y += 80; draw_remove_option(self, curr_y, self.t("|GOLD|GOLDEN |WHITE|Goal animation:", "|GOLD|Animación de GOL |WHITE|DE ORO:"), self.golden_goal_anim_enabled, self.golden_goal_anim_rect, self.golden_goal_anim_text_rect, offset=off, surface=surface)
            curr_y += 80; draw_remove_option(self, curr_y, self.t("Re-rolls (|ORANGE|ORANGE|WHITE|/|YELLOW|YELLOW|WHITE|):", "Re-rolls (|ORANGE|NARANJA|WHITE|/|YELLOW|AMARILLO|WHITE|):"), self.reroll_enabled, self.reroll_rect, self.reroll_text_rect, offset=off, surface=surface)
            if self.reroll_enabled: curr_y += 80; draw_remove_option(self, curr_y, self.t("All Re-roll (|RED|RED|WHITE|/|GREEN|GREEN|WHITE|):", "Todo Re-roll (|RED|ROJO|WHITE|/|GREEN|VERDE|WHITE|):"), self.all_reroll_enabled, self.all_reroll_rect, self.all_reroll_text_rect, offset=off, surface=surface)
            curr_y += 80; draw_remove_option(self, curr_y, self.t("Equal watches (20%):", "Relojes iguales (20%):"), self.equal_watches_enabled, self.equal_watches_rect, self.equal_watches_text_rect, offset=off, surface=surface)
            curr_y += 80; draw_remove_option(self, curr_y, self.t("Equal powers (25%):", "Poderes iguales (25%):"), self.equal_powers_enabled, self.equal_powers_rect, self.equal_powers_text_rect, offset=off, surface=surface)
            curr_y += 80; draw_remove_option(self, curr_y, self.t("Watches kept:", "Relojes guardados:"), self.watches_kept_enabled, self.watches_kept_rect, self.watches_kept_text_rect, offset=off, surface=surface)
            
            curr_y += 80
            surface.blit(self.small_font.render(self.t("Watch spawn hits:", "Golpes para spawn de reloj:"), True, WHITE), (lm, self.modifiers_panel_rect.y + curr_y - off))
            self.watch_spawn_hits_rect.update(ox, self.modifiers_panel_rect.y + curr_y - 5 - off, 80, 40)
            pygame.draw.rect(surface, BLACK, self.watch_spawn_hits_rect); pygame.draw.rect(surface, WHITE, self.watch_spawn_hits_rect, 2)
            surface.blit(self.small_font.render(str(self.watch_spawn_hits_options[self.watch_spawn_hits_idx]), True, WHITE), self.small_font.render(str(self.watch_spawn_hits_options[self.watch_spawn_hits_idx]), True, WHITE).get_rect(center=self.watch_spawn_hits_rect.center))

            curr_y += 80; draw_rich_text(surface, self.t("Power auto grant hits:", "Toques para recibir\nun nuevo poder:"), (lm, self.modifiers_panel_rect.y + curr_y - off), self.small_font)
            self.power_auto_grant_hits_rect.update(ox, self.modifiers_panel_rect.y + curr_y - 5 - off, 80, 40)
            pygame.draw.rect(surface, BLACK, self.power_auto_grant_hits_rect); pygame.draw.rect(surface, WHITE, self.power_auto_grant_hits_rect, 2)
            surface.blit(self.small_font.render(str(self.power_auto_grant_hits_options[self.power_auto_grant_hits_idx]), True, WHITE), self.small_font.render(str(self.power_auto_grant_hits_options[self.power_auto_grant_hits_idx]), True, WHITE).get_rect(center=self.power_auto_grant_hits_rect.center))

            curr_y += 80; draw_remove_option(self, curr_y, self.t("Start with power:", "Iniciar con poder:"), self.start_with_power_enabled, self.start_with_power_rect, self.start_with_power_text_rect, offset=off, surface=surface)
            
            curr_y += 80; draw_remove_option(self, curr_y, self.t("Remove a watch", "Eliminar un reloj"), self.remove_watches_expanded, self.remove_watches_toggle_rect, self.remove_watches_toggle_text_rect, is_checkbox=False, offset=off, surface=surface)
            if self.remove_watches_expanded:
                curr_y += 60; draw_remove_option(self, curr_y, self.t(" - Remove |BLUE| BLUE |WHITE| watch", " - Eliminar reloj |BLUE| AZUL"), self.remove_blue, self.remove_blue_rect, self.remove_blue_text_rect, active_color=BLUE, offset=off, surface=surface)
                curr_y += 60; draw_remove_option(self, curr_y, self.t(" - Remove |RED| RED |WHITE| watch", " - Eliminar reloj |RED| ROJO"), self.remove_red, self.remove_red_rect, self.remove_red_text_rect, active_color=RED, offset=off, surface=surface)
                curr_y += 60; draw_remove_option(self, curr_y, self.t(" - Remove |PURPLE| PURPLE |WHITE| watch", " - Eliminar reloj |PURPLE| PÚRPURA"), self.remove_purple, self.remove_purple_rect, self.remove_purple_text_rect, active_color=PURPLE, offset=off, surface=surface)
                curr_y += 60; draw_remove_option(self, curr_y, self.t(" - Remove |WHITE| WHITE |WHITE| watch", " - Eliminar reloj |WHITE| BLANCO"), self.remove_white, self.remove_white_rect, self.remove_white_text_rect, active_color=WHITE, offset=off, surface=surface)
                curr_y += 60; draw_remove_option(self, curr_y, self.t(" - Remove |YELLOW| YELLOW |WHITE| watch", " - Eliminar reloj |YELLOW| AMARILLO"), self.remove_yellow, self.remove_yellow_rect, self.remove_yellow_text_rect, active_color=YELLOW, offset=off, surface=surface)
            
            curr_y += 80; draw_remove_option(self, curr_y, self.t("Remove a power", "Eliminar un poder"), self.remove_power_expanded, self.remove_power_toggle_rect, self.remove_power_toggle_text_rect, is_checkbox=False, offset=off, surface=surface)
            if self.remove_power_expanded:
                curr_y += 60; draw_remove_option(self, curr_y, self.t(" - Remove |RED| RED |WHITE| power", " - Eliminar poder |RED| ROJO"), self.remove_power_red, self.remove_power_red_rect, self.remove_power_red_text_rect, active_color=RED, offset=off, surface=surface)
                curr_y += 60; draw_remove_option(self, curr_y, self.t(" - Remove |GREEN| GREEN |WHITE| power", " - Eliminar poder |GREEN| VERDE"), self.remove_power_green, self.remove_power_green_rect, self.remove_power_green_text_rect, active_color=GREEN, offset=off, surface=surface)
                curr_y += 60; draw_remove_option(self, curr_y, self.t(" - Remove |YELLOW| YELLOW |WHITE| power", " - Eliminar poder |YELLOW| AMARILLO"), self.remove_power_yellow, self.remove_power_yellow_rect, self.remove_power_yellow_text_rect, active_color=YELLOW, offset=off, surface=surface)
                curr_y += 60; draw_remove_option(self, curr_y, self.t(" - Remove |ORANGE| ORANGE |WHITE| power", " - Eliminar poder |ORANGE| NARANJA"), self.remove_power_orange, self.remove_power_orange_rect, self.remove_power_orange_text_rect, active_color=ORANGE, offset=off, surface=surface)

            self.max_y_rendered = curr_y

        elif self.modifiers_tab == "EXTRAS":
            self._draw_extras_content(100, off, lm, ox, surface)
            # max_y_rendered se actualiza dentro de _draw_extras_content

        elif self.modifiers_tab == "SKINS":
            curr_y = 100
            draw_rich_text(surface, self.t("Change |ORANGE| ORANGE |WHITE| power:", "Cambiar poder |ORANGE| NARANJA:"), (lm, self.modifiers_panel_rect.y + curr_y - off), self.small_font)
            self.orange_skin_rect.update(ox, self.modifiers_panel_rect.y + curr_y - 5 - off, 130, 40)
            pygame.draw.rect(surface, BLACK, self.orange_skin_rect); pygame.draw.rect(surface, WHITE, self.orange_skin_rect, 2)
            skin_name = self.orange_skin_options[self.orange_skin_idx]
            # HADOUKEN no se traduce, Default -> Normal
            display_name = self.t(skin_name, "Normal" if skin_name == "Default" else skin_name)
            skin_color = WHITE if skin_name == "Default" else CYAN
            st = self.small_font.render(display_name, True, skin_color)
            surface.blit(st, st.get_rect(center=self.orange_skin_rect.center))
            
            curr_y += 80
            draw_rich_text(surface, self.t("Change |YELLOW| YELLOW |WHITE| watch:", "Cambiar reloj |YELLOW| AMARILLO:"), (lm, self.modifiers_panel_rect.y + curr_y - off), self.small_font)
            self.yellow_watch_skin_rect.update(ox, self.modifiers_panel_rect.y + curr_y - 5 - off, 130, 40)
            pygame.draw.rect(surface, BLACK, self.yellow_watch_skin_rect); pygame.draw.rect(surface, WHITE, self.yellow_watch_skin_rect, 2)
            y_skin_name = self.yellow_watch_skin_options[self.yellow_watch_skin_idx]
            # CROSS -> CRUZ, Default -> Normal
            y_display_name = self.t(y_skin_name, "CRUZ" if y_skin_name == "CROSS" else ("Normal" if y_skin_name == "Default" else y_skin_name))
            y_skin_color = WHITE if y_skin_name == "Default" else BROWN
            st2 = self.small_font.render(y_display_name, True, y_skin_color)
            surface.blit(st2, st2.get_rect(center=self.yellow_watch_skin_rect.center))

            curr_y += 80
            draw_rich_text(surface, self.t("Change BALL skin:", "Cambiar aspecto PELOTA:"), (lm, self.modifiers_panel_rect.y + curr_y - off), self.small_font)
            self.ball_skin_rect.update(ox, self.modifiers_panel_rect.y + curr_y - 5 - off, 130, 40)
            pygame.draw.rect(surface, BLACK, self.ball_skin_rect); pygame.draw.rect(surface, WHITE, self.ball_skin_rect, 2)
            b_skin_name = self.ball_skin_options[self.ball_skin_idx]
            b_map = {"Default": "Clásica", "Fireball": "Fuego", "Neon": "Neón", "CHEESE": "QUESO"}
            b_display_name = self.t(b_skin_name, b_map.get(b_skin_name, b_skin_name))
            b_skin_color = WHITE if b_skin_name == "Default" else (YELLOW if b_skin_name == "CHEESE" else GREEN)
            st3 = self.small_font.render(b_display_name, True, b_skin_color)
            surface.blit(st3, st3.get_rect(center=self.ball_skin_rect.center))
            
            self.max_y_rendered = curr_y + 40

        # Update scroll limits
        self.max_scroll = max(0, self.max_y_rendered + 60 - 330)
        self.scroll_y = max(0, min(self.scroll_y, self.max_scroll))

    def _draw_extras_content(self, start_y, off, lm, ox, surface):
        cy = start_y
        mpos = pygame.mouse.get_pos()
        active_tooltip = None
        
        draw_remove_option(self, cy, self.t("Enable |ORANGE| ORANGE |WHITE| watch", "Activar reloj |ORANGE| NARANJA"), self.orange_watch_enabled, self.orange_watch_rect, self.orange_watch_text_rect, active_color=ORANGE, offset=off, surface=surface)
        cy += 60; draw_remove_option(self, cy, self.t("Enable |GOLD|X2 MULTIPLIER |WHITE|at start", "Activar |GOLD|MULTIPLICADOR X2 |WHITE|al inicio"), self.start_x2_enabled, self.start_x2_rect, self.start_x2_text_rect, active_color=GOLD, offset=off, surface=surface)
        cy += 60; draw_remove_option(self, cy, self.t("Enable |BLUE|MAG|RED|NET|WHITE| power", "Activar poder |BLUE|MAG|RED|NET"), self.magnet_power_enabled, self.magnet_power_rect, self.magnet_power_text_rect, active_color=GRAY, offset=off, surface=surface)
        cy += 60; draw_remove_option(self, cy, self.t("Enable |GHOST| GHOST |WHITE| power", "Activar poder |GHOST| FANTASMA"), self.ghost_power_enabled, self.ghost_power_rect, self.ghost_power_text_rect, active_color=GHOST_COLOR, offset=off, surface=surface)
        if self.ghost_power_enabled:
            cy += 60; draw_remove_option(self, cy, self.t(" - |CYAN|Identical |WHITE|ball", " - Pelota |CYAN|idéntica"), self.ghost_identical_enabled, self.ghost_identical_rect, self.ghost_identical_text_rect, active_color=CYAN, offset=off, surface=surface)
        cy += 60; draw_remove_option(self, cy, self.t("Enable |GUM_PINK|GUM|WHITE| power", "Activar poder de |GUM_PINK|CHICLE"), self.gum_power_enabled, self.gum_power_rect, self.gum_power_text_rect, active_color=GUM_PINK, offset=off, surface=surface)
        if self.gum_power_rect.collidepoint(mpos) or self.gum_power_text_rect.collidepoint(mpos):
            if self.language == "EN":
                active_tooltip = ["Paddles turn pink. Balls stick automatically.", "Sticking consumes 1 charge per second.", "Press power key to shoot a giant gum ball."]
            else:
                active_tooltip = ["Las paletas se vuelven rosas. Las pelotas se pegan solas.", "Estar pegado consume 1 carga por segundo.", "Usa el botón de poder para tirar un chicle gigante."]
        cy += 60; draw_remove_option(self, cy, self.t("|GOLD|GOLDEN |WHITE|GOAL rule", "|GOLD|GOL DE ORO |WHITE|(Regla)"), self.experimental_golden_goal, self.experimental_golden_goal_rect, self.experimental_golden_goal_text_rect, active_color=GOLD, offset=off, surface=surface)
        cy += 60; draw_remove_option(self, cy, self.t("Allow floating planets", "Activar planetas flotantes"), self.floating_planets_enabled, self.floating_planets_rect, self.floating_planets_text_rect, active_color=CYAN, offset=off, surface=surface)
        if self.floating_planets_enabled:
            cy += 60; self._draw_sub_selector(cy, self.t("Gravity:", "Fuerza de gravedad:"), self.gravity_force_names[self.gravity_force_idx], self.gravity_force_rect, off, ox, lm, surface, sub_val=self.gravity_force_options[self.gravity_force_idx])
            cy += 60; self._draw_sub_selector(cy, self.t("Gravity Radius:", "Radio de gravedad:"), self.gravity_radius_names[self.gravity_radius_idx], self.gravity_radius_rect, off, ox, lm, surface, sub_val=str(self.gravity_radius_options[self.gravity_radius_idx]))
            cy += 60; draw_remove_option(self, cy, self.t("Destructible planets", "Planetas destructibles"), self.destructible_planets_enabled, self.destructible_planets_rect, self.destructible_planets_text_rect, active_color=RED, offset=off, surface=surface)
            if self.destructible_planets_enabled:
                cy += 60; self._draw_sub_selector(cy, self.t("Planet resistance:", "Resistencia:"), self.planet_resistance_names[self.planet_resistance_idx], self.planet_resistance_rect, off, ox, lm, surface, sub_val=str(self.planet_resistance_options[self.planet_resistance_idx]))
        
        cy += 60; draw_remove_option(self, cy, self.t("Dimensional |BLUE|POR|RED|TALS", "|BLUE|POR|RED|TALES |WHITE|Dimensionales"), self.portals_enabled, self.portals_rect, self.portals_text_rect, active_color=CYAN, offset=off, surface=surface)
        if self.portals_text_rect.collidepoint(mpos):
            active_tooltip = ["Teleport balls between Blue and Orange PORTALS."]

        if self.portals_enabled:
            cy += 60; self._draw_sub_selector(cy, self.t("PORTAL size:", "Tamaño del PORTAL:"), self.portal_size_names[self.portal_size_idx], self.portal_size_rect, off, ox, lm, surface, sub_val=str(self.portal_size_options[self.portal_size_idx]), text_rect=self.portal_size_text_rect)
            if self.portal_size_text_rect.collidepoint(mpos):
                active_tooltip = ["Change the length of the PORTALS."]

            cy += 60; draw_remove_option(self, cy, self.t("Vertical PORTALS", "PORTALES Verticales"), self.portals_vertical, self.portals_vertical_rect, self.portals_vertical_text_rect, active_color=BLUE, offset=off, surface=surface)
            if self.portals_vertical_text_rect.collidepoint(mpos):
                active_tooltip = ["Flip PORTALS to vertical orientation on the side walls."]
            cy += 60; draw_remove_option(self, cy, self.t("2 more |RED|POR|GREEN|TALS", "2 |RED|POR|GREEN|TALES |WHITE|más"), self.more_portals_enabled, self.more_portals_rect, self.more_portals_text_rect, active_color=BLUE, offset=off, surface=surface)
            if self.more_portals_text_rect.collidepoint(mpos):
                active_tooltip = ["Add RED and GREEN PORTALS (Cross-connection)."]
                
        cy += 60; draw_remove_option(self, cy, self.t("Intrusive Mouse", "Ratón Intruso"), self.add_mouse_enabled, self.add_mouse_rect, self.add_mouse_text_rect, active_color=BROWN, offset=off, surface=surface)
        if self.add_mouse_enabled:
            cy += 60; self._draw_sub_selector(cy, self.t("Mouse speed:", "Velocidad de ratón:"), self.mouse_speed_names[self.mouse_speed_idx], self.mouse_speed_rect, off, ox, lm, surface, sub_val=str(self.mouse_speed_options[self.mouse_speed_idx]))
            cy += 60; self._draw_sub_selector(cy, self.t("Mouse appear time:", "Tiempo aparición:"), self.mouse_appear_names[self.mouse_appear_idx], self.mouse_appear_rect, off, ox, lm, surface, sub_val=f"{self.mouse_appear_options[self.mouse_appear_idx]}s")
        
        cy += 60; draw_remove_option(self, cy, self.t("Enable |GRAY|REVOLVER|WHITE| power", "Activar poder de |GRAY|REVOLVER"), self.revolver_enabled, self.revolver_rect, self.revolver_text_rect, active_color=GUN_METAL, offset=off, surface=surface)
        if self.revolver_rect.collidepoint(mpos) or self.revolver_text_rect.collidepoint(mpos):
            if self.language == "EN":
                active_tooltip = ["Orbital item. Grants a 6-shooter (3 shots for balance).", "Yellow bullets travel at 2x speed.", "Hits are LETHAL to the opponent.", "Bullets go through and disappear if they miss."]
            else:
                active_tooltip = ["Ítem orbital. Otorga un revólver de 3 tiros.", "Las balas amarillas van a velocidad x2.", "Los impactos son LETALES para el oponente.", "Las balas siguen de largo si fallas."]
        
        self.max_y_rendered = cy + 40
        
        # Dibujamos el tooltip al FINAL para que esté por encima de todo
        if active_tooltip:
            from ui_components import draw_tooltip
            draw_tooltip(self, active_tooltip, surface)

    def _draw_sub_selector(self, curr_y, label, val_name, rect, off, ox, lm, surface, sub_val=None, text_rect=None):
        draw_rich_text(surface, label, (lm, self.modifiers_panel_rect.y + curr_y - off), self.small_font)
        rect.update(ox, self.modifiers_panel_rect.y + curr_y - 5 - off, 130, 40)
        pygame.draw.rect(surface, BLACK, rect); pygame.draw.rect(surface, WHITE, rect, 2)
        
        translations = {
            "None": "Ninguno", "Low": "Bajo", "Medium": "Medio", "High": "Alto", "Extreme": "Extremo",
            "Minion": "Minion", "Short": "Pequeño", "Default": "Normal", "Big": "Grande", "Giant": "Gigante",
            "Slow": "Lento", "Normal": "Normal", "Fast": "Rápido", "Sonic": "Sónico",
            "Moon": "Luna", "Planet": "Planeta", "Gas Giant": "Gigante Gaseoso", "Star": "Estrella",
            "CHEESE": "QUESO", "EARTH": "TIERRA"
        }
        translated_name = translations.get(val_name, val_name) if self.language == "ES" else val_name
        
        color = WHITE
        if val_name == "Moon": color = (180, 180, 180)
        elif val_name == "Planet": color = BROWN
        elif val_name == "Gas Giant": color = (100, 200, 255)
        elif val_name == "Star": color = YELLOW
        
        # Auto-encogimiento para nombres largos
        f_to_use = self.small_font
        if f_to_use.size(translated_name)[0] > rect.width - 10:
            f_to_use = self.tiny_font
            
        st = f_to_use.render(translated_name, True, color)
        surface.blit(st, st.get_rect(center=rect.center))
        if sub_val:
            ss = self.tiny_font.render(str(sub_val), True, GRAY)
            surface.blit(ss, (rect.right + 10, rect.centery - ss.get_height()//2))

    def _draw_tooltips(self, clip, surface):
        m = pygame.mouse.get_pos()
        if not clip.collidepoint(m): return
        
    def _draw_tooltips(self, clip, surface):
        m = pygame.mouse.get_pos()
        if not clip.collidepoint(m): return
        
        # Construir la lista de áreas según la pestaña activa
        areas = []
        
        if self.modifiers_tab == "ALL":
            areas = [
                (self.match_point_text_rect, "match_point"),
                (self.golden_goal_anim_text_rect, "golden_goal_anim"),
                (self.reroll_text_rect, "reroll"),
                (self.equal_watches_text_rect, "equal_watches"),
                (self.equal_powers_text_rect, "equal_powers"),
                (self.watches_kept_text_rect, "watches_kept"),
                (self.watch_spawn_hits_text_rect, "watch_spawn"),
                (self.power_auto_grant_hits_text_rect, "power_spawn"),
                (self.start_with_power_text_rect, "start_with_power"),
                (self.encapsulate_powers_text_rect, "encapsulate_powers")
            ]
        elif self.modifiers_tab == "EXTRAS":
            areas = [
                (self.remove_watches_toggle_text_rect, "remove_power_menu"),
                (self.orange_watch_text_rect, "orange_watch"),
                (self.magnet_power_text_rect, "magnet_power"),
                (self.ghost_power_text_rect, "ghost_power"),
                (self.experimental_golden_goal_text_rect, "exp_golden_goal"),
                (self.floating_planets_text_rect, "floating_planets"),
                (self.gravity_force_rect, "gravity_force"),
                (self.gravity_radius_rect, "gravity_radius"),
                (self.destructible_planets_text_rect, "destructible_planets"),
                (self.planet_resistance_rect, "planet_resistance"),
                (self.portals_text_rect, "portals"),
                (self.portal_size_rect, "portal_size"),
                (self.portals_vertical_text_rect, "portals_vertical"),
                (self.more_portals_text_rect, "more_portals"),
                (self.add_mouse_text_rect, "add_mouse")
            ]
        
        lines = []
        for rect, key in areas:
            if rect.collidepoint(m):
                lang_dict = assets.TOOLTIPS.get(self.language, assets.TOOLTIPS["EN"])
                lines = lang_dict.get(key, [])
                break
                
        draw_tooltip(self, lines, surface=surface)

    def _draw_game_over(self, surface):
        # Fondo oscuro semi-transparente
        ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        ov.set_alpha(180)
        ov.fill(BLACK)
        surface.blit(ov, (0,0))
        
        lines = self.winner_text.split("\n")
        for i, line in enumerate(lines):
            if "|" in line:
                # Calcular ancho real ignorando las etiquetas |TAG|
                import re
                clean_txt = re.sub(r'\|[^|]*\|', '', line)
                tw = self.tiny_font.render(clean_txt, True, WHITE).get_width()
                draw_rich_text(surface, line, (SCREEN_WIDTH//2 - tw//2, SCREEN_HEIGHT//3 + 60), self.tiny_font)
            else:
                f = self.large_font if i == 0 else self.font
                color = GOLD if i == 0 else WHITE
                txt = f.render(line, True, color)
                surface.blit(txt, txt.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//3 + i*60)))

        # Botones
        self.btn_gameover_restart.update(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 40, 300, 50)
        self.btn_gameover_menu.update(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 105, 300, 50)
        
        btn_labels = [
            (self.btn_gameover_restart, self.t("Restart Game", "Reiniciar Juego")),
            (self.btn_gameover_menu, self.t("Back to Menu", "Volver al Menú"))
        ]
        
        mpos = pygame.mouse.get_pos()
        for r, txt in btn_labels:
            is_hover = r.collidepoint(mpos)
            b_col = (40, 40, 40) if is_hover else BLACK
            s_col = GOLD if is_hover else WHITE
            pygame.draw.rect(surface, b_col, r)
            pygame.draw.rect(surface, s_col, r, 3)
            
            # Lógica de auto-encogimiento para el menú principal
            f_to_use = self.font
            if f_to_use.size(txt)[0] > r.width - 20:
                f_to_use = self.small_font
                
            st = f_to_use.render(txt, True, WHITE)
            surface.blit(st, st.get_rect(center=r.center))

    def _draw_settings(self, surface):
        pygame.draw.rect(surface, BLACK, self.modifiers_panel_rect); pygame.draw.rect(surface, WHITE, self.modifiers_panel_rect, 4)
        
        # Título bilingüe
        title = "SETTINGS" if self.language == "EN" else "AJUSTES"
        t = self.font.render(title, True, WHITE)
        surface.blit(t, t.get_rect(center=(SCREEN_WIDTH//2, self.modifiers_panel_rect.y+40)))
        
        lm = self.modifiers_panel_rect.x + 100
        ox = self.modifiers_panel_rect.centerx + 50
        cy = self.modifiers_panel_rect.y + 120
        
        # 1. Idioma
        label_lang = "Language / Idioma"
        draw_rich_text(surface, label_lang, (lm, cy), self.small_font)
        self.lang_rect.update(ox, cy - 5, 130, 40)
        pygame.draw.rect(surface, BLACK, self.lang_rect); pygame.draw.rect(surface, WHITE, self.lang_rect, 2)
        txt_lang = "ESPAÑOL" if self.language == "ES" else "ENGLISH"
        st = self.small_font.render(txt_lang, True, YELLOW)
        surface.blit(st, st.get_rect(center=self.lang_rect.center))
        
        # 2. VFX
        cy += 80
        label_vfx = "Visual Effects" if self.language == "EN" else "Efectos Visuales"
        draw_rich_text(surface, f"{label_vfx}:", (lm, cy), self.small_font)
        self.vfx_rect.update(ox + 50, cy - 5, 30, 30)
        pygame.draw.rect(surface, BLACK, self.vfx_rect); pygame.draw.rect(surface, WHITE, self.vfx_rect, 2)
        if self.vfx_enabled: pygame.draw.rect(surface, GREEN, self.vfx_rect.inflate(-10, -10))
        
        # 3. VOLUME
        cy += 80
        label_vol = "Volume" if self.language == "EN" else "Volumen"
        draw_rich_text(surface, f"{label_vol}:", (lm, cy), self.small_font)
        
        # Dibujar barra
        self.volume_bar_rect.update(ox, cy + 10, 200, 10)
        pygame.draw.rect(surface, GRAY, self.volume_bar_rect)
        pygame.draw.rect(surface, WHITE, self.volume_bar_rect, 1)
        
        # Dibujar handle (basado en self.sfx_volume)
        handle_x = self.volume_bar_rect.x + (self.sfx_volume * self.volume_bar_rect.width)
        self.volume_handle_rect.center = (handle_x, self.volume_bar_rect.centery)
        pygame.draw.rect(surface, WHITE, self.volume_handle_rect)
        
        # Porcentaje
        pct_txt = f"{int(self.sfx_volume * 100)}%"
        pst = self.tiny_font.render(pct_txt, True, WHITE)
        surface.blit(pst, (self.volume_bar_rect.right + 15, cy + 5))
        
        # 4. Shake
        cy += 80
        label_shake = "Screen Shake" if self.language == "EN" else "Temblor de Pantalla"
        draw_rich_text(surface, f"{label_shake}:", (lm, cy), self.small_font)
        self.shake_rect.update(ox + 50, cy - 5, 30, 30)
        pygame.draw.rect(surface, BLACK, self.shake_rect); pygame.draw.rect(surface, WHITE, self.shake_rect, 2)
        if self.shake_enabled: pygame.draw.rect(surface, GREEN, self.shake_rect.inflate(-10, -10))
        
        # 1. Botón BACK (Esquina superior derecha del panel)
        self.settings_back_btn_rect.update(self.modifiers_panel_rect.right - 100, self.modifiers_panel_rect.y + 20, 80, 40)
        pygame.draw.rect(surface, BLACK, self.settings_back_btn_rect); pygame.draw.rect(surface, WHITE, self.settings_back_btn_rect, 2)
        back_txt = self.t("BACK", "VOLVER")
        bt = self.tiny_font.render(back_txt, True, WHITE)
        surface.blit(bt, bt.get_rect(center=self.settings_back_btn_rect.center))

        # 2. Botón APPLY (Centro abajo del panel)
        self.settings_apply_btn_rect.update(SCREEN_WIDTH//2 - 65, self.modifiers_panel_rect.bottom - 60, 130, 45)
        pygame.draw.rect(surface, (0, 100, 0), self.settings_apply_btn_rect) # Verde oscuro para Aplicar
        pygame.draw.rect(surface, WHITE, self.settings_apply_btn_rect, 2)
        apply_txt = self.t("APPLY", "APLICAR")
        at = self.small_font.render(apply_txt, True, WHITE)
        surface.blit(at, at.get_rect(center=self.settings_apply_btn_rect.center))

    def run(self):
        try:
            while True:
                dt = self.clock.tick(FPS) / 1000.0
                self.handle_input(dt)
                self.update(dt)
                self.draw()
        except Exception as e:
            import traceback
            print(f"CRASH DETECTADO: {e}")
            traceback.print_exc()
            pygame.quit()
