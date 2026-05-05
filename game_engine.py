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
        pygame.display.set_caption("Pong Kombat v0.3.3")
        
        self.clock = pygame.time.Clock()
        self.audio = AudioManager()
        self.vfx = VFXManager()
        self.init_fonts()
        self.init_entities()
        self.init_game_state()
        self.init_modifier_variables()

    def init_fonts(self):
        self.font = pygame.font.SysFont("Arial", 36, bold=True)
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
        self.hourglass_rect = None
        self.hourglass_type = 0
        self.zone_type = 0
        self.slow_zone_owner = 0
        self.last_hitter = 0
        self.wall_sound_cooldown = 0.0
        
        # Screen Shake
        self.shake_amount = 0
        self.shake_timer = 0

    def init_modifier_variables(self):
        # Botones y Paneles
        self.btn_play_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 40, 300, 80)
        self.btn_modifiers_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 60, 300, 80)
        
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
        self.tab_all_rect = pygame.Rect(0, 0, 90, 45)
        self.tab_extras_rect = pygame.Rect(0, 0, 110, 45)
        self.tab_skins_rect = pygame.Rect(0, 0, 110, 45)

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
        self.magnet_power_enabled = False
        self.magnet_power_rect = pygame.Rect(0,0,30,30)
        self.magnet_power_text_rect = pygame.Rect(0,0,0,0)
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
                if event.button == 1: self.is_dragging_scrollbar = False
                    
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
                self.state = STATE_PRESS_TO_START
            elif self.btn_modifiers_rect.collidepoint(event.pos):
                self.audio.play('hit')
                self.state = STATE_MODIFIERS
        
        elif self.state == STATE_MODIFIERS:
            if self.scrollbar_thumb_rect.collidepoint(event.pos):
                self.is_dragging_scrollbar = True
                self.scroll_offset_y = event.pos[1] - self.scrollbar_thumb_rect.y
            elif self.back_btn_rect.collidepoint(event.pos):
                self.audio.play('pop'); self.state = STATE_MAIN_MENU; self.scroll_y = 0
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
                if event.pos[1] > self.modifiers_panel_rect.top + 60:
                    self._handle_modifier_clicks(event)
                    # Recalcular max_scroll tras abrir/cerrar acordeones
                    self.max_scroll = max(0, self.max_y_rendered + 60 - 330)
                    self.scroll_y = min(self.scroll_y, self.max_scroll)
        
        elif self.state == STATE_GAME_OVER:
            if self.btn_gameover_restart.collidepoint(event.pos):
                self.audio.play('hit'); self.reset_game()
            elif self.btn_gameover_menu.collidepoint(event.pos):
                self.audio.play('hit'); self.reset_game(); self.state = STATE_MAIN_MENU

    def _handle_modifier_clicks(self, event):
        if self.modifiers_tab == "SKINS":
            if self.orange_skin_rect.collidepoint(event.pos):
                self.audio.play('pop'); self.orange_skin_idx = (self.orange_skin_idx + 1) % len(self.orange_skin_options)
            elif self.yellow_watch_skin_rect.collidepoint(event.pos):
                self.audio.play('pop'); self.yellow_watch_skin_idx = (self.yellow_watch_skin_idx + 1) % len(self.yellow_watch_skin_options)
            elif self.ball_skin_rect.collidepoint(event.pos):
                self.audio.play('pop'); self.ball_skin_idx = (self.ball_skin_idx + 1) % len(self.ball_skin_options)
        
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
        if self.state == STATE_MODIFIERS and self.is_dragging_scrollbar:
            new_y = event.pos[1] - self.scroll_offset_y
            limit_bottom = self.scrollbar_rect.bottom - self.scrollbar_thumb_height
            self.scrollbar_thumb_rect.y = max(self.scrollbar_rect.top, min(new_y, limit_bottom))
            
            scroll_fraction = (self.scrollbar_thumb_rect.y - self.scrollbar_rect.top) / (self.scrollbar_rect.height - self.scrollbar_thumb_height)
            self.scroll_y = scroll_fraction * self.max_scroll

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
            if ball.is_ghost:
                if ball.ghost_owner == 2: self.goal_scored(2)
                if ball in self.balls: self.balls.remove(ball)
            elif ball.is_orange: self._handle_orange_bounce(True, ball)
            elif self.paddle1.has_extra_life: self._handle_extra_life_save(True, ball)
            else: self.goal_scored(2)
        elif ball.rect.left > SCREEN_WIDTH:
            if ball.is_ghost:
                if ball.ghost_owner == 1: self.goal_scored(1)
                if ball in self.balls: self.balls.remove(ball)
            elif ball.is_orange: self._handle_orange_bounce(False, ball)
            elif self.paddle2.has_extra_life: self._handle_extra_life_save(False, ball)
            else: self.goal_scored(1)

        # 6. Paletas
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
        if ball.is_orange:
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
                self.global_hits = 0; self.spawn_random_watch()

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
        if paddle.power_stored == POWER_GHOST:
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
            msg = f"PLAYER {player} WINS!\n|YELLOW|(Player {player} won by GOLDEN Goal rule)"
            if player == 1: self.score1 = self.max_score; self.winner_text = msg
            else: self.score2 = self.max_score; self.winner_text = msg
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
                msg = f"PLAYER {winner} WINS!"
                if self.match_point_enabled:
                    msg += f"\n|YELLOW|(Player {winner} won by MATCH POINT rule)"
                self.state = STATE_GAME_OVER; self.winner_text = msg; return

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
        
        # Prioridad 1: Golden Goal (Muerte súbita natural o forzada por modificador)
        # Se activa si: a) Salió por azar (is_golden_goal_round) 
        # o b) Ambos están a 1 punto de ganar (Sudden Death) Y el modificador está ON
        is_at_final_point = (self.score1 == self.max_score-1 and self.score2 == self.max_score-1)
        
        if self.is_golden_goal_round or (is_at_final_point and self.experimental_golden_goal):
            print("!!! GOLDEN GOAL ANNOUNCEMENT !!!")
            self.show_golden_goal_anim = True
            self.golden_goal_anim_timer = 2.5
            self.serve_timer = 3.0
            self.audio.play('golden_goal')
            return

        # Prioridad 2: Match Point (Solo si no hay Golden Goal prioritario)
        if self.match_point_enabled:
            pts1, pts2 = max(self.max_score, self.score2+2)-self.score1, max(self.max_score, self.score1+2)-self.score2
            if pts1 == 1 or pts2 == 1:
                self.show_match_point_anim = True
                self.match_point_anim_timer = 2.5
                self.serve_timer = 3.0
                self.audio.play('match_point')
                return
        
        # Caso especial: Sudden Death natural (sin modificador Golden Goal activo)
        if is_at_final_point and not self.match_point_enabled:
            self.show_golden_goal_anim = True
            self.golden_goal_anim_timer = 2.5
            self.serve_timer = 3.0
            self.audio.play('golden_goal')

    def update(self, dt):
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
                        if self.mouse.rect.colliderect(ball.rect):
                            self.audio.play('nom')
                            # Penalizar al último que la tocó
                            p_responsible = self.last_hitter
                            if p_responsible == 1:
                                if self.score1 > 0: 
                                    self.score1 -= 1
                                    if ball in self.balls: self.balls.remove(ball)
                                    self.mouse = None
                                    self.mouse_hits_counter = 0
                                    if not self.balls:
                                        self._reset_round_state()
                                        self.state = STATE_SERVE
                                        self.serve_timer = 1.75
                                        self.serve_direction = random.choice([-1, 1])
                                        self.balls = [Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
                                        speed = 300 * self.initial_ball_speed_options[self.initial_ball_speed_idx]
                                        self.balls[0].serve(self.serve_direction, speed)
                                else: 
                                    # Caso 0 puntos: punto al rival (usamos point_scored para activar MATCH POINT)
                                    if ball in self.balls: self.balls.remove(ball)
                                    self.mouse = None
                                    self.mouse_hits_counter = 0
                                    self.point_scored(2, 1)
                            else:
                                if self.score2 > 0: 
                                    self.score2 -= 1
                                    if ball in self.balls: self.balls.remove(ball)
                                    self.mouse = None
                                    self.mouse_hits_counter = 0
                                    if not self.balls:
                                        self._reset_round_state()
                                        self.state = STATE_SERVE
                                        self.serve_timer = 1.75
                                        self.serve_direction = random.choice([-1, 1])
                                        self.balls = [Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
                                        speed = 300 * self.initial_ball_speed_options[self.initial_ball_speed_idx]
                                        self.balls[0].serve(self.serve_direction, speed)
                                else: 
                                    # Caso 0 puntos: punto al rival
                                    if ball in self.balls: self.balls.remove(ball)
                                    self.mouse = None
                                    self.mouse_hits_counter = 0
                                    self.point_scored(1, 1)
                            break

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
        if self.shake_timer > 0: self.shake_timer -= dt
            
        self.vfx.update(dt)

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
        ball.color = (100, 200, 255)

    def trigger_shake(self, amount, duration):
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
                        ball.draw(temp_surf, skin=self.ball_skin_options[self.ball_skin_idx])
                
                if self.mouse:
                    self.mouse.draw(temp_surf)
            elif self.state == STATE_PRESS_TO_START:
                t = self.font.render("Presiona ESPACIO para Sacar", True, WHITE)
                temp_surf.blit(t, t.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 100)))
            
            if self.is_x2_item_active: self._draw_x2_icon(temp_surf)
            self._draw_score(temp_surf)
            
        if self.state == STATE_MAIN_MENU: self._draw_main_menu(temp_surf)
        elif self.state == STATE_MODIFIERS: self._draw_modifiers(temp_surf)
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
        if self.paddle1.has_extra_life: pygame.draw.line(surface, YELLOW, (2, 0), (2, SCREEN_HEIGHT), 5)
        if self.paddle2.has_extra_life: pygame.draw.line(surface, YELLOW, (SCREEN_WIDTH-2, 0), (SCREEN_WIDTH-2, SCREEN_HEIGHT), 5)

    def _draw_dashed_line(self, surface, color, start, end, width, dash):
        x1, y1 = start; x2, y2 = end
        if x1 == x2:
            for y in range(y1, y2, dash*2): pygame.draw.line(surface, color, (x1, y), (x1, min(y+dash, y2)), width)
        else:
            for x in range(x1, x2, dash*2): pygame.draw.line(surface, color, (x, y1), (x+dash, y1), width)

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
        t1, t2, t3 = self.large_font.render("PONG ", True, WHITE), self.large_font.render("KOMBAT", True, RED), self.large_font.render(" 3.0", True, WHITE)
        tw = t1.get_width() + t2.get_width() + t3.get_width()
        sx, ty = SCREEN_WIDTH//2 - tw//2, SCREEN_HEIGHT//4
        surface.blit(t1, (sx, ty)); surface.blit(t2, (sx+t1.get_width(), ty)); surface.blit(t3, (sx+t1.get_width()+t2.get_width(), ty))
        for r, txt in [(self.btn_play_rect, "PLAY"), (self.btn_modifiers_rect, "MODIFIERS")]:
            pygame.draw.rect(surface, BLACK, r); pygame.draw.rect(surface, WHITE, r, 4)
            st = self.font.render(txt, True, WHITE); surface.blit(st, st.get_rect(center=r.center))

    def _draw_modifiers(self, surface):
        pygame.draw.rect(surface, BLACK, self.modifiers_panel_rect); pygame.draw.rect(surface, WHITE, self.modifiers_panel_rect, 4)
        t = self.font.render("MATCH MODIFIERS", True, WHITE); surface.blit(t, t.get_rect(center=(SCREEN_WIDTH//2, self.modifiers_panel_rect.y+30)))
        pygame.draw.rect(surface, BLACK, self.back_btn_rect); pygame.draw.rect(surface, WHITE, self.back_btn_rect, 2)
        bt = self.small_font.render("BACK", True, WHITE); surface.blit(bt, bt.get_rect(center=self.back_btn_rect.center))
        
        # Tabs
        tab_y = self.modifiers_panel_rect.top - 44
        self.tab_all_rect.topleft = (self.modifiers_panel_rect.left, tab_y)
        self.tab_extras_rect.topleft = (self.tab_all_rect.right + 5, tab_y)
        self.tab_skins_rect.topleft = (self.tab_extras_rect.right + 5, tab_y)
        for r, txt, bg in [(self.tab_all_rect, "ALL", (40,40,40) if self.modifiers_tab=="ALL" else BLACK), (self.tab_extras_rect, "EXTRAS", (0,80,0) if self.modifiers_tab=="EXTRAS" else (0,40,0)), (self.tab_skins_rect, "SKINS", (80,0,80) if self.modifiers_tab=="SKINS" else (40,0,40))]:
            pygame.draw.rect(surface, bg, r, border_top_left_radius=8, border_top_right_radius=8)
            pygame.draw.rect(surface, WHITE, r, 2, border_top_left_radius=8, border_top_right_radius=8)
            st = self.small_font.render(txt, True, WHITE); surface.blit(st, st.get_rect(center=r.center))
            
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
            surface.blit(self.small_font.render("Score limit:", True, WHITE), (lm, self.modifiers_panel_rect.y + curr_y - off))
            self.score_btn_rect.update(ox, self.modifiers_panel_rect.y + curr_y - 5 - off, 80, 40)
            pygame.draw.rect(surface, BLACK, self.score_btn_rect); pygame.draw.rect(surface, WHITE, self.score_btn_rect, 2)
            sv = self.small_font.render(str(self.max_score), True, WHITE); surface.blit(sv, sv.get_rect(center=self.score_btn_rect.center))
            
            inc_val = f"{self.ball_speed_multiplier_options[self.ball_speed_multiplier_idx]-1:g}"
            curr_y += 80; self._draw_sub_selector(curr_y, "Ball speed increase:", self.ball_speed_multiplier_names[self.ball_speed_multiplier_idx], self.ball_speed_btn_rect, off, ox, lm, surface, sub_val=inc_val)
            
            curr_y += 80
            self._draw_sub_selector(curr_y, "Initial ball speed:", self.initial_ball_speed_names[self.initial_ball_speed_idx], self.initial_ball_speed_rect, off, ox, lm, surface, sub_val=f"x{self.initial_ball_speed_options[self.initial_ball_speed_idx]}")
            
            curr_y += 80
            y_spd = f"{int(self.yellow_speed_up_options[self.yellow_speed_up_idx]*100)}%"
            self._draw_sub_selector(curr_y, "|YELLOW|Yellow |WHITE|Power Speed Up:", self.yellow_speed_up_names[self.yellow_speed_up_idx], self.yellow_speed_up_rect, off, ox, lm, surface, sub_val=y_spd)
            
            curr_y += 80; draw_remove_option(self, curr_y, "Numbers encapsulating powers", self.encapsulate_powers_enabled, self.encapsulate_powers_rect, self.encapsulate_powers_text_rect, active_color=CYAN, offset=off, surface=surface)
            
            curr_y += 80; draw_remove_option(self, curr_y, "MATCH POINT:", self.match_point_enabled, self.match_point_rect, self.match_point_text_rect, offset=off, surface=surface)
            curr_y += 80; draw_remove_option(self, curr_y, "|GOLD|GOLDEN |WHITE|Goal animation:", self.golden_goal_anim_enabled, self.golden_goal_anim_rect, self.golden_goal_anim_text_rect, offset=off, surface=surface)
            curr_y += 80; draw_remove_option(self, curr_y, "Re-rolls (|ORANGE|ORANGE|WHITE|/|YELLOW|YELLOW|WHITE|):", self.reroll_enabled, self.reroll_rect, self.reroll_text_rect, offset=off, surface=surface)
            if self.reroll_enabled: curr_y += 80; draw_remove_option(self, curr_y, "All Re-roll (|RED|RED|WHITE|/|GREEN|GREEN|WHITE|):", self.all_reroll_enabled, self.all_reroll_rect, self.all_reroll_text_rect, offset=off, surface=surface)
            curr_y += 80; draw_remove_option(self, curr_y, "Equal watches (20%):", self.equal_watches_enabled, self.equal_watches_rect, self.equal_watches_text_rect, offset=off, surface=surface)
            curr_y += 80; draw_remove_option(self, curr_y, "Equal powers (25%):", self.equal_powers_enabled, self.equal_powers_rect, self.equal_powers_text_rect, offset=off, surface=surface)
            curr_y += 80; draw_remove_option(self, curr_y, "Watches kept:", self.watches_kept_enabled, self.watches_kept_rect, self.watches_kept_text_rect, offset=off, surface=surface)
            
            curr_y += 80
            surface.blit(self.small_font.render("Watch spawn hits:", True, WHITE), (lm, self.modifiers_panel_rect.y + curr_y - off))
            self.watch_spawn_hits_rect.update(ox, self.modifiers_panel_rect.y + curr_y - 5 - off, 80, 40)
            pygame.draw.rect(surface, BLACK, self.watch_spawn_hits_rect); pygame.draw.rect(surface, WHITE, self.watch_spawn_hits_rect, 2)
            surface.blit(self.small_font.render(str(self.watch_spawn_hits_options[self.watch_spawn_hits_idx]), True, WHITE), self.small_font.render(str(self.watch_spawn_hits_options[self.watch_spawn_hits_idx]), True, WHITE).get_rect(center=self.watch_spawn_hits_rect.center))
            
            curr_y += 80
            surface.blit(self.small_font.render("Power auto grant hits:", True, WHITE), (lm, self.modifiers_panel_rect.y + curr_y - off))
            self.power_auto_grant_hits_rect.update(ox, self.modifiers_panel_rect.y + curr_y - 5 - off, 80, 40)
            pygame.draw.rect(surface, BLACK, self.power_auto_grant_hits_rect); pygame.draw.rect(surface, WHITE, self.power_auto_grant_hits_rect, 2)
            surface.blit(self.small_font.render(str(self.power_auto_grant_hits_options[self.power_auto_grant_hits_idx]), True, WHITE), self.small_font.render(str(self.power_auto_grant_hits_options[self.power_auto_grant_hits_idx]), True, WHITE).get_rect(center=self.power_auto_grant_hits_rect.center))

            curr_y += 80; draw_remove_option(self, curr_y, "Start with power:", self.start_with_power_enabled, self.start_with_power_rect, self.start_with_power_text_rect, offset=off, surface=surface)
            
            curr_y += 80; draw_remove_option(self, curr_y, "Remove a watch", self.remove_watches_expanded, self.remove_watches_toggle_rect, self.remove_watches_toggle_text_rect, is_checkbox=False, offset=off, surface=surface)
            if self.remove_watches_expanded:
                curr_y += 60; draw_remove_option(self, curr_y, " - Remove |BLUE| BLUE |WHITE| watch", self.remove_blue, self.remove_blue_rect, self.remove_blue_text_rect, active_color=BLUE, offset=off, surface=surface)
                curr_y += 60; draw_remove_option(self, curr_y, " - Remove |RED| RED |WHITE| watch", self.remove_red, self.remove_red_rect, self.remove_red_text_rect, active_color=RED, offset=off, surface=surface)
                curr_y += 60; draw_remove_option(self, curr_y, " - Remove |PURPLE| PURPLE |WHITE| watch", self.remove_purple, self.remove_purple_rect, self.remove_purple_text_rect, active_color=PURPLE, offset=off, surface=surface)
                curr_y += 60; draw_remove_option(self, curr_y, " - Remove |WHITE| WHITE |WHITE| watch", self.remove_white, self.remove_white_rect, self.remove_white_text_rect, active_color=WHITE, offset=off, surface=surface)
                curr_y += 60; draw_remove_option(self, curr_y, " - Remove |YELLOW| YELLOW |WHITE| watch", self.remove_yellow, self.remove_yellow_rect, self.remove_yellow_text_rect, active_color=YELLOW, offset=off, surface=surface)
            
            curr_y += 80; draw_remove_option(self, curr_y, "Remove a power", self.remove_power_expanded, self.remove_power_toggle_rect, self.remove_power_toggle_text_rect, is_checkbox=False, offset=off, surface=surface)
            if self.remove_power_expanded:
                curr_y += 60; draw_remove_option(self, curr_y, " - Remove |RED| RED |WHITE| power", self.remove_power_red, self.remove_power_red_rect, self.remove_power_red_text_rect, active_color=RED, offset=off, surface=surface)
                curr_y += 60; draw_remove_option(self, curr_y, " - Remove |GREEN| GREEN |WHITE| power", self.remove_power_green, self.remove_power_green_rect, self.remove_power_green_text_rect, active_color=GREEN, offset=off, surface=surface)
                curr_y += 60; draw_remove_option(self, curr_y, " - Remove |YELLOW| YELLOW |WHITE| power", self.remove_power_yellow, self.remove_power_yellow_rect, self.remove_power_yellow_text_rect, active_color=YELLOW, offset=off, surface=surface)
                curr_y += 60; draw_remove_option(self, curr_y, " - Remove |ORANGE| ORANGE |WHITE| power", self.remove_power_orange, self.remove_power_orange_rect, self.remove_power_orange_text_rect, active_color=ORANGE, offset=off, surface=surface)

            self.max_y_rendered = curr_y

        elif self.modifiers_tab == "EXTRAS":
            self._draw_extras_content(100, off, lm, ox, surface)
            # max_y_rendered se actualiza dentro de _draw_extras_content

        elif self.modifiers_tab == "SKINS":
            curr_y = 100
            draw_rich_text(surface, "Change |ORANGE| ORANGE |WHITE| power:", (lm, self.modifiers_panel_rect.y + curr_y - off), self.small_font)
            self.orange_skin_rect.update(ox, self.modifiers_panel_rect.y + curr_y - 5 - off, 130, 40)
            pygame.draw.rect(surface, BLACK, self.orange_skin_rect); pygame.draw.rect(surface, WHITE, self.orange_skin_rect, 2)
            skin_name = self.orange_skin_options[self.orange_skin_idx]
            skin_color = WHITE if skin_name == "Default" else CYAN
            st = self.small_font.render(skin_name, True, skin_color)
            surface.blit(st, st.get_rect(center=self.orange_skin_rect.center))
            
            curr_y += 80
            draw_rich_text(surface, "Change |YELLOW| YELLOW |WHITE| watch:", (lm, self.modifiers_panel_rect.y + curr_y - off), self.small_font)
            self.yellow_watch_skin_rect.update(ox, self.modifiers_panel_rect.y + curr_y - 5 - off, 130, 40)
            pygame.draw.rect(surface, BLACK, self.yellow_watch_skin_rect); pygame.draw.rect(surface, WHITE, self.yellow_watch_skin_rect, 2)
            y_skin_name = self.yellow_watch_skin_options[self.yellow_watch_skin_idx]
            y_skin_color = WHITE if y_skin_name == "Default" else BROWN
            st2 = self.small_font.render(y_skin_name, True, y_skin_color)
            surface.blit(st2, st2.get_rect(center=self.yellow_watch_skin_rect.center))

            curr_y += 80
            draw_rich_text(surface, "Change BALL skin:", (lm, self.modifiers_panel_rect.y + curr_y - off), self.small_font)
            self.ball_skin_rect.update(ox, self.modifiers_panel_rect.y + curr_y - 5 - off, 130, 40)
            pygame.draw.rect(surface, BLACK, self.ball_skin_rect); pygame.draw.rect(surface, WHITE, self.ball_skin_rect, 2)
            b_skin_name = self.ball_skin_options[self.ball_skin_idx]
            b_skin_color = WHITE if b_skin_name == "Default" else (YELLOW if b_skin_name == "CHEESE" else GREEN)
            st3 = self.small_font.render(b_skin_name, True, b_skin_color)
            surface.blit(st3, st3.get_rect(center=self.ball_skin_rect.center))
            
            self.max_y_rendered = curr_y + 40

        # Update scroll limits
        self.max_scroll = max(0, self.max_y_rendered + 60 - 330)
        self.scroll_y = max(0, min(self.scroll_y, self.max_scroll))

    def _draw_extras_content(self, start_y, off, lm, ox, surface):
        cy = start_y
        mpos = pygame.mouse.get_pos()
        active_tooltip = None
        
        draw_remove_option(self, cy, "Enable |ORANGE| ORANGE |WHITE| watch", self.orange_watch_enabled, self.orange_watch_rect, self.orange_watch_text_rect, active_color=ORANGE, offset=off, surface=surface)
        cy += 60; draw_remove_option(self, cy, "Enable |BLUE|MAG|RED|NET|WHITE| power", self.magnet_power_enabled, self.magnet_power_rect, self.magnet_power_text_rect, active_color=GRAY, offset=off, surface=surface)
        cy += 60; draw_remove_option(self, cy, "Enable |GHOST| GHOST |WHITE| power", self.ghost_power_enabled, self.ghost_power_rect, self.ghost_power_text_rect, active_color=GHOST_COLOR, offset=off, surface=surface)
        cy += 60; draw_remove_option(self, cy, "|GOLD|GOLDEN |WHITE|GOAL rule", self.experimental_golden_goal, self.experimental_golden_goal_rect, self.experimental_golden_goal_text_rect, active_color=GOLD, offset=off, surface=surface)
        cy += 60; draw_remove_option(self, cy, "Allow floating planets", self.floating_planets_enabled, self.floating_planets_rect, self.floating_planets_text_rect, active_color=CYAN, offset=off, surface=surface)
        if self.floating_planets_enabled:
            cy += 60; self._draw_sub_selector(cy, "Gravity:", self.gravity_force_names[self.gravity_force_idx], self.gravity_force_rect, off, ox, lm, surface, sub_val=self.gravity_force_options[self.gravity_force_idx])
            cy += 60; self._draw_sub_selector(cy, "Radius:", self.gravity_radius_names[self.gravity_radius_idx], self.gravity_radius_rect, off, ox, lm, surface, sub_val=self.gravity_radius_options[self.gravity_radius_idx])
            cy += 60; draw_remove_option(self, cy, " Destructible Planets", self.destructible_planets_enabled, self.destructible_planets_rect, self.destructible_planets_text_rect, active_color=ORANGE, offset=off, surface=surface)
            if self.destructible_planets_enabled:
                cy += 60; self._draw_sub_selector(cy, "Resistance:", self.planet_resistance_names[self.planet_resistance_idx], self.planet_resistance_rect, off, ox, lm, surface, sub_val=self.planet_resistance_options[self.planet_resistance_idx])
        
        cy += 60; draw_remove_option(self, cy, "Enable |BLUE|POR|ORANGE|TALS", self.portals_enabled, self.portals_rect, self.portals_text_rect, active_color=BLUE, offset=off, surface=surface)
        if self.portals_text_rect.collidepoint(mpos):
            active_tooltip = ["Teleport balls between Blue and Orange PORTALS."]

        if self.portals_enabled:
            cy += 60; self._draw_sub_selector(cy, "PORTAL size:", self.portal_size_names[self.portal_size_idx], self.portal_size_rect, off, ox, lm, surface, sub_val=self.portal_size_options[self.portal_size_idx], text_rect=self.portal_size_text_rect)
            if self.portal_size_text_rect.collidepoint(mpos):
                active_tooltip = ["Change the length of the PORTALS."]

            cy += 60; draw_remove_option(self, cy, " Vertical PORTALS", self.portals_vertical, self.portals_vertical_rect, self.portals_vertical_text_rect, active_color=BLUE, offset=off, surface=surface)
            if self.portals_vertical_text_rect.collidepoint(mpos):
                active_tooltip = ["Flip PORTALS to vertical orientation on the side walls."]
            cy += 60; draw_remove_option(self, cy, " 2 more |RED|POR|GREEN|TALS", self.more_portals_enabled, self.more_portals_rect, self.more_portals_text_rect, active_color=BLUE, offset=off, surface=surface)
            if self.more_portals_text_rect.collidepoint(mpos):
                active_tooltip = ["Add RED and GREEN PORTALS (Cross-connection)."]
                
        cy += 60; draw_remove_option(self, cy, "X2 multiplier", self.start_x2_enabled, self.start_x2_rect, self.start_x2_text_rect, active_color=GOLD, offset=off, surface=surface)
        cy += 60; draw_remove_option(self, cy, "Add a |GRAY|MOUS|PINK|E", self.add_mouse_enabled, self.add_mouse_rect, self.add_mouse_text_rect, active_color=GRAY, offset=off, surface=surface)
        if self.add_mouse_enabled:
            cy += 60; self._draw_sub_selector(cy, "Initial mouse speed:", self.mouse_speed_names[self.mouse_speed_idx], self.mouse_speed_rect, off, ox, lm, surface, sub_val=self.mouse_speed_options[self.mouse_speed_idx])
            cy += 60; self._draw_sub_selector(cy, "It appears after:", self.mouse_appear_names[self.mouse_appear_idx], self.mouse_appear_rect, off, ox, lm, surface)
        
        self.max_y_rendered = cy + 40
        
        # Dibujamos el tooltip al FINAL para que esté por encima de todo
        if active_tooltip:
            from ui_components import draw_tooltip
            draw_tooltip(self, active_tooltip, surface)

    def _draw_sub_selector(self, y, label, val, rect, off, ox, lm, surface, sub_val=None, text_rect=None):
        draw_y = self.modifiers_panel_rect.y + y - off
        # Label
        from ui_components import draw_rich_text
        if text_rect: text_rect.update(lm, draw_y - 5, 350, 30) # Área más generosa
        draw_rich_text(surface, label, (lm, draw_y), self.small_font)
        rect.update(ox, self.modifiers_panel_rect.y + y - 5 - off, 130, 40)
        pygame.draw.rect(surface, BLACK, rect); pygame.draw.rect(surface, WHITE, rect, 2)
        
        # Color dinámico según el nombre del planeta
        color = WHITE
        if val == "Moon": color = (180, 180, 180)
        elif val == "Planet": color = BROWN
        elif val == "Gas Giant": color = (100, 200, 255)
        elif val == "Star": color = YELLOW
        elif val == "FLASH": color = CYAN
        
        st = self.small_font.render(val, True, color)
        if sub_val is not None:
            # Dibujar el nombre un poco más arriba y el valor debajo
            surface.blit(st, st.get_rect(center=(rect.centerx, rect.centery - 8)))
            sv = self.tiny_font.render(f"({sub_val})", True, (180, 180, 180))
            surface.blit(sv, sv.get_rect(center=(rect.centerx, rect.centery + 10)))
        else:
            surface.blit(st, st.get_rect(center=rect.center))

    def _draw_tooltips(self, clip, surface):
        m = pygame.mouse.get_pos()
        if not clip.collidepoint(m): return
        lines = []
        
        # Lista filtrada por pestaña
        tooltip_map = []
        
        if self.modifiers_tab == "ALL":
            tooltip_map = [
                (self.match_point_text_rect, "match_point"), (self.match_point_rect, "match_point"),
                (self.golden_goal_anim_text_rect, "exp_golden_goal"), (self.golden_goal_anim_rect, "exp_golden_goal"),
                (self.reroll_text_rect, "reroll"), (self.reroll_rect, "reroll"),
                (self.all_reroll_text_rect, "all_reroll"), (self.all_reroll_rect, "all_reroll"),
                (self.equal_watches_text_rect, "equal_watches"), (self.equal_watches_rect, "equal_watches"),
                (self.equal_powers_text_rect, "equal_powers"), (self.equal_powers_rect, "equal_powers"),
                (self.watches_kept_text_rect, "watches_kept"), (self.watches_kept_rect, "watches_kept"),
                (self.watch_spawn_hits_rect, "watch_spawn"), (self.power_auto_grant_hits_rect, "power_spawn"),
                (self.start_with_power_text_rect, "start_with_power"), (self.start_with_power_rect, "start_with_power"),
                (self.encapsulate_powers_text_rect, "encapsulate_powers"), (self.encapsulate_powers_rect, "encapsulate_powers")
            ]
        elif self.modifiers_tab == "EXTRAS":
            tooltip_map = [
                (self.orange_watch_text_rect, "orange_watch"), (self.orange_watch_rect, "orange_watch"),
                (self.magnet_power_text_rect, "magnet_power"), (self.magnet_power_rect, "magnet_power"),
                (self.experimental_golden_goal_text_rect, "exp_golden_goal"), (self.experimental_golden_goal_rect, "exp_golden_goal"),
                (self.floating_planets_text_rect, "floating_planets"), (self.floating_planets_rect, "floating_planets"),
                (self.gravity_force_rect, "gravity_force"), (self.gravity_radius_rect, "gravity_radius"),
                (self.destructible_planets_text_rect, "destructible_planets"), (self.destructible_planets_rect, "destructible_planets"),
                (self.planet_resistance_rect, "planet_resistance"),
                (self.start_x2_text_rect, "x2_multiplier"), (self.start_x2_rect, "x2_multiplier"),
                (self.ghost_power_text_rect, "ghost_power"), (self.ghost_power_rect, "ghost_power"),
                (self.add_mouse_text_rect, "add_mouse"), (self.add_mouse_rect, "add_mouse")
            ]
        elif self.modifiers_tab == "SKINS":
            tooltip_map = [
                (self.orange_skin_rect, "orange_skin")
            ]

        for rect, key in tooltip_map:
            if rect.collidepoint(m):
                lines = assets.TOOLTIPS.get(key, [])
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
        
        for r, t in [(self.btn_gameover_restart, "Restart Game"), (self.btn_gameover_menu, "Back to Menu")]:
            is_hover = r.collidepoint(pygame.mouse.get_pos())
            b_col = (50, 50, 50) if is_hover else BLACK
            s_col = GOLD if is_hover else WHITE
            pygame.draw.rect(surface, b_col, r)
            pygame.draw.rect(surface, s_col, r, 3)
            st = self.font.render(t, True, WHITE)
            surface.blit(st, st.get_rect(center=r.center))

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
