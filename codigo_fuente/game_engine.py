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
from menu_manager import MenuManager
from ai_controller import AIController
from physics_engine import PhysicsEngine
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
        self.menus = MenuManager(self)
        self.ai_controller = AIController(self)
        self.physics = PhysicsEngine(self)
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
        
        # Sub-modificador: Probabilidad de aparición
        self.revolver_prob_options = [0.1, 0.25, 0.5, 1.0]
        self.revolver_prob_names = ["Low (10%)", "Default (25%)", "Quite (50%)", "Always (100%)"]
        self.revolver_prob_idx = 1
        self.revolver_prob_rect = pygame.Rect(0,0,220,40)
        self.revolver_prob_text_rect = pygame.Rect(0,0,0,0)
        
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
        elif self.revolver_enabled and self.revolver_prob_rect.collidepoint(event.pos):
            self.audio.play('pop'); self.revolver_prob_idx = (self.revolver_prob_idx + 1) % len(self.revolver_prob_options)
        
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
        # Delegado al PhysicsEngine.update()
        pass


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
            
            # Reloj Púrpura (Efecto especial: Poder cada 3 toques)
            current_z = (self.p1_zone_type if paddle == self.paddle1 else self.p2_zone_type) if self.watches_kept_enabled else self.zone_type
            is_purple = (current_z == 4)
            
            if is_purple:
                if paddle.hits >= 3:
                    paddle.grant_random_power(self)
                    paddle.hits = 0
            elif paddle.hits >= req:
                paddle.grant_random_power(self)
                paddle.hits = 0

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
                # Chance dinámica de Revólver al salir un reloj
                prob = self.revolver_prob_options[self.revolver_prob_idx]
                if self.revolver_enabled and not self.revolver_item_active and random.random() < prob:
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
                # 1. Activar poderes automáticamente (Delegado a ai_controller si se quiere, 
                # pero mantenemos la lógica de activación rápida aquí por ahora para no complicar el AIController)
                if self.paddle2.power_stored != POWER_NONE:
                    if self.paddle2.power_stored == POWER_GHOST:
                        if abs(self.paddle1.rect.centery - SCREEN_HEIGHT // 2) > 100 or random.random() < 0.01:
                            self.activate_paddle_power(self.paddle2, 2)
                    elif self.paddle2.power_stored == POWER_MAGNET:
                        if self.paddle1.power_active != POWER_ORANGE:
                            self.activate_paddle_power(self.paddle2, 2)
                    else:
                        self.activate_paddle_power(self.paddle2, 2)
                
                self.ai_controller.update(dt)

            # Actualizar Paletas y Timers
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

            # Actualizar Proyectiles de Chicle
            for gp in self.gum_projectiles[:]:
                gp.update(dt)
                if not gp.active:
                    self.gum_projectiles.remove(gp)

            # --- FÍSICAS CENTRALIZADAS ---
            self.physics.update(dt)

            # Lógica post-física (VFX, imanes visuales, etc.)
            for ball in self.balls[:]:
                # Imanes visuales (color azul)
                in_p1 = ball.rect.centerx < SCREEN_WIDTH // 2
                for i, p in enumerate([self.paddle1, self.paddle2]):
                    side = (i == 0 and in_p1) or (i == 1 and not in_p1)
                    if p.power_active == POWER_MAGNET and side:
                        self.physics.apply_magnet_force(p, dt, ball)
                    elif ball.color == (100, 200, 255) and not ball.is_fireball and not ball.is_orange and not ball.is_ghost:
                        self.reset_ball_visuals(ball)
                
                # Rastro Hadouken
                if ball == self.balls[0] and ball.is_orange and self.orange_skin_idx == 1:
                    self.vfx.trail(ball.rect.centerx, ball.rect.centery, (100, 200, 255))

            # --- LÓGICA DE ÍTEM REVÓLVER (ÓRBITA) ---
            if self.revolver_enabled and self.revolver_item_active:
                self.revolver_angle += dt * 1.5 
                center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
                rx = center_x + math.cos(self.revolver_angle) * self.revolver_orbit_radius
                ry = center_y + math.sin(self.revolver_angle) * self.revolver_orbit_radius
                self.revolver_item_rect = pygame.Rect(rx - 15, ry - 15, 30, 30)
                
                # Colisión con pelota
                for ball in self.balls:
                    if ball.rect.colliderect(self.revolver_item_rect):
                        self.revolver_item_active = False
                        self.revolver_item_rect = None
                        self.audio.play('speed') 
                        target_p = self.paddle1 if self.last_hitter == 1 else self.paddle2
                        target_p.power_stored = POWER_REVOLVER
                        target_p.color = GUN_METAL
                        self.global_hits = 0 
                        break

    def _get_zone_multiplier(self, ball):
        in_p1 = ball.rect.centerx < SCREEN_WIDTH // 2
        z_type = (self.p1_zone_type if in_p1 else self.p2_zone_type) if self.watches_kept_enabled else (self.zone_type if ((self.slow_zone_owner == 1 and in_p1) or (self.slow_zone_owner == 2 and not in_p1)) else 0)
        return 0.5 if z_type == 1 else (1.25 if z_type == 2 else 1.0)



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
            
        if self.state == STATE_MAIN_MENU: self.menus.draw_main_menu(temp_surf)
        elif self.state == STATE_MODIFIERS: self.menus.draw_modifiers(temp_surf)
        elif self.state == STATE_SETTINGS: self.menus.draw_settings(temp_surf)
        elif self.state == STATE_MODE_SELECTION: self.menus.draw_mode_selection(temp_surf)
        elif self.state == STATE_GAME_OVER: self.menus.draw_game_over(temp_surf)
        
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
        tw = t1.get_width() + t2.get_width()
        sx, sy = SCREEN_WIDTH//2 - tw//2, SCREEN_HEIGHT//2 - t1.get_height()//2
        surface.blit(t1, (sx, sy)); surface.blit(t2, (sx + t1.get_width(), sy))

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
