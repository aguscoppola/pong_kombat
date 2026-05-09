import pygame
import re
from constants import *
from ui_components import draw_rich_text, draw_remove_option, draw_tooltip

class MenuManager:
    def __init__(self, game):
        self.game = game

    def draw_main_menu(self, surface):
        ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)); ov.set_alpha(160); ov.fill(BLACK); surface.blit(ov, (0,0))
        t1, t2 = self.game.large_font.render("PONG ", True, WHITE), self.game.large_font.render("KOMBAT", True, RED)
        tw = t1.get_width() + t2.get_width()
        sx, ty = SCREEN_WIDTH//2 - tw//2, SCREEN_HEIGHT//4 - 20
        surface.blit(t1, (sx, ty)); surface.blit(t2, (sx+t1.get_width(), ty))
        mpos = pygame.mouse.get_pos()
        for r, txt in [(self.game.btn_play_rect, self.game.t("PLAY", "JUGAR")), (self.game.btn_modifiers_rect, self.game.t("MODIFIERS", "MODIFICADORES")), (self.game.btn_settings_rect, self.game.t("SETTINGS", "AJUSTES"))]:
            is_hover = r.collidepoint(mpos); pygame.draw.rect(surface, (40, 40, 40) if is_hover else BLACK, r); pygame.draw.rect(surface, WHITE, r, 4)
            f_to_use = self.game.font
            if f_to_use.size(txt)[0] > r.width - 20: f_to_use = self.game.medium_font
            st = f_to_use.render(txt, True, WHITE); surface.blit(st, st.get_rect(center=r.center))

    def draw_mode_selection(self, surface):
        surface.fill(BLACK)
        title = self.game.large_font.render(self.game.t("SELECT MODE", "SELECCIONAR MODO"), True, WHITE); surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        mpos = pygame.mouse.get_pos()
        for btn, label, is_solo in [(self.game.btn_multi_rect, "MULTIPLAYER", False), (self.game.btn_solo_rect, "SOLO", True)]:
            hover = btn.collidepoint(mpos); color = WHITE if hover else GRAY; pygame.draw.rect(surface, color, btn, 4)
            txt = self.game.medium_font.render(label, True, color); surface.blit(txt, (btn.centerx - txt.get_width()//2, btn.top + 30))
            img_rect = pygame.Rect(btn.x + 20, btn.y + 80, btn.width - 40, btn.height - 130); pygame.draw.rect(surface, (30, 30, 30), img_rect)
            pygame.draw.rect(surface, WHITE, (img_rect.x + 20, img_rect.centery - 30, 10, 60)); pygame.draw.rect(surface, WHITE, (img_rect.centerx - 5, img_rect.centery - 5, 10, 10))
            if not is_solo: pygame.draw.rect(surface, WHITE, (img_rect.right - 30, img_rect.centery - 30, 10, 60))
            else:
                monitor_rect = pygame.Rect(img_rect.right - 70, img_rect.centery - 35, 50, 70); pygame.draw.rect(surface, WHITE, monitor_rect, 2)
                ai_txt = self.game.small_font.render("AI", True, WHITE); surface.blit(ai_txt, (monitor_rect.centerx - ai_txt.get_width()//2, monitor_rect.centery - ai_txt.get_height()//2))
        pygame.draw.rect(surface, BLACK, self.game.back_btn_rect); pygame.draw.rect(surface, WHITE, self.game.back_btn_rect, 2)
        bt = self.game.small_font.render(self.game.t("BACK", "VOLVER"), True, WHITE); surface.blit(bt, bt.get_rect(center=self.game.back_btn_rect.center))

    def draw_modifiers(self, surface):
        pygame.draw.rect(surface, BLACK, self.game.modifiers_panel_rect); pygame.draw.rect(surface, WHITE, self.game.modifiers_panel_rect, 4)
        title_txt = self.game.t("MATCH MODIFIERS", "MODIFICADORES DE LA PARTIDA")
        f = self.game.font if self.game.font.size(title_txt)[0] < 500 else self.game.medium_font
        t = f.render(title_txt, True, WHITE); surface.blit(t, t.get_rect(center=(SCREEN_WIDTH//2, self.game.modifiers_panel_rect.y+30)))
        pygame.draw.rect(surface, BLACK, self.game.back_btn_rect); pygame.draw.rect(surface, WHITE, self.game.back_btn_rect, 2)
        bt = self.game.small_font.render(self.game.t("BACK", "VOLVER"), True, WHITE); surface.blit(bt, bt.get_rect(center=self.game.back_btn_rect.center))
        tab_y = self.game.modifiers_panel_rect.top - 44
        self.game.tab_all_rect.topleft, self.game.tab_extras_rect.topleft, self.game.tab_skins_rect.topleft = (self.game.modifiers_panel_rect.left, tab_y), (self.game.tab_all_rect.right + 5, tab_y), (self.game.tab_extras_rect.right + 5, tab_y)
        for r, txt, key in [(self.game.tab_all_rect, self.game.t("ALL", "TODO"), "ALL"), (self.game.tab_extras_rect, self.game.t("EXTRAS", "EXTRAS"), "EXTRAS"), (self.game.tab_skins_rect, self.game.t("SKINS", "ASPECTOS"), "SKINS")]:
            bg = (40,40,40) if self.game.modifiers_tab==key else BLACK
            pygame.draw.rect(surface, bg, r, border_top_left_radius=8, border_top_right_radius=8); pygame.draw.rect(surface, WHITE, r, 2, border_top_left_radius=8, border_top_right_radius=8)
            surface.blit(self.game.tiny_font.render(txt, True, WHITE), self.game.tiny_font.render(txt, True, WHITE).get_rect(center=r.center))
        old_clip = surface.get_clip(); clip = pygame.Rect(self.game.modifiers_panel_rect.x+10, self.game.modifiers_panel_rect.y+60, self.game.modifiers_panel_rect.width-40, self.game.modifiers_panel_rect.height-70)
        surface.set_clip(clip); self._draw_modifier_content(surface); surface.set_clip(old_clip)
        self.game.scroll_y = max(0, min(self.game.scroll_y, self.game.max_scroll))
        if self.game.max_scroll > 0: self.game.scrollbar_thumb_rect.y = self.game.scrollbar_rect.y + (self.game.scroll_y / self.game.max_scroll) * (self.game.scrollbar_rect.height - self.game.scrollbar_thumb_height)
        pygame.draw.rect(surface, (50,50,50), self.game.scrollbar_rect); pygame.draw.rect(surface, WHITE, self.game.scrollbar_thumb_rect)
        self._draw_tooltips(clip, surface)

    def _draw_modifier_content(self, surface):
        off, lm, ox = self.game.scroll_y, self.game.modifiers_panel_rect.x + 50, self.game.modifiers_panel_rect.centerx + 50
        self.game.max_y_rendered = 0
        for r in [self.game.match_point_rect, self.game.golden_goal_anim_rect, self.game.reroll_rect, self.game.all_reroll_rect, self.game.equal_watches_rect, self.game.equal_powers_rect, self.game.watches_kept_rect, self.game.remove_watches_toggle_rect, self.game.remove_power_toggle_rect, self.game.experimental_toggle_rect]: r.y = -1000
        if self.game.modifiers_tab == "ALL": self._draw_all_tab_full(surface, off, lm, ox)
        elif self.game.modifiers_tab == "EXTRAS": self._draw_extras_tab_full(surface, off, lm, ox)
        elif self.game.modifiers_tab == "SKINS": self._draw_skins_tab_full(surface, off, lm, ox)
        self.game.max_scroll = max(0, self.game.max_y_rendered + 60 - 330)

    def _draw_all_tab_full(self, surface, off, lm, ox):
        cy = 100
        surface.blit(self.game.small_font.render(self.game.t("Score limit:", "Límite de puntos:"), True, WHITE), (lm, self.game.modifiers_panel_rect.y + cy - off))
        self.game.score_btn_rect.update(ox, self.game.modifiers_panel_rect.y + cy - 5 - off, 80, 40); pygame.draw.rect(surface, BLACK, self.game.score_btn_rect); pygame.draw.rect(surface, WHITE, self.game.score_btn_rect, 2)
        surface.blit(self.game.small_font.render(str(self.game.max_score), True, WHITE), self.game.small_font.render(str(self.game.max_score), True, WHITE).get_rect(center=self.game.score_btn_rect.center))
        cy += 80; self._draw_sub_selector(cy, self.game.t("Ball speed increase:", "Aumento de velocidad:"), self.game.ball_speed_multiplier_names[self.game.ball_speed_multiplier_idx], self.game.ball_speed_btn_rect, off, ox, lm, surface, sub_val=f"{self.game.ball_speed_multiplier_options[self.game.ball_speed_multiplier_idx]-1:g}")
        cy += 80; self._draw_sub_selector(cy, self.game.t("Initial ball speed:", "Velocidad inicial:"), self.game.initial_ball_speed_names[self.game.initial_ball_speed_idx], self.game.initial_ball_speed_rect, off, ox, lm, surface, sub_val=f"x{self.game.initial_ball_speed_options[self.game.initial_ball_speed_idx]}")
        cy += 80; self._draw_sub_selector(cy, self.game.t("|YELLOW|Yellow |WHITE|Power Speed Up:", "Aumento de velocidad\ndel poder |YELLOW|AMARILLO"), self.game.yellow_speed_up_names[self.game.yellow_speed_up_idx], self.game.yellow_speed_up_rect, off, ox, lm, surface, sub_val=f"{int(self.game.yellow_speed_up_options[self.game.yellow_speed_up_idx]*100)}%")
        cy += 80; draw_remove_option(self.game, cy, self.game.t("Numbers encapsulating powers", "Los números\nencapsulan poderes"), self.game.encapsulate_powers_enabled, self.game.encapsulate_powers_rect, self.game.encapsulate_powers_text_rect, active_color=CYAN, offset=off, surface=surface)
        cy += 80; draw_remove_option(self.game, cy, self.game.t("MATCH POINT:", "PUNTO DE PARTIDA:"), self.game.match_point_enabled, self.game.match_point_rect, self.game.match_point_text_rect, offset=off, surface=surface)
        cy += 80; draw_remove_option(self.game, cy, self.game.t("|GOLD|GOLDEN |WHITE|Goal animation:", "|GOLD|Animación de GOL |WHITE|DE ORO:"), self.game.golden_goal_anim_enabled, self.game.golden_goal_anim_rect, self.game.golden_goal_anim_text_rect, offset=off, surface=surface)
        cy += 80; draw_remove_option(self.game, cy, self.game.t("Re-rolls (|ORANGE|ORANGE|WHITE|/|YELLOW|YELLOW|WHITE|):", "Re-rolls (|ORANGE|NARANJA|WHITE|/|YELLOW|AMARILLO|WHITE|):"), self.game.reroll_enabled, self.game.reroll_rect, self.game.reroll_text_rect, offset=off, surface=surface)
        if self.game.reroll_enabled: cy += 80; draw_remove_option(self.game, cy, self.game.t("All Re-roll (|RED|RED|WHITE|/|GREEN|GREEN|WHITE|):", "Todo Re-roll (|RED|ROJO|WHITE|/|GREEN|VERDE|WHITE|):"), self.game.all_reroll_enabled, self.game.all_reroll_rect, self.game.all_reroll_text_rect, offset=off, surface=surface)
        cy += 80; draw_remove_option(self.game, cy, self.game.t("Equal watches (20%):", "Relojes iguales (20%):"), self.game.equal_watches_enabled, self.game.equal_watches_rect, self.game.equal_watches_text_rect, offset=off, surface=surface)
        cy += 80; draw_remove_option(self.game, cy, self.game.t("Equal powers (25%):", "Poderes iguales (25%):"), self.game.equal_powers_enabled, self.game.equal_powers_rect, self.game.equal_powers_text_rect, offset=off, surface=surface)
        cy += 80; draw_remove_option(self.game, cy, self.game.t("Watches kept:", "Relojes guardados:"), self.game.watches_kept_enabled, self.game.watches_kept_rect, self.game.watches_kept_text_rect, offset=off, surface=surface)
        cy += 80; surface.blit(self.game.small_font.render(self.game.t("Watch spawn hits:", "Golpes para spawn de reloj:"), True, WHITE), (lm, self.game.modifiers_panel_rect.y + cy - off))
        self.game.watch_spawn_hits_rect.update(ox, self.game.modifiers_panel_rect.y + cy - 5 - off, 80, 40); pygame.draw.rect(surface, BLACK, self.game.watch_spawn_hits_rect); pygame.draw.rect(surface, WHITE, self.game.watch_spawn_hits_rect, 2)
        surface.blit(self.game.small_font.render(str(self.game.watch_spawn_hits_options[self.game.watch_spawn_hits_idx]), True, WHITE), self.game.small_font.render(str(self.game.watch_spawn_hits_options[self.game.watch_spawn_hits_idx]), True, WHITE).get_rect(center=self.game.watch_spawn_hits_rect.center))
        cy += 80; draw_rich_text(surface, self.game.t("Power auto grant hits:", "Toques para recibir\nun nuevo poder:"), (lm, self.game.modifiers_panel_rect.y + cy - off), self.game.small_font)
        self.game.power_auto_grant_hits_rect.update(ox, self.game.modifiers_panel_rect.y + cy - 5 - off, 80, 40); pygame.draw.rect(surface, BLACK, self.game.power_auto_grant_hits_rect); pygame.draw.rect(surface, WHITE, self.game.power_auto_grant_hits_rect, 2)
        surface.blit(self.game.small_font.render(str(self.game.power_auto_grant_hits_options[self.game.power_auto_grant_hits_idx]), True, WHITE), self.game.small_font.render(str(self.game.power_auto_grant_hits_options[self.game.power_auto_grant_hits_idx]), True, WHITE).get_rect(center=self.game.power_auto_grant_hits_rect.center))
        cy += 80; draw_remove_option(self.game, cy, self.game.t("Start with power:", "Iniciar con poder:"), self.game.start_with_power_enabled, self.game.start_with_power_rect, self.game.start_with_power_text_rect, offset=off, surface=surface)
        cy += 80; draw_remove_option(self.game, cy, self.game.t("Remove a watch", "Eliminar un reloj"), self.game.remove_watches_expanded, self.game.remove_watches_toggle_rect, self.game.remove_watches_toggle_text_rect, is_checkbox=False, offset=off, surface=surface)
        if self.game.remove_watches_expanded:
            for lbl, col in [("BLUE", BLUE), ("RED", RED), ("PURPLE", PURPLE), ("WHITE", WHITE), ("YELLOW", YELLOW)]:
                cy += 60; draw_remove_option(self.game, cy, f" - Remove |{lbl}| {lbl} |WHITE| watch", getattr(self.game, f"remove_{lbl.lower()}"), getattr(self.game, f"remove_{lbl.lower()}_rect"), getattr(self.game, f"remove_{lbl.lower()}_text_rect"), active_color=col, offset=off, surface=surface)
        cy += 80; draw_remove_option(self.game, cy, self.game.t("Remove a power", "Eliminar un poder"), self.game.remove_power_expanded, self.game.remove_power_toggle_rect, self.game.remove_power_toggle_text_rect, is_checkbox=False, offset=off, surface=surface)
        if self.game.remove_power_expanded:
            for lbl, col in [("RED", RED), ("GREEN", GREEN), ("YELLOW", YELLOW), ("ORANGE", ORANGE)]:
                cy += 60; draw_remove_option(self.game, cy, f" - Remove |{lbl}| {lbl} |WHITE| power", getattr(self.game, f"remove_power_{lbl.lower()}"), getattr(self.game, f"remove_power_{lbl.lower()}_rect"), getattr(self.game, f"remove_power_{lbl.lower()}_text_rect"), active_color=col, offset=off, surface=surface)
        self.game.max_y_rendered = cy

    def _draw_extras_tab_full(self, surface, off, lm, ox):
        cy = 100
        draw_remove_option(self.game, cy, self.game.t("Enable |ORANGE| ORANGE |WHITE| watch", "Activar reloj |ORANGE| NARANJA"), self.game.orange_watch_enabled, self.game.orange_watch_rect, self.game.orange_watch_text_rect, active_color=ORANGE, offset=off, surface=surface)
        cy += 60; draw_remove_option(self.game, cy, self.game.t("Enable |GOLD|X2 MULTIPLIER |WHITE|at start", "Activar |GOLD|MULTIPLICADOR X2 |WHITE|al inicio"), self.game.start_x2_enabled, self.game.start_x2_rect, self.game.start_x2_text_rect, active_color=GOLD, offset=off, surface=surface)
        cy += 60; draw_remove_option(self.game, cy, self.game.t("Enable |BLUE|MAG|RED|NET|WHITE| power", "Activar poder |BLUE|MAG|RED|NET"), self.game.magnet_power_enabled, self.game.magnet_power_rect, self.game.magnet_power_text_rect, active_color=GRAY, offset=off, surface=surface)
        cy += 60; draw_remove_option(self.game, cy, self.game.t("Enable |GHOST| GHOST |WHITE| power", "Activar poder |GHOST| FANTASMA"), self.game.ghost_power_enabled, self.game.ghost_power_rect, self.game.ghost_power_text_rect, active_color=GHOST_COLOR, offset=off, surface=surface)
        if self.game.ghost_power_enabled: cy += 60; draw_remove_option(self.game, cy, " - |CYAN|Identical |WHITE|ball", self.game.ghost_identical_enabled, self.game.ghost_identical_rect, self.game.ghost_identical_text_rect, active_color=CYAN, offset=off, surface=surface)
        cy += 60; draw_remove_option(self.game, cy, self.game.t("Enable |GUM_PINK|GUM|WHITE| power", "Activar poder de |GUM_PINK|CHICLE"), self.game.gum_power_enabled, self.game.gum_power_rect, self.game.gum_power_text_rect, active_color=GUM_PINK, offset=off, surface=surface)
        cy += 60; draw_remove_option(self.game, cy, self.game.t("|GOLD|GOLDEN |WHITE|GOAL rule", "|GOLD|GOL DE ORO |WHITE|(Regla)"), self.game.experimental_golden_goal, self.game.experimental_golden_goal_rect, self.game.experimental_golden_goal_text_rect, active_color=GOLD, offset=off, surface=surface)
        cy += 60; draw_remove_option(self.game, cy, self.game.t("Allow floating planets", "Activar planetas flotantes"), self.game.floating_planets_enabled, self.game.floating_planets_rect, self.game.floating_planets_text_rect, active_color=CYAN, offset=off, surface=surface)
        if self.game.floating_planets_enabled:
            cy += 60; self._draw_sub_selector(cy, self.game.t("Gravity:", "Fuerza de gravedad:"), self.game.gravity_force_names[self.game.gravity_force_idx], self.game.gravity_force_rect, off, ox, lm, surface, sub_val=self.game.gravity_force_options[self.game.gravity_force_idx], text_rect=self.game.gravity_force_text_rect)
            cy += 60; self._draw_sub_selector(cy, self.game.t("Gravity Radius:", "Radio de gravedad:"), self.game.gravity_radius_names[self.game.gravity_radius_idx], self.game.gravity_radius_rect, off, ox, lm, surface, sub_val=str(self.game.gravity_radius_options[self.game.gravity_radius_idx]), text_rect=self.game.gravity_radius_text_rect)
            cy += 60; draw_remove_option(self.game, cy, self.game.t("Destructible planets", "Planetas destructibles"), self.game.destructible_planets_enabled, self.game.destructible_planets_rect, self.game.destructible_planets_text_rect, active_color=RED, offset=off, surface=surface)
            if self.game.destructible_planets_enabled: cy += 60; self._draw_sub_selector(cy, self.game.t("Planet resistance:", "Resistencia:"), self.game.planet_resistance_names[self.game.planet_resistance_idx], self.game.planet_resistance_rect, off, ox, lm, surface, sub_val=str(self.game.planet_resistance_options[self.game.planet_resistance_idx]), text_rect=self.game.planet_resistance_text_rect)
        cy += 60; draw_remove_option(self.game, cy, self.game.t("Dimensional |BLUE|POR|RED|TALS", "|BLUE|POR|RED|TALES |WHITE|Dimensionales"), self.game.portals_enabled, self.game.portals_rect, self.game.portals_text_rect, active_color=CYAN, offset=off, surface=surface)
        if self.game.portals_enabled:
            cy += 60; self._draw_sub_selector(cy, self.game.t("PORTAL size:", "Tamaño del PORTAL:"), self.game.portal_size_names[self.game.portal_size_idx], self.game.portal_size_rect, off, ox, lm, surface, sub_val=str(self.game.portal_size_options[self.game.portal_size_idx]), text_rect=self.game.portal_size_text_rect)
            cy += 60; draw_remove_option(self.game, cy, self.game.t("Vertical PORTALS", "PORTALES Verticales"), self.game.portals_vertical, self.game.portals_vertical_rect, self.game.portals_vertical_text_rect, active_color=BLUE, offset=off, surface=surface)
            cy += 60; draw_remove_option(self.game, cy, self.game.t("2 more |RED|POR|GREEN|TALS", "2 |RED|POR|GREEN|TALES |WHITE|más"), self.game.more_portals_enabled, self.game.more_portals_rect, self.game.more_portals_text_rect, active_color=BLUE, offset=off, surface=surface)
        cy += 60; draw_remove_option(self.game, cy, self.game.t("Intrusive Mouse", "Ratón Intruso"), self.game.add_mouse_enabled, self.game.add_mouse_rect, self.game.add_mouse_text_rect, active_color=BROWN, offset=off, surface=surface)
        if self.game.add_mouse_enabled:
            cy += 60; self._draw_sub_selector(cy, self.game.t("Mouse speed:", "Velocidad de ratón:"), self.game.mouse_speed_names[self.game.mouse_speed_idx], self.game.mouse_speed_rect, off, ox, lm, surface, sub_val=str(self.game.mouse_speed_options[self.game.mouse_speed_idx]), text_rect=self.game.mouse_speed_text_rect)
            cy += 60; self._draw_sub_selector(cy, self.game.t("Mouse appear time:", "Tiempo aparición:"), self.game.mouse_appear_names[self.game.mouse_appear_idx], self.game.mouse_appear_rect, off, ox, lm, surface, sub_val=f"{self.game.mouse_appear_options[self.game.mouse_appear_idx]}s", text_rect=self.game.mouse_appear_text_rect)
        cy += 60; draw_remove_option(self.game, cy, self.game.t("Enable |GRAY|REVOLVER|WHITE| power", "Activar poder de |GRAY|REVOLVER"), self.game.revolver_enabled, self.game.revolver_rect, self.game.revolver_text_rect, active_color=(100,100,100), offset=off, surface=surface)
        if self.game.revolver_enabled: cy += 60; self._draw_sub_selector(cy, self.game.t(" - Probability of appear:", " - Probabilidad de aparición:"), self.game.revolver_prob_names[self.game.revolver_prob_idx], self.game.revolver_prob_rect, off, ox, lm, surface, text_rect=self.game.revolver_prob_text_rect)
        self.game.max_y_rendered = cy

    def _draw_skins_tab_full(self, surface, off, lm, ox):
        cy = 100
        # 1. Orange Power Skin
        lbl1 = self.game.t("Change |ORANGE| ORANGE |WHITE| power:", "Cambiar poder |ORANGE| NARANJA:")
        draw_rich_text(surface, lbl1, (lm, self.game.modifiers_panel_rect.y + cy - off), self.game.small_font)
        self.game.orange_skin_rect.update(ox, self.game.modifiers_panel_rect.y + cy - 5 - off, 130, 40)
        pygame.draw.rect(surface, BLACK, self.game.orange_skin_rect); pygame.draw.rect(surface, WHITE, self.game.orange_skin_rect, 2)
        name = self.game.orange_skin_options[self.game.orange_skin_idx]
        d_name = self.game.t(name, "Normal" if name=="Default" else name)
        col = CYAN if name.upper() == "HADOUKEN" else WHITE
        surface.blit(self.game.small_font.render(d_name, True, col), self.game.small_font.render(d_name, True, col).get_rect(center=self.game.orange_skin_rect.center))
        
        # 2. Yellow Watch Skin
        cy += 80
        lbl2 = self.game.t("Change |YELLOW| YELLOW |WHITE| watch:", "Cambiar reloj |YELLOW| AMARILLO:")
        draw_rich_text(surface, lbl2, (lm, self.game.modifiers_panel_rect.y + cy - off), self.game.small_font)
        self.game.yellow_watch_skin_rect.update(ox, self.game.modifiers_panel_rect.y + cy - 5 - off, 130, 40)
        pygame.draw.rect(surface, BLACK, self.game.yellow_watch_skin_rect); pygame.draw.rect(surface, WHITE, self.game.yellow_watch_skin_rect, 2)
        y_name = self.game.yellow_watch_skin_options[self.game.yellow_watch_skin_idx]
        y_d_name = self.game.t(y_name, "CRUZ" if y_name == "CROSS" else ("Normal" if y_name == "Default" else y_name))
        y_col = BROWN if y_name.upper() == "CROSS" else WHITE
        surface.blit(self.game.small_font.render(y_d_name, True, y_col), self.game.small_font.render(y_d_name, True, y_col).get_rect(center=self.game.yellow_watch_skin_rect.center))

        # 3. Ball Skin
        cy += 80
        lbl3 = self.game.t("Change BALL skin:", "Cambiar aspecto PELOTA:")
        draw_rich_text(surface, lbl3, (lm, self.game.modifiers_panel_rect.y + cy - off), self.game.small_font)
        self.game.ball_skin_rect.update(ox, self.game.modifiers_panel_rect.y + cy - 5 - off, 130, 40)
        pygame.draw.rect(surface, BLACK, self.game.ball_skin_rect); pygame.draw.rect(surface, WHITE, self.game.ball_skin_rect, 2)
        b_name = self.game.ball_skin_options[self.game.ball_skin_idx]
        b_map = {"Default": "Clásica", "Fireball": "Fuego", "Neon": "Neón", "CHEESE": "QUESO", "Tennis": "TENNIS"}
        b_d_name = self.game.t(b_name, b_map.get(b_name, b_name))
        b_col = WHITE
        if b_name.upper() == "CHEESE": b_col = YELLOW
        elif b_name.upper() == "TENNIS": b_col = GREEN
        surface.blit(self.game.small_font.render(b_d_name, True, b_col), self.game.small_font.render(b_d_name, True, b_col).get_rect(center=self.game.ball_skin_rect.center))
        
        self.game.max_y_rendered = cy

    def draw_settings(self, surface):
        pygame.draw.rect(surface, BLACK, self.game.modifiers_panel_rect); pygame.draw.rect(surface, WHITE, self.game.modifiers_panel_rect, 4)
        t = self.game.font.render(self.game.t("SETTINGS", "AJUSTES"), True, WHITE); surface.blit(t, t.get_rect(center=(SCREEN_WIDTH//2, self.game.modifiers_panel_rect.y+40)))
        lm, ox, cy = self.game.modifiers_panel_rect.x + 100, self.game.modifiers_panel_rect.centerx + 50, self.game.modifiers_panel_rect.y + 120
        draw_rich_text(surface, "Language / Idioma", (lm, cy), self.game.small_font)
        self.game.lang_rect.update(ox, cy - 5, 130, 40); pygame.draw.rect(surface, BLACK, self.game.lang_rect); pygame.draw.rect(surface, WHITE, self.game.lang_rect, 2)
        surface.blit(self.game.small_font.render("ESPAÑOL" if self.game.language=="ES" else "ENGLISH", True, YELLOW), self.game.small_font.render("ESPAÑOL" if self.game.language=="ES" else "ENGLISH", True, YELLOW).get_rect(center=self.game.lang_rect.center))
        cy += 80; draw_rich_text(surface, self.game.t("Visual Effects:", "Efectos Visuales:"), (lm, cy), self.game.small_font)
        self.game.vfx_rect.update(ox + 50, cy - 5, 30, 30); pygame.draw.rect(surface, BLACK, self.game.vfx_rect); pygame.draw.rect(surface, WHITE, self.game.vfx_rect, 2)
        if self.game.vfx_enabled: pygame.draw.rect(surface, GREEN, self.game.vfx_rect.inflate(-10, -10))
        cy += 80; draw_rich_text(surface, self.game.t("Volume:", "Volumen:"), (lm, cy), self.game.small_font)
        self.game.volume_bar_rect.update(ox, cy + 10, 200, 10); pygame.draw.rect(surface, GRAY, self.game.volume_bar_rect); pygame.draw.rect(surface, WHITE, self.game.volume_bar_rect, 1)
        self.game.volume_handle_rect.center = (self.game.volume_bar_rect.x + (self.game.sfx_volume * self.game.volume_bar_rect.width), self.game.volume_bar_rect.centery); pygame.draw.rect(surface, WHITE, self.game.volume_handle_rect)
        cy += 80; draw_rich_text(surface, self.game.t("Screen Shake:", "Temblor de Pantalla:"), (lm, cy), self.game.small_font)
        self.game.shake_rect.update(ox + 50, cy - 5, 30, 30); pygame.draw.rect(surface, BLACK, self.game.shake_rect); pygame.draw.rect(surface, WHITE, self.game.shake_rect, 2)
        if self.game.shake_enabled: pygame.draw.rect(surface, GREEN, self.game.shake_rect.inflate(-10, -10))
        self.game.settings_back_btn_rect.update(self.game.modifiers_panel_rect.right - 100, self.game.modifiers_panel_rect.y + 20, 80, 40); pygame.draw.rect(surface, BLACK, self.game.settings_back_btn_rect); pygame.draw.rect(surface, WHITE, self.game.settings_back_btn_rect, 2)
        surface.blit(self.game.tiny_font.render(self.game.t("BACK", "VOLVER"), True, WHITE), self.game.tiny_font.render(self.game.t("BACK", "VOLVER"), True, WHITE).get_rect(center=self.game.settings_back_btn_rect.center))
        self.game.settings_apply_btn_rect.update(SCREEN_WIDTH//2 - 65, self.game.modifiers_panel_rect.bottom - 60, 130, 45); pygame.draw.rect(surface, (0, 100, 0), self.game.settings_apply_btn_rect); pygame.draw.rect(surface, WHITE, self.game.settings_apply_btn_rect, 2)
        surface.blit(self.game.small_font.render(self.game.t("APPLY", "APLICAR"), True, WHITE), self.game.small_font.render(self.game.t("APPLY", "APLICAR"), True, WHITE).get_rect(center=self.game.settings_apply_btn_rect.center))

    def draw_game_over(self, surface):
        ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)); ov.set_alpha(180); ov.fill(BLACK); surface.blit(ov, (0,0))
        lines = self.game.winner_text.split("\n")
        for i, line in enumerate(lines):
            f = self.game.large_font if i == 0 else self.game.font
            
            # Limpiar tags para calcular el ancho real (centrado)
            clean_line = re.sub(r'\|[A-Z_]+\|', '', line)
            tw = f.size(clean_line)[0]
            pos = (SCREEN_WIDTH // 2 - tw // 2, SCREEN_HEIGHT // 3 + i * 60)
            
            # Usar draw_rich_text para renderizar con colores
            draw_rich_text(surface, line, pos, f, GOLD if i==0 else WHITE)
            
        self.game.btn_gameover_restart.update(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 40, 300, 50); self.game.btn_gameover_menu.update(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 105, 300, 50)
        for r, txt in [(self.game.btn_gameover_restart, self.game.t("Restart Game", "Reiniciar Juego")), (self.game.btn_gameover_menu, self.game.t("Back to Menu", "Volver al Menú"))]:
            is_hover = r.collidepoint(pygame.mouse.get_pos()); pygame.draw.rect(surface, (40, 40, 40) if is_hover else BLACK, r); pygame.draw.rect(surface, GOLD if is_hover else WHITE, r, 3)
            surface.blit(self.game.font.render(txt, True, WHITE), self.game.font.render(txt, True, WHITE).get_rect(center=r.center))

    def _draw_sub_selector(self, curr_y, label, val_name, rect, off, ox, lm, surface, sub_val=None, text_rect=None):
        draw_y = self.game.modifiers_panel_rect.y + curr_y - off
        draw_rich_text(surface, label, (lm, draw_y), self.game.small_font)
        if text_rect: text_rect.update(lm, draw_y, 400, 30)
        
        rect.update(ox, draw_y - 5, 130, 40); pygame.draw.rect(surface, BLACK, rect); pygame.draw.rect(surface, WHITE, rect, 2)
        translations = {"None": "Ninguno", "Low": "Bajo", "Medium": "Medio", "High": "Alto", "Extreme": "Extremo", "Default": "Normal", "Slow": "Lento", "Fast": "Rápido", "Sonic": "Sónico", "Moon": "Luna", "Planet": "Planeta", "Gas Giant": "Gigante", "Star": "Estrella"}
        
        # Colores especiales para planetas
        col = WHITE
        v_upper = val_name.upper()
        if "MOON" in v_upper: col = (180, 180, 180)
        elif "PLANET" in v_upper: col = (50, 100, 255)
        elif "GAS GIANT" in v_upper: col = (230, 180, 140)
        elif "STAR" in v_upper: col = YELLOW
        
        st = self.game.small_font.render(translations.get(val_name, val_name) if self.game.language=="ES" else val_name, True, col)
        surface.blit(st, st.get_rect(center=rect.center))
        if sub_val: surface.blit(self.game.tiny_font.render(str(sub_val), True, GRAY), (rect.right + 10, rect.centery - self.game.tiny_font.get_height()//2))

    def _draw_tooltips(self, clip, surface):
        m = pygame.mouse.get_pos()
        if not clip.collidepoint(m): return
        import assets
        lang_dict = assets.TOOLTIPS.get(self.game.language, assets.TOOLTIPS["EN"])
        
        # Filtrar áreas según la pestaña activa
        areas = []
        tab = self.game.modifiers_tab
        
        if tab == "ALL":
            areas = [
                (self.game.match_point_text_rect, "match_point"), (self.game.golden_goal_anim_text_rect, "golden_goal_anim"), 
                (self.game.reroll_text_rect, "reroll"), (self.game.equal_watches_text_rect, "equal_watches"), 
                (self.game.equal_powers_rect, "equal_powers"), (self.game.watches_kept_text_rect, "watches_kept"), 
                (self.game.watch_spawn_hits_text_rect, "watch_spawn"), (self.game.power_auto_grant_hits_text_rect, "power_spawn"), 
                (self.game.start_with_power_text_rect, "start_with_power"), (self.game.encapsulate_powers_text_rect, "encapsulate_powers")
            ]
        elif tab == "EXTRAS":
            areas = [
                (self.game.orange_watch_text_rect, "orange_watch"), (self.game.start_x2_text_rect, "start_x2"),
                (self.game.magnet_power_text_rect, "magnet_power"), (self.game.ghost_power_text_rect, "ghost_power"), 
                (self.game.ghost_identical_text_rect, "ghost_identical"), (self.game.gum_power_text_rect, "gum_power"),
                (self.game.experimental_golden_goal_text_rect, "exp_golden_goal"), (self.game.floating_planets_text_rect, "floating_planets"), 
                (self.game.destructible_planets_text_rect, "destructible_planets"), (self.game.portals_text_rect, "portals"), 
                (self.game.portals_vertical_text_rect, "portals_vertical"), (self.game.more_portals_text_rect, "more_portals"),
                (self.game.add_mouse_text_rect, "add_mouse"), (self.game.revolver_text_rect, "revolver")
            ]
        
        for rect, key in areas:
            if rect.collidepoint(m): draw_tooltip(self.game, lang_dict.get(key, []), surface); break
