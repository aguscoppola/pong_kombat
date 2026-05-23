import pygame
import asyncio
import random
import math
import os
import sys
import re
import json
from constants import *
from entities import Ball, Paddle, Particle, Mouse
from ui_components import draw_rich_text, draw_remove_option, draw_tooltip
from audio_manager import AudioManager
from vfx_manager import VFXManager
from menu_manager import MenuManager
from ai_controller import AIController
from physics_engine import PhysicsEngine
import assets

class Game:
    def __init__(self, base_dir=None):

       # 1. Definimos la ruta de la carpeta en AppData
        appdata_path = os.path.join(os.environ['APPDATA'], 'PongKombat')
        if not os.path.exists(appdata_path):
            os.makedirs(appdata_path)
        
        # 2. Definimos el archivo de guardado
        self.save_path = os.path.join(appdata_path, "save_data.json")
        print(f"DEBUG: Guardando configuraciones en: {self.save_path}")

        # 3. Cargamos el progreso
        self.first_time_playing = True
        self.load_progress()

        # Mantenemos self.base_dir solo para los assets (imágenes/sonidos)
        self.base_dir = base_dir if base_dir else os.path.dirname(os.path.abspath(__file__))

        pygame.mixer.pre_init(44100, -16, 2, 4096)
        pygame.init()
        pygame.mixer.init()
        # --- v0.7.0: ESCALADO DINÁMICO (Móviles/Web) ---
        # SCALED permite que Pygame gestione automáticamente el escalado de 800x600 
        # a cualquier tamaño de ventana o pantalla, manteniendo las coordenadas lógicas.
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SCALED | pygame.RESIZABLE)
        pygame.display.set_caption("Pong Kombat v0.7.0 - Mobile & Web Edition")
        # Icono de ventana (v0.6.0)
        try:
            icon_path = os.path.join(self.base_dir, "archivos", "pong_kombat_cover.png")
            if os.path.exists(icon_path):
                icon = pygame.image.load(icon_path)
                pygame.display.set_icon(icon)
            else:
                icon = pygame.Surface((32, 32))
                icon.fill((10, 10, 10))
                pygame.draw.rect(icon, (255, 50, 50), (2, 6, 6, 20))
                pygame.draw.rect(icon, (50, 150, 255), (24, 6, 6, 20))
                pygame.draw.circle(icon, (255, 255, 255), (16, 16), 4)
                pygame.display.set_icon(icon)
        except: pass
        
        self.clock = pygame.time.Clock()
        self.audio = AudioManager()
        self.shake_duration = 0
        self.shake_intensity = 0
        self.shake_offset = [0, 0]
        
        # --- NUEVO EN v0.6.0: TUTORIAL PROMPT ---
        self.first_time_playing = True # Cambiar a False tras aceptar/rechazar o cargar de config
        self.show_tutorial_prompt = True
        self.tutorial_active = False
        self.tutorial_step = 0
        self.tutorial_text_full = ""
        self.tutorial_text_visible = ""
        self.tutorial_text_index = 0
        self.tutorial_text_timer = 0
        self.tutorial_word_delay = 0.15 # Segundos entre palabras
        self.btn_tutorial_yes_rect = pygame.Rect(SCREEN_WIDTH//2 - 110, SCREEN_HEIGHT//2 + 40, 100, 40)
        self.btn_tutorial_no_rect = pygame.Rect(SCREEN_WIDTH//2 + 10, SCREEN_HEIGHT//2 + 40, 100, 40)
        
        self.vfx = VFXManager()
        self.menus = MenuManager(self)
        self.ai_controller = AIController(self)
        self.physics = PhysicsEngine(self)
        self.init_fonts()
        self.init_entities()
        self.init_game_state()
        self.init_modifier_variables()
        self.init_endless_pool()
        self.load_progress() # NUEVO v0.6.1: Cargar progreso al iniciar
        
        # Iniciar música del menú
        if self.music_enabled:
            self.audio.play_music('menu_music.wav', volume=self.music_volume)
        else:
            self.audio.stop_music()

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
        
        # MODO MÓVIL (v0.7.0)
        self.mobile_mode = False
        self.geographic_controls = False
        
        # MODO ENDLESS (v0.8.0)
        self.endless_active = False
        self.endless_level = 1
        self.endless_active_modifiers = []
        self.endless_new_modifier_text = ""
        self.endless_intro_timer = 0.0
        self.endless_intro_x = SCREEN_WIDTH
        self.fingers = {} # finger_id -> (x, y)
        
        # Screen Shake
        self.shake_amount = 0
        self.shake_timer = 0
        
        # Secuencia final tutorial
        self.tutorial_end_menu_timer = 0
        self.tutorial_cooldown_timer = 0 # Cooldown para evitar saltos accidentales (v0.7.0)
        
        # Secuencia de Recompensa (v0.6.0)
        self.reward_step = 0
        self.reward_text_full = ""
        self.reward_text_visible = ""
        self.reward_char_timer = 0
        self.input_cooldown = 0.0

        # MODO ARCADE (v0.6.0)
        self.arcade_active = False
        self.arcade_level = 1
        self.arcade_intro_timer = 0
        self.arcade_intro_x = SCREEN_WIDTH
        self.arcade_intro_text = ""
        self.arcade_level_start_timer = 0

    def init_modifier_variables(self):
        # Botones Principales (v0.4.0 - Restaurado a 3 botones grandes)
        self.btn_play_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 100, 300, 70)
        self.btn_tutorial_help_rect = pygame.Rect(self.btn_play_rect.right + 20, self.btn_play_rect.centery - 20, 40, 40)
        self.btn_modifiers_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 15, 300, 70)
        self.btn_settings_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 70, 300, 70)
        self.btn_credits_rect = pygame.Rect(SCREEN_WIDTH - 60, SCREEN_HEIGHT - 60, 40, 40)
        
        # Botones Móviles (v0.7.0)
        bw, bh = 100, 70
        self.btn_p1_up = pygame.Rect(10, SCREEN_HEIGHT - bh*2 - 20, bw, bh)
        self.btn_p1_down = pygame.Rect(10, SCREEN_HEIGHT - bh - 10, bw, bh)
        self.btn_p1_power = pygame.Rect(10, SCREEN_HEIGHT // 2 - bh // 2, bw, bh)

        self.btn_p2_up = pygame.Rect(SCREEN_WIDTH - bw - 10, SCREEN_HEIGHT - bh*2 - 20, bw, bh)
        self.btn_p2_down = pygame.Rect(SCREEN_WIDTH - bw - 10, SCREEN_HEIGHT - bh - 10, bw, bh)
        self.btn_p2_power = pygame.Rect(SCREEN_WIDTH - bw - 10, SCREEN_HEIGHT // 2 - bh // 2, bw, bh)
        self.mobile_controls_toggle_rect = pygame.Rect(0,0,30,30)
        self.geo_controls_rect = pygame.Rect(0,0,25,25)
        
        # Pre-allocate surfaces for mobile buttons to achieve beautiful semi-transparency without per-frame overhead
        self.mobile_btn_surf_normal = pygame.Surface((bw, bh), pygame.SRCALPHA)
        self.mobile_btn_surf_active = pygame.Surface((bw, bh), pygame.SRCALPHA)
        pygame.draw.rect(self.mobile_btn_surf_normal, (20, 20, 20, 100), (0, 0, bw, bh), border_radius=15)
        pygame.draw.rect(self.mobile_btn_surf_normal, (255, 255, 255, 120), (0, 0, bw, bh), 2, border_radius=15)
        pygame.draw.rect(self.mobile_btn_surf_active, (50, 50, 50, 160), (0, 0, bw, bh), border_radius=15)
        pygame.draw.rect(self.mobile_btn_surf_active, (255, 255, 255, 220), (0, 0, bw, bh), 3, border_radius=15)

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
        
        # Scroll para Settings
        self.settings_scroll_y = 0
        self.settings_max_scroll = 200
        self.settings_scrollbar_rect = pygame.Rect(self.modifiers_panel_rect.right - 20, self.modifiers_panel_rect.y + 60, 10, self.modifiers_panel_rect.height - 70)
        self.settings_scrollbar_thumb_rect = pygame.Rect(self.settings_scrollbar_rect.x, self.settings_scrollbar_rect.y, 10, 50)
        self.is_dragging_settings_scrollbar = False
        
        # --- v0.7.0: MÓVILES ---
        self.mobile_mode = False
        if sys.platform == "emscripten":
            try:
                import platform
                ua = platform.window.navigator.userAgent.lower()
                if any(m in ua for m in ["android", "iphone", "ipad", "ipod"]):
                    self.mobile_mode = True
            except Exception as e:
                print(f"Error detectando móvil: {e}")

        self.mobile_controls_toggle_rect = pygame.Rect(0,0,30,30)
        self.geographic_controls = False
        self.geo_controls_rect = pygame.Rect(0,0,30,30)

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
        self.initial_ball_speed_options = [0.8, 1.0, 1.2, 1.25, 1.5]
        self.initial_ball_speed_idx = 1
        self.yellow_speed_up_options = [0.1, 0.2, 0.4, 0.6]
        self.yellow_speed_up_idx = 1
        self.encapsulate_powers_enabled = False
        self.ball_speed_btn_rect = pygame.Rect(0,0,130,40)
        self.initial_ball_speed_rect = pygame.Rect(0,0,130,40)
        self.yellow_speed_up_rect = pygame.Rect(0,0,130,40)
        self.encapsulate_powers_rect = pygame.Rect(0,0,30,30)
        self.encapsulate_powers_text_rect = pygame.Rect(0,0,0,0)
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
        self.music_enabled = True
        self.music_rect = pygame.Rect(0,0,30,30)
        self.music_volume = 0.4
        self.music_volume_bar_rect = pygame.Rect(0,0,200,10)
        self.music_volume_handle_rect = pygame.Rect(0,0,15,30)
        self.is_dragging_music_volume = False
        self.music_in_match = False
        self.music_in_match_rect = pygame.Rect(0,0,30,30)
        self.volume_bar_rect = pygame.Rect(0,0,200,10)
        self.volume_handle_rect = pygame.Rect(0,0,15,30)
        self.is_dragging_volume = False
        self.shake_enabled = True
        self.shake_rect = pygame.Rect(0,0,30,30)
        self.fullscreen_enabled = False
        self.fullscreen_rect = pygame.Rect(0,0,30,30)
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
        self.watch_spawn_hits_idx = 1
        self.watch_spawn_hits_rect = pygame.Rect(0,0,80,40)
        self.watch_spawn_hits_text_rect = pygame.Rect(0,0,0,0)
        self.power_auto_grant_hits_options = [3, 5, 7, 10, 12]
        self.power_auto_grant_hits_idx = 1
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
        self.remove_blue_text_rect = pygame.Rect(0,0,0,0)
        self.remove_red_text_rect = pygame.Rect(0,0,0,0)
        self.remove_purple_text_rect = pygame.Rect(0,0,0,0)
        self.remove_white_text_rect = pygame.Rect(0,0,0,0)
        self.remove_yellow_text_rect = pygame.Rect(0,0,0,0)

        self.remove_power_expanded = False
        self.remove_power_toggle_rect = pygame.Rect(0,0,30,30)
        self.remove_power_toggle_text_rect = pygame.Rect(0,0,0,0)
        self.remove_power_red = self.remove_power_green = self.remove_power_yellow = self.remove_power_orange = False
        self.remove_power_red_rect = pygame.Rect(0,0,30,30)
        self.remove_power_green_rect = pygame.Rect(0,0,30,30)
        self.remove_power_yellow_rect = pygame.Rect(0,0,30,30)
        self.remove_power_orange_rect = pygame.Rect(0,0,30,30)
        self.remove_power_red_text_rect = pygame.Rect(0,0,0,0)
        self.remove_power_green_text_rect = pygame.Rect(0,0,0,0)
        self.remove_power_yellow_text_rect = pygame.Rect(0,0,0,0)
        self.remove_power_orange_text_rect = pygame.Rect(0,0,0,0)

        self.experimental_expanded = False
        self.experimental_toggle_rect = pygame.Rect(0,0,30,30)
        self.experimental_toggle_text_rect = pygame.Rect(0,0,0,0)
        self.orange_watch_enabled = False
        self.orange_watch_rect = pygame.Rect(0,0,30,30)
        self.orange_watch_text_rect = pygame.Rect(0,0,0,0)
        self.tictactoe_enabled = False
        self.tictactoe_rect = pygame.Rect(0,0,30,30)
        self.tictactoe_text_rect = pygame.Rect(0,0,0,0)
        self.tictactoe_board = [None] * 9
        self.tictactoe_winner = None
        self.tictactoe_win_line = None
        self.tictactoe_win_timer = 0.0
        self.magnet_power_enabled = False
        self.magnet_power_rect = pygame.Rect(0,0,30,30)
        self.magnet_power_text_rect = pygame.Rect(0,0,0,0)
        self.ghost_power_enabled = False
        self.ghost_power_rect = pygame.Rect(0,0,30,30)
        self.ghost_power_text_rect = pygame.Rect(0,0,0,0)
        self.ghost_identical_enabled = False
        self.ghost_identical_rect = pygame.Rect(0,0,30,30)
        self.ghost_identical_text_rect = pygame.Rect(0,0,0,0)
        self.gum_power_enabled = False
        self.gum_power_rect = pygame.Rect(0,0,30,30)
        self.gum_power_text_rect = pygame.Rect(0,0,0,0)
        self.gum_projectiles = []
        self.cloudy_day_enabled = False
        self.cloudy_day_rect = pygame.Rect(0,0,30,30)
        self.cloudy_day_text_rect = pygame.Rect(0,0,0,0)
        self.cloud_size_options = [0.5, 1.0, 1.5, 2.0]
        self.cloud_size_names = ["Clear", "Cloudy", "Rainy", "TORRENCIAL"]
        self.cloud_size_idx = 1
        self.cloud_size_rect = pygame.Rect(0,0,130,40)
        self.cloud_size_text_rect = pygame.Rect(0,0,0,0)
        self.clouds = []
        self.cloud_spawn_timer = 0
        
        self.rainy_day_enabled = False
        self.rainy_day_rect = pygame.Rect(0,0,30,30)
        self.rainy_day_text_rect = pygame.Rect(0,0,0,0)
        self.rain_drops = []
        self.rain_timer = 0.0
        self.rain_sound_playing = False
        
        # Sub-modificadores de lluvia (Drop Size y Precipitation)
        self.rain_drop_size_options = [0.5, 1.0, 2.0, 3.0, 5.0]
        self.rain_drop_size_names = ["thin", "Default", "mid", "big", "TORRENCIAL"]
        self.rain_drop_size_idx = 1  # Default (x1)
        self.rain_drop_size_rect = pygame.Rect(0,0,130,40)
        self.rain_drop_size_text_rect = pygame.Rect(0,0,0,0)
        
        self.rain_precipitation_options = [0.5, 1.0, 2.0, 3.0]
        self.rain_precipitation_names = ["2 mm", "10 mm", "30 mm", "50 mm"]
        self.rain_precipitation_idx = 1  # 10 mm (x1)
        self.rain_precipitation_rect = pygame.Rect(0,0,130,40)
        self.rain_precipitation_text_rect = pygame.Rect(0,0,0,0)
        
        # Sub-modificador LIGHTNING
        self.lightning_enabled = False
        self.lightning_rect = pygame.Rect(0,0,30,30)
        self.lightning_text_rect = pygame.Rect(0,0,0,0)
        self.lightning_active = False
        self.lightning_flash_timer = 0.0
        self.lightning_timer = 0.0
        self.experimental_golden_goal = False
        self.experimental_golden_goal_rect = pygame.Rect(0,0,30,30)
        self.experimental_golden_goal_text_rect = pygame.Rect(0,0,0,0)
        self.floating_planets_enabled = False
        self.floating_planets_rect = pygame.Rect(0,0,30,30)
        self.floating_planets_text_rect = pygame.Rect(0,0,0,0)
        self.portals_enabled = False
        self.portals_rect = pygame.Rect(0,0,30,30)
        self.portals_text_rect = pygame.Rect(0,0,0,0)
        self.portal_size_options = [25, 50, 75, 125, 180, 200]
        self.portal_size_names = ["Minion", "Short", "Default", "Big", "Huge", "Giant"]
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
        self.revolver_prob_options = [0.1, 0.25, 0.5, 1.0]
        self.revolver_prob_names = ["Low Prob", "Default", "Quite", "Always"]
        self.revolver_prob_idx = 1
        self.revolver_prob_rect = pygame.Rect(0,0,220,40)
        self.revolver_prob_text_rect = pygame.Rect(0,0,0,0)
        
        self.sleeping_power_enabled = False
        self.sleeping_power_rect = pygame.Rect(0,0,30,30)
        self.sleeping_power_text_rect = pygame.Rect(0,0,0,0)
        self.sleep_projectiles = []
        
        self.start_x2_enabled = False
        self.start_x2_rect = pygame.Rect(0,0,30,30)
        self.start_x2_text_rect = pygame.Rect(0,0,0,0)
        
        self.add_mouse_enabled = False
        self.add_mouse_rect = pygame.Rect(0,0,30,30)
        self.add_mouse_text_rect = pygame.Rect(0,0,0,0)
        self.mouse_speed_options = [100, 200, 300, 500]
        self.mouse_speed_idx = 1
        self.mouse_speed_rect = pygame.Rect(0,0,130,40)
        self.mouse_appear_options = [10, 15, 20, 25]
        self.mouse_appear_idx = 1
        self.mouse_appear_rect = pygame.Rect(0,0,130,40)

        self.gravity_force_options = [1000, 2500, 5000, 8000]
        self.gravity_force_names = ["Moon", "Planet", "Gas Giant", "Star"]
        self.gravity_force_idx = 1
        self.gravity_force_rect = pygame.Rect(0,0,130,40)
        self.gravity_radius_options = [50, 100, 150, 180, 250]
        self.gravity_radius_idx = 1
        self.gravity_radius_rect = pygame.Rect(0,0,130,40)
        self.destructible_planets_enabled = False
        self.destructible_planets_rect = pygame.Rect(0,0,30,30)
        self.destructible_planets_text_rect = pygame.Rect(0,0,0,0)
        self.planet_resistance_options = [1, 3, 5, 10]
        self.planet_resistance_idx = 1
        self.planet_resistance_rect = pygame.Rect(0,0,130,40)
        
        self.portal_red_rect = pygame.Rect(0,0,0,0)
        self.portal_green_rect = pygame.Rect(0,0,0,0)
        
        # Endless CHAOS
        self.endless_chaos_enabled = False
        self.endless_chaos_rect = pygame.Rect(0,0,30,30)
        self.endless_chaos_text_rect = pygame.Rect(0,0,0,0)
        
        self.endless_chaos_options = [0, 1, 2, 3, 4, 5]
        self.endless_chaos_names = ["0 mods", "1 mod", "2 mods", "3 mods", "4 mods", "5 mods"]
        self.endless_chaos_idx = 0
        self.endless_chaos_amount_rect = pygame.Rect(0,0,130,40)
        self.endless_chaos_amount_text_rect = pygame.Rect(0,0,0,0)
        
        self.endless_chaos_accumulation = False
        self.endless_chaos_accumulation_rect = pygame.Rect(0,0,30,30)
        self.endless_chaos_accumulation_text_rect = pygame.Rect(0,0,0,0)
        
        # State variables for banner animations
        self.chaos_banner_text = ""
        self.chaos_banner_timer = 0.0
        self.chaos_banner_duration = 0.0
        self.chaos_banner_x = SCREEN_WIDTH + 400
        self.chaos_active_modifiers = []
        self.initial_modifier_snapshot = {}
        
        self._update_portal_rects()

        # Planetas
        self.planet1_pos = (SCREEN_WIDTH // 2, 80)
        self.planet2_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80)
        self.planet_radius = 22
        self.gravity_radius_options = [100, 180, 250, 350]
        self.gravity_radius_names = ["Moon", "Planet", "Gas Giant", "Star"]
        self.gravity_radius_idx = 1
        self.gravity_radius_rect = pygame.Rect(0,0,80,40)
        self.gravity_radius_text_rect = pygame.Rect(0,0,0,0)
        self.gravity_force_options = [5.0, 10.0, 15.0, 20.0]
        self.gravity_force_names = ["Moon", "Planet", "Gas Giant", "Star"]
        self.gravity_force_idx = 1
        self.gravity_force_rect = pygame.Rect(0,0,80,40)
        self.gravity_force_text_rect = pygame.Rect(0,0,0,0)
        self.destructible_planets_enabled = False
        self.destructible_planets_rect = pygame.Rect(0,0,30,30)
        self.destructible_planets_text_rect = pygame.Rect(0,0,0,0)
        self.planet1_hits = self.planet2_hits = 0
        self.planet1_alive = self.planet2_alive = True
        self.planet_resistance_options = [5, 7, 10, 13]
        self.planet_resistance_names = ["Moon", "Planet", "Gas Giant", "Star"]
        self.planet_resistance_idx = 2
        self.planet_resistance_text_rect = pygame.Rect(0,0,0,0)
        
        # Selección de Modo
        self.is_ai_mode = False
        # Botones gigantes (350x400)
        bw, bh = 300, 350
        self.btn_multi_rect = pygame.Rect(SCREEN_WIDTH//4 - bw//2, SCREEN_HEIGHT//2 - bh//2 + 30, bw, bh)
        self.btn_solo_rect = pygame.Rect(SCREEN_WIDTH*3//4 - bw//2, SCREEN_HEIGHT//2 - bh//2 + 30, bw, bh)
        
        # Modo SOLO sub-modos (v0.6.0)
        self.btn_classic_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 110, 300, 60)
        self.btn_arcade_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 30, 300, 60)
        self.btn_arcade_tutorial_help_rect = pygame.Rect(self.btn_arcade_rect.right + 10, self.btn_arcade_rect.y + 5, 50, 50)
        self.btn_arcade_level_selector_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, self.btn_arcade_rect.bottom + 5, 200, 30)
        self.btn_endless_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 50, 300, 60)
        self.btn_help_endless_rect = pygame.Rect(self.btn_endless_rect.right + 10, self.btn_endless_rect.y + 5, 50, 50)
        self.show_endless_help = False
        self.arcade_tutorial_step = 0
        self.test_arcade_level = 1
        self.btn_solo_sub_back_rect = pygame.Rect(20, 20, 80, 40)
        
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
        
        # Gorro de Corona (v0.6.0)
        self.arcade_completed = False # Desbloqueable
        self.endless_chaos_unlocked = False # Recompensa de nivel 7/7 endless
        self.crown_hat_options = ["None", "Player 1", "Player 2", "Both"]
        self.crown_hat_idx = 0
        self.crown_hat_rect = pygame.Rect(0,0,130,40)
        
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
        self.mouse_speed_idx = 1
        self.mouse_speed_rect = pygame.Rect(0,0,130,40)
        self.mouse_speed_text_rect = pygame.Rect(0,0,0,0)
        
        self.mouse_appear_options = [1, 2, 3, 5]
        self.mouse_appear_names = ["1st hit", "2nd hit", "3rd hit", "5th hit"]
        self.mouse_appear_idx = 1
        self.mouse_appear_rect = pygame.Rect(0,0,180,40)
        self.mouse_appear_text_rect = pygame.Rect(0,0,0,0)
        
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


    def _reset_modifiers(self):
        """Restablece todos los modificadores a sus valores por defecto (v0.6.0 Fix)"""
        self.max_score = 6
        self.match_point_enabled = False
        self.reroll_enabled = True
        self.all_reroll_enabled = False
        self.equal_watches_enabled = False
        self.equal_powers_enabled = False
        self.watches_kept_enabled = False
        self.watch_spawn_hits_idx = 1
        self.power_auto_grant_hits_idx = 1
        self.start_with_power_enabled = True
        self.remove_blue = self.remove_red = self.remove_purple = self.remove_white = self.remove_yellow = False
        self.remove_power_red = self.remove_power_green = self.remove_power_yellow = self.remove_power_orange = False
        self.orange_watch_enabled = False
        self.tictactoe_enabled = False
        self.magnet_power_enabled = False
        self.ghost_power_enabled = False
        self.ghost_identical_enabled = False
        self.gum_power_enabled = False
        self.experimental_golden_goal = False
        self.floating_planets_enabled = False
        self.portals_enabled = False
        self.portal_size_idx = 2
        self.portals_vertical = False
        self.more_portals_enabled = False
        self.revolver_enabled = False
        self.sleeping_power_enabled = False
        self.start_x2_enabled = False
        self.add_mouse_enabled = False
        self.mouse_speed_idx = 1
        self.initial_ball_speed_idx = 1
        self.ball_speed_multiplier_idx = 1
        self.destructible_planets_enabled = False
        self.endless_chaos_enabled = False
        self.endless_chaos_idx = 0
        self.endless_chaos_accumulation = False
        
        # Resetear variables y estados de Clima
        self.cloudy_day_enabled = False
        self.cloud_size_idx = 1
        self.clouds = []
        self.cloud_spawn_timer = 0
        self.rainy_day_enabled = False
        self.rain_drops = []
        self.rain_timer = 0.0
        self.rain_drop_size_idx = 1
        self.rain_precipitation_idx = 1
        self.lightning_enabled = False
        self.lightning_active = False
        self.lightning_flash_timer = 0.0
        self.lightning_timer = 0.0
        if self.rain_sound_playing:
            self.audio.fadeout('rainy', 500)
            self.rain_sound_playing = False
            
        self.reset_tictactoe()
        self._update_portal_rects()

    def save_progress(self):
        """Guarda el progreso del usuario en un archivo JSON (v0.6.1)"""
        data = {
            "first_time_playing": self.first_time_playing,
            "arcade_completed": self.arcade_completed,
            "crown_hat_idx": self.crown_hat_idx,
            "language": self.language,
            "music_enabled": self.music_enabled,
            "music_in_match": self.music_in_match,
            "sfx_volume": self.sfx_volume,
            "music_volume": self.music_volume,
            "vfx_enabled": self.vfx_enabled,
            "shake_enabled": self.shake_enabled,
            "geographic_controls": self.geographic_controls,
            "endless_chaos_unlocked": getattr(self, 'endless_chaos_unlocked', False)
        }
        try:
            with open(self.save_path, "w") as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Error al guardar progreso: {e}")

    def load_progress(self):
        """Carga el progreso del usuario desde el archivo JSON (v0.6.1)"""
        # Cámbialo por esto:
        if os.path.exists(self.save_path):            
            try:
                # Cámbialo por esto
                with open(self.save_path, "r") as f:
                    data = json.load(f)
                    self.first_time_playing = data.get("first_time_playing", True)
                    self.show_tutorial_prompt = self.first_time_playing
                    self.arcade_completed = data.get("arcade_completed", False)
                    self.crown_hat_idx = data.get("crown_hat_idx", 0)
                    self.language = data.get("language", "EN")
                    self.music_enabled = data.get("music_enabled", True)
                    self.music_in_match = data.get("music_in_match", False)
                    self.sfx_volume = data.get("sfx_volume", 0.5)
                    self.music_volume = data.get("music_volume", 0.4)
                    self.vfx_enabled = data.get("vfx_enabled", True)
                    self.shake_enabled = data.get("shake_enabled", True)
                    self.geographic_controls = data.get("geographic_controls", False)
                    self.endless_chaos_unlocked = data.get("endless_chaos_unlocked", False)
                    
                    # FORZAR RESET PARA TESTEO (v0.7.4): Permitir siempre ver la pantalla de recompensa final en cada inicio de juego
                    self.endless_chaos_unlocked = False
                    self.arcade_completed = False
                    
                    # Sincronizar volúmenes con AudioManager
                    self.audio.master_volume = self.sfx_volume
                    for s in self.audio.sounds.values():
                        # Obtener nombre del sonido para buscar su volumen base
                        for name, sound in self.audio.sounds.items():
                            if sound == s:
                                s.set_volume(self.audio.sound_base_volumes[name] * self.audio.master_volume)
                                break
            except Exception as e:
                print(f"Error al cargar progreso: {e}")

    def reset_game(self, skip_announcement=False):
        # self._reset_modifiers() # REMOVED (v0.6.0 Fix) - Wipes classic mode modifiers
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
        self.reset_tictactoe()
        
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
        
        # Resetear variables dinámicas y de renderizado de Clima
        self.clouds = []
        self.rain_drops = []
        self.rain_timer = 0.0
        self.cloud_spawn_timer = 0
        self.lightning_active = False
        self.lightning_flash_timer = 0.0
        self.lightning_timer = 0.0
        if self.rain_sound_playing:
            self.audio.fadeout('rainy', 500)
            self.rain_sound_playing = False
        
        # Reset Endless Chaos variables
        self.chaos_banner_text = ""
        self.chaos_banner_timer = 0.0
        self.chaos_banner_duration = 0.0
        self.chaos_banner_x = SCREEN_WIDTH + 400
        self.chaos_active_modifiers = []
        self.initial_modifier_snapshot = {}
        self.trigger_endless_chaos()

        self.state = STATE_SERVE
        self.serve_timer = 2.0
        if hasattr(self, "chaos_banner_timer") and self.chaos_banner_timer > 0.0:
            self.serve_timer = self.chaos_banner_timer
        self.serve_direction = random.choice([1, -1])
        self.balls = [Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        self.balls[0].serve(self.serve_direction, 300 * self.initial_ball_speed_options[self.initial_ball_speed_idx])
        
        if not skip_announcement:
            self._check_for_announcements()

    def reset_tictactoe(self):
        self.tictactoe_board = [None] * 9
        self.tictactoe_winner = None
        self.tictactoe_win_line = None
        self.tictactoe_win_timer = 0.0

    def _check_tictactoe_win(self):
        winning_lines = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8], # Horizontales
            [0, 3, 6], [1, 4, 7], [2, 5, 8], # Verticales
            [0, 4, 8], [2, 4, 6]             # Diagonales
        ]
        for line in winning_lines:
            v0 = self.tictactoe_board[line[0]]
            v1 = self.tictactoe_board[line[1]]
            v2 = self.tictactoe_board[line[2]]
            if v0 is not None and v0 == v1 and v1 == v2:
                self.tictactoe_winner = v0
                self.tictactoe_win_line = line
                self.tictactoe_win_timer = 0.8
                self.audio.play('explosion')
                winner_paddle = self.paddle1 if v0 == 1 else self.paddle2
                self._grant_tictactoe_power(winner_paddle)
                break

    def _grant_tictactoe_power(self, paddle):
        if paddle.power_active in [POWER_SHIELD, POWER_MAGNET]:
            return
        all_p = [
            (POWER_FIREBALL, RED, not self.remove_power_red),
            (POWER_SHIELD, GREEN, not self.remove_power_green),
            (POWER_SPEED, YELLOW, not self.remove_power_yellow),
            (POWER_ORANGE, ORANGE, not self.remove_power_orange),
            (POWER_MAGNET, GRAY, self.magnet_power_enabled),
            (POWER_GHOST, GHOST_COLOR, self.ghost_power_enabled),
            (POWER_GUM, GUM_PINK, self.gum_power_enabled),
            (POWER_SLEEP, SLEEP_PURPLE, self.sleeping_power_enabled)
        ]
        available = [p for p in all_p if p[2]]
        if not available:
            return
        p_type, p_color, _ = random.choice(available)
        
        if paddle.power_stored == POWER_NONE:
            paddle.power_stored = p_type
            paddle.color = p_color
            if p_type == POWER_GUM:
                paddle.power_active = POWER_GUM
                paddle.gum_charges = 3
                paddle.color = GUM_PINK
                paddle.power_stored = POWER_NONE
        elif self.encapsulate_powers_enabled:
            paddle.power_encapsulated = p_type
            paddle.encapsulated_color = p_color

    def init_endless_pool(self):
        self.endless_pool = [
            # Toggles
            {"id": "encapsulate_powers", "type": "toggle", "field": "encapsulate_powers_enabled", 
             "text_en": "|GRAY|Encapsulating|WHITE| powers", "text_es": "Poderes |GRAY|encapsulados|WHITE|"},
            {"id": "cloudy_day", "type": "toggle", "field": "cloudy_day_enabled", 
             "text_en": "Enable |GRAY|CLOUDY|WHITE| day", "text_es": "Día |GRAY|NUBLADO|WHITE| activo"},
            {"id": "rainy_day", "type": "toggle", "field": "rainy_day_enabled", 
             "text_en": "Enable |BLUE|RAINY|WHITE| day", "text_es": "Día |BLUE|LLUVIOSO|WHITE| activo"},
            {"id": "lightning", "type": "toggle", "field": "lightning_enabled", "depends_on": "rainy_day_enabled",
             "text_en": "Enable |YELLOW|LIGHTNING|WHITE| in rain", "text_es": "|YELLOW|RELÁMPAGOS|WHITE| en lluvia"},
            {"id": "floating_planets", "type": "toggle", "field": "floating_planets_enabled", 
             "text_en": "Allow floating |CYAN|planets|WHITE|", "text_es": "|CYAN|Planetas|WHITE| flotantes activos"},
            {"id": "destructible_planets", "type": "toggle", "field": "destructible_planets_enabled", "depends_on": "floating_planets_enabled",
             "text_en": "Destructible |RED|planets|WHITE|", "text_es": "|RED|Planetas|WHITE| destructibles"},
            {"id": "portals", "type": "toggle", "field": "portals_enabled", 
             "text_en": "Dimensional |PURPLE|PORTALS|WHITE|", "text_es": "|PURPLE|PORTALES|WHITE| dimensionales"},
            {"id": "portals_vertical", "type": "toggle", "field": "portals_vertical", "depends_on": "portals_enabled",
             "text_en": "Vertical |PURPLE|PORTALS|WHITE|", "text_es": "|PURPLE|PORTALES|WHITE| verticales"},
            {"id": "more_portals", "type": "toggle", "field": "more_portals_enabled", "depends_on": "portals_enabled",
             "text_en": "2 more |PURPLE|PORTALS|WHITE|", "text_es": "2 |PURPLE|PORTALES|WHITE| más"},
            {"id": "revolver", "type": "toggle", "field": "revolver_enabled", 
             "text_en": "Enable |GOLD|REVOLVER|WHITE| power", "text_es": "Poder de |GOLD|REVÓLVER|WHITE| activo"},
            {"id": "sleeping_power", "type": "toggle", "field": "sleeping_power_enabled", 
             "text_en": "Enable |PURPLE|SLEEPING|WHITE| power", "text_es": "Poder de |PURPLE|SUEÑO|WHITE| activo"},
            {"id": "start_x2", "type": "toggle", "field": "start_x2_enabled", 
             "text_en": "Enable |YELLOW|X2|WHITE| multiplier", "text_es": "Multiplicador |YELLOW|X2|WHITE| activo"},
            {"id": "add_mouse", "type": "toggle", "field": "add_mouse_enabled", 
             "text_en": "Intrusive |GRAY|Mouse|WHITE|", "text_es": "|GRAY|Ratón|WHITE| Intruso activo"},
            {"id": "orange_watch", "type": "toggle", "field": "orange_watch_enabled", 
             "text_en": "Enable |ORANGE|ORANGE|WHITE| watch", "text_es": "Reloj |ORANGE|NARANJA|WHITE| activo"},
            {"id": "magnet_power", "type": "toggle", "field": "magnet_power_enabled", 
             "text_en": "Enable |GRAY|MAGNET|WHITE| power", "text_es": "Poder |GRAY|MAGNÉTICO|WHITE| activo"},
            {"id": "ghost_power", "type": "toggle", "field": "ghost_power_enabled", 
             "text_en": "Enable |GHOST|GHOST|WHITE| power", "text_es": "Poder |GHOST|FANTASMA|WHITE| activo"},
            {"id": "ghost_identical", "type": "toggle", "field": "ghost_identical_enabled", "depends_on": "ghost_power_enabled",
             "text_en": "Identical |GHOST|GHOST|WHITE| ball", "text_es": "Pelota |GHOST|fantasma|WHITE| idéntica"},
            {"id": "gum_power", "type": "toggle", "field": "gum_power_enabled", 
             "text_en": "Enable |PINK|GUM|WHITE| power", "text_es": "Poder de |PINK|CHICLE|WHITE| activo"},
            {"id": "tictactoe", "type": "toggle", "field": "tictactoe_enabled", 
             "text_en": "Enable |CYAN|Tic-tac-toe|WHITE|", "text_es": "Activar |CYAN|Ta-Te-Ti|WHITE|"},
            {"id": "experimental_golden_goal", "type": "toggle", "field": "experimental_golden_goal", 
             "text_en": "|GOLD|GOLDEN GOAL|WHITE| rule", "text_es": "Regla de |GOLD|GOL DE ORO|WHITE|"},
            {"id": "equal_powers", "type": "toggle", "field": "equal_powers_enabled", 
             "text_en": "Equal powers (|YELLOW|25%|WHITE|)", "text_es": "Poderes iguales (|YELLOW|25%|WHITE|)"},
            {"id": "equal_watches", "type": "toggle", "field": "equal_watches_enabled", 
             "text_en": "Equal watches (|YELLOW|20%|WHITE|)", "text_es": "Relojes iguales (|YELLOW|20%|WHITE|)"},
            {"id": "watches_kept", "type": "toggle", "field": "watches_kept_enabled", 
             "text_en": "Watches kept in |CYAN|zone|WHITE|", "text_es": "Relojes guardados en |CYAN|zona|WHITE|"},
            
            # Removal Accordions
            {"id": "remove_blue", "type": "toggle", "field": "remove_blue", 
             "text_en": "Remove |BLUE|BLUE|WHITE| watch", "text_es": "Eliminar reloj |BLUE|AZUL|WHITE|"},
            {"id": "remove_red", "type": "toggle", "field": "remove_red", 
             "text_en": "Remove |RED|RED|WHITE| watch", "text_es": "Eliminar reloj |RED|ROJO|WHITE|"},
            {"id": "remove_purple", "type": "toggle", "field": "remove_purple", 
             "text_en": "Remove |PURPLE|PURPLE|WHITE| watch", "text_es": "Eliminar reloj |PURPLE|VIOLETA|WHITE|"},
            {"id": "remove_white", "type": "toggle", "field": "remove_white", 
             "text_en": "Remove |WHITE|WHITE|WHITE| watch", "text_es": "Eliminar reloj |WHITE|BLANCO|WHITE|"},
            {"id": "remove_yellow", "type": "toggle", "field": "remove_yellow", 
             "text_en": "Remove |YELLOW|YELLOW|WHITE| watch", "text_es": "Eliminar reloj |YELLOW|AMARILLO|WHITE|"},
             
            {"id": "remove_power_red", "type": "toggle", "field": "remove_power_red", 
             "text_en": "Remove |RED|RED|WHITE| power", "text_es": "Eliminar poder |RED|ROJO|WHITE|"},
            {"id": "remove_power_green", "type": "toggle", "field": "remove_power_green", 
             "text_en": "Remove |GREEN|GREEN|WHITE| power", "text_es": "Eliminar poder |GREEN|VERDE|WHITE|"},
            {"id": "remove_power_yellow", "type": "toggle", "field": "remove_power_yellow", 
             "text_en": "Remove |YELLOW|YELLOW|WHITE| power", "text_es": "Eliminar poder |YELLOW|AMARILLO|WHITE|"},
            {"id": "remove_power_orange", "type": "toggle", "field": "remove_power_orange", 
             "text_en": "Remove |ORANGE|ORANGE|WHITE| power", "text_es": "Eliminar poder |ORANGE|NARANJA|WHITE|"},

            # Scales (indices of options)
            {"id": "cloud_size", "type": "scale", "field": "cloud_size_idx", "max_idx": 3, "depends_on_any": ["cloudy_day_enabled", "rainy_day_enabled"],
             "names_en": ["Clear |GRAY|clouds|WHITE|", "|GRAY|Cloudy|WHITE|", "|BLUE|Rainy|WHITE| clouds", "|YELLOW|TORRENCIAL|WHITE| clouds"],
             "names_es": ["|GRAY|Nubes|WHITE| despejadas", "|GRAY|Nublado|WHITE|", "|BLUE|Nubes|WHITE| de lluvia", "|YELLOW|Nubes TORRENCIALES|WHITE|"]},
            {"id": "rain_drop_size", "type": "scale", "field": "rain_drop_size_idx", "max_idx": 4, "depends_on": "rainy_day_enabled",
             "names_en": ["Thin |BLUE|rain|WHITE| drops", "Default |BLUE|rain|WHITE| drops", "Mid |BLUE|rain|WHITE| drops", "Big |BLUE|rain|WHITE| drops", "|YELLOW|TORRENCIAL|WHITE| rain drops"],
             "names_es": ["|BLUE|Gotas|WHITE| finas de lluvia", "|BLUE|Gotas|WHITE| normales", "|BLUE|Gotas|WHITE| medianas", "|BLUE|Gotas|WHITE| grandes", "|YELLOW|Gotas TORRENCIALES|WHITE|"]},
            {"id": "rain_precipitation", "type": "scale", "field": "rain_precipitation_idx", "max_idx": 3, "depends_on": "rainy_day_enabled",
             "names_en": ["|BLUE|2 mm|WHITE| precipitation", "|BLUE|10 mm|WHITE| precipitation", "|BLUE|30 mm|WHITE| precipitation", "|YELLOW|50 mm|WHITE| precipitation"],
             "names_es": ["Precipitación de |BLUE|2 mm|WHITE|", "Precipitación de |BLUE|10 mm|WHITE|", "Precipitación de |BLUE|30 mm|WHITE|", "Precipitación de |YELLOW|50 mm|WHITE|"]},
            {"id": "gravity_force", "type": "scale", "field": "gravity_force_idx", "max_idx": 3, "depends_on": "floating_planets_enabled",
             "names_en": ["|GRAY|Moon|WHITE| gravity", "|CYAN|Planet|WHITE| gravity", "|ORANGE|Gas Giant|WHITE| gravity", "|YELLOW|Star|WHITE| gravity"],
             "names_es": ["Gravedad de |GRAY|Luna|WHITE|", "Gravedad de |CYAN|Planeta|WHITE|", "Gravedad de |ORANGE|Gigante Gaseoso|WHITE|", "Gravedad de |YELLOW|Estrella|WHITE|"]},
            {"id": "gravity_radius", "type": "scale", "field": "gravity_radius_idx", "max_idx": 3, "depends_on": "floating_planets_enabled",
             "names_en": ["|GRAY|Moon|WHITE| gravity radius", "|CYAN|Planet|WHITE| gravity radius", "|ORANGE|Gas Giant|WHITE| gravity radius", "|YELLOW|Star|WHITE| gravity radius"],
             "names_es": ["Radio de gravedad de |GRAY|Luna|WHITE|", "Radio de gravedad de |CYAN|Planeta|WHITE|", "Radio de gravedad de |ORANGE|Gigante|WHITE|", "Radio de gravedad de |YELLOW|Estrella|WHITE|"]},
            {"id": "planet_resistance", "type": "scale", "field": "planet_resistance_idx", "max_idx": 3, "depends_on": "floating_planets_enabled",
             "names_en": ["|GRAY|Moon|WHITE| planet resistance", "|CYAN|Planet|WHITE| resistance", "|ORANGE|Gas Giant|WHITE| resistance", "|YELLOW|Star|WHITE| planet resistance"],
             "names_es": ["Resistencia de |GRAY|Luna|WHITE|", "Resistencia de |CYAN|Planeta|WHITE|", "Resistencia de |ORANGE|Gigante|WHITE|", "Resistencia de |YELLOW|Estrella|WHITE|"]},
            {"id": "portal_size", "type": "scale", "field": "portal_size_idx", "max_idx": 5, "depends_on": "portals_enabled",
             "names_en": ["|PURPLE|Minion|WHITE| portal size", "|PURPLE|Short|WHITE| portal size", "|PURPLE|Default|WHITE| portal size", "|PURPLE|Big|WHITE| portal size", "|PURPLE|Planet|WHITE| portal size", "|PURPLE|Giant|WHITE| portal size"],
             "names_es": ["Portal tamaño |PURPLE|Minion|WHITE|", "Portal tamaño |PURPLE|Corto|WHITE|", "Portal tamaño |PURPLE|Normal|WHITE|", "Portal tamaño |PURPLE|Grande|WHITE|", "Portal tamaño |PURPLE|Planeta|WHITE|", "Portal tamaño |PURPLE|Gigante|WHITE|"]},
            {"id": "revolver_prob", "type": "scale", "field": "revolver_prob_idx", "max_idx": 3, "depends_on": "revolver_enabled",
             "names_en": ["Low |GOLD|revolver|WHITE| prob", "Default |GOLD|revolver|WHITE| prob", "Quite |GOLD|revolver|WHITE| prob", "|GOLD|Always revolver|WHITE| prob"],
             "names_es": ["Probabilidad de |GOLD|revólver|WHITE| baja", "Probabilidad normal", "Probabilidad bastante alta", "Probabilidad del |GOLD|100%|WHITE|"]},
            {"id": "mouse_speed", "type": "scale", "field": "mouse_speed_idx", "max_idx": 3, "depends_on": "add_mouse_enabled",
             "names_en": ["Slow |GRAY|mouse|WHITE| speed", "Normal |GRAY|mouse|WHITE| speed", "Default |GRAY|mouse|WHITE| speed", "|RED|Fast mouse|WHITE| speed"],
             "names_es": ["Velocidad de |GRAY|ratón|WHITE| lenta", "Velocidad de |GRAY|ratón|WHITE| normal", "Velocidad de |GRAY|ratón|WHITE| estándar", "Velocidad de |RED|ratón rápida|WHITE|"]},
            {"id": "mouse_appear", "type": "scale", "field": "mouse_appear_idx", "max_idx": 3, "depends_on": "add_mouse_enabled",
             "names_en": ["|GRAY|Mouse|WHITE| on 1st hit", "|GRAY|Mouse|WHITE| on 2nd hit", "|GRAY|Mouse|WHITE| on 3rd hit", "|GRAY|Mouse|WHITE| on 5th hit"],
             "names_es": ["|GRAY|Ratón|WHITE| al primer golpe", "|GRAY|Ratón|WHITE| al segundo golpe", "|GRAY|Ratón|WHITE| al tercer golpe", "|GRAY|Ratón|WHITE| al quinto golpe"]},
            {"id": "initial_ball_speed", "type": "scale", "field": "initial_ball_speed_idx", "max_idx": 4,
             "names_en": ["Low initial ball speed", "Default initial ball speed", "Mid initial ball speed", "|RED|Fast|WHITE| initial ball speed", "|YELLOW|FLASH|WHITE| initial ball speed"],
             "names_es": ["Velocidad inicial de pelota baja", "Velocidad inicial normal", "Velocidad inicial media", "Velocidad inicial |RED|rápida|WHITE|", "Velocidad inicial |YELLOW|FLASH|WHITE|"]},
            {"id": "ball_speed_multiplier", "type": "scale", "field": "ball_speed_multiplier_idx", "max_idx": 3,
             "names_en": ["Low ball speed increase", "Default ball speed increase", "Original ball speed increase", "|RED|Fast|WHITE| ball speed increase"],
             "names_es": ["Aumento de velocidad de pelota bajo", "Aumento normal", "Aumento original", "Aumento |RED|rápido|WHITE|"]},
            {"id": "yellow_speed_up", "type": "scale", "field": "yellow_speed_up_idx", "max_idx": 3,
             "names_en": ["Low |YELLOW|yellow|WHITE| speed up", "Default |YELLOW|yellow|WHITE| speed up", "Big |YELLOW|yellow|WHITE| speed up", "Giant |YELLOW|yellow|WHITE| speed up"],
             "names_es": ["Aumento |YELLOW|amarillo|WHITE| bajo", "Aumento |YELLOW|amarillo|WHITE| normal", "Aumento |YELLOW|amarillo|WHITE| grande", "Aumento |YELLOW|amarillo|WHITE| gigante"]},
            {"id": "watch_spawn_hits", "type": "scale", "field": "watch_spawn_hits_idx", "max_idx": 3,
             "names_en": ["Watches spawn every |RED|3|WHITE| hits", "Watches spawn every 5 hits", "Watches spawn every 10 hits", "Watches spawn every 15 hits"],
             "names_es": ["Relojes cada |RED|3|WHITE| golpes", "Relojes cada 5 golpes", "Relojes cada 10 golpes", "Relojes cada 15 golpes"]},
            {"id": "power_auto_grant_hits", "type": "scale", "field": "power_auto_grant_hits_idx", "max_idx": 4,
             "names_en": ["Power every |RED|3|WHITE| hits", "Power every 5 hits", "Power every 7 hits", "Power every 10 hits", "Power every 12 hits"],
             "names_es": ["Poder cada |RED|3|WHITE| toques", "Poder cada 5 toques", "Poder cada 7 toques", "Poder cada 10 toques", "Poder cada 12 toques"]}
        ]

    def apply_chaos_modifiers(self):
        # 1. Restore all modifiers to their snapshot baseline
        for field, val in self.initial_modifier_snapshot.items():
            setattr(self, field, val)
        
        # 2. Re-apply portal rects updating if any portal modifier changed
        portals_updated = False

        # 3. Apply cumulatively each active chaos modifier
        for mod in self.chaos_active_modifiers:
            field = mod["field"]
            if mod["type"] == "toggle":
                setattr(self, field, True)
                if field in ["portals_enabled", "more_portals_enabled", "portals_vertical"]:
                    portals_updated = True
            elif mod["type"] == "scale":
                setattr(self, field, mod["value"])
                if field == "portal_size_idx":
                    portals_updated = True

        if portals_updated:
            self._update_portal_rects()

    def trigger_endless_chaos(self):
        # Check if Endless Chaos is active, and we are not in Endless or Arcade mode
        if self.endless_active or self.arcade_active:
            return
        if not getattr(self, "endless_chaos_enabled", False):
            return
        
        # 1. Take snapshot on the very first point of the match
        if not hasattr(self, "initial_modifier_snapshot") or not self.initial_modifier_snapshot:
            self.initial_modifier_snapshot = {}
            for item in self.endless_pool:
                self.initial_modifier_snapshot[item["field"]] = getattr(self, item["field"])
            self.chaos_active_modifiers = []
        else:
            if not getattr(self, "endless_chaos_accumulation", False):
                self.chaos_active_modifiers = []
            self.apply_chaos_modifiers()
            
        # 2. Pick random modifiers from self.endless_pool
        added_en = []
        added_es = []
        
        k = self.endless_chaos_options[self.endless_chaos_idx]
        
        for idx_range in range(k):
            # Apply existing chaos modifiers first to ensure current state is correct for dependency checks
            self.apply_chaos_modifiers()
            
            # Find eligible candidates
            candidates = []
            for item in self.endless_pool:
                # Regla: El ratón no puede aumentar su velocidad
                if item["id"] == "mouse_speed":
                    continue

                # Reglas: No permitir Gol de Oro experimental ni Multiplicador X2 en Modo Infinito / Caos
                if item["id"] in ["start_x2", "experimental_golden_goal"]:
                    continue

                # Regla: Los modificadores de "Remove..." solo pueden aparecer si no se filtran
                if item["id"].startswith("remove_"):
                    continue

                field = item["field"]
                snap_val = self.initial_modifier_snapshot.get(field, None)
                
                if item["type"] == "toggle":
                    # If manually enabled from the start, or already active in game, not eligible
                    if snap_val is True or getattr(self, field) is True:
                        continue
                elif item["type"] == "scale":
                    # If manually set to max from the start, or already at max in game, not eligible
                    if snap_val == item["max_idx"] or getattr(self, field) >= item["max_idx"]:
                        continue
                
                # Check dependencies:
                if "depends_on" in item:
                    dep_field = item["depends_on"]
                    if not getattr(self, dep_field):
                        continue
                if "depends_on_any" in item:
                    dep_fields = item["depends_on_any"]
                    if not any(getattr(self, f) for f in dep_fields):
                        continue
                
                candidates.append(item)
            
            if not candidates:
                break
                
            chosen = random.choice(candidates)
            
            if chosen["type"] == "toggle":
                new_mod = {
                    "id": chosen["id"],
                    "type": "toggle",
                    "field": chosen["field"],
                    "text_en": chosen["text_en"],
                    "text_es": chosen["text_es"]
                }
                added_en.append(chosen["text_en"])
                added_es.append(chosen["text_es"])
            else:
                curr_idx = getattr(self, chosen["field"])
                next_idx = curr_idx + 1
                new_mod = {
                    "id": chosen["id"],
                    "type": "scale",
                    "field": chosen["field"],
                    "value": next_idx,
                    "text_en": chosen["names_en"][next_idx],
                    "text_es": chosen["names_es"][next_idx]
                }
                added_en.append(chosen["names_en"][next_idx])
                added_es.append(chosen["names_es"][next_idx])
                
            self.chaos_active_modifiers.append(new_mod)
        
        # Apply the accumulated modifications
        self.apply_chaos_modifiers()
        
        # Trigger banner/text sliding from right to left!
        if added_en:
            txt_en = f"NEW CHAOS: {' - '.join(added_en)}"
            txt_es = f"NUEVO CAOS: {' - '.join(added_es)}"
            self.chaos_banner_text = self.t(txt_en, txt_es)
            num_mods = len(added_en)
            self.chaos_banner_duration = 5.0 + num_mods * 0.5
            self.chaos_banner_timer = self.chaos_banner_duration
            self.chaos_banner_x = SCREEN_WIDTH + 400

    def apply_endless_modifiers(self):
        # 1. Restablecer todos los modificadores a baseline
        self._reset_modifiers()
        
        # 2. Forzar partida a 1 punto
        self.max_score = 1
        self.match_point_enabled = False
        self.experimental_golden_goal = False
        
        # 3. Aplicar acumulativamente cada modificador activo
        for mod in self.endless_active_modifiers:
            field = mod["field"]
            if mod["type"] == "toggle":
                setattr(self, field, True)
                if field in ["portals_enabled", "more_portals_enabled", "portals_vertical"]:
                    self._update_portal_rects()
            elif mod["type"] == "scale":
                setattr(self, field, mod["value"])
                if field == "portal_size_idx":
                    self._update_portal_rects()

    def generate_next_endless_modifier(self):
        added_en = []
        added_es = []
        
        for _ in range(self.endless_level):
            # 1. Aplicar los modificadores temporales de self para evaluar estado
            self.apply_endless_modifiers()
            
            # 2. Encontrar candidatos elegibles en el pool
            candidates = []
            extras_ids = {
                "orange_watch", "magnet_power", "ghost_power", "ghost_identical", 
                "gum_power", "tictactoe", "floating_planets", "destructible_planets", 
                "portals", "portals_vertical", "more_portals", "add_mouse", "revolver", 
                "sleeping_power", "cloudy_day", "rainy_day", "lightning"
            }
            
            for item in self.endless_pool:
                # Regla: El ratón no puede aumentar su velocidad en Endless
                if item["id"] == "mouse_speed":
                    continue

                # Reglas: No permitir Gol de Oro experimental ni Multiplicador X2 en Modo Infinito
                if item["id"] in ["start_x2", "experimental_golden_goal"]:
                    continue

                # Regla: Los modificadores de "Remove..." solo pueden aparecer desde el nivel 3 en adelante
                if self.endless_level < 3 and item["id"].startswith("remove_"):
                    continue
                
                # Regla: En el primer nivel (nivel 1), obligatoriamente debe ser del apartado EXTRAS
                if self.endless_level == 1 and item["id"] not in extras_ids:
                    continue

                # Comprobar dependencias requeridas
                if "depends_on" in item:
                    dep_field = item["depends_on"]
                    if not getattr(self, dep_field):
                        continue
                if "depends_on_any" in item:
                    dep_fields = item["depends_on_any"]
                    if not any(getattr(self, f) for f in dep_fields):
                        continue

                field = item["field"]
                if item["type"] == "toggle":
                    if not getattr(self, field):
                        candidates.append(item)
                elif item["type"] == "scale":
                    curr_idx = getattr(self, field)
                    if field in ["watch_spawn_hits_idx", "power_auto_grant_hits_idx"]:
                        if curr_idx == 1:
                            candidates.append(item)
                    else:
                        if curr_idx < item["max_idx"]:
                            candidates.append(item)
            
            if not candidates:
                if not added_en:
                    self.endless_new_modifier_text = self.t("MAXIMUM CHAOS REACHED!", "¡CAOS MÁXIMO ALCANZADO!")
                    return
                else:
                    break
                
            # 3. Elegir uno al azar
            chosen = random.choice(candidates)
            
            # 4. Formatear y añadir al registro de modificadores activos
            if chosen["type"] == "toggle":
                new_mod = {
                    "id": chosen["id"],
                    "type": "toggle",
                    "field": chosen["field"],
                    "text_en": chosen["text_en"],
                    "text_es": chosen["text_es"]
                }
                added_en.append(chosen["text_en"])
                added_es.append(chosen["text_es"])
            else:
                curr_idx = getattr(self, chosen["field"])
                if chosen["field"] in ["watch_spawn_hits_idx", "power_auto_grant_hits_idx"]:
                    next_idx = 0
                else:
                    next_idx = curr_idx + 1
                new_mod = {
                    "id": chosen["id"],
                    "type": "scale",
                    "field": chosen["field"],
                    "value": next_idx,
                    "text_en": chosen["names_en"][next_idx],
                    "text_es": chosen["names_es"][next_idx]
                }
                added_en.append(chosen["names_en"][next_idx])
                added_es.append(chosen["names_es"][next_idx])
                
            self.endless_active_modifiers.append(new_mod)
            self.apply_endless_modifiers()
            
        if added_en:
            txt_en = f"NEW CHAOS: {' - '.join(added_en)}"
            txt_es = f"NUEVO CAOS: {' - '.join(added_es)}"
            self.endless_new_modifier_text = self.t(txt_en, txt_es)

    def start_endless_mode(self):
        self.endless_active = True
        self.arcade_active = False
        self.is_ai_mode = True
        self.endless_level = 1
        self.endless_active_modifiers = []
        self.score1 = self.score2 = 0
        self.tutorial_active = False
        
        # Generar el primer modificador
        self.generate_next_endless_modifier()
        
        self.reset_game(skip_announcement=True)
        
        # Iniciar animaciones de HUD y saque
        self.endless_intro_timer = 4.0 + (self.endless_level - 1)
        self.endless_intro_x = SCREEN_WIDTH + 400
        self.serve_timer = self.endless_intro_timer + 1.0
        self.serve_direction = random.choice([1, -1])
        
        # Iniciar saques
        self.state = STATE_SERVE
        self.balls[0].serve(self.serve_direction, 300 * self.initial_ball_speed_options[self.initial_ball_speed_idx])

    def start_arcade_level(self, level):
        self._reset_modifiers() # Limpieza total antes de empezar (v0.6.0 Fix)
        self.arcade_active = True
        self.arcade_level = level
        self.is_ai_mode = True
        self.score1 = self.score2 = 0
        self.tutorial_active = False 
        
        self.init_modifier_variables()
        self.is_ai_mode = True
        self.modifiers_tab = "ALL"
        
        # Pantalla negra intermedia v0.6.0
        self.state = STATE_ARCADE_LEVEL_START
        self.arcade_level_start_timer = 2.0

    def _setup_arcade_gameplay(self, level):
        if level == 1:
            self.max_score = 1
            self.match_point_enabled = False
            self.is_golden_goal_round = True # Iniciar con Gol de Oro (v0.6.0 Fix)
            # Eliminar relojes
            self.remove_blue = self.remove_red = self.remove_purple = self.remove_white = self.remove_yellow = True
            self.orange_watch_enabled = False
            # Solo RED y GREEN poderes
            self.remove_power_red = False
            self.remove_power_green = False
            self.remove_power_yellow = True
            self.remove_power_orange = True
            self.magnet_power_enabled = False
            self.ghost_power_enabled = False
            self.gum_power_enabled = False
            self.revolver_enabled = False
            self.equal_powers_enabled = True
            
            # Poder inicial otorgado DESPUÉS de las restricciones
            self.paddle1.grant_random_power(self)
            self.paddle2.grant_random_power(self)
            
            self.arcade_intro_text = self.t(
                "Clocks removed,\nonly |RED|RED|WHITE| and |GREEN|GREEN|WHITE| power active.\n|GOLD|GOLDEN GOAL.",
                "Relojes eliminados,\nsolo poderes |RED|ROJO|WHITE| y |GREEN|VERDE|WHITE| activos.\n|GOLD|GOL DE ORO."
            )
            self.arcade_intro_timer = 6.0 
            self.arcade_intro_x = SCREEN_WIDTH + 500
            
            self.state = STATE_SERVE
            self.serve_timer = 8.5 # Intro(6s) + GoldenGoalAnim(2.5s)
            self.show_golden_goal_anim = False # Esperar a que termine la intro (v0.6.0 Fix)
            self.serve_direction = random.choice([1, -1])
            self.balls = [Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
            self.balls[0].serve(self.serve_direction, 300 * self.initial_ball_speed_options[self.initial_ball_speed_idx])
            
        elif level == 2:
            self.max_score = 1
            self.match_point_enabled = False
            self.is_golden_goal_round = True
            # Activar relojes (Clásico)
            self.remove_blue = self.remove_red = self.remove_purple = self.remove_white = self.remove_yellow = False
            self.orange_watch_enabled = False
            self.start_with_power_enabled = True
            # Activar todos los poderes clásicos
            self.remove_power_red = self.remove_power_green = self.remove_power_yellow = self.remove_power_orange = False
            
            # Otorgar poder inicial
            self.paddle1.grant_random_power(self)
            self.paddle2.grant_random_power(self)
            
            self.arcade_intro_text = self.t(
                "Enable |BLUE|CLASSIC|WHITE| powers.\n|GOLD|GOLDEN GOAL.",
                "Poderes |BLUE|CLÁSICOS|WHITE| activados.\n|GOLD|GOL DE ORO."
            )
            self.arcade_intro_timer = 6.0 
            self.arcade_intro_x = SCREEN_WIDTH + 500
            
            self.state = STATE_SERVE
            self.serve_timer = 8.5 # Intro(6s) + GoldenGoalAnim(2.5s)
            self.show_golden_goal_anim = False
            self.serve_direction = random.choice([1, -1])
            self.balls = [Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
            self.balls[0].serve(self.serve_direction, 300 * self.initial_ball_speed_options[self.initial_ball_speed_idx])
            
        elif level == 3:
            self.max_score = 1
            self.match_point_enabled = True
            # Relojes cada 5 toques
            self.watch_spawn_hits_idx = 1 # 5 hits
            self.power_auto_grant_hits_idx = 1 # 5 hits
            self.remove_blue = self.remove_red = self.remove_purple = self.remove_white = self.remove_yellow = False
            self.orange_watch_enabled = True
            self.start_x2_enabled = True
            self.start_with_power_enabled = True
            
            # Activar todos los poderes clásicos
            self.remove_power_red = self.remove_power_green = self.remove_power_yellow = self.remove_power_orange = False
            
            # Otorgar poder inicial
            self.paddle1.grant_random_power(self)
            self.paddle2.grant_random_power(self)
            
            self.arcade_intro_text = self.t(
                "Power/Clock every 5 hits.\n|ORANGE|ORANGE|WHITE| clock and |YELLOW|X2|WHITE| enabled.\n|GOLD|MATCH POINT|WHITE| at 1 point.",
                "Poder/Reloj cada 5 toques.\nReloj |ORANGE|NARANJA|WHITE| y |YELLOW|X2|WHITE| activos.\n|GOLD|PUNTO DE PARTIDA|WHITE| a 1 punto."
            )
            self.arcade_intro_timer = 6.0 
            self.arcade_intro_x = SCREEN_WIDTH + 500
            
            self.state = STATE_SERVE
            self.serve_timer = 6.0
            self.serve_direction = random.choice([1, -1])
            self.balls = [Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
            self.balls[0].serve(self.serve_direction, 300 * self.initial_ball_speed_options[self.initial_ball_speed_idx])

        elif level == 4:
            # NIVEL ESPECIAL: 50% VARIANTE 1, 50% VARIANTE 2
            variant = random.choice([1, 2])
            self.watch_spawn_hits_idx = 1 # 5 hits
            self.power_auto_grant_hits_idx = 1 # 5 hits
            self.remove_blue = self.remove_red = self.remove_purple = self.remove_white = self.remove_yellow = False
            self.start_with_power_enabled = True
            
            if variant == 1:
                self.max_score = 3
                # Solo poderes raros
                self.remove_power_red = self.remove_power_green = self.remove_power_yellow = self.remove_power_orange = True
                self.magnet_power_enabled = True
                self.ghost_power_enabled = True
                self.gum_power_enabled = True
                self.revolver_enabled = True
                self.revolver_prob_idx = 3 # 100% Always
                self.equal_powers_enabled = True
                
                self.arcade_intro_text = self.t(
                    "SPECIAL LEVEL: |PURPLE|VARIANT 1|WHITE|\n|GRAY|MAGNET|WHITE|, |GHOST|GHOST|WHITE|, |PINK|GUM|WHITE| and |GOLD|REVOLVER|WHITE|.\nClock every 5 hits. Best of 3.",
                    "NIVEL ESPECIAL: |PURPLE|VARIANTE 1|WHITE|\n|GRAY|MAGNETO|WHITE|, |GHOST|FANTASMA|WHITE|, |PINK|CHICLE|WHITE| y |GOLD|REVÓLVER|WHITE|.\nReloj cada 5 toques. Al mejor de 3."
                )
            else:
                self.max_score = 3
                # Clásico + Ratón
                self.remove_power_red = self.remove_power_green = self.remove_power_yellow = self.remove_power_orange = False
                self.add_mouse_enabled = True
                self.mouse_speed_idx = 0
                self.mouse_appear_idx = 0 # 1st hit
                
                self.arcade_intro_text = self.t(
                    "SPECIAL LEVEL: |PURPLE|VARIANT 2|WHITE|\n|BLUE|CLASSIC|WHITE| mechanics + |GRAY|MOUSE|WHITE|.\n3-point game. Clock every 5 hits.",
                    "NIVEL ESPECIAL: |PURPLE|VARIANTE 2|WHITE|\nMećanicas |BLUE|CLÁSICAS|WHITE| + |GRAY|RATÓN|WHITE|.\nPartida a 3. Reloj cada 5 toques."
                )
            
            # Otorgar poder inicial
            self.paddle1.grant_random_power(self)
            self.paddle2.grant_random_power(self)
            
            self.arcade_intro_timer = 6.0 
            self.arcade_intro_x = SCREEN_WIDTH + 500
            self.state = STATE_SERVE
            self.serve_timer = 6.0
            self.serve_direction = random.choice([1, -1])
            self.balls = [Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
            self.balls[0].serve(self.serve_direction, 300 * self.initial_ball_speed_options[self.initial_ball_speed_idx])

        elif level == 5:
            self.max_score = 3
            self.match_point_enabled = False
            self.show_match_point_anim = False
            self.show_golden_goal_anim = False
            self.experimental_golden_goal = False
            self.is_golden_goal_round = False
            
            self.watch_spawn_hits_idx = 1 # 5 hits
            self.power_auto_grant_hits_idx = 1 # 5 hits
            
            # Velocidad inicial x1.0
            self.initial_ball_speed_idx = 1 # Default (1.0)
            
            # 2 Portales activos
            self.portals_enabled = True
            self.more_portals_enabled = False
            self.portal_size_idx = 2 # Original (75)
            self._update_portal_rects()
            
            # Planetas por defecto (no destructibles)
            self.floating_planets_enabled = True
            self.gravity_force_idx = 1 # Planet
            self.gravity_radius_idx = 3 # Planet (180)
            self.destructible_planets_enabled = False
            
            # Relojes se quedan
            self.watches_kept_enabled = True
            
            # Números encapsuladores
            self.encapsulate_powers_enabled = True
            
            # Poderes clásicos y revólver activos
            self.remove_blue = self.remove_red = self.remove_purple = self.remove_white = self.remove_yellow = False
            self.orange_watch_enabled = False
            self.remove_power_red = self.remove_power_green = self.remove_power_yellow = self.remove_power_orange = False
            
            self.magnet_power_enabled = False
            self.ghost_power_enabled = False
            self.gum_power_enabled = False
            self.sleeping_power_enabled = False
            self.revolver_enabled = True
            self.revolver_prob_idx = 1 # Default
            
            self.start_with_power_enabled = True
            self.paddle1.grant_random_power(self)
            self.paddle2.grant_random_power(self)
            
            # Desactivar clima y extras no deseados
            self.cloudy_day_enabled = False
            self.rainy_day_enabled = False
            self.lightning_enabled = False
            self.add_mouse_enabled = False
            self.start_x2_enabled = False
            
            self.arcade_intro_text = self.t(
                "|RED|LEVEL 5|WHITE|\n|PURPLE|Planets|WHITE|, 2 |BLUE|POR|RED|TALS|WHITE|, |BLUE|CLASSIC|WHITE| Powers & |GOLD|Revolver|WHITE|.\n|ORANGE|Hourglasses|WHITE| Stay and |YELLOW|Encapsulating Numbers|WHITE| active.\nPower every 5 hits. Win 3 points.",
                "|RED|NIVEL 5|WHITE|\n|PURPLE|Planetas|WHITE|, 2 |BLUE|POR|RED|TALES|WHITE|, Poderes |BLUE|CLÁSICOS|WHITE| y |GOLD|Revólver|WHITE|.\nLos |ORANGE|Relojes|WHITE| se Quedan y |YELLOW|Números Encapsuladores|WHITE| activos.\nPoder cada 5 toques. Gana a 3 puntos."
            )
            self.arcade_intro_timer = 6.0 
            self.arcade_intro_x = SCREEN_WIDTH + 500
            
            self.state = STATE_SERVE
            self.serve_timer = 6.0
            self.serve_direction = random.choice([1, -1])
            self.balls = [Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
            self.balls[0].serve(self.serve_direction, 300 * self.initial_ball_speed_options[self.initial_ball_speed_idx])

        elif level == 6:
            variant = random.choice([1, 2])
            self.watch_spawn_hits_idx = 0 # 3 hits
            self.power_auto_grant_hits_idx = 0 # 3 hits
            self.max_score = 3
            self.match_point_enabled = False
            self.show_match_point_anim = False
            self.show_golden_goal_anim = False
            self.is_golden_goal_round = False
            
            self.initial_ball_speed_idx = 3 # 1.25

            # Reseteamos todas las variables para evitar herencias
            self.floating_planets_enabled = False
            self.portals_enabled = False
            self.more_portals_enabled = False
            self.add_mouse_enabled = False
            self.experimental_golden_goal = False
            self.watches_kept_enabled = False
            self.encapsulate_powers_enabled = False
            self.start_x2_enabled = False
            
            if variant == 1:
                # Enable RAINY day, con todos sus sub-modificadores activos + Lightning
                self.rainy_day_enabled = True
                self.lightning_enabled = True
                self.rain_drop_size_idx = 4 # TORRENCIAL (size 5.0)
                self.rain_precipitation_idx = 3 # 50 mm (precipitation 3.0)
                
                self.cloudy_day_enabled = False
                
                # solo poderes: Gum, Ghost, Sleeping, REVOLVER (100%)
                self.remove_power_red = self.remove_power_green = self.remove_power_yellow = self.remove_power_orange = True
                self.magnet_power_enabled = False
                self.ghost_power_enabled = True
                self.gum_power_enabled = True
                self.sleeping_power_enabled = True
                self.revolver_enabled = True
                self.revolver_prob_idx = 3 # 100% Always
                
                # Relojes activos todos
                self.remove_blue = self.remove_red = self.remove_purple = self.remove_white = self.remove_yellow = False
                self.orange_watch_enabled = True
                
                self.arcade_intro_text = self.t(
                    "|RED|LEVEL 6: VARIANT 1|WHITE|\n|CYAN|RAINY Day|WHITE| (|BLUE|Torrencial|WHITE| + |YELLOW|Lightning|WHITE|).\nPowers: |PINK|Gum|WHITE|, |GHOST|Ghost|WHITE|, |PURPLE|Sleep|WHITE| & |GOLD|Revolver|WHITE| (100%).\nPower every 3 hits. Best of 3.",
                    "|RED|NIVEL 6: VARIANTE 1|WHITE|\n|CYAN|DÍA LLUVIOSO|WHITE| (|BLUE|Torrencial|WHITE| + |YELLOW|Relámpago|WHITE|).\nPoderes: |PINK|Chicle|WHITE|, |GHOST|Fantasma|WHITE|, |PURPLE|Sueño|WHITE| y |GOLD|Revólver|WHITE| (100%).\nPoder cada 3 toques. Al mejor de 3."
                )
            else:
                # Variante 2: Enable CLOUDY day, con TORRENCIAL size, Enable RAINY day pero solo lluvia basica (10mm)
                self.cloudy_day_enabled = True
                self.cloud_size_idx = 3 # TORRENCIAL (size 2.0)
                
                self.rainy_day_enabled = True
                self.lightning_enabled = False
                self.rain_drop_size_idx = 1 # Default (x1)
                self.rain_precipitation_idx = 1 # 10 mm
                
                # Planetas por defecto (no destructibles)
                self.floating_planets_enabled = True
                self.gravity_force_idx = 1 # Planet
                self.gravity_radius_idx = 3 # Planet (180)
                self.destructible_planets_enabled = False
                
                # TODOS los poderes activos (verde, chicle, revolver, sleeping, etc)
                self.remove_power_red = self.remove_power_green = self.remove_power_yellow = self.remove_power_orange = False
                self.magnet_power_enabled = True
                self.ghost_power_enabled = True
                self.gum_power_enabled = True
                self.sleeping_power_enabled = True
                self.revolver_enabled = True
                self.revolver_prob_idx = 1 # Default
                
                # solo esta activado el reloj violeta
                self.remove_blue = True
                self.remove_red = True
                self.remove_purple = False
                self.remove_white = True
                self.remove_yellow = True
                self.orange_watch_enabled = False
                
                # 2 portales activos
                self.portals_enabled = True
                self.more_portals_enabled = False
                self.portal_size_idx = 2 # Default (75)
                self._update_portal_rects()
                
                self.arcade_intro_text = self.t(
                    "|RED|LEVEL 6: VARIANT 2|WHITE|\n|PURPLE|Planets|WHITE|, |GRAY|CLOUDY Day|WHITE| (|BLUE|Torrencial|WHITE|) & |CYAN|Rainy|WHITE| (10mm).\n|GREEN|ALL|WHITE| Powers enabled. 2 |BLUE|POR|RED|TALS|WHITE| active.\nOnly |PURPLE|Purple Watch|WHITE| active (3 hits). Best of 3.",
                    "|RED|NIVEL 6: VARIANTE 2|WHITE|\n|PURPLE|Planetas|WHITE|, |GRAY|DÍA NUBLADO|WHITE| (|BLUE|Torrencial|WHITE|) y |CYAN|Lluvia|WHITE| (10mm).\n|GREEN|TODOS|WHITE| los poderes. 2 |BLUE|POR|RED|TALES|WHITE|.\nSolo |PURPLE|Reloj Violeta|WHITE| (cada 3 toques). Al mejor de 3."
                )
                
            self.start_with_power_enabled = True
            self.paddle1.grant_random_power(self)
            self.paddle2.grant_random_power(self)
            
            self.arcade_intro_timer = 6.0 
            self.arcade_intro_x = SCREEN_WIDTH + 500
            self.state = STATE_SERVE
            self.serve_timer = 6.0
            self.serve_direction = random.choice([1, -1])
            self.balls = [Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
            self.balls[0].serve(self.serve_direction, 300 * self.initial_ball_speed_options[self.initial_ball_speed_idx])

        elif level == 7:
            # --- NIVEL FINAL: BOSS BATTLE STYLE ---
            self.max_score = 6
            self.match_point_enabled = True
            self.show_match_point_anim = False
            self.show_golden_goal_anim = False
            self.experimental_golden_goal = True # Para que si se empata al final se decida por Gol de Oro
            
            # poderes/relojes cada 5 toques
            self.watch_spawn_hits_idx = 1 # 5 hits
            self.power_auto_grant_hits_idx = 1 # 5 hits
            
            # Velocidad inicial x1.0 (v0.7.2)
            self.initial_ball_speed_idx = 1 # Default (1.0)
            
            # Entorno Caótico: 4 Portales (FORZAR RECTÁNGULOS)
            self.portals_enabled = True
            self.more_portals_enabled = True
            self.portal_size_idx = 2 # Original (75)
            self._update_portal_rects()
            
            # TODOS los modificadores de EXTRAS activos (exceptuando el ratón)
            self.orange_watch_enabled = True
            self.start_x2_enabled = True
            self.magnet_power_enabled = True
            self.ghost_power_enabled = True
            self.ghost_identical_enabled = True
            self.gum_power_enabled = True
            self.experimental_golden_goal = True
            
            # Planetas flotantes destructibles
            self.floating_planets_enabled = True
            self.gravity_force_idx = 1 # Planet
            self.gravity_radius_idx = 3 # Planet (180)
            self.destructible_planets_enabled = True
            self.planet_resistance_idx = 1 # Planet (3 hits)
            
            self.add_mouse_enabled = False # Excluido
            self.sleeping_power_enabled = True
            
            # REVOLVER 100%
            self.revolver_enabled = True
            self.revolver_prob_idx = 3 # 100% / Always
            
            # Cloudy y Rainy day en default + Lightning
            self.cloudy_day_enabled = True
            self.cloud_size_idx = 1 # Default (Cloudy)
            
            self.rainy_day_enabled = True
            self.lightning_enabled = True
            self.rain_drop_size_idx = 1 # Default
            self.rain_precipitation_idx = 1 # 10 mm
            
            # Todos los relojes y poderes clásicos permitidos
            self.remove_blue = self.remove_red = self.remove_purple = self.remove_white = self.remove_yellow = False
            self.remove_power_red = self.remove_power_green = self.remove_power_yellow = self.remove_power_orange = False
            self.watches_kept_enabled = False
            self.encapsulate_powers_enabled = False
            
            self.start_with_power_enabled = True
            self.paddle1.grant_random_power(self)
            self.paddle2.grant_random_power(self)
            
            self.arcade_intro_text = self.t(
                "|RED|FINAL BOSS (LEVEL 7)|WHITE|\n4 |BLUE|POR|RED|TALS|WHITE|, |PURPLE|Destructible Planets|WHITE|, |CYAN|Extreme Weather|WHITE|.\n|GOLD|MATCH POINT|WHITE|, |YELLOW|X2|WHITE| & |RED|GOLDEN GOAL|WHITE|.\nPower every 5 hits. Win 6 points.",
                "|RED|BOSS FINAL (NIVEL 7)|WHITE|\n4 |BLUE|POR|RED|TALES|WHITE|, |PURPLE|Planetas Destructibles|WHITE|, |CYAN|Clima Extremo|WHITE|.\n|GOLD|MATCH POINT|WHITE|, |YELLOW|X2|WHITE| y |RED|GOL DE ORO|WHITE|.\nPoder cada 5 toques. Gana a 6 puntos."
            )
            self.arcade_intro_timer = 6.0 
            self.arcade_intro_x = SCREEN_WIDTH + 500
            
            self.state = STATE_SERVE
            self.serve_timer = 7.5
            self.serve_direction = random.choice([1, -1])
            self.balls = [Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
            self.balls[0].serve(self.serve_direction, 300 * self.initial_ball_speed_options[self.initial_ball_speed_idx])

    def handle_input(self, events, dt):
        if self.input_cooldown > 0:
            self.input_cooldown -= dt

        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.fingers[0] = event.pos # Simular dedo con el ratón
                self._handle_mouse_click(event)
            
            if event.type == pygame.FINGERDOWN:
                tx, ty = event.x * SCREEN_WIDTH, event.y * SCREEN_HEIGHT
                self.fingers[event.finger_id] = (tx, ty)
                # Simular clic para menús
                pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (int(tx), int(ty)), "button": 1}))

            if event.type == pygame.FINGERMOTION:
                tx, ty = event.x * SCREEN_WIDTH, event.y * SCREEN_HEIGHT
                self.fingers[event.finger_id] = (tx, ty)

            if event.type == pygame.FINGERUP:
                if event.finger_id in self.fingers:
                    tx, ty = self.fingers[event.finger_id]
                    del self.fingers[event.finger_id]
                    pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONUP, {"pos": (int(tx), int(ty)), "button": 1}))
            
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if 0 in self.fingers: del self.fingers[0]
                    self.is_dragging_scrollbar = False
                    self.is_dragging_volume = False
                    self.is_dragging_music_volume = False
                    self.is_dragging_settings_scrollbar = False
                    
            if event.type == pygame.MOUSEMOTION:
                if 0 in self.fingers: self.fingers[0] = event.pos
                self._handle_mouse_motion(event)
                if self.is_dragging_volume:
                    rel_x = max(0, min(event.pos[0] - self.volume_bar_rect.x, self.volume_bar_rect.width))
                    self.sfx_volume = rel_x / self.volume_bar_rect.width
                    self.audio.master_volume = self.sfx_volume
                elif self.is_dragging_music_volume:
                    rel_x = max(0, min(event.pos[0] - self.music_volume_bar_rect.x, self.music_volume_bar_rect.width))
                    self.music_volume = rel_x / self.music_volume_bar_rect.width
                    self.audio.set_music_volume(self.music_volume)
                elif self.is_dragging_settings_scrollbar:
                    self._handle_settings_scrollbar_drag(event)
                elif self.is_dragging_scrollbar:
                    self._handle_scrollbar_drag(event)

            # --- SCROLL CON RUEDA ---
            if event.type == pygame.MOUSEWHEEL:
                scroll_speed = 30
                if self.state == STATE_MODIFIERS:
                    self.scroll_y = max(0, min(self.scroll_y - event.y * scroll_speed, self.max_scroll))
                elif self.state == STATE_SETTINGS:
                    self.settings_scroll_y = max(0, min(self.settings_scroll_y - event.y * scroll_speed, self.settings_max_scroll))

            if event.type == pygame.KEYDOWN:
                # REGLA ESTRICTA (v0.7.0 Fix): El tutorial SOLO avanza si el juego está 'frenado' (No en PLAYING)
                if self.tutorial_active and self.state != STATE_PLAYING:
                    if event.key == pygame.K_SPACE or self.tutorial_step == 4:
                        self._next_tutorial_step()
                else:
                    self._handle_keydown(event)

        self._handle_continuous_input(dt)

    def _handle_mouse_click(self, event):
        if event.button != 1: return
        if self.input_cooldown > 0: return # Bloquear clics si estamos en cooldown
        
        # Activar cooldown para el próximo clic
        self.input_cooldown = 0.1
        
        # --- AVANCE DE TUTORIAL ARCADE POR CLIC (v0.7.2) ---
        if self.state == STATE_ARCADE_TUTORIAL:
            self._next_arcade_tutorial_step()
            return
            
        # --- AVANCE DE TUTORIAL POR CLIC (v0.7.0 Fix) ---
        # El tutorial avanza si no estamos jugando, O si estamos en las fases de explicación congeladas (14-28)
        is_frozen_gameplay = self.state == STATE_PLAYING and (14 <= self.tutorial_step <= 28)
        if self.tutorial_active and (self.state != STATE_PLAYING or is_frozen_gameplay):
            # BLOQUEO: Si el paso requiere un botón específico, solo avanzamos si pulsan ese botón
            btn_steps = {
                1: self.btn_settings_rect,
                2: self.settings_apply_btn_rect,
                3: self.btn_modifiers_rect,
                5: self.tab_extras_rect,
                6: self.tab_skins_rect,
                8: self.settings_back_btn_rect,
                9: self.btn_play_rect,
                10: self.btn_solo_rect
            }
            
            if self.tutorial_step in btn_steps:
                # Si el clic es sobre el botón que el tutorial pide, NO interceptar para dejar que el botón funcione
                if btn_steps[self.tutorial_step].collidepoint(event.pos):
                    pass # Dejar que el botón maneje su clic y llame a _next_tutorial_step() si corresponde
                else:
                    # En pasos de botón, si tocan la caja de texto abajo, permitimos avanzar el TEXTO (pero no el paso)
                    if event.pos[1] > SCREEN_HEIGHT - 100:
                        if self.tutorial_text_visible != self.tutorial_text_full:
                            self.tutorial_text_visible = self.tutorial_text_full
                            return
            else:
                # Pasos informativos: Cualquier clic/toque en la pantalla avanza
                # (A menos que sea el botón de volver en los menús que no es el paso actual)
                self._next_tutorial_step()
                return
        if self.mobile_mode and self.state in [STATE_PLAYING, STATE_SERVE]:
            if self.btn_p1_power.collidepoint(event.pos): self.activate_paddle_power(self.paddle1, 1)
            if not self.is_ai_mode and self.btn_p2_power.collidepoint(event.pos): self.activate_paddle_power(self.paddle2, 2)

        if self.state == STATE_MAIN_MENU:
            if self.show_tutorial_prompt:
                if self.btn_tutorial_no_rect.collidepoint(event.pos):
                    self.audio.play('hit')
                    self.show_tutorial_prompt = False
                    self.first_time_playing = False
                    self.save_progress() # Guardar que ya no es primera vez
                elif self.btn_tutorial_yes_rect.collidepoint(event.pos):
                    self.audio.play('hit')
                    self.show_tutorial_prompt = False
                    self.tutorial_active = True
                    self.first_time_playing = False
                    self.save_progress() # Guardar
                    self._start_tutorial_step(0)
                return

            if self.btn_play_rect.collidepoint(event.pos):
                if self.tutorial_active and self.tutorial_step != 9: return # Bloqueado
                self.audio.play('hit')
                if self.tutorial_active and self.tutorial_step == 9:
                    self.is_ai_mode = True # 1. Contra IA correctamente
                    self.reset_game()
                    self.global_hits = 0 # RESETEAR GOLPES PARA EVITAR APARICION INSTANTANEA
                    self.state = STATE_SERVE 
                    # 4. Forzar paletas blancas y sin poder
                    self.paddle1.power_active = POWER_NONE
                    self.paddle1.power_stored = POWER_NONE
                    self.paddle1.color = WHITE
                    self.paddle2.power_active = POWER_NONE
                    self.paddle2.power_stored = POWER_NONE
                    self.paddle2.color = WHITE
                    self._start_tutorial_step(11)
                else:
                    self.state = STATE_MODE_SELECTION
            elif self.btn_modifiers_rect.collidepoint(event.pos):
                if self.tutorial_active and self.tutorial_step != 3: return # Bloqueado en tutorial
                self.audio.play('hit')
                self.state = STATE_MODIFIERS
                if self.tutorial_active and self.tutorial_step == 3: self._start_tutorial_step(5)
            elif self.btn_credits_rect.collidepoint(event.pos):
                self.audio.play('hit')
                self.state = STATE_CREDITS
                self.modifiers_tab = "ALL"
                self.scroll_y = 0
            elif self.btn_settings_rect.collidepoint(event.pos):
                # EXCEPCIÓN: Permitido en el paso 1 del tutorial
                if self.tutorial_active and self.tutorial_step != 1: return 
                
                self.audio.play('hit')
                self.state = STATE_SETTINGS
                self.settings_scroll_y = 0
                if self.tutorial_active: self._start_tutorial_step(2)
                # Crear backup para poder cancelar cambios con BACK
                self.settings_backup = {
                    "lang": self.language,
                    "vfx": self.vfx_enabled,
                    "vol": self.sfx_volume,
                    "music": self.music_enabled,
                    "mvol": self.music_volume,
                    "m_match": self.music_in_match,
                    "shake": self.shake_enabled,
                    "fullscreen": self.fullscreen_enabled # v0.7.0 Fix
                }
            elif self.btn_tutorial_help_rect.collidepoint(event.pos):
                if not self.tutorial_active:
                    self.audio.play('hit')
                    self.show_tutorial_prompt = True
        
        elif self.state == STATE_MODIFIERS:
            if self.scrollbar_thumb_rect.collidepoint(event.pos):
                self.is_dragging_scrollbar = True
                self.scroll_offset_y = event.pos[1] - self.scrollbar_thumb_rect.y
            elif self.back_btn_rect.collidepoint(event.pos):
                if self.tutorial_active and self.tutorial_step != 8: return # Bloqueado si no es el paso 8
                self.audio.play('hit'); self.state = STATE_MAIN_MENU; self.scroll_y = 0
                if self.tutorial_active and self.tutorial_step == 8: self._start_tutorial_step(9)
                self.mouse = None # Limpiar ratón al salir
                self.scrollbar_thumb_rect.y = self.scrollbar_rect.y
                self.remove_watches_expanded = False
            
            # Pestañas
            elif self.tab_all_rect.collidepoint(event.pos):
                if self.tutorial_active and self.tutorial_step >= 4: return # Bloqueado
                if self.modifiers_tab != "ALL": self.audio.play('hit'); self.modifiers_tab = "ALL"; self.scroll_y = 0
            elif self.tab_extras_rect.collidepoint(event.pos):
                if self.tutorial_active and self.tutorial_step != 5: return # Solo permitido en paso 5
                if self.modifiers_tab != "EXTRAS": self.audio.play('hit'); self.modifiers_tab = "EXTRAS"; self.scroll_y = 0
                if self.tutorial_active and self.tutorial_step == 5: self._start_tutorial_step(6)
            elif self.tab_skins_rect.collidepoint(event.pos):
                if self.tutorial_active and self.tutorial_step != 6: return # Solo paso 6
                if self.modifiers_tab != "SKINS": self.audio.play('hit'); self.modifiers_tab = "SKINS"; self.scroll_y = 0
                if self.tutorial_active and self.tutorial_step == 6: self._start_tutorial_step(7)
            
            # Contenido del panel
            elif self.modifiers_panel_rect.collidepoint(event.pos):
                if self.tutorial_active: return # BLOQUEO TOTAL EN TUTORIAL para el contenido
                
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
                self.state = STATE_SOLO_SUBMODE_SELECTION # Nuevo flujo v0.6.0
            elif self.back_btn_rect.collidepoint(event.pos):
                self.audio.play('hit')
                self.state = STATE_MAIN_MENU
        elif self.state == STATE_SOLO_SUBMODE_SELECTION:
            # === 1. POSICIONAMIENTO DE BOTONES (Se ejecuta siempre al entrar) ===
            if self.arcade_completed:
                self.btn_endless_rect.y = self.btn_arcade_level_selector_rect.bottom + 15
            else:
                self.btn_endless_rect.y = SCREEN_HEIGHT // 2 + 50

            self.btn_help_endless_rect.x = self.btn_endless_rect.right + 10
            self.btn_help_endless_rect.y = self.btn_endless_rect.y + 5

           # === EVALUACIÓN DE CLICS (ADENTRO DEL SUBMENÚ) ===
            
            # PRIORIDAD 1: El botón exclusivo de volver (¡Ahora sí!)
            if self.btn_solo_sub_back_rect.collidepoint(event.pos):
                self.audio.play('hit')
                self.state = STATE_MAIN_MENU
                
           # PRIORIDAD 2: El botón de ayuda de ARCADE
            elif self.btn_arcade_tutorial_help_rect.collidepoint(event.pos):
                self.audio.play('pop')
                self.state = STATE_ARCADE_TUTORIAL
                
                # Vaciamos los textos por si quedó algo de la vez anterior
                self.tutorial_text_visible = ""
                self.tutorial_text_full = ""
                
                self.arcade_tutorial_step = 0  # <--- Empezamos en 0
                self._next_arcade_tutorial_step()  # Al llamar a la función, le suma 1 y cae PERFECTO en el Paso 1

            # PRIORIDAD 3: Si la ayuda de Endless estaba abierta, cualquier otro clic la cierra
            elif self.show_endless_help:
                self.show_endless_help = False

            # PRIORIDAD 4: Si toca el botón (?) de ENDLESS, se abre su ayuda
            elif self.btn_help_endless_rect.collidepoint(event.pos):
                self.show_endless_help = True

            # PRIORIDAD 5: Los modos de juego
            elif self.btn_classic_rect.collidepoint(event.pos):
                self.audio.play('hit')
                self.state = STATE_PRESS_TO_START
                
            elif self.btn_arcade_rect.collidepoint(event.pos):
                self.audio.play('hit')
                start_lvl = self.test_arcade_level if self.arcade_completed else 1
                self.start_arcade_level(start_lvl)
                
            elif self.btn_endless_rect.collidepoint(event.pos):
                self.audio.play('hit')
                self.start_endless_mode()
               # Sincronizar la posición del botón ENDLESS según si el test LEVEL está desbloqueado
            if self.arcade_completed:
                self.btn_endless_rect.y = self.btn_arcade_level_selector_rect.bottom + 15
            else:
                self.btn_endless_rect.y = SCREEN_HEIGHT // 2 + 50

            # Sincronizar la posición del botón amarillo (?)
            self.btn_help_endless_rect.x = self.btn_endless_rect.right + 10
            self.btn_help_endless_rect.y = self.btn_endless_rect.y + 5

# === EVALUACIÓN DE CLICS (ADENTRO DEL SUBMENÚ) ===
            
            # PRIORIDAD 1: El botón exclusivo de volver
            if self.btn_solo_sub_back_rect.collidepoint(event.pos):
                self.audio.play('hit')
                self.state = STATE_MAIN_MENU
                
            # PRIORIDAD 2: El botón de ayuda de ARCADE
            elif self.btn_arcade_tutorial_help_rect.collidepoint(event.pos):
                self.audio.play('pop')
                self.state = STATE_ARCADE_TUTORIAL
                self.tutorial_text_visible = ""
                self.tutorial_text_full = ""
                self.arcade_tutorial_step = 0
                self._next_arcade_tutorial_step()

            elif self.btn_help_endless_rect.collidepoint(event.pos):
                 self.audio.play('pop')
                 self.state = STATE_ENDLESS_TUTORIAL

            # Limpiamos los textos viejos y disparamos el paso 1
                 self.tutorial_text_visible = ""
                 self.tutorial_text_full = ""
                 self.endless_tutorial_step = 0
                 self._next_endless_tutorial_step()

            # PRIORIDAD 4: Los botones para iniciar los modos de juego
            elif self.btn_classic_rect.collidepoint(event.pos):
                self.audio.play('hit')
                self.state = STATE_PRESS_TO_START
                
            elif self.btn_arcade_rect.collidepoint(event.pos):
                self.audio.play('hit')
                start_lvl = self.test_arcade_level if self.arcade_completed else 1
                self.start_arcade_level(start_lvl)
                
            elif self.btn_endless_rect.collidepoint(event.pos):
                self.audio.play('hit')
                self.start_endless_mode()
                self.arcade_tutorial_step = 0
                self.tutorial_text_visible = ""
                self.tutorial_text_index = 0
                press = "|GRAY|" + (self.t("(touch the screen).", "(toca la pantalla).") if self.mobile_mode else self.t("(press space).", "(presiona espacio)."))
                self.tutorial_text_full = self.t("This is ARCADE mode; there are 7 levels that you must complete in one go. ", "Este es el modo ARCADE; hay 7 niveles que debes completar de una sola vez. ") + press
        elif self.arcade_completed and self.btn_arcade_level_selector_rect.collidepoint(event.pos):
                self.audio.play('hit')
                self.test_arcade_level = (self.test_arcade_level % 7) + 1
        elif self.btn_solo_sub_back_rect.collidepoint(event.pos):
                self.audio.play('hit')
                self.state = STATE_MODE_SELECTION
        
        elif self.state == STATE_SETTINGS:
            if self.settings_back_btn_rect.collidepoint(event.pos):
                if self.tutorial_active: return # Bloqueado en tutorial
                self.audio.play('hit')
                # Restaurar backup (Descartar cambios)
                self.language = self.settings_backup["lang"]
                self.music_enabled = self.settings_backup["music"]
                self.music_volume = self.settings_backup["mvol"]
                self.music_in_match = self.settings_backup["m_match"]
                self.audio.set_music_volume(self.music_volume)
                if self.music_enabled: self.audio.play_music('menu_music.wav', volume=self.music_volume)
                else: self.audio.stop_music()
                self.shake_enabled = self.settings_backup["shake"]
                self.fullscreen_enabled = self.settings_backup["fullscreen"] # v0.7.0 Fix
                self.state = STATE_MAIN_MENU
            elif self.lang_rect.collidepoint(event.pos):
                self.audio.play('hit'); self.language = "EN" if self.language == "ES" else "ES"
                if self.tutorial_active:
                    # Refrescar el texto completo pero sin reiniciar el visible para evitar saltos bruscos
                    # aunque es mejor reiniciar para que la frase tenga sentido completa.
                    self._start_tutorial_step(self.tutorial_step)
            elif self.vfx_rect.collidepoint(event.pos):
                if self.tutorial_active: return # Bloqueado en tutorial
                self.audio.play('hit'); self.vfx_enabled = not self.vfx_enabled
            elif self.volume_bar_rect.collidepoint(event.pos) or self.volume_handle_rect.collidepoint(event.pos):
                if self.tutorial_active: return # Bloqueado en tutorial
                self.is_dragging_volume = True
                # Actualizar posición inmediata
                rel_x = max(0, min(event.pos[0] - self.volume_bar_rect.x, self.volume_bar_rect.width))
                self.sfx_volume = rel_x / self.volume_bar_rect.width
                self.audio.master_volume = self.sfx_volume
            elif self.music_rect.collidepoint(event.pos):
                self.audio.play('hit'); self.music_enabled = not self.music_enabled
                if self.music_enabled: self.audio.play_music('menu_music.wav', volume=self.music_volume)
                else: self.audio.stop_music()
            elif self.music_enabled and (self.music_volume_bar_rect.collidepoint(event.pos) or self.music_volume_handle_rect.collidepoint(event.pos)):
                self.is_dragging_music_volume = True
                rel_x = max(0, min(event.pos[0] - self.music_volume_bar_rect.x, self.music_volume_bar_rect.width))
                self.music_volume = rel_x / self.music_volume_bar_rect.width
                self.audio.set_music_volume(self.music_volume)
            elif self.music_enabled and self.music_in_match_rect.collidepoint(event.pos):
                self.audio.play('hit'); self.music_in_match = not self.music_in_match
            elif self.shake_rect.collidepoint(event.pos):
                if self.tutorial_active: return # Bloqueado en tutorial
                self.audio.play('hit'); self.shake_enabled = not self.shake_enabled
            elif self.fullscreen_rect.collidepoint(event.pos):
                self.audio.play('hit'); self.fullscreen_enabled = not self.fullscreen_enabled
            elif self.mobile_controls_toggle_rect.collidepoint(event.pos):
                self.audio.play('hit'); self.mobile_mode = not self.mobile_mode
            elif self.mobile_mode and self.geo_controls_rect.collidepoint(event.pos):
                self.audio.play('hit'); self.geographic_controls = not self.geographic_controls
            elif self.settings_apply_btn_rect.collidepoint(event.pos):
                self.audio.play('hit')
                
                # --- APLICAR PANTALLA COMPLETA (v0.7.0 Fix) ---
                # Solo aplicar si ha cambiado respecto al estado real actual de la ventana
                is_currently_fs = (pygame.display.get_surface().get_flags() & pygame.FULLSCREEN) != 0
                if self.fullscreen_enabled != is_currently_fs and sys.platform != "emscripten":
                    pygame.display.toggle_fullscreen()
                
                self.state = STATE_MAIN_MENU
                if self.tutorial_active and self.tutorial_step == 2:
                    self._start_tutorial_step(3)
            elif self.settings_scrollbar_rect.collidepoint(event.pos) or self.settings_scrollbar_thumb_rect.collidepoint(event.pos):
                self.is_dragging_settings_scrollbar = True
                self._handle_settings_scrollbar_drag(event)
        elif self.state == STATE_CREDITS:
            if self.back_btn_rect.collidepoint(event.pos):
                self.audio.play('hit'); self.state = STATE_MAIN_MENU

        elif self.state == STATE_ENDLESS_REWARD:
            self._advance_endless_reward()

        elif self.state == STATE_GAME_OVER:
            if self.tutorial_active: return 
            
            # Modo Arcade Nivel 7: Solo botón de recompensa (v0.7.3)
            is_level_7_win = self.arcade_active and int(self.arcade_level) == 7 and self.score1 > self.score2
            
            if is_level_7_win:
                if self.btn_gameover_restart.collidepoint(event.pos):
                    # Sonido quitado por petición del usuario (v0.6.0)
                    self.state = STATE_ARCADE_REWARD
                    self.reward_step = 0
                    self._init_reward_text()
            else:
                if self.btn_gameover_restart.collidepoint(event.pos):
                    self.audio.play('hit')
                    if self.endless_active:
                        if self.score1 > self.score2:
                            self.endless_level += 1
                        else:
                            self.endless_level = 1
                            self.endless_active_modifiers = []
                        self.generate_next_endless_modifier()
                        self.reset_game(skip_announcement=True)
                        self.endless_intro_timer = 4.0 + (self.endless_level - 1)
                        self.endless_intro_x = SCREEN_WIDTH + 400
                        self.serve_timer = self.endless_intro_timer + 1.0
                        self.serve_direction = random.choice([1, -1])
                        self.state = STATE_SERVE
                        self.balls[0].serve(self.serve_direction, 300 * self.initial_ball_speed_options[self.initial_ball_speed_idx])
                    elif self.arcade_active:
                        if self.score1 > self.score2:
                            self.arcade_level += 1
                            self.start_arcade_level(self.arcade_level)
                        else:
                            self.start_arcade_level(1)
                    else:
                        self.score1 = self.score2 = 0
                        self.state = STATE_PRESS_TO_START
                elif self.btn_gameover_menu.collidepoint(event.pos):
                    self.audio.play('hit')
                    if self.endless_active:
                        self._reset_modifiers()
                        self.endless_active = False
                    elif self.arcade_active:
                        self._reset_modifiers()
                        self.arcade_active = False
                    self.reset_game(skip_announcement=True)
                    self.state = STATE_MAIN_MENU
                    self.show_match_point_anim = self.show_golden_goal_anim = False

        elif self.state == STATE_PRESS_TO_START:
            self.audio.play('hit')
            self.reset_game()
        
        elif self.state == STATE_SERVE:
            # En el saque, cualquier toque/clic lanza la bola (v0.7.0)
            if not (self.tutorial_active and self.tutorial_step in [11, 12, 13]):
                self.serve_timer = 0

        elif self.state == STATE_ARCADE_REWARD:
            self._advance_arcade_reward()

    def _handle_modifier_clicks(self, event):
        if self.modifiers_tab == "SKINS":
            if self.orange_skin_rect.collidepoint(event.pos):
                self.audio.play('hit'); self.orange_skin_idx = (self.orange_skin_idx + 1) % len(self.orange_skin_options)
            elif self.yellow_watch_skin_rect.collidepoint(event.pos):
                self.audio.play('hit'); self.yellow_watch_skin_idx = (self.yellow_watch_skin_idx + 1) % len(self.yellow_watch_skin_options)
            elif self.ball_skin_rect.collidepoint(event.pos):
                self.audio.play('hit'); self.ball_skin_idx = (self.ball_skin_idx + 1) % len(self.ball_skin_options)
            elif self.arcade_completed and self.crown_hat_rect.collidepoint(event.pos):
                self.audio.play('hit'); self.crown_hat_idx = (self.crown_hat_idx + 1) % len(self.crown_hat_options)
                self.save_progress() # Guardar selección cosmética
        
        elif self.modifiers_tab == "ALL":
            if self.score_btn_rect.collidepoint(event.pos):
                self.audio.play('hit')
                self.max_score = 3 if self.max_score == 1 else (6 if self.max_score == 3 else (9 if self.max_score == 6 else 1))
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
        if self.endless_chaos_rect.collidepoint(event.pos) or self.endless_chaos_text_rect.collidepoint(event.pos):
            if getattr(self, "endless_chaos_unlocked", False):
                self.audio.play('pop')
                self.endless_chaos_enabled = not self.endless_chaos_enabled
        elif self.endless_chaos_enabled and self.endless_chaos_amount_rect.collidepoint(event.pos):
            if getattr(self, "endless_chaos_unlocked", False):
                self.audio.play('pop')
                self.endless_chaos_idx = (self.endless_chaos_idx + 1) % len(self.endless_chaos_options)
        elif self.endless_chaos_enabled and (self.endless_chaos_accumulation_rect.collidepoint(event.pos) or self.endless_chaos_accumulation_text_rect.collidepoint(event.pos)):
            if getattr(self, "endless_chaos_unlocked", False):
                self.audio.play('pop')
                self.endless_chaos_accumulation = not self.endless_chaos_accumulation
        elif self.tictactoe_rect.collidepoint(event.pos) or self.tictactoe_text_rect.collidepoint(event.pos): self.audio.play('pop'); self.tictactoe_enabled = not self.tictactoe_enabled
        elif self.orange_watch_rect.collidepoint(event.pos) or self.orange_watch_text_rect.collidepoint(event.pos): self.audio.play('pop'); self.orange_watch_enabled = not self.orange_watch_enabled
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
        elif self.sleeping_power_rect.collidepoint(event.pos) or self.sleeping_power_text_rect.collidepoint(event.pos):
            self.audio.play('pop'); self.sleeping_power_enabled = not self.sleeping_power_enabled
        elif self.cloudy_day_rect.collidepoint(event.pos) or self.cloudy_day_text_rect.collidepoint(event.pos):
            self.audio.play('pop'); self.cloudy_day_enabled = not self.cloudy_day_enabled
        elif self.cloudy_day_enabled and self.cloud_size_rect.collidepoint(event.pos):
            self.audio.play('pop'); self.cloud_size_idx = (self.cloud_size_idx + 1) % len(self.cloud_size_options)
        elif self.rainy_day_rect.collidepoint(event.pos) or self.rainy_day_text_rect.collidepoint(event.pos):
            self.audio.play('pop'); self.rainy_day_enabled = not self.rainy_day_enabled
        elif self.rainy_day_enabled and self.rain_drop_size_rect.collidepoint(event.pos):
            self.audio.play('pop'); self.rain_drop_size_idx = (self.rain_drop_size_idx + 1) % len(self.rain_drop_size_options)
        elif self.rainy_day_enabled and self.rain_precipitation_rect.collidepoint(event.pos):
            self.audio.play('pop'); self.rain_precipitation_idx = (self.rain_precipitation_idx + 1) % len(self.rain_precipitation_options)
        elif self.rainy_day_enabled and (self.lightning_rect.collidepoint(event.pos) or self.lightning_text_rect.collidepoint(event.pos)):
            self.audio.play('pop'); self.lightning_enabled = not self.lightning_enabled
        
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
            
    def _handle_scrollbar_drag(self, event):
        rel_y = max(0, min(event.pos[1] - self.scrollbar_rect.y, self.scrollbar_rect.height))
        scroll_pct = rel_y / self.scrollbar_rect.height
        self.scroll_y = scroll_pct * self.max_scroll

    def _handle_settings_scrollbar_drag(self, event):
        rel_y = max(0, min(event.pos[1] - self.settings_scrollbar_rect.y, self.settings_scrollbar_rect.height))
        scroll_pct = rel_y / self.settings_scrollbar_rect.height
        self.settings_scroll_y = scroll_pct * self.settings_max_scroll

    def _handle_mouse_motion(self, event):
        mpos = event.pos
        current_hover = None
        
        # 1. Detectar sobre qué botón estamos según el estado
        if self.state == STATE_MAIN_MENU:
            for r in [self.btn_play_rect, self.btn_modifiers_rect, self.btn_settings_rect, self.btn_tutorial_help_rect]:
                if r.collidepoint(mpos): current_hover = r
        elif self.state == STATE_MODIFIERS:
            if self.back_btn_rect.collidepoint(mpos): current_hover = self.back_btn_rect
        elif self.state == STATE_SETTINGS:
            # Solo detectamos hover para el botón de volver en settings si queremos, 
            # pero el usuario pidió silenciar los botones DENTRO de settings.
            pass
        elif self.state == STATE_SOLO_SUBMODE_SELECTION:
            # Ponemos en una lista todos los botones de esta pantalla
            botones_submenu = [
                self.btn_classic_rect, 
                self.btn_arcade_rect, 
                self.btn_endless_rect, 
                self.btn_solo_sub_back_rect,
                self.btn_help_endless_rect,
                self.btn_arcade_tutorial_help_rect
            ]
            # Si el mouse está sobre cualquiera de ellos, lo marcamos como el hover actual
            for r in botones_submenu:
                if r.collidepoint(mpos):
                    current_hover = r        
        
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

    def _handle_mouse_wheel(self, event):
        if self.state == STATE_MODIFIERS:
            self.scroll_y -= event.y * 30
            self.scroll_y = max(0, min(self.scroll_y, self.max_scroll))

    def _handle_keydown(self, event):
        if self.state == STATE_ARCADE_TUTORIAL:
            if event.key == pygame.K_SPACE:
                self._next_arcade_tutorial_step()
            return
        
        elif self.state == STATE_ENDLESS_TUTORIAL:
            self._next_endless_tutorial_step()
        if self.state == STATE_ARCADE_REWARD:
            if event.key == pygame.K_SPACE:
                self._advance_arcade_reward()
            return

        if self.state == STATE_ENDLESS_REWARD:
            if event.key == pygame.K_SPACE:
                self._advance_endless_reward()
            return

        if self.tutorial_active:
            # Solo avanzar si es Espacio
            if event.key == pygame.K_SPACE:
                self._next_tutorial_step()
            
            # Permitir activación de poderes en el tutorial (solo si no está pausado por texto)
            if self.state == STATE_PLAYING:
                if self.tutorial_active and 14 <= self.tutorial_step <= 28:
                    return
                if event.key == pygame.K_d: self.activate_paddle_power(self.paddle1, 1)
                if event.key == pygame.K_RIGHT: self.activate_paddle_power(self.paddle2, 2)
            return
            
        if self.state == STATE_PRESS_TO_START and event.key == pygame.K_SPACE:
            self.audio.play('hit')
            self.reset_game()
        elif self.state == STATE_SERVE and event.key == pygame.K_SPACE:
            # Mantener la funcionalidad de saltar el saque si se desea, pero el texto visual ya no estará aquí.
            if not (self.tutorial_active and self.tutorial_step in [11, 12, 13]):
                self.serve_timer = 0
        elif self.state == STATE_PLAYING:
            if event.key == pygame.K_d: self.activate_paddle_power(self.paddle1, 1)
            # Solo permitir activar poder si no es la IA (v0.6.0 Fix)
            if not self.is_ai_mode and event.key == pygame.K_RIGHT: self.activate_paddle_power(self.paddle2, 2)

    def _handle_continuous_input(self, dt):
        keys = pygame.key.get_pressed()
        if self.state in [STATE_PLAYING, STATE_SERVE, STATE_GAME_OVER]:
            # BLOQUEO DE MOVIMIENTO EN TUTORIAL PAUSADO (Pasos con manto negro)
            if self.tutorial_active and 14 <= self.tutorial_step <= 27:
                return

            p_speed = 400 # PADDLE_SPEED
            if keys[pygame.K_w]: self.paddle1.move(-1, dt, p_speed)
            if keys[pygame.K_s]: self.paddle1.move(1, dt, p_speed)
            
            # --- MOVIMIENTO MÓVIL (v0.7.0) ---
            if self.mobile_mode:
                for fx, fy in self.fingers.values():
                    if self.geographic_controls:
                        # Control Geográfico: Mover hacia el punto tocado
                        if fx < SCREEN_WIDTH // 2: # Lado Jugador 1
                            # Evitar mover si estamos tocando el botón de poder
                            if not self.btn_p1_power.collidepoint(fx, fy):
                                target_y = fy
                                dy = target_y - self.paddle1.rect.centery
                                if abs(dy) > 5:
                                    move_step = p_speed * dt
                                    if abs(dy) < move_step:
                                        self.paddle1.rect.centery = target_y
                                    else:
                                        self.paddle1.move(1 if dy > 0 else -1, dt, p_speed)
                        else: # Lado Jugador 2
                            if not self.is_ai_mode and not self.btn_p2_power.collidepoint(fx, fy):
                                target_y = fy
                                dy = target_y - self.paddle2.rect.centery
                                if abs(dy) > 5:
                                    move_step = p_speed * dt
                                    if abs(dy) < move_step:
                                        self.paddle2.rect.centery = target_y
                                    else:
                                        self.paddle2.move(1 if dy > 0 else -1, dt, p_speed)
                    else:
                        # Control Clásico (Botones)
                        if self.btn_p1_up.collidepoint(fx, fy): self.paddle1.move(-1, dt, p_speed)
                        if self.btn_p1_down.collidepoint(fx, fy): self.paddle1.move(1, dt, p_speed)
                        # Jugador 2
                        if not self.is_ai_mode:
                            if self.btn_p2_up.collidepoint(fx, fy): self.paddle2.move(-1, dt, p_speed)
                            if self.btn_p2_down.collidepoint(fx, fy): self.paddle2.move(1, dt, p_speed)

            # Bloqueo de controles manuales para la IA (v0.6.0 Fix)
            if not self.is_ai_mode:
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
            # Destruir paleta visualmente (v0.6.0 Fix: Letalidad absoluta)
            paddle.is_destroyed = True
            self.vfx.explosion(paddle.rect.centerx, paddle.rect.centery, YELLOW)
            
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
            # Destruir paleta visualmente (v0.6.0 Fix: Letalidad absoluta)
            paddle.is_destroyed = True
            self.vfx.explosion(paddle.rect.centerx, paddle.rect.centery, BROWN)
            self.trigger_shake(15, 0.6) # Gran impacto
            
            # Penalización: El oponente gana el punto
            scoring_player = 2 if paddle == self.paddle1 else 1
            self.goal_scored(scoring_player)
            return
            
        self.audio.play('pop'); self.last_hitter = 1 if paddle == self.paddle1 else 2
        # Decrementar penalización de sueño si existe (v0.6.0)
        if paddle.sleep_hits_left > 0:
            paddle.sleep_hits_left -= 1
            if paddle.sleep_hits_left <= 0:
                self.vfx.burst(paddle.rect.centerx, paddle.rect.centery, WHITE)
                
        self.mouse_hits_counter += 1
        if ball.is_fireball:
            ball.is_fireball = False; self.reset_ball_visuals(ball); ball.speed /= 2; self.audio.fadeout('fire', 500)

        ball.speed *= self.ball_speed_multiplier_options[self.ball_speed_multiplier_idx]
        
        if not (paddle.power_active == POWER_SHIELD or paddle.white_zone_hits_left > 0):
            paddle.hits += 1
            # TUTORIAL: Forzar 7 toques para el poder
            req = 7 if self.tutorial_active else self.power_auto_grant_hits_options[self.power_auto_grant_hits_idx]
            
            if self.reroll_enabled:
                if paddle.power_stored == POWER_SPEED:
                    paddle.yellow_power_hits += 1
                    if paddle.yellow_power_hits >= 2: paddle.grant_random_power(self); paddle.yellow_power_hits = 0
                elif paddle.power_stored == POWER_ORANGE:
                    paddle.orange_power_hits += 1
                    if paddle.orange_power_hits >= 2: paddle.grant_random_power(self); paddle.orange_power_hits = 0

            req = self.power_auto_grant_hits_options[self.power_auto_grant_hits_idx]
            
            # Reloj Púrpura (Efecto especial: Meditación - Poder por quedarse quieto)
            if self.watches_kept_enabled:
                is_purple = (self.p1_zone_type == 3) if paddle == self.paddle1 else (self.p2_zone_type == 3)
            else:
                is_purple = (self.zone_type == 3 and self.slow_zone_owner == (1 if paddle == self.paddle1 else 2))
            
            got_power = False
            # Bloqueo de Re-roll para SLEEP (No sobrescribir si ya lo tenemos)
            if paddle.power_stored == POWER_SLEEP:
                pass 
            elif is_purple:
                # Mecánica v0.7.2: Bajo el reloj violeta, la paleta no recibe poderes por golpes.
                # Se obtienen quedándose completamente quieto por 5 segundos.
                pass
            elif paddle.hits >= req:
                paddle.grant_random_power(self)
                paddle.hits = 0
                got_power = True

            # TUTORIAL: Disparar el paso 22 al obtener el primer poder
            if got_power and self.tutorial_active and paddle == self.paddle1 and self.tutorial_step == 215:
                self._start_tutorial_step(22)

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
            
            # TUTORIAL: Forzar aparición a los 10 toques
            req = 10 if self.tutorial_active else self.watch_spawn_hits_options[self.watch_spawn_hits_idx]
            
            if self.global_hits >= req:
                self.global_hits = 0
                self.spawn_random_watch()
                
                # TUTORIAL: Disparar Paso 14 al salir el reloj
                if self.tutorial_active and self.tutorial_step == 135:
                    self._start_tutorial_step(14)
                # Chance dinámica de Revólver al salir un reloj
                prob = self.revolver_prob_options[self.revolver_prob_idx]
                if self.revolver_enabled and not self.revolver_item_active and random.random() < prob:
                    self.revolver_item_active = True
                    self.revolver_angle = 0.0

    def reset_ball_visuals(self, ball):
        ball.is_orange = False
        ball.is_fireball = False
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
        if not avail: return
        
        self.hourglass_rect = pygame.Rect(SCREEN_WIDTH//2 - 15, SCREEN_HEIGHT//2 - 20, 30, 40)
        self.is_x2_item_active = False
        if self.equal_watches_enabled: self.hourglass_type = random.choice([w[0] for w in avail])
        else:
            total = sum(w[1] for w in avail)
            r, acc = random.random() * total, 0
            for w, weight in avail:
                acc += weight
                if r <= acc: self.hourglass_type = w; break
        
        # TUTORIAL: Forzar reloj AZUL (Tipo 1) SOLAMENTE para el primer reloj
        if self.tutorial_active and getattr(self, 'tutorial_first_watch_spawned', False) == False:
            self.hourglass_type = 1
            self.tutorial_first_watch_spawned = True
    def activate_paddle_power(self, paddle, owner):
        if paddle.power_active in [POWER_SHIELD, POWER_MAGNET]:
            return
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
            
            # Desactivar revólver al agotar balas (v0.6.0)
            if paddle.revolver_shots_left <= 0:
                paddle.power_active = POWER_NONE
                paddle.color = WHITE
                self.audio.stop('fire') # Por si acaso
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
                self.gum_projectiles.append(GumProjectile(px, paddle.rect.centery, dir_x, paddle))
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
        elif paddle.power_active == POWER_SLEEP:
            from entities import SleepProjectile
            self.audio.play('sleep_shoot') # v0.6.0 Fix: Nuevo sonido
            px = paddle.rect.right if owner == 1 else paddle.rect.left
            dir_x = 1 if owner == 1 else -1
            # Lanzar gran proyectil inicial (v0.6.0 Fix: 2.5x speed)
            base_speed = 300 * self.initial_ball_speed_options[self.initial_ball_speed_idx]
            proj = SleepProjectile(px, paddle.rect.centery, base_speed * 2.5 * dir_x, 0, is_child=False)
            proj.owner_immunity = 0.2
            proj.owner_ref = paddle
            self.sleep_projectiles.append(proj)
            paddle.power_active = POWER_NONE
            paddle.color = WHITE
        else:
            paddle.activate_power(self)

    def _reset_round_state(self):
        # Detener sonidos de bucle
        self.audio.stop('fire')
        self.audio.stop('ghost') # Por si acaso
        self.audio.fadeout('rainy', 1000)
        self.rain_sound_playing = False
        
        # Reset global round variables (relojes, zonas, multiplicadores)
        self.global_hits = 0
        self.clouds = []
        self.rain_drops = []
        self.rain_timer = 0.0
        self.cloud_spawn_timer = 0
        self.hourglass_rect = None
        self.is_x2_item_active = False
        self.pending_x2_spawn = False
        self.zone_type = self.slow_zone_owner = self.p1_zone_type = self.p2_zone_type = self.last_hitter = 0
        self.planet1_alive = self.planet2_alive = True
        self.planet1_hits = self.planet2_hits = 0
        self.paddle1.reset()
        self.paddle2.reset()
        if self.start_with_power_enabled and not self.tutorial_active:
            self.paddle1.grant_random_power(self)
            self.paddle2.grant_random_power(self)
            
        # Resetear RATÓN (v0.6.0)
        self.mouse = None
        # Resetear REVOLVER ITEM (v0.6.0 Fix)
        self.revolver_item_active = False
        self.revolver_item_rect = None
        # Resetear SLEEP (v0.6.0)
        self.sleep_projectiles = []
        self.mouse_hits_counter = 0
        self.reset_tictactoe()

    def goal_scored(self, player):
        self.audio.play('goal')
        self.vibrate(150) # Vibración al anotar gol (v0.7.0 Polish)
        self._reset_round_state()
        if self.is_golden_goal_round:
            self.is_golden_goal_round = False
            msg_win = self.t(f"PLAYER {player} WINS!", f"¡EL JUGADOR {player} GANA!")
            self.winner_text = msg_win
            # Ocultar razón en nivel 7 para mayor limpieza (v0.7.3)
            if int(self.arcade_level) != 7:
                msg_reason = self.t(f"(Player {player} won by GOLDEN Goal rule)", f"(El Jugador {player} ganó por Gol de Oro)")
                self.winner_text += f"\n|YELLOW|{msg_reason}"
            if player == 1: self.score1 = self.max_score
            else: self.score2 = self.max_score
            self.state = STATE_GAME_OVER
            
            # Celebración si es nivel final (v0.6.0 Fix)
            self._trigger_victory_celebration(player)
            return

        inc = 2 if self.ball_is_x2 else 1
        self.point_scored(player, inc)

    def point_scored(self, player, increment=1):
        if player == 1: self.score1 += increment; s_dir = 1
        else: self.score2 += increment; s_dir = -1
        self.ball_is_x2 = False
        self._check_victory(s_dir)

    def _check_victory(self, s_dir):
        # Comprobar Victoria
        tut_max_score = 3 if self.tutorial_active else self.max_score
        if self.score1 >= tut_max_score or self.score2 >= tut_max_score:
            # Si el Match Point está activado, debe haber una diferencia de 2
            if self.match_point_enabled and abs(self.score1 - self.score2) < 2 and not self.tutorial_active:
                # Continuamos (Deuce)
                pass
            else:
                winner = 1 if self.score1 >= tut_max_score else 2
                if self.endless_active:
                    if winner == 1:
                        self.winner_text = self.t(f"LEVEL {self.endless_level} PASSED!", f"¡NIVEL {self.endless_level} SUPERADO!")
                    else:
                        self.winner_text = self.t("GAME OVER", "FIN DE JUEGO")
                else:
                    msg_win = self.t(f"PLAYER {winner} WINS!", f"¡EL JUGADOR {winner} GANA!")
                    self.winner_text = msg_win
                    # No mostrar mensaje de ventaja en nivel 7 ni si fue gol de oro (v0.7.3)
                    if self.match_point_enabled and not self.tutorial_active and int(self.arcade_level) != 7 and not self.is_golden_goal_round:
                        self.winner_text += "\n|YELLOW|" + self.t(f"(By advantage of 2 points)", f"(Por ventaja de 2 puntos)")
                
                if self.endless_active and winner == 1 and self.endless_level == 7 and not getattr(self, 'endless_chaos_unlocked', False):
                    self.state = STATE_ENDLESS_REWARD
                    self.reward_step = 0
                    self._init_endless_reward_text()
                else:
                    self.state = STATE_GAME_OVER
                
                # CELEBRACIÓN NIVEL FINAL (v0.6.0)
                if not self.endless_active:
                    self._trigger_victory_celebration(winner)
                else:
                    if winner == 1:
                        is_reward_level = (self.endless_level == 7)
                        if is_reward_level and not getattr(self, 'endless_chaos_unlocked', False):
                            self.audio.play('victory_arcade')
                            self.vfx.confetti_rain(200)
                        else:
                            self.audio.play('bell')
                    else:
                        self.audio.play('error')

                # TUTORIAL ENDGAME
                if self.tutorial_active:
                    self._start_tutorial_step(29)
                return

        # Si no hay victoria, preparamos el saque
        self.trigger_endless_chaos()
        self.state = STATE_SERVE
        self.serve_direction = s_dir
        self.balls = [Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        self.balls[0].serve(s_dir, 300 * self.initial_ball_speed_options[self.initial_ball_speed_idx])
        
        # Activar el temporizador de saque y anuncios (Match Point, etc)
        self.serve_timer = 1.75 # Cooldown de seguridad
        if hasattr(self, "chaos_banner_timer") and self.chaos_banner_timer > 0.0:
            self.serve_timer = self.chaos_banner_timer
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

    def _trigger_victory_celebration(self, winner):
        # Solo en el nivel 7 del modo arcade (v0.7.3)
        if int(self.arcade_level) == 7:
            if winner == 1:
                if not self.arcade_completed:
                    self.audio.play('victory_arcade')
                else:
                    self.audio.play('bell')
                # Evitar duplicar el texto si ya se añadió
                if "|GOLD|" not in self.winner_text:
                    self.winner_text += "\n|GOLD|CHAMPION!" if self.language=="EN" else "\n|GOLD|¡CAMPEÓN!"
            else:
                self.audio.play('error')

    def _advance_endless_reward(self):
        if len(getattr(self, "reward_text_visible", "")) < len(getattr(self, "reward_text_full", "")):
            self.reward_text_visible = self.reward_text_full
        else:
            self.audio.play('hit')
            if getattr(self, "reward_step", 0) == 0:
                self.reward_step = 1
                self._init_endless_reward_text()
                self.endless_chaos_unlocked = True
                self.save_progress()
            else:
                self.state = STATE_GAME_OVER

    def _advance_arcade_reward(self):
        if len(self.reward_text_visible) < len(self.reward_text_full):
            # Saltar animación
            self.reward_text_visible = self.reward_text_full
        else:
            self.audio.play('hit')
            if self.reward_step == 0:
                self.reward_step = 1
                self._init_reward_text()
            else:
                self.reset_game()
                self.state = STATE_MAIN_MENU
                self.save_progress() # Guardar cambios en ajustes
                self.arcade_active = False
                self.arcade_completed = True # ¡DESBLOQUEADO!
                self.save_progress() # Guardar victoria arcade

    def _init_reward_text(self):
        if self.reward_step == 0:
            instr = "|GRAY|" + (self.t(" (touch the screen to continue)", " (toca la pantalla para continuar)") if self.mobile_mode else self.t(" (press space to continue)", " (pulsa espacio para continuar)"))
            self.reward_text_full = self.t("CONGRATULATIONS! You beat ARCADE mode, you're now a PONG KOMBAT pro.", 
                                         "¡FELICIDADES! Has superado el modo ARCADE, ahora eres un profesional de PONG KOMBAT.") + instr
        else:
            instr = "|GRAY|" + (self.t(" (touch the screen to finish)", " (toca la pantalla para finalizar)") if self.mobile_mode else self.t(" (press space to finish)", " (pulsa espacio para finalizar)"))
            self.reward_text_full = self.t("You can now equip the CROWN in the SKINS section of the menu.", 
                                         "Ahora puedes equipar la CORONA en el apartado de SKINS del menú.") + instr
        self.reward_text_visible = ""
        self.reward_char_timer = 0

    def _init_endless_reward_text(self):
        if self.reward_step == 0:
            instr = "|GRAY|" + (self.t(" (touch the screen to continue)", " (toca la pantalla para continuar)") if self.mobile_mode else self.t(" (press space to continue)", " (pulsa espacio para continuar)"))
            self.reward_text_full = self.t("|WHITE|Wow, you're having an amazing streak in ENDLESS mode! You deserve a new modifier.", 
                                         "|WHITE|¡Wow, llevas una racha increíble en el modo ENDLESS! Te mereces un nuevo modificador.") + instr
        else:
            instr = "|GRAY|" + (self.t(" (touch the screen to finish)", " (toca la pantalla para finalizar)") if self.mobile_mode else self.t(" (press space to finish)", " (pulsa espacio para finalizar)"))
            self.reward_text_full = self.t("|WHITE|You can now try it in the EXTRAS tab", 
                                         "|WHITE|Ahora puedes probarlo en la pestaña EXTRAS") + instr
        self.reward_text_visible = ""
        self.reward_char_timer = 0

    def _check_for_announcements(self):
        # Evitar anuncios si no estamos en una partida activa (v0.6.0 Fix)
        if self.state not in [STATE_PLAYING, STATE_SERVE]:
            self.show_match_point_anim = self.show_golden_goal_anim = False
            return

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
        
        # Prioridad 3: Golden Goal Experimental (v0.6.0 Fix: Respetar modificador de EXTRAS)
        is_at_final_point = (self.score1 == self.max_score-1 and self.score2 == self.max_score-1)
        if is_at_final_point and self.experimental_golden_goal:
            if not self.show_golden_goal_anim:
                self.is_golden_goal_round = True 
                self.show_golden_goal_anim = True
                self.golden_goal_anim_timer = 2.5
                self.serve_timer = 3.0
                self.audio.play('golden_goal')
            return

    def update(self, dt):
        if hasattr(self, "chaos_banner_timer") and self.chaos_banner_timer > 0.0:
            self.chaos_banner_timer -= dt
            if self.chaos_banner_timer < 0.0:
                self.chaos_banner_timer = 0.0
            
            t = self.chaos_banner_timer
            duration = getattr(self, "chaos_banner_duration", 5.0)
            if duration <= 2.0:
                duration = 5.0
            
            if t > duration - 1.0:
                progress = duration - t
                self.chaos_banner_x = SCREEN_WIDTH + 600 - (SCREEN_WIDTH + 600 - SCREEN_WIDTH // 2) * progress
            elif t > 1.0:
                self.chaos_banner_x = SCREEN_WIDTH // 2
            else:
                progress = 1.0 - t
                self.chaos_banner_x = SCREEN_WIDTH // 2 - (SCREEN_WIDTH // 2 + 600) * progress

        if self.tictactoe_enabled and self.tictactoe_win_timer > 0.0:
            self.tictactoe_win_timer -= dt
            if self.tictactoe_win_timer <= 0.0:
                self.reset_tictactoe()

        self.vfx.enabled = self.vfx_enabled
        self.vfx.update(dt)

        # Gestión dinámica de la música según el estado y configuración
        if self.music_enabled:
            is_match_state = self.state in [STATE_PLAYING, STATE_SERVE, STATE_ARCADE_LEVEL_START]
            should_play = True
            if is_match_state and not self.music_in_match:
                should_play = False
            
            # Si debería sonar pero no está sonando (mixer.music.get_busy() no es fiable al 100% con loops, 
            # pero para detectar si está cargada y activa sirve)
            if should_play and not pygame.mixer.music.get_busy():
                self.audio.play_music('menu_music.wav', volume=self.music_volume)
            elif not should_play and pygame.mixer.music.get_busy():
                self.audio.stop_music(fadeout_ms=1500)
        else:
            if pygame.mixer.music.get_busy():
                self.audio.stop_music(fadeout_ms=1500)
        
        # Secuencia final tutorial en menú
        if self.state == STATE_MAIN_MENU and self.tutorial_active and self.tutorial_step == 31:
            if self.tutorial_end_menu_timer > 0:
                self.tutorial_end_menu_timer -= dt
                # Fase de partículas (2.5s a 1.0s -> duración 1.5s)
                if self.tutorial_end_menu_timer > 1.0:
                    count = int((2.5 - self.tutorial_end_menu_timer) * 10) + 1
                    self.vfx.burst(self.btn_tutorial_help_rect.centerx, self.btn_tutorial_help_rect.centery, WHITE, count=count)
                elif not self.tutorial_explosion_played:
                    self.audio.play('explosion')
                    self.tutorial_explosion_played = True
                return # Bloquear el resto del update si estamos en esta fase? No, mejor dejar que el resto corra si es necesario.

        # Actualizar Screen Shake
        if self.shake_timer > 0:
            self.shake_timer -= dt
            if self.shake_timer <= 0:
                self.shake_amount = 0

        # Actualizar Timers de Anuncios (v0.6.0)
        if self.show_match_point_anim:
            self.match_point_anim_timer -= dt
            if self.match_point_anim_timer <= 0: self.show_match_point_anim = False
        if self.show_golden_goal_anim:
            self.golden_goal_anim_timer -= dt
            if self.golden_goal_anim_timer <= 0: self.show_golden_goal_anim = False

        if self.endless_active and self.endless_intro_timer > 0:
            self.endless_intro_timer -= dt
            if self.endless_intro_x > SCREEN_WIDTH // 2:
                self.endless_intro_x -= 1000 * dt
                if self.endless_intro_x < SCREEN_WIDTH // 2:
                    self.endless_intro_x = SCREEN_WIDTH // 2

        if self.state == STATE_ARCADE_REWARD or self.state == STATE_ENDLESS_REWARD:
            if len(getattr(self, "reward_text_visible", "")) < len(getattr(self, "reward_text_full", "")):
                self.reward_char_timer -= dt
                if self.reward_char_timer <= 0:
                    self.reward_char_timer = 0.03
                    next_char = self.reward_text_full[len(self.reward_text_visible)]
                    self.reward_text_visible += next_char
                    if next_char == " " or len(self.reward_text_visible) == 1:
                        if not self.mobile_mode:
                            self.audio.play('pop')
            return

        if self.state == STATE_ARCADE_LEVEL_START:
            self.arcade_level_start_timer -= dt
            if self.arcade_level_start_timer <= 0:
                self._setup_arcade_gameplay(self.arcade_level)
            return

        if self.state == STATE_SERVE:
            # Durante el tutorial pasos 11, 12 y 13, el juego está congelado
            if self.tutorial_active and self.tutorial_step in [11, 12, 13]:
                # Solo permitir movimiento de paletas
                self.paddle1.update(dt, self)
                self.paddle2.update(dt, self)
                self._update_tutorial(dt)
                return

            if hasattr(self, "chaos_banner_timer") and self.chaos_banner_timer > 0.0:
                if self.serve_timer < self.chaos_banner_timer:
                    self.serve_timer = self.chaos_banner_timer

            self.serve_timer -= dt
            if self.serve_timer <= 0: self.state = STATE_PLAYING; self.paddle1.is_destroyed = self.paddle2.is_destroyed = False
            if self.show_match_point_anim: 
                self.match_point_anim_timer -= dt
                if self.match_point_anim_timer <= 0: self.show_match_point_anim = False
            if self.show_golden_goal_anim: 
                self.golden_goal_anim_timer -= dt
                if self.golden_goal_anim_timer <= 0: self.show_golden_goal_anim = False
                
        elif self.state == STATE_PLAYING:
            # Congelar el juego en los Pasos 14 al 28 (explicaciones de relojes y poderes)
            if self.tutorial_active and 14 <= self.tutorial_step <= 28:
                self.paddle1.update(dt, self)
                self.paddle2.update(dt, self)
                self._update_tutorial(dt)
                return

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

            # Actualizar Proyectiles de Sueño (v0.6.0)
            for sp in self.sleep_projectiles[:]:
                sp.update(dt, self)
                if not sp.active:
                    self.sleep_projectiles.remove(sp)

            # --- DÍA NUBLADO (CLOUDY DAY) ---
            if self.cloudy_day_enabled:
                self.cloud_spawn_timer += dt
                if self.cloud_spawn_timer >= 1.0:
                    self.cloud_spawn_timer = 0
                    if random.random() < 0.5: # 50/50 Chance
                        from entities import Cloud
                        # Velocidad exponencial si > 30 toques
                        speed_mult = 1.0
                        if self.global_hits > 30:
                            # 1.1^n donde n es cada golpe extra tras el 30
                            speed_mult = min(5.0, 1.1 ** (self.global_hits - 30))
                        
                        size_mult = self.cloud_size_options[self.cloud_size_idx]
                        
                        # Aparecer por la izquierda (1) o derecha (-1)
                        direction = 1 if random.random() < 0.5 else -1
                        start_x = -300 if direction == 1 else SCREEN_WIDTH + 300
                        start_y = random.randint(50, SCREEN_HEIGHT - 50)
                        self.clouds.append(Cloud(start_x, start_y, direction, size_mult, speed_mult))
                
                for c in self.clouds[:]:
                    c.update(dt)
                    if not c.active:
                        self.clouds.remove(c)
                
            # --- GOTAS DE LLUVIA (RAINY DAY) ---
            if self.rainy_day_enabled:
                if self.state == STATE_PLAYING:
                    self.rain_timer += dt
                
                # Gestionar el sonido de fondo ambiental en bucle de lluvia
                if self.state in [STATE_PLAYING, STATE_SERVE, STATE_PRESS_TO_START]:
                    if not self.rain_sound_playing:
                        self.audio.play('rainy', loops=-1, fade_ms=3000)
                        self.rain_sound_playing = True
                else:
                    if self.rain_sound_playing:
                        self.audio.fadeout('rainy', 1000)
                        self.rain_sound_playing = False
                
                # Progresión suave de 0 a la cantidad de gotas según precipitación en los primeros 12 segundos
                precip_mult = self.rain_precipitation_options[self.rain_precipitation_idx]
                max_drops = int(130 * precip_mult)
                rain_progress = min(1.0, self.rain_timer / 12.0)
                max_allowed = int(rain_progress * max_drops)
                
                if len(self.rain_drops) < max_allowed:
                    for _ in range(max_allowed - len(self.rain_drops)):
                        self.rain_drops.append({
                            "x": random.uniform(0, SCREEN_WIDTH + 150),
                            "y": random.uniform(-SCREEN_HEIGHT, 0), # Lluvia progresiva que cae desde el cielo
                            "vx": random.uniform(-120, -60),
                            "vy": random.uniform(400, 700),
                            "length": random.uniform(8, 16),
                            "width": random.randint(1, 2)
                        })
                
                for drop in self.rain_drops:
                    drop["x"] += drop["vx"] * dt
                    drop["y"] += drop["vy"] * dt
                    if drop["y"] > SCREEN_HEIGHT or drop["x"] < -20:
                        drop["y"] = random.uniform(-20, 0)
                        drop["x"] = random.uniform(0, SCREEN_WIDTH + 150)
                        drop["vx"] = random.uniform(-120, -60)
                        drop["vy"] = random.uniform(400, 700)
                        drop["length"] = random.uniform(8, 16)
                        drop["width"] = random.randint(1, 2)
                
                # Lógica de Relámpago (LIGHTNING)
                if self.lightning_enabled and self.state in [STATE_PLAYING, STATE_SERVE]:
                    if self.lightning_active:
                        self.lightning_flash_timer -= dt
                        if self.lightning_flash_timer <= 0:
                            self.lightning_active = False
                            self.lightning_flash_timer = 0.0
                    
                    self.lightning_timer += dt
                    if self.lightning_timer >= 1.0:
                        self.lightning_timer -= 1.0
                        if random.random() < 0.05:
                            self.lightning_active = True
                            self.lightning_flash_timer = 1.1
                            self.audio.play('thunder')
                else:
                    self.lightning_active = False
                    self.lightning_flash_timer = 0.0
                    self.lightning_timer = 0.0
            else:
                self.rain_drops = []
                self.rain_timer = 0.0
                self.lightning_active = False
                self.lightning_flash_timer = 0.0
                self.lightning_timer = 0.0
                if self.rain_sound_playing:
                    self.audio.fadeout('rainy', 1000)
                    self.rain_sound_playing = False

            # --- FÍSICAS CENTRALIZADAS ---
            self.physics.update(dt)
            
            # --- ENTIDADES ESPECIALES (v0.6.0) ---
            self._update_game_entities(dt)

            # Lógica del RATÓN (v0.5.0)
            if self.add_mouse_enabled:
                if self.mouse is None:
                    appear_at = self.mouse_appear_options[self.mouse_appear_idx]
                    if self.mouse_hits_counter >= appear_at:
                        # Aparecer ratón asomándose por el piso (v0.6.0)
                        self.mouse = Mouse(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 35)
                        self.audio.play('squeak')
                else:
                    # Actualizar ratón (solo persigue pelotas sólidas, no fantasmas)
                    solid_balls = [b for b in self.balls if not b.is_ghost]
                    if solid_balls:
                        self.mouse.update(dt, solid_balls[0], self.mouse_speed_options[self.mouse_speed_idx])
                        
                        # Colisión con la pelota (Comer/Explotar) - v0.6.0 Arcade Fix
                        for b in solid_balls:
                            if self.mouse.rect.colliderect(b.rect):
                                if b.is_orange:
                                    self.audio.play('explosion')
                                    self.vfx.explosion(self.mouse.rect.centerx, self.mouse.rect.centery, (150, 150, 150))
                                    self.mouse = None
                                    b.reset_orange(BALL_SIZE)
                                    break
                                else:
                                    self.audio.play('nom')
                                    self.vfx.burst(self.mouse.rect.centerx, self.mouse.rect.centery, YELLOW)
                                    # Penalización al último golpeador (v0.6.0 New Logic)
                                    s_dir = 1
                                    if self.last_hitter == 1:
                                        if self.score1 > 0: self.score1 -= 1
                                        else: self.score2 += 1; s_dir = -1
                                    elif self.last_hitter == 2:
                                        if self.score2 > 0: self.score2 -= 1
                                        else: self.score1 += 1; s_dir = 1
                                    
                                    self._reset_round_state()
                                    self._check_victory(s_dir)
                                    break
        self._update_tutorial(dt)
        self._update_arcade_intro(dt)

    def _update_arcade_intro(self, dt):
        if not self.arcade_active or self.arcade_intro_timer <= 0: return
        
        self.arcade_intro_timer -= dt
        target_center_x = SCREEN_WIDTH // 2
        
        if self.arcade_intro_timer > 5.0:
            # Entrada (1s)
            t = (6.0 - self.arcade_intro_timer)
            start_x = SCREEN_WIDTH + 500
            self.arcade_intro_x = start_x + (target_center_x - start_x) * t
        elif self.arcade_intro_timer > 1.0:
            # Centro (4s)
            self.arcade_intro_x = target_center_x
        else:
            # Salida (1s)
            t = (1.0 - self.arcade_intro_timer)
            end_x = -500
            self.arcade_intro_x = target_center_x + (end_x - target_center_x) * t
            
        if self.arcade_intro_timer <= 0:
            if self.is_golden_goal_round:
                self.show_golden_goal_anim = True
                self.golden_goal_anim_timer = 2.5
                self.audio.play('golden_goal')
                self.serve_timer = 3.0 # Dar tiempo a la animación (v0.6.0 Fix)
            elif self.match_point_enabled:
                self.show_match_point_anim = True
                self.match_point_anim_timer = 2.5
                self.audio.play('match_point')
                self.serve_timer = 3.0

    def _update_tutorial(self, dt):
        if not self.tutorial_active and self.state != STATE_ARCADE_TUTORIAL and self.state != STATE_ENDLESS_TUTORIAL: return
       
        # Efecto Typewriter (Palabra por palabra)
        if self.tutorial_cooldown_timer > 0:
            self.tutorial_cooldown_timer -= dt

        if self.tutorial_text_visible != self.tutorial_text_full:
            self.tutorial_text_timer += dt
            if self.tutorial_text_timer >= self.tutorial_word_delay:
                self.tutorial_text_timer = 0
                words = self.tutorial_text_full.split(" ")
                if self.tutorial_text_index < len(words):
                    self.tutorial_text_visible += (" " if self.tutorial_text_index > 0 else "") + words[self.tutorial_text_index]
                    self.tutorial_text_index += 1
                    if not self.mobile_mode:
                        self.audio.play('pop')

    def _start_tutorial_step(self, step):
        self.tutorial_step = step
        self.tutorial_text_index = 0
        self.tutorial_text_visible = ""
        self.tutorial_cooldown_timer = 1.0 # 1 segundo de cooldown al iniciar cada paso (v0.7.0)
        
        # --- Variables de texto dinámico para PC/Móvil ---
        if self.mobile_mode:
            s_cont = "|GRAY|" + self.t("(touch the screen to continue...)", "(toca la pantalla para continuar...)")
            s_press = "|GRAY|" + self.t("(touch the screen)", "(toca la pantalla)")
            s_click = self.t("touch", "toca")
            p1_ctrl = self.t("Player 1 Controls: Up: 'left up arrow', Down: 'left down arrow', and power: 'left STAR'", "Controles Jugador 1: Arriba: 'flecha arriba izq', Abajo: 'flecha abajo izq' y Poder: 'ESTRELLA izq'")
            p2_ctrl = self.t("Player 2 Controls: Up: 'right up arrow', Down: 'right down arrow', and power: 'right STAR'", "Controles Jugador 2: Arriba: 'flecha arriba der', Abajo: 'flecha abajo der' y Poder: 'ESTRELLA der'")
            p_pow = self.t("the power button (STAR)", "el botón de poder (ESTRELLA)")
            s_end = self.t("touch the screen.", "toca la pantalla.")
        else:
            s_cont = "|GRAY|" + self.t("(press space to continue...)", "(pulsa espacio para continuar...)")
            s_press = "|GRAY|" + self.t("(press space)", "(pulsa espacio)")
            s_click = self.t("click", "haz clic")
            p1_ctrl = self.t("Player 1 Controls: Up: 'W', Down: 'S', and Power: 'D'", "Controles Jugador 1: Arriba: 'W', Abajo: 'S' y Poder: 'D'")
            p2_ctrl = self.t("Player 2 Controls: Up: 'Up Arrow', Down: 'Down Arrow', and Power: 'Left Arrow'", "Controles Jugador 2: Arriba: 'Flecha Arriba', Abajo: 'Flecha Abajo' y Poder: 'Flecha Izquierda'")
            p_pow = self.t("your power key (D)", "tu tecla de poder (D)")
            s_end = self.t("press the space bar.", "presiona la barra espaciadora.")

        if step == 0:
            self.tutorial_text_full = self.t("Welcome to the tutorial! ", "¡Bienvenido al tutorial! ") + s_cont
        elif step == 1:
            self.tutorial_text_full = self.t("Here is the SETTINGS button. You can change the language and volume", "Aquí está el botón de AJUSTES. Puedes cambiar el idioma y el volumen")
        elif step == 2:
            self.tutorial_text_full = self.t("If you want, change the language to Spanish, or just press 'APPLY'", "Si quieres, cambia el idioma a Español, o simplemente pulsa 'APLICAR'")
        elif step == 3:
            self.tutorial_text_full = self.t("You can also modify the game; just ", "También puedes modificar el juego; solo ") + s_click + self.t(" the MODIFIERS button", " en el botón MODIFICADORES")
        elif step == 4:
            self.tutorial_text_full = self.t("Here are the MODIFIERS. In the 'ALL' tab, you can change the game rules ", "Aquí están los MODIFICADORES. En la pestaña 'TODO', puedes cambiar las reglas del juego ") + s_cont
        elif step == 5:
            self.tutorial_text_full = self.t("You can switch tabs to see other modifiers. ", "Puedes cambiar de pestaña para ver otros modificadores. ") + s_click.capitalize() + self.t(" on the EXTRAS tab to continue", " en la pestaña EXTRAS para continuar")
        elif step == 6:
            self.tutorial_text_full = self.t("You can also change the appearance of some powers in the SKIN tab", "También puedes cambiar la apariencia de algunos poderes en la pestaña ASPECTOS")
        elif step == 7:
            self.tutorial_text_full = self.t("Here you can see the available skins ", "Aquí puedes ver los aspectos disponibles ") + s_cont
        elif step == 8:
            self.tutorial_text_full = self.t("Okay, you now understand how modifiers work. Now let's go back to the menu", "Bien, ahora ya entiendes cómo funcionan los modificadores. Volvamos al menú")
        elif step == 9:
            self.tutorial_text_full = self.t("Now let's start a game. ", "Ahora empecemos una partida. ") + s_click.capitalize() + self.t(" on PLAY", " en JUGAR")
        elif step == 10:
            self.tutorial_text_full = self.t("You can play against the AI or a friend. For this tutorial, we will choose SOLO mode", "Puedes jugar contra la IA o un amigo. Para este tutorial, elegiremos el modo SOLO")
        elif step == 11:
            self.tutorial_text_full = p1_ctrl
        elif step == 12:
            self.tutorial_text_full = p2_ctrl
        elif step == 13:
            self.tutorial_text_full = self.t("Excellent! You are ready. Let's start the match!", "¡Excelente! Ya estás listo. ¡Empecemos el partido!")
        elif step == 14:
            self.tutorial_text_full = self.t("Look! A clock, each clock appears every 10 taps spread between the 2 palettes ", "¡Mira! Un reloj, cada reloj aparece cada 10 toques repartidos entre las 2 paletas ") + s_press
        elif step == 15:
            self.tutorial_text_full = self.t("There are 5 types of watches: Blue, Red, Violet, Yellow, and White.", "Hay 5 tipos de relojes: Azul, Rojo, Violeta, Amarillo y Blanco.")
        elif step == 16:
            self.tutorial_text_full = self.t("Blue Watch: Slows the ball down by 50% when it enters your half of the court.", "Reloj Azul: Ralentiza la pelota en un 50% cuando entra en tu mitad de la cancha.")
        elif step == 17:
            self.tutorial_text_full = self.t("Red Watch: Accelerate the ball by 25% when it enters your half of the court.", "Reloj Rojo: Acelera la pelota en un 25% cuando entra en tu mitad de la cancha.")
        elif step == 18:
            self.tutorial_text_full = self.t("Violet Watch: You get a power if your paddle stays completely still for 3 seconds.", "Reloj Violeta: Obtienes un poder si tu paleta se queda completamente quieta por 3 segundos.")
        elif step == 19:
            self.tutorial_text_full = self.t("Yellow Watch: Grants an extra life, blocking the next goal against you.", "Reloj Amarillo: Otorga una vida extra, bloqueando el próximo gol en tu contra.")
        elif step == 20:
            self.tutorial_text_full = self.t("White Watch: Your paddle occupies half the court for 5 touches, then you return to normal.", "Reloj Blanco: Tu paleta ocupa media cancha durante 5 toques, luego vuelves a la normalidad.")
        elif step == 21:
            self.tutorial_text_full = self.t("The probabilities for each watch are: BLUE (25%), VIOLET (25%), RED (25%), YELLOW (15%) and WHITE (10%).", "Las probabilidades para cada reloj son: AZUL (25%), VIOLETA (25%), ROJO (25%), AMARILLO (15%) y BLANCO (10%).")
        elif step == 22:
            self.tutorial_text_full = self.t("You got a power! You receive a new power every 7 taps.", "¡Obtuviste un poder! Recibes un nuevo poder cada 7 toques.")
        elif step == 23:
            self.tutorial_text_full = self.t("Green Power: Doubles your paddle size and protects you for 3 hits.", "Poder Verde: Duplica el tamaño de tu paleta y te protege por 3 golpes.")
        elif step == 24:
            self.tutorial_text_full = self.t("Red Power: The ball turns reddish and goes at X2 speed until the opponent touches it.", "Poder Rojo: La pelota se vuelve rojiza y va a velocidad X2 hasta que el oponente la toca.")
        elif step == 25:
            self.tutorial_text_full = self.t("Yellow Power: Your paddle's movement speed increases by 50% permanently and is also cumulative.", "Poder Amarillo: La velocidad de movimiento de tu paleta aumenta un 50% permanentemente y además es acumulativo.")
        elif step == 26:
            self.tutorial_text_full = self.t("Orange Power: Giant ball grows 50% faster per touch. Opponent must dodge it; catching it gives you a point!", "Poder Naranja: Bola gigante un 50% más rápida por toque. El rival debe esquivarla; si la toca, es punto.")
        elif step == 27:
            self.tutorial_text_full = self.t("Probability of each power: GREEN, RED and YELLOW (30%) and ORANGE (10%).", "Probabilidad de cada poder: VERDE, ROJO y AMARILLO (30%) y NARANJA (10%).")
        elif step == 28:
            self.tutorial_text_full = self.t("Great! Now press ", "¡Genial! Ahora presiona ") + p_pow + self.t(" to use your power!", " para usarlo.")
        elif step == 29:
            self.tutorial_text_full = self.t("Normally a classic game ends at 6 points, but so you can go and try the full game, I set it to 3.", "Normalmente una partida clásica termina a los 6 puntos, pero para que puedas ir a probar el juego completo, lo ajusté a 3.")
        elif step == 30:
            self.tutorial_text_full = self.t("Okay, you've already tried the basic mechanics, but you can add MANY more that completely change the way you play.", "Bien, ya probaste las mecánicas básicas, pero puedes añadir MUCHAS más que cambian por completo la forma de jugar.")
        elif step == 31:
            self.tutorial_text_full = self.t("I almost forgot! You can press the \"?\" button to watch the tutorial again if you like.", "¡Casi lo olvido! Puedes presionar el botón \"?\" para ver el tutorial de nuevo si quieres.")
            self.tutorial_explosion_played = False
        elif step == 32:
            self.tutorial_text_full = self.t("That's the end of the tutorial. You can now modify whatever you want. To finish, ", "Ese es el final del tutorial. Ahora puedes modificar lo que quieras. Para finalizar, ") + s_end


    def _next_tutorial_step(self):
        # PROTECCIÓN (v0.7.0 Fix): No avanzar si estamos en cooldown (evita doble click accidental)
        if self.tutorial_cooldown_timer > 0:
            return

        # No avanzar si estamos en una fase de juego activa (bloqueo total hasta cumplir condición)
        if self.tutorial_step in [135, 215, 285]:
            return

        # 1. Completar texto si está escribiéndose
        if self.tutorial_text_visible != self.tutorial_text_full:
            self.tutorial_text_visible = self.tutorial_text_full
            return
        
        # 2. Bloqueo de pasos que requieren interacción obligatoria con la UI
        # (1:Ajustes, 2:Aplicar, 3:Modificadores, 5:Extras, 6:Aspectos, 8:Volver, 9:Jugar, 10:Solo)
        blocked_steps = [1, 2, 3, 5, 6, 8, 9, 10]
        if self.tutorial_step in blocked_steps:
            return

        # 3. Incrementar paso
        self.tutorial_step += 1
        
        # 4. Transiciones especiales de Gameplay / Menú Final
        if self.tutorial_step == 14: # Tras el mensaje de "Empecemos" (13)
            self.tutorial_step = 135 # Fase Gameplay 1 (Relojes)
            self.state = STATE_PLAYING
            self.global_hits = 0
            return
        elif self.tutorial_step == 22: # Tras el mensaje de Probabilidades (21)
            self.tutorial_step = 215 # Fase Gameplay 2 (Poderes)
            self.state = STATE_PLAYING
            return
        elif self.tutorial_step == 29: # Tras el mensaje final (28)
            self.tutorial_step = 285 # Fase Gameplay 3 (Libre)
            self.state = STATE_PLAYING
            return
        elif self.tutorial_step == 31:
            # Fin de la pantalla de Game Over, regreso animado al menú
            self.state = STATE_MAIN_MENU
            self.tutorial_end_menu_timer = 2.5
            self.audio.play('reveal')
        elif self.tutorial_step == 33:
            self.tutorial_active = False
            return

        # 5. Iniciar el nuevo paso
        self._start_tutorial_step(self.tutorial_step)

    def _next_arcade_tutorial_step(self):
        if self.tutorial_text_visible != self.tutorial_text_full:
            self.tutorial_text_visible = self.tutorial_text_full
            return

        if not self.mobile_mode:
            self.audio.play('pop')
            
        self.arcade_tutorial_step += 1
        
        if self.arcade_tutorial_step > 2:
            self.state = STATE_SOLO_SUBMODE_SELECTION
            return

        # --- CONTROL DE TEXTOS CON DOS IDIOMAS ---
        if self.arcade_tutorial_step == 1:
            self.tutorial_text_visible = ""
            self.tutorial_text_full = self.t(
                "This is ARCADE mode! 7 levels, each one harder than the last (press space to continue).",
                "¡Este es el modo ARCADE! 7 niveles, cada uno más difícil que el anterior (presiona espacio para continuar)."
            )
            self.tutorial_text_index = 0
            self.tutorial_text_timer = 0

        elif self.arcade_tutorial_step == 2:
            self.tutorial_text_visible = ""
            self.tutorial_text_full = self.t(
                "The difficulty increases with each level you pass. If you beat the final level, you'll receive a reward.",
                "La dificultad aumenta con cada nivel superado. Si vences el nivel final, recibirás una recompensa."
            )
            self.tutorial_text_index = 0
            self.tutorial_text_timer = 0

    def _next_endless_tutorial_step(self):
        # Si la máquina de escribir no terminó, la forzamos a terminar de golpe
        if self.tutorial_text_visible != self.tutorial_text_full:
            self.tutorial_text_visible = self.tutorial_text_full
            return

        # Reproducir sonido si no estamos en celular
        if not self.mobile_mode:
            self.audio.play('pop')
            
        # Sumamos 1 al paso del tutorial
        self.endless_tutorial_step += 1
        
        # Si nos pasamos del paso 2, cerramos el tutorial y volvemos al submenú
        if self.endless_tutorial_step > 2:
            self.state = STATE_SOLO_SUBMODE_SELECTION
            self.tutorial_text_full = ""
            self.tutorial_text_visible = ""
            return

        # === CONTROL DE TEXTOS DEL MODO ENDLESS ===
        if self.endless_tutorial_step == 1:
            self.tutorial_text_visible = ""
            self.tutorial_text_full = self.t(
                "Welcome to ENDLESS mode! Here, the goal is simply to survive as long as possible.",
                "¡Bienvenido al modo SIN FIN! Aquí, el objetivo es simplemente sobrevivir tanto como sea posible."
            )
            self.tutorial_text_index = 0
            self.tutorial_text_timer = 0

        elif self.endless_tutorial_step == 2:
            self.tutorial_text_visible = ""
            self.tutorial_text_full = self.t(
                "The ball gets faster with every hit. Precision is key. Good luck! (press space to finish).",
                "La pelota se vuelve más rápida con cada golpe. La precisión es clave. ¡Buena suerte! (presiona espacio para terminar)."
            )
            self.tutorial_text_index = 0
            self.tutorial_text_timer = 0

    def _next_endless_tutorial_step(self):
        # Si la máquina de escribir no terminó, la forzamos a terminar de golpe
        if self.tutorial_text_visible != self.tutorial_text_full:
            self.tutorial_text_visible = self.tutorial_text_full
            return

        # Reproducir sonido si no estamos en celular
        if not self.mobile_mode:
            self.audio.play('pop')
            
        # Sumamos 1 al paso del tutorial
        self.endless_tutorial_step += 1
        
        # Si pasamos del paso 4, cerramos el tutorial y volvemos al menú de selección
        if self.endless_tutorial_step > 4:
            self.state = STATE_SOLO_SUBMODE_SELECTION
            self.tutorial_text_full = ""
            self.tutorial_text_visible = ""
            return

        # === CONTROL DE TEXTOS DEL MODO ENDLESS ===
        if self.endless_tutorial_step == 1:
            # Detecta si es celular o PC para el botón de continuar
            if self.mobile_mode:
                en_prompt = "(touch the screen to continue)"
                es_prompt = "(toca la pantalla para continuar)"
            else:
                en_prompt = "(press space to continue)"
                es_prompt = "(presiona espacio para continuar)"
                
            self.tutorial_text_visible = ""
            self.tutorial_text_full = self.t(
                f"Here's ENDLESS mode! An infinite mode of PONG KOMBAT.\n{en_prompt}",
                f"¡Este es el modo SIN FIN! Un modo infinito de PONG KOMBAT.\n{es_prompt}"
            )
            self.tutorial_text_index = 0
            self.tutorial_text_timer = 0

        elif self.endless_tutorial_step == 2:
            self.tutorial_text_visible = ""
            self.tutorial_text_full = self.t(
                "An additional modifier will be added at each level.\nOne more modifier will be added to that amount\nfor each level cleared.",
                "Se añadirá un modificador adicional en cada nivel.\nSe sumará un modificador más a esa cantidad\npor cada nivel superado."
            )
            self.tutorial_text_index = 0
            self.tutorial_text_timer = 0
            
        elif self.endless_tutorial_step == 3:
            self.tutorial_text_visible = ""
            self.tutorial_text_full = self.t(
                "If you achieve a long winning streak,\nyou will receive a reward.",
                "Si logras una larga racha de victorias,\nrecibirás una recompensa."
            )
            self.tutorial_text_index = 0
            self.tutorial_text_timer = 0
            
        elif self.endless_tutorial_step == 4:
            self.tutorial_text_visible = ""
            self.tutorial_text_full = self.t(
                "Each game is played to one point, and if you lose by one point,\nyou start over. There's no room for error!",
                "Cada partida se juega a un punto, y si pierdes por un punto,\nvuelves a empezar. ¡No hay margen de error!"
            )
            self.tutorial_text_index = 0
            self.tutorial_text_timer = 0

    def _update_game_entities(self, dt):
        # 1. LÓGICA DE ÍTEM REVÓLVER (ÓRBITA) - Fuera del bucle de pelotas para evitar velocidad duplicada
        if self.revolver_enabled and self.revolver_item_active:
            self.revolver_angle += dt * 1.5 
            center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
            rx = center_x + math.cos(self.revolver_angle) * self.revolver_orbit_radius
            ry = center_y + math.sin(self.revolver_angle) * self.revolver_orbit_radius
            self.revolver_item_rect = pygame.Rect(rx - 15, ry - 15, 30, 30)
            
            # Colisión con pelota para capturar ítem
            for b in self.balls:
                if b.rect.colliderect(self.revolver_item_rect):
                    self.revolver_item_active = False
                    self.revolver_item_rect = None
                    self.audio.play('speed') 
                    target_p = self.paddle1 if self.last_hitter == 1 else self.paddle2
                    if target_p.power_active not in [POWER_SHIELD, POWER_MAGNET]:
                        target_p.power_stored = POWER_REVOLVER
                        target_p.color = GUN_METAL
                    self.global_hits = 0 
                    break

        # 2. Lógica post-física por cada pelota
        for ball in self.balls[:]:
            # --- COLISIÓN CHICLE (GUM) ---
            for gp in self.gum_projectiles[:]:
                if gp.rect.colliderect(ball.rect):
                    # El proyectil desaparece al chocar (v0.6.0 Fix)
                    gp.active = False
                    # Pero SOLO repele si es una pelota sólida normal (no fantasma, no bala)
                    if not ball.is_ghost and not ball.is_bullet:
                        self.audio.play('explosion')
                        # Cambiar dirección y dar un 50% de velocidad extra (v0.6.0 Fix)
                        ball.vx *= -1.5
                        ball.vy *= 1.5
                        # Pequeño impulso aleatorio para que no sea predecible
                        ball.vy += random.uniform(-50, 50)
                        self.vfx.explosion(ball.rect.centerx, ball.rect.centery, GUM_PINK)
                    break

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

    def _get_zone_multiplier(self, ball):
        in_p1 = ball.rect.centerx < SCREEN_WIDTH // 2
        z_type = (self.p1_zone_type if in_p1 else self.p2_zone_type) if self.watches_kept_enabled else (self.zone_type if ((self.slow_zone_owner == 1 and in_p1) or (self.slow_zone_owner == 2 and not in_p1)) else 0)
        return 0.5 if z_type == 1 else (1.25 if z_type == 2 else 1.0)



    def trigger_shake(self, amount, duration):
        if not self.shake_enabled: return
        self.shake_amount = amount
        self.shake_timer = duration
        if amount > 5: self.vibrate(int(duration * 1000)) # Vibrar si el impacto es fuerte (v0.7.0)

    def vibrate(self, duration_ms):
        """Retroalimentación háptica para móviles (v0.7.0)"""
        if sys.platform == "emscripten" and self.mobile_mode:
            try:
                import platform
                platform.window.navigator.vibrate(duration_ms)
            except: pass

    def _draw_chaos_banner(self, surface):
        if getattr(self, "state", 0) not in [STATE_SERVE, STATE_PLAYING, STATE_GAME_OVER, STATE_PRESS_TO_START]:
            return
        if not hasattr(self, "chaos_banner_timer") or self.chaos_banner_timer <= 0.0:
            return
            
        banner_font = self.medium_font
        max_text_width = SCREEN_WIDTH - 120
        
        # Calcular saltos de línea para estimar el tamaño del banner
        words = self.chaos_banner_text.split(' ')
        new_text = ""
        current_line = ""
        for word in words:
            clean_word = re.sub(r'\|[A-Z_]+\|', '', word)
            clean_line = re.sub(r'\|[A-Z_]+\|', '', current_line)
            
            if banner_font.size(clean_line + clean_word)[0] < max_text_width:
                current_line += (word + " ")
            else:
                new_text += current_line.strip() + "\n"
                current_line = word + " "
        new_text += current_line.strip()
        
        lines = new_text.split('\n')
        line_height = banner_font.get_linesize()
        text_total_h = len(lines) * line_height
        
        padding_y = 16
        banner_h = text_total_h + padding_y * 2
        banner_y = SCREEN_HEIGHT // 3 - banner_h // 2
        banner_width = SCREEN_WIDTH + 400
        
        banner_surf = pygame.Surface((banner_width, banner_h), pygame.SRCALPHA)
        banner_surf.fill((30, 0, 0, 200)) # Dark red translucent
        pygame.draw.line(banner_surf, RED, (0, 0), (banner_width, 0), 3)
        pygame.draw.line(banner_surf, RED, (0, banner_h - 1), (banner_width, banner_h - 1), 3)
        
        surface.blit(banner_surf, (int(self.chaos_banner_x) - banner_width // 2, banner_y))
        
        text_y = banner_y + padding_y
        draw_rich_text(surface, new_text, (int(self.chaos_banner_x), text_y), banner_font, default_color=WHITE, align="center")

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
                # Dibujar Coronas DETRÁS de la pelota y anuncios (v0.6.0 Fix)
                from ui_components import draw_crown
                if self.crown_hat_idx > 0:
                    if self.crown_hat_idx in [1, 3]: # Player 1
                        draw_crown(temp_surf, self.paddle1.rect.centerx, self.paddle1.rect.top - 5, size=0.5)
                    if self.crown_hat_idx in [2, 3]: # Player 2
                        draw_crown(temp_surf, self.paddle2.rect.centerx, self.paddle2.rect.top - 5, size=0.5)

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
                
                for sp in self.sleep_projectiles:
                    sp.draw(temp_surf)
            
            # Dibujar Gotas de lluvia (Rainy Day) debajo de las nubes pero sobre el resto del juego
            if self.rainy_day_enabled and self.rain_drops:
                size_mult = self.rain_drop_size_options[self.rain_drop_size_idx]
                for drop in self.rain_drops:
                    length = drop["length"] * size_mult
                    width = max(1, int(drop["width"] * size_mult))
                    dx = (drop["vx"] / drop["vy"]) * length
                    dy = length
                    pygame.draw.line(temp_surf, (140, 180, 255), (drop["x"], drop["y"]), (drop["x"] + dx, drop["y"] + dy), width)
            
            if self.cloudy_day_enabled:
                for c in self.clouds:
                    c.draw(temp_surf)

            if self.is_x2_item_active: self._draw_x2_icon(temp_surf)
            self._draw_score(temp_surf)
            
            # Indicador de inicio de partida (v0.6.0)
            if self.state == STATE_PRESS_TO_START:
                if int(pygame.time.get_ticks() / 500) % 2 == 0:
                    if self.mobile_mode:
                        txt = self.t("TOUCH TO START", "TOCA PARA EMPEZAR")
                    else:
                        txt = self.t("PRESS SPACE TO START", "PRESIONA ESPACIO PARA EMPEZAR")
                    st = self.font.render(txt, True, WHITE)
                    temp_surf.blit(st, st.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)))
            
            # Indicador de inicio de saque (Opcional, quitado de aquí por petición)
            # if self.state == STATE_SERVE: ...
            
            # --- CAPA DE CONTROLES MÓVILES (v0.7.0) ---
            if self.mobile_mode:
                self._draw_mobile_controls(temp_surf)
            
        if self.state == STATE_MAIN_MENU: self.menus.draw_main_menu(temp_surf)
        elif self.state == STATE_MODIFIERS: self.menus.draw_modifiers(temp_surf)
        elif self.state == STATE_SETTINGS: self.menus.draw_settings(temp_surf)
        elif self.state == STATE_MODE_SELECTION: self.menus.draw_mode_selection(temp_surf)
        elif self.state == STATE_SOLO_SUBMODE_SELECTION or self.state == STATE_ENDLESS_TUTORIAL: self.menus.draw_solo_submode_selection(temp_surf)
        elif self.state == STATE_ARCADE_TUTORIAL:
            self.menus.draw_arcade_tutorial(temp_surf)
        elif self.state == STATE_CREDITS:
            self.menus.draw_credits(temp_surf)
        elif self.state == STATE_ARCADE_LEVEL_START:
            # Fondo Rojo Oscuro para el Nivel Final (v0.7.3)
            bg_color = (60, 0, 0) if self.arcade_level == 7 else BLACK
            temp_surf.fill(bg_color)
            txt = self.large_font.render(f"LEVEL {self.arcade_level}", True, WHITE)
            temp_surf.blit(txt, txt.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)))
        elif self.state == STATE_GAME_OVER: self.menus.draw_game_over(temp_surf)
        elif self.state == STATE_ENDLESS_REWARD:
            self.menus.draw_game_over(temp_surf)
            self._draw_endless_reward(temp_surf)
        elif self.state == STATE_ARCADE_REWARD: self.menus.draw_arcade_reward(temp_surf)
        
        self.vfx.draw(temp_surf)

        self.vfx.draw(temp_surf)

        # MODO ENDLESS INTRO OVERLAY (v0.8.0)
        if self.endless_active and self.endless_intro_timer > 0:
            lvl_text = self.t(f"LEVEL {self.endless_level}", f"NIVEL {self.endless_level}")
            st_title = self.large_font.render(lvl_text, True, YELLOW)
            temp_surf.blit(st_title, st_title.get_rect(center=(int(self.endless_intro_x), SCREEN_HEIGHT // 2 - 80)))
            
            # --- NUEVA LÓGICA DE ESCALADO Y MULTILÍNEA DINÁMICA ---
            max_w = SCREEN_WIDTH - 120
            max_h = 130  # Espacio vertical máximo deseado
            
            current_size = 36
            best_font = self.font
            wrapped_lines = []
            
            while current_size >= 14:
                test_font = pygame.font.SysFont("Arial", current_size, bold=True)
                line_height = test_font.get_linesize()
                
                words = self.endless_new_modifier_text.split(' ')
                new_lines = []
                current_line = ""
                for word in words:
                    clean_word = re.sub(r'\|[A-Z_]+\|', '', word)
                    clean_line = re.sub(r'\|[A-Z_]+\|', '', current_line)
                    
                    if test_font.size(clean_line + clean_word)[0] < max_w:
                        current_line += (word + " ")
                    else:
                        new_lines.append(current_line.strip())
                        current_line = word + " "
                new_lines.append(current_line.strip())
                
                total_height = len(new_lines) * line_height
                
                if total_height <= max_h or current_size == 14:
                    best_font = test_font
                    wrapped_lines = new_lines
                    break
                else:
                    current_size = max(14, int(current_size * 0.9))
            
            mod_text = f"|WHITE|{'\n'.join(wrapped_lines)}"
            draw_rich_text(temp_surf, mod_text, (int(self.endless_intro_x), SCREEN_HEIGHT // 2), best_font, max_width=None, align="center")

        # CAPA FINAL: Animaciones de Anuncio (siempre encima de todo lo demás)
        if self.show_match_point_anim and self.match_point_anim_timer > 0: 
            self._draw_match_point_anim(temp_surf)
        if self.show_golden_goal_anim and self.golden_goal_anim_timer > 0: 
            self._draw_golden_goal_anim(temp_surf)
            
        # Capa de Relámpago (LIGHTNING)
        if self.rainy_day_enabled and self.lightning_enabled and self.lightning_active and self.lightning_flash_timer > 0:
            if self.lightning_flash_timer > 0.5:
                opacity = 255
            else:
                opacity = int((self.lightning_flash_timer / 0.5) * 255)
            opacity = max(0, min(255, opacity))
            flash_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            flash_surf.fill(WHITE)
            flash_surf.set_alpha(opacity)
            temp_surf.blit(flash_surf, (0, 0))
        
        self.screen.fill(BLACK)
        self.screen.blit(temp_surf, (off_x, off_y))
        
        # CAPA FINAL: Tutorial (Fuera de temp_surf para que no tiemble con el shake si se desea, 
        # pero aquí lo ponemos al final para que siempre sea visible)
        if self.tutorial_active:
            self.menus.draw_tutorial_only(self.screen)
        
        if self.arcade_active and self.arcade_intro_timer > 0:
            # Dibujar texto de intro arcade
            # Calculamos ancho de la línea más larga para centrar el bloque
            lines = self.arcade_intro_text.split("\n")
            max_tw = 0
            for line in lines:
                # Limpiar tags para el cálculo del ancho (usando regex para ser precisos)
                clean_l = re.sub(r'\|[A-Z_]+\|', '', line)
                max_tw = max(max_tw, self.font.size(clean_l)[0])
            
            # Altura total del bloque
            # Usar fuente pequeña en español para que los modificadores no ocupen tanto (v0.6.0 Fix)
            f = self.small_font if self.language == "ES" else self.font
            th = len(lines) * f.get_linesize()
            draw_rich_text(self.screen, self.arcade_intro_text, (self.arcade_intro_x - max_tw // 2, SCREEN_HEIGHT // 2 - th // 2), f, max_width=max_tw, align="center")
            
        self._draw_chaos_banner(self.screen)
        
        pygame.display.flip()

    def _draw_endless_reward(self, surface):
        if hasattr(self.menus, 'ov_180'):
            surface.blit(self.menus.ov_180, (0,0))
        else:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            surface.blit(overlay, (0, 0))
        
        step = getattr(self, "reward_step", 0)
        
        if step == 1:
            panel_w, panel_h = 550, 320
            panel_rect = pygame.Rect(SCREEN_WIDTH//2 - panel_w//2, SCREEN_HEIGHT//2 - panel_h//2 - 50, panel_w, panel_h)
            pygame.draw.rect(surface, (15, 15, 15), panel_rect)
            pygame.draw.rect(surface, WHITE, panel_rect, 3)
            
            top_txt = self.t("You unlocked the new EXTRA modifier:", "Desbloqueaste el nuevo modificador EXTRA:")
            draw_rich_text(surface, f"|WHITE|{top_txt}", (SCREEN_WIDTH//2, panel_rect.y + 50), self.small_font, align="center")
            
            name = "ENDLESS CHAOS"
            draw_rich_text(surface, f"|GOLD|{name}", (SCREEN_WIDTH//2, panel_rect.y + 110), self.large_font, align="center")

        box_h = 110
        box = pygame.Rect(0, SCREEN_HEIGHT - box_h, SCREEN_WIDTH, box_h)
        pygame.draw.rect(surface, (20, 20, 20), box)
        pygame.draw.rect(surface, WHITE, box, 2)
        
        msg = getattr(self, "reward_text_visible", "")
        # Usamos cached surface como en el tutorial de Arcade para evitar pestañeos
        if not hasattr(self, "cached_reward_text"): self.cached_reward_text = ""
        if not hasattr(self, "cached_reward_surface"): self.cached_reward_surface = pygame.Surface((SCREEN_WIDTH, 200), pygame.SRCALPHA)
        
        if self.cached_reward_text != msg:
            self.cached_reward_text = msg
            self.cached_reward_surface.fill((0, 0, 0, 0))
            draw_rich_text(self.cached_reward_surface, f"{msg}", (0, 0), self.small_font, max_width=SCREEN_WIDTH - 100)
            
        surface.blit(self.cached_reward_surface, (50, SCREEN_HEIGHT - box_h + 30))

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

        if self.tictactoe_enabled:
            # 1. Dibujar líneas de la cuadrícula
            # Líneas verticales (x = 370, x = 430)
            pygame.draw.line(surface, (120, 120, 120), (370, 210), (370, 390), 3)
            pygame.draw.line(surface, (120, 120, 120), (430, 210), (430, 390), 3)
            # Líneas horizontales (y = 270, y = 330)
            pygame.draw.line(surface, (120, 120, 120), (310, 270), (490, 270), 3)
            pygame.draw.line(surface, (120, 120, 120), (310, 330), (490, 330), 3)
            
            # 2. Dibujar símbolos (X e O)
            for i in range(9):
                val = self.tictactoe_board[i]
                if val is None: continue
                
                row = i // 3
                col = i % 3
                cell_left = 310 + col * 60
                cell_top = 210 + row * 60
                pad = 14
                
                if val == 1: # X (Azul)
                    pygame.draw.line(surface, (50, 150, 255), (cell_left + pad, cell_top + pad), (cell_left + 60 - pad, cell_top + 60 - pad), 5)
                    pygame.draw.line(surface, (50, 150, 255), (cell_left + 60 - pad, cell_top + pad), (cell_left + pad, cell_top + 60 - pad), 5)
                elif val == 2: # O (Rojo)
                    pygame.draw.circle(surface, (255, 50, 50), (cell_left + 30, cell_top + 30), 16, 5)
                    
            # 3. Dibujar línea ganadora
            if self.tictactoe_winner is not None and self.tictactoe_win_line is not None:
                start_idx = self.tictactoe_win_line[0]
                end_idx = self.tictactoe_win_line[2]
                
                start_r, start_c = start_idx // 3, start_idx % 3
                end_r, end_c = end_idx // 3, end_idx % 3
                
                p_start = (310 + start_c * 60 + 30, 210 + start_r * 60 + 30)
                p_end = (310 + end_c * 60 + 30, 210 + end_r * 60 + 30)
                
                color = (50, 150, 255) if self.tictactoe_winner == 1 else (255, 50, 50)
                pygame.draw.line(surface, color, p_start, p_end, 7)

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
        g_idx = max(getattr(self, 'gravity_force_idx', 1), getattr(self, 'gravity_radius_idx', 1), getattr(self, 'planet_resistance_idx', 1))
        px_size = 5
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

    def _draw_mobile_controls(self, surface):
        """Dibuja botones virtuales temáticos Pixel-Art Semi-transparentes (v0.7.2)"""
        
        up_matrix = [
            [0,0,0,1,0,0,0],
            [0,0,1,1,1,0,0],
            [0,1,1,1,1,1,0],
            [1,1,1,1,1,1,1]
        ]
        
        down_matrix = [
            [1,1,1,1,1,1,1],
            [0,1,1,1,1,1,0],
            [0,0,1,1,1,0,0],
            [0,0,0,1,0,0,0]
        ]
        
        # Estrella pixel-art de 8 bits (Estilo retro limpio y sólido, 13x13): 0=transparente, 1=sólido
        star_matrix = [
            [0,0,0,0,0,0,1,0,0,0,0,0,0],
            [0,0,0,0,0,1,1,1,0,0,0,0,0],
            [0,0,0,0,0,1,1,1,0,0,0,0,0],
            [0,0,0,0,1,1,1,1,1,0,0,0,0],
            [1,1,1,1,1,1,1,1,1,1,1,1,1],
            [0,1,1,1,1,1,1,1,1,1,1,1,0],
            [0,0,1,1,1,1,1,1,1,1,1,0,0],
            [0,0,0,1,1,1,1,1,1,1,0,0,0],
            [0,0,1,1,1,1,1,1,1,1,1,0,0],
            [0,1,1,1,1,0,0,0,1,1,1,1,0],
            [0,1,1,1,0,0,0,0,0,1,1,1,0],
            [1,1,1,0,0,0,0,0,0,0,1,1,1],
            [1,1,0,0,0,0,0,0,0,0,0,1,1]
        ]

        def draw_pixel_icon(surf, matrix, rect, color, pixel_size=10):
            rows, cols = len(matrix), len(matrix[0])
            sx = rect.centerx - (cols * pixel_size) // 2
            sy = rect.centery - (rows * pixel_size) // 2
            for r in range(rows):
                for c in range(cols):
                    if matrix[r][c]:
                        pygame.draw.rect(surf, color, (sx + c * pixel_size, sy + r * pixel_size, pixel_size, pixel_size))

        players = [(self.paddle1, [(self.btn_p1_up, up_matrix), (self.btn_p1_down, down_matrix), (self.btn_p1_power, star_matrix)])]
        if not self.is_ai_mode:
            players.append((self.paddle2, [(self.btn_p2_up, up_matrix), (self.btn_p2_down, down_matrix), (self.btn_p2_power, star_matrix)]))

        for paddle, btns in players:
            if self.geographic_controls:
                btns = [(btns[2][0], star_matrix)] # Solo power
                
            for r, matrix in btns:
                is_active = any(r.collidepoint(pos) for pos in self.fingers.values())
                
                # Blit del fondo semi-transparente pre-asignado libre de overhead
                bg_surf = self.mobile_btn_surf_active if is_active else self.mobile_btn_surf_normal
                surface.blit(bg_surf, r.topleft)
                
                if matrix == star_matrix:
                    # Dibuja la estrella con color temático según el poder o color del paddle
                    R, G, B = paddle.color
                    mult = 1.0 if is_active else 0.75
                    color = (int(R * mult), int(G * mult), int(B * mult))
                    draw_pixel_icon(surface, matrix, r, color, pixel_size=4)
                else:
                    # Flechas: Blanco si activo, gris si no
                    color = WHITE if is_active else (160, 160, 160)
                    draw_pixel_icon(surface, matrix, r, color, pixel_size=8)

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
        """Versión síncrona clásica (PC)"""
        try:
            while True:
                events = pygame.event.get()
                for event in events:
                    if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                
                dt = self.clock.tick(FPS) / 1000.0
                self.handle_input(events, dt)
                self.update(dt)
                self.draw()
        except Exception as e:
            import traceback
            print(f"CRASH DETECTADO: {e}")
            traceback.print_exc()
            pygame.quit()

    async def run_async(self):
        """Versión asíncrona para Web/Pygbag (Móviles)"""
        try:
            while True:
                events = pygame.event.get()
                for event in events:
                    if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                
                dt = self.clock.tick(FPS) / 1000.0
                self.handle_input(events, dt)
                self.update(dt)
                self.draw()
                
                await asyncio.sleep(0) # Liberar control al navegador
        except Exception as e:
            import traceback
            print(f"CRASH ASYNC DETECTADO: {e}")
            traceback.print_exc()
            pygame.quit()
