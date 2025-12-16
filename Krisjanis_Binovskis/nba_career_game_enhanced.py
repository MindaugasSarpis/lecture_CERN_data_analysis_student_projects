"""
NBA Career Game - Enhanced with Game-by-Game Simulation
Now includes 82-game seasons with events and gradual stat development
"""

import pygame
import random
import time
import json
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
import sys
import os
import math

# Add the current directory to path so we can import the analyzer
sys.path.append('.')
from nba_career_analyzer import NBACareerAnalyzer

# Initialize Pygame
pygame.init()
pygame.font.init()

# Screen dimensions
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# Colors
COLORS = {
    'bg_dark': (20, 25, 40),
    'bg_light': (30, 40, 60),
    'text_primary': (240, 240, 240),
    'text_secondary': (180, 180, 180),
    'accent': (255, 165, 0),
    'success': (0, 255, 100),
    'warning': (255, 200, 0),
    'danger': (255, 80, 80),
    'stat_improve': (0, 255, 150),
    'stat_decline': (255, 100, 100),
    'money': (0, 255, 255),
    'blue': (59, 130, 246),
    'green': (16, 185, 129),
    'purple': (139, 92, 246),
    'yellow': (245, 158, 11),
    'red': (239, 68, 68)
}

# Fonts
FONT_SMALL = pygame.font.Font(None, 20)
FONT_MEDIUM = pygame.font.Font(None, 28)
FONT_LARGE = pygame.font.Font(None, 36)
FONT_TITLE = pygame.font.Font(None, 48)
FONT_STATS = pygame.font.Font(None, 32)

class GameState(Enum):
    MAIN_MENU = "main_menu"
    PLAYER_CREATION = "player_creation"
    CAREER_SIMULATION = "career_simulation"
    GAME_SIM = "game_sim"
    EVENT = "event"
    RESULT = "result"
    CAREER_SUMMARY = "career_summary"
    FINAL_SUMMARY = "final_summary"

class PlayerPosition(Enum):
    POINT_GUARD = "Point Guard"
    SHOOTING_GUARD = "Shooting Guard"
    SMALL_FORWARD = "Small Forward"
    POWER_FORWARD = "Power Forward"
    CENTER = "Center"

@dataclass
class PlayerAttributes:
    scoring: float = 0.3
    playmaking: float = 0.3
    defense: float = 0.3
    athleticism: float = 0.3
    clutch: float = 0.3
    discipline: float = 0.3
    
    def get_total(self) -> float:
        return sum([self.scoring, self.playmaking, self.defense, 
                   self.athleticism, self.clutch, self.discipline]) / 6

@dataclass
class PlayerStats:
    points: int = 0
    rebounds: int = 0
    assists: int = 0
    games_played: int = 0
    
    def get_ppg(self) -> float:
        return self.points / max(self.games_played, 1)
    
    def get_rpg(self) -> float:
        return self.rebounds / max(self.games_played, 1)
    
    def get_apg(self) -> float:
        return self.assists / max(self.games_played, 1)

@dataclass
class SeasonStats:
    games_played: int = 0
    total_points: int = 0
    total_rebounds: int = 0
    total_assists: int = 0
    current_ppg: float = 0.0
    current_rpg: float = 0.0
    current_apg: float = 0.0

@dataclass
class Player:
    position: PlayerPosition
    attributes: PlayerAttributes
    stats: PlayerStats = field(default_factory=PlayerStats)
    season_stats: SeasonStats = field(default_factory=SeasonStats)
    level: int = 1
    reputation: int = 50
    money: int = 50000
    experience: int = 0
    name: str = "Player"
    
    def get_overall(self) -> int:
        return int(self.attributes.get_total() * 99)

@dataclass
class GameEvent:
    title: str
    description: str
    impact: Dict[str, float]  # stat_name: multiplier
    duration: int  # number of games
    is_positive: bool

class NBACareerGameEnhanced:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("NBA Career Game - Enhanced Edition")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Game state
        self.state = GameState.MAIN_MENU
        self.player = None
        self.current_event = None
        self.event_result = None
        
        # Season simulation
        self.current_season = 1
        self.current_game = 1
        self.total_seasons = 15
        self.total_games = 82
        self.season_history = []
        
        # Career simulation
        self.current_career_year = 0
        self.career_trajectory = None
        
        # Data analyzer - using relative paths for CSV files
        self.analyzer = NBACareerAnalyzer(
            '2021-2022 NBA Player Stats - Regular.csv',
            '2021-2022 NBA Player Stats - Playoffs.csv'
        )
        
        # UI elements
        self.buttons = []
        self.selected_position = None
        self.selected_archetype = None
        
        # Game simulation
        self.is_simulating = False
        self.sim_speed = 0.1  # Faster simulation for game-by-game
        self.last_game_time = 0
        
        # Colors for different tiers
        self.tier_colors = {
            'Elite Player': COLORS['success'],
            'Starter': COLORS['blue'],
            'Role Player': COLORS['yellow'],
            'Bench Player': COLORS['text_secondary']
        }
        
        # Event system
        self.active_events = []
        self.event_pool = self._create_event_pool()
        
        # Season performance modifiers
        self.current_modifiers = {'ppg': 1.0, 'rpg': 1.0, 'apg': 1.0}

    def _create_event_pool(self) -> List[GameEvent]:
        """Create a pool of possible events that can occur during the season"""
        events = [
            # Positive Events
            GameEvent("Hot Streak", "You're on fire! Everything is clicking.", 
                     {'ppg': 1.3, 'rpg': 1.2, 'apg': 1.2}, 5, True),
            GameEvent("Training Breakthrough", "New training method is paying off!", 
                     {'ppg': 1.25, 'rpg': 1.1, 'apg': 1.1}, 8, True),
            GameEvent("Team Chemistry", "Great chemistry with teammates!", 
                     {'ppg': 1.2, 'rpg': 1.3, 'apg': 1.4}, 6, True),
            GameEvent("Coaching Confidence", "Coach has full confidence in you!", 
                     {'ppg': 1.4, 'rpg': 1.0, 'apg': 1.0}, 4, True),
            GameEvent("Playoff Push", "Stepping up for the playoff push!", 
                     {'ppg': 1.35, 'rpg': 1.25, 'apg': 1.15}, 7, True),
            GameEvent("Contract Year", "Playing for that new contract!", 
                     {'ppg': 1.3, 'rpg': 1.2, 'apg': 1.1}, 10, True),
            GameEvent("All-Star Form", "Playing at an All-Star level!", 
                     {'ppg': 1.4, 'rpg': 1.3, 'apg': 1.3}, 6, True),
            GameEvent("Leadership Role", "Embracing leadership responsibilities!", 
                     {'ppg': 1.15, 'rpg': 1.35, 'apg': 1.4}, 8, True),
            
            # Negative Events
            GameEvent("Shooting Slump", "Can't buy a basket lately...", 
                     {'ppg': 0.7, 'rpg': 0.9, 'apg': 0.9}, 5, False),
            GameEvent("Minor Injury", "Playing through a nagging injury", 
                     {'ppg': 0.8, 'rpg': 0.7, 'apg': 0.8}, 3, False),
            GameEvent("Fatigue", "Worn down by the long season", 
                     {'ppg': 0.75, 'rpg': 0.8, 'apg': 0.85}, 6, False),
            GameEvent("Team Conflict", "Issues with teammates/coach", 
                     {'ppg': 0.7, 'rpg': 0.7, 'apg': 0.6}, 4, False),
            GameEvent("Personal Issues", "Off-court distractions affecting play", 
                     {'ppg': 0.65, 'rpg': 0.8, 'apg': 0.7}, 5, False),
            GameEvent("Reduced Minutes", "Coach cutting your playing time", 
                     {'ppg': 0.6, 'rpg': 0.6, 'apg': 0.6}, 8, False),
            GameEvent("Bad Form", "Just not playing well right now", 
                     {'ppg': 0.7, 'rpg': 0.75, 'apg': 0.7}, 7, False),
            GameEvent("Trade Rumors", "Uncertainty affecting performance", 
                     {'ppg': 0.75, 'rpg': 0.8, 'apg': 0.75}, 6, False),
            
            # Neutral/Mixed Events
            GameEvent("Role Change", "Adjusting to new team role", 
                     {'ppg': 0.9, 'rpg': 1.1, 'apg': 1.2}, 10, True),
            GameEvent("System Change", "New offensive system takes adjustment", 
                     {'ppg': 0.85, 'rpg': 0.9, 'apg': 1.1}, 8, True),
            GameEvent("Rookie Wall", "Hitting the rookie wall", 
                     {'ppg': 0.7, 'rpg': 0.8, 'apg': 0.7}, 10, False),
            GameEvent("Veteran Savvy", "Using experience to impact games", 
                     {'ppg': 1.0, 'rpg': 1.1, 'apg': 1.3}, 12, True),
        ]
        return events

    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()

    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.state == GameState.CAREER_SIMULATION:
                        self.toggle_simulation()
                    elif self.state == GameState.MAIN_MENU:
                        self.state = GameState.PLAYER_CREATION
                elif event.key == pygame.K_ESCAPE:
                    if self.state == GameState.CAREER_SIMULATION:
                        self.state = GameState.MAIN_MENU
                        self.is_simulating = False
                    elif self.state in [GameState.PLAYER_CREATION, GameState.CAREER_SUMMARY, GameState.FINAL_SUMMARY]:
                        self.state = GameState.MAIN_MENU
                elif event.key == pygame.K_n:
                    if self.state == GameState.CAREER_SIMULATION:
                        self.simulate_next_game()
                elif event.key == pygame.K_RIGHT:
                    if self.state == GameState.CAREER_SIMULATION:
                        self.sim_speed = max(0.05, self.sim_speed - 0.05)
                elif event.key == pygame.K_LEFT:
                    if self.state == GameState.CAREER_SIMULATION:
                        self.sim_speed = min(2.0, self.sim_speed + 0.05)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.handle_mouse_click(event.pos)

    def handle_mouse_click(self, pos):
        """Handle mouse clicks"""
        # Check position buttons
        for i, pos_enum in enumerate(PlayerPosition):
            button_rect = pygame.Rect(220, 140 + i * 35, 200, 30)
            if button_rect.collidepoint(pos):
                self.selected_position = pos_enum
                return
        
        # Check archetype buttons
        archetypes = ['Scorer', 'Playmaker', 'Defender', 'All-Around', 'Specialist', 'Prospect']
        for i, arch in enumerate(archetypes):
            button_rect = pygame.Rect(570, 140 + i * 35, 200, 30)
            if button_rect.collidepoint(pos):
                self.selected_archetype = arch
                return
        
        # Check regular buttons
        for button in self.buttons:
            if button.is_clicked(pos):
                button.callback()
                break

    def update(self):
        """Update game logic"""
        self.buttons = []
        
        # Auto simulation logic
        if self.state == GameState.CAREER_SIMULATION and self.is_simulating:
            current_time = time.time()
            if current_time - self.last_game_time >= self.sim_speed:
                self.simulate_next_game()
                self.last_game_time = current_time

    def simulate_next_game(self):
        """Simulate the next game in the season"""
        if self.current_game > self.total_games:
            # Season is over, advance to next year
            self.end_season()
            return
        
        # Get base stats from current career year
        if not self.career_trajectory or self.current_career_year >= len(self.career_trajectory):
            return
        
        year_data = self.career_trajectory[self.current_career_year]
        
        # Calculate game stats with current modifiers
        base_ppg = year_data['PPG']
        base_rpg = year_data['RPG']
        base_apg = year_data['APG']
        
        # Apply event modifiers
        game_ppg = base_ppg * self.current_modifiers['ppg'] * random.uniform(0.5, 1.5)
        game_rpg = base_rpg * self.current_modifiers['rpg'] * random.uniform(0.3, 2.0)
        game_apg = base_apg * self.current_modifiers['apg'] * random.uniform(0.3, 2.0)
        
        # Add realistic game-to-game variation
        game_ppg = max(0, game_ppg)
        game_rpg = max(0, game_rpg)
        game_apg = max(0, game_apg)
        
        # Update season stats
        self.player.season_stats.games_played += 1
        self.player.season_stats.total_points += int(game_ppg)
        self.player.season_stats.total_rebounds += int(game_rpg)
        self.player.season_stats.total_assists += int(game_apg)
        
        # Calculate current averages
        games = self.player.season_stats.games_played
        self.player.season_stats.current_ppg = self.player.season_stats.total_points / games
        self.player.season_stats.current_rpg = self.player.season_stats.total_rebounds / games
        self.player.season_stats.current_apg = self.player.season_stats.total_assists / games
        
        # Trigger events occasionally (about every 10 games)
        if random.random() < 0.1 and not self.active_events:
            self.trigger_random_event()
        
        # Update active events
        self.update_active_events()
        
        # Advance game counter
        self.current_game += 1

    def trigger_random_event(self):
        """Trigger a random event that affects performance"""
        event = random.choice(self.event_pool)
        self.active_events.append(event)
        self.current_event = event
        
        # Update modifiers
        for stat, multiplier in event.impact.items():
            self.current_modifiers[stat] = multiplier
        
        print(f"🎯 EVENT: {event.title} - {event.description}")

    def update_active_events(self):
        """Update and remove expired events"""
        expired_events = []
        
        for i, event in enumerate(self.active_events):
            event.duration -= 1
            if event.duration <= 0:
                expired_events.append(i)
        
        # Remove expired events (in reverse order)
        for i in reversed(expired_events):
            expired_event = self.active_events.pop(i)
            print(f"✅ Event ended: {expired_event.title}")
        
        # Reset modifiers if no active events
        if not self.active_events:
            self.current_modifiers = {'ppg': 1.0, 'rpg': 1.0, 'apg': 1.0}
        else:
            # Recalculate modifiers from remaining events
            self.current_modifiers = {'ppg': 1.0, 'rpg': 1.0, 'apg': 1.0}
            for event in self.active_events:
                for stat, multiplier in event.impact.items():
                    self.current_modifiers[stat] *= multiplier

    def end_season(self):
        """End the current season and prepare for the next"""
        # Record season stats
        season_summary = {
            'season': self.current_season,
            'games_played': self.player.season_stats.games_played,
            'ppg': self.player.season_stats.current_ppg,
            'rpg': self.player.season_stats.current_rpg,
            'apg': self.player.season_stats.current_apg,
            'total_points': self.player.season_stats.total_points,
            'total_rebounds': self.player.season_stats.total_rebounds,
            'total_assists': self.player.season_stats.total_assists
        }
        
        self.season_history.append(season_summary)
        
        # Advance to next season or end career
        if self.current_season < self.total_seasons and self.current_career_year < len(self.career_trajectory) - 1:
            self.current_season += 1
            self.current_game = 1
            self.current_career_year += 1
            
            # Reset season stats
            self.player.season_stats = SeasonStats()
            self.active_events = []
            self.current_modifiers = {'ppg': 1.0, 'rpg': 1.0, 'apg': 1.0}
            
            print(f"🎉 Season {self.current_season - 1} completed! Starting season {self.current_season}")
        else:
            # Career is over
            self.show_career_summary()

    def draw(self):
        """Draw everything"""
        self.screen.fill(COLORS['bg_dark'])
        
        if self.state == GameState.MAIN_MENU:
            self.draw_main_menu()
        elif self.state == GameState.PLAYER_CREATION:
            self.draw_player_creation()
        elif self.state == GameState.CAREER_SIMULATION:
            self.draw_career_simulation()
        elif self.state == GameState.EVENT:
            self.draw_event()
        elif self.state == GameState.RESULT:
            self.draw_result()
        elif self.state == GameState.CAREER_SUMMARY:
            self.draw_career_summary()
        elif self.state == GameState.FINAL_SUMMARY:
            self.draw_final_summary()
        
        pygame.display.flip()

    def draw_main_menu(self):
        """Draw main menu with enhanced features"""
        # Title
        title = FONT_TITLE.render("NBA CAREER GAME", True, COLORS['accent'])
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 120))
        self.screen.blit(title, title_rect)
        
        subtitle = FONT_LARGE.render("Enhanced Game-by-Game Edition", True, COLORS['text_secondary'])
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 170))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Features with game-by-game emphasis
        features = [
            " 82-game seasons with gradual stat development",
            " Random events affecting performance",
            " Real NBA statistics from 628 players",
            " Position-specific performance benchmarks",
            " Realistic career development curves",
            " Data-driven player archetypes",
            " Interactive game-by-game simulation",
            "",
            "Based on 2021-2022 NBA Season Data"
        ]
        
        y_offset = 250
        for feature in features:
            if feature:
                desc = FONT_MEDIUM.render(feature, True, COLORS['text_secondary'])
                desc_rect = desc.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
                self.screen.blit(desc, desc_rect)
            y_offset += 35
        
        # Start button
        self.draw_button("START CAREER", SCREEN_WIDTH // 2, 550, 
                        lambda: self.start_player_creation())
        
        # Instructions
        inst_y = 620
        inst1 = FONT_MEDIUM.render("Experience an 82-game NBA season with realistic events!", True, COLORS['text_primary'])
        inst1_rect = inst1.get_rect(center=(SCREEN_WIDTH // 2, inst_y))
        self.screen.blit(inst1, inst1_rect)

    def draw_player_creation(self):
        """Draw player creation with data-driven elements"""
        # Title
        title = FONT_LARGE.render("Create Your Player", True, COLORS['text_primary'])
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 40))
        self.screen.blit(title, title_rect)
        
        # Position selection
        pos_text = FONT_MEDIUM.render("Choose Position:", True, COLORS['text_secondary'])
        self.screen.blit(pos_text, (200, 100))
        
        positions = list(PlayerPosition)
        for i, pos in enumerate(positions):
            y_pos = 140 + i * 35
            color = COLORS['accent'] if self.selected_position == pos else COLORS['text_primary']
            pos_name = FONT_MEDIUM.render(pos.value, True, color)
            self.screen.blit(pos_name, (220, y_pos))
            
            # Draw selection highlight
            if self.selected_position == pos:
                pygame.draw.rect(self.screen, COLORS['accent'], (215, y_pos - 5, 200, 35), 2)
        
        # Archetype selection
        archetype_text = FONT_MEDIUM.render("Choose Archetype:", True, COLORS['text_secondary'])
        self.screen.blit(archetype_text, (550, 100))
        
        archetypes = ['Scorer', 'Playmaker', 'Defender', 'All-Around', 'Specialist', 'Prospect']
        for i, arch in enumerate(archetypes):
            y_pos = 140 + i * 35
            color = COLORS['accent'] if self.selected_archetype == arch else COLORS['text_primary']
            arch_name = FONT_MEDIUM.render(arch, True, color)
            self.screen.blit(arch_name, (570, y_pos))
            
            # Draw selection highlight
            if self.selected_archetype == arch:
                pygame.draw.rect(self.screen, COLORS['accent'], (565, y_pos - 5, 200, 35), 2)
        
        # Show position benchmarks if position selected
        if self.selected_position:
            bench_y = 400
            bench_title = FONT_MEDIUM.render(f"{self.selected_position.value} Benchmarks:", True, COLORS['accent'])
            self.screen.blit(bench_title, (200, bench_y))
            
            pos_benchmarks = self.analyzer.position_benchmarks.get(self.selected_position.value, {})
            if pos_benchmarks:
                bench_data = [
                    f"Elite PPG: {pos_benchmarks['PPG']['elite']:.1f}",
                    f"Starter PPG: {pos_benchmarks['PPG']['starter']:.1f}",
                    f"Elite RPG: {pos_benchmarks['RPG']['elite']:.1f}",
                    f"Elite APG: {pos_benchmarks['APG']['elite']:.1f}"
                ]
                
                for i, data in enumerate(bench_data):
                    data_text = FONT_SMALL.render(data, True, COLORS['text_secondary'])
                    self.screen.blit(data_text, (220, bench_y + 30 + i * 20))
        
        # Start button - only enabled when both position and archetype are selected
        if self.selected_position and self.selected_archetype:
            self.draw_button("START CAREER", SCREEN_WIDTH // 2, 600, 
                           lambda: self.create_player_and_start())
        else:
            # Draw disabled button
            button_text = "Select Position and Archetype First"
            text_surface = FONT_MEDIUM.render(button_text, True, COLORS['text_secondary'])
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, 600))
            self.screen.blit(text_surface, text_rect)

    def draw_career_simulation(self):
        """Draw career simulation with game-by-game stats"""
        if not self.player or not self.career_trajectory:
            return
        
        # Player info header
        info_y = 20
        pos_text = FONT_LARGE.render(self.player.position.value, True, COLORS['accent'])
        self.screen.blit(pos_text, (50, info_y))
        
        overall_text = FONT_LARGE.render(f"Overall: {self.player.get_overall()}", 
                                        True, COLORS['success'])
        self.screen.blit(overall_text, (50, info_y + 40))
        
        # Season info
        season_text = FONT_LARGE.render(f"Season {self.current_season} - Game {self.current_game}/82", True, COLORS['accent'])
        self.screen.blit(season_text, (SCREEN_WIDTH // 2 - 200, 10))
        
        age_text = FONT_MEDIUM.render(f"Age: {22 + self.current_career_year}", True, COLORS['text_primary'])
        self.screen.blit(age_text, (SCREEN_WIDTH // 2 - 200, 40))
        
        # Current season stats (big display)
        stats_y = 130
        stats_title = FONT_LARGE.render("Current Season Stats", True, COLORS['text_primary'])
        self.screen.blit(stats_title, (SCREEN_WIDTH // 2 - 150, stats_y))
        
        # PPG
        ppg_y = 180
        ppg_text = FONT_STATS.render(f"PPG: {self.player.season_stats.current_ppg:.1f}", True, COLORS['success'])
        self.screen.blit(ppg_text, (200, ppg_y))
        
        # RPG
        rpg_text = FONT_STATS.render(f"RPG: {self.player.season_stats.current_rpg:.1f}", True, COLORS['success'])
        self.screen.blit(rpg_text, (400, ppg_y))
        
        # APG
        apg_text = FONT_STATS.render(f"APG: {self.player.season_stats.current_apg:.1f}", True, COLORS['success'])
        self.screen.blit(apg_text, (600, ppg_y))
        
        # Games played
        games_text = FONT_STATS.render(f"Games: {self.player.season_stats.games_played}/82", True, COLORS['text_primary'])
        self.screen.blit(games_text, (800, ppg_y))
        
        # Performance tier
        tier_y = 230
        if self.career_trajectory and self.current_career_year < len(self.career_trajectory):
            tier = self.career_trajectory[self.current_career_year]['Performance_Tier']
            tier_color = self.tier_colors.get(tier, COLORS['text_secondary'])
            tier_text = FONT_LARGE.render(f"Tier: {tier}", True, tier_color)
            self.screen.blit(tier_text, (SCREEN_WIDTH // 2 - 100, tier_y))
        
        # Career progress
        progress_y = 280
        progress_text = FONT_MEDIUM.render(f"Career Progress: Season {self.current_season}/15", True, COLORS['text_secondary'])
        self.screen.blit(progress_text, (SCREEN_WIDTH // 2 - 150, progress_y))
        
        # Career totals
        totals_y = 320
        total_points = sum(year['PPG'] * 82 for year in self.career_trajectory[:self.current_career_year])
        if self.player.season_stats.games_played > 0:
            total_points += self.player.season_stats.total_points
        totals_text = FONT_MEDIUM.render(f"Career Points: {total_points:.0f}", True, COLORS['money'])
        self.screen.blit(totals_text, (SCREEN_WIDTH // 2 - 100, totals_y))
        
        # Active events
        if self.active_events:
            event_y = 380
            event_title = FONT_MEDIUM.render("Active Events:", True, COLORS['warning'])
            self.screen.blit(event_title, (50, event_y))
            
            for i, event in enumerate(self.active_events[:3]):  # Show max 3 events
                event_text = FONT_SMALL.render(f"• {event.title} ({event.duration} games)", True, COLORS['text_secondary'])
                self.screen.blit(event_text, (50, event_y + 25 + i * 20))
        
        # Simulation controls
        sim_y = 450
        if self.is_simulating:
            status_text = f"SIMULATING... Game {self.current_game}/82 (Press SPACE to pause)"
            status_color = COLORS['success']
        else:
            status_text = "PAUSED (Press SPACE to resume or N for next game)"
            status_color = COLORS['warning']
        
        status = FONT_LARGE.render(status_text, True, status_color)
        status_rect = status.get_rect(center=(SCREEN_WIDTH // 2, sim_y))
        self.screen.blit(status, status_rect)
        
        # Speed controls
        speed_y = 520
        speed_text = FONT_MEDIUM.render(f"Speed: {self.sim_speed:.2f}s/game (Use ← → to adjust)", True, COLORS['text_secondary'])
        speed_rect = speed_text.get_rect(center=(SCREEN_WIDTH // 2, speed_y))
        self.screen.blit(speed_text, speed_rect)
        
        # Controls
        controls_y = 560
        controls = [
            "SPACE - Pause/Resume Simulation",
            "N - Next Game",
            "← → - Adjust Speed",
            "ESC - Back to Menu"
        ]
        
        for i, control in enumerate(controls):
            control_text = FONT_MEDIUM.render(control, True, COLORS['text_secondary'])
            control_rect = control_text.get_rect(center=(SCREEN_WIDTH // 2, controls_y + i * 25))
            self.screen.blit(control_text, control_rect)
        
        # Next game button
        self.draw_button("NEXT GAME", SCREEN_WIDTH // 2, 700, 
                        lambda: self.simulate_next_game())

    def create_player_and_start(self):
        """Create player and generate career trajectory from data"""
        if not self.selected_position or not self.selected_archetype:
            return
            
        # Generate career trajectory using real data
        trajectory = self.analyzer.simulate_career_trajectory(
            self.selected_position.value, 
            self.selected_archetype, 
            starting_age=22, 
            years=self.total_seasons
        )
        
        self.career_trajectory = trajectory.to_dict('records')
        self.current_career_year = 0
        
        # Create player object
        self.player = Player(
            position=self.selected_position,
            attributes=PlayerAttributes(),
            name=f"{self.selected_archetype} {self.selected_position.value}"
        )
        
        # Set initial stats from first year
        if self.career_trajectory:
            first_year = self.career_trajectory[0]
            # Don't set initial stats, let them develop naturally
        
        self.state = GameState.CAREER_SIMULATION

    def show_career_summary(self):
        """Show final career summary"""
        import pandas as pd
        summary = self.analyzer.get_career_summary(pd.DataFrame(self.career_trajectory))
        self.career_summary = summary
        self.state = GameState.FINAL_SUMMARY

    def draw_final_summary(self):
        """Draw final career summary"""
        if not self.career_summary:
            return
            
        # Title
        title = FONT_TITLE.render("Career Complete!", True, COLORS['accent'])
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)
        
        # Career summary stats
        summary_data = [
            f"Years Played: {self.career_summary['Years_Played']}",
            f"Career PPG: {self.career_summary['Career_PPG']:.1f}",
            f"Career RPG: {self.career_summary['Career_RPG']:.1f}",
            f"Career APG: {self.career_summary['Career_APG']:.1f}",
            f"Peak PPG: {self.career_summary['Peak_PPG']:.1f} (Year {self.career_summary['Peak_Year']})",
            f"Total Points: {self.career_summary['Total_Points']:.0f}",
            f"Total Rebounds: {self.career_summary['Total_Rebounds']:.0f}",
            f"Total Assists: {self.career_summary['Total_Assists']:.0f}",
            f"Total Games: {self.career_summary['Total_Games']}"
        ]
        
        y_pos = 120
        for i, stat in enumerate(summary_data):
            stat_text = FONT_MEDIUM.render(stat, True, COLORS['text_primary'])
            stat_rect = stat_text.get_rect(center=(SCREEN_WIDTH // 2, y_pos + i * 35))
            self.screen.blit(stat_text, stat_rect)
        
        # Performance evaluation
        eval_y = 450
        if self.career_summary['Career_PPG'] >= 25:
            evaluation = "HALL OF FAME CAREER!"
            eval_color = COLORS['success']
        elif self.career_summary['Career_PPG'] >= 20:
            evaluation = "ALL-STAR CAREER!"
            eval_color = COLORS['blue']
        elif self.career_summary['Career_PPG'] >= 15:
            evaluation = "SOLID STARTER CAREER!"
            eval_color = COLORS['yellow']
        else:
            evaluation = "ROLE PLAYER CAREER!"
            eval_color = COLORS['text_secondary']
        
        eval_text = FONT_LARGE.render(evaluation, True, eval_color)
        eval_rect = eval_text.get_rect(center=(SCREEN_WIDTH // 2, eval_y))
        self.screen.blit(eval_text, eval_rect)
        
        # Buttons
        self.draw_button("NEW CAREER", SCREEN_WIDTH // 2 - 200, 550, 
                        lambda: self.reset_game())
        self.draw_button("EXIT GAME", SCREEN_WIDTH // 2 + 200, 550, 
                        lambda: self.exit_game())

    def reset_game(self):
        """Reset the game to start over"""
        self.__init__()

    def exit_game(self):
        """Exit the game"""
        self.running = False

    def toggle_simulation(self):
        """Toggle simulation state"""
        self.is_simulating = not self.is_simulating

    def start_player_creation(self):
        """Start the player creation process"""
        self.state = GameState.PLAYER_CREATION

    def draw_event(self):
        """Draw event popup"""
        if not self.current_event:
            return
        
        # Draw event overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Event box
        box_width = 600
        box_height = 300
        box_x = (SCREEN_WIDTH - box_width) // 2
        box_y = (SCREEN_HEIGHT - box_height) // 2
        
        pygame.draw.rect(self.screen, COLORS['bg_light'], (box_x, box_y, box_width, box_height), border_radius=15)
        pygame.draw.rect(self.screen, COLORS['accent'], (box_x, box_y, box_width, box_height), 3, border_radius=15)
        
        # Event title
        title_color = COLORS['success'] if self.current_event.is_positive else COLORS['danger']
        title = FONT_LARGE.render(self.current_event.title, True, title_color)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, box_y + 50))
        self.screen.blit(title, title_rect)
        
        # Event description
        desc = FONT_MEDIUM.render(self.current_event.description, True, COLORS['text_primary'])
        desc_rect = desc.get_rect(center=(SCREEN_WIDTH // 2, box_y + 120))
        self.screen.blit(desc, desc_rect)
        
        # Impact details
        impact_text = "Stat Impact:"
        impact_title = FONT_MEDIUM.render(impact_text, True, COLORS['text_secondary'])
        impact_rect = impact_title.get_rect(center=(SCREEN_WIDTH // 2, box_y + 170))
        self.screen.blit(impact_title, impact_rect)
        
        # Show impacts
        y_offset = 200
        for stat, multiplier in self.current_event.impact.items():
            impact_desc = f"{stat.upper()}: {multiplier:.1f}x"
            impact_color = COLORS['success'] if multiplier > 1.0 else COLORS['danger']
            impact_text = FONT_SMALL.render(impact_desc, True, impact_color)
            impact_rect = impact_text.get_rect(center=(SCREEN_WIDTH // 2, box_y + y_offset))
            self.screen.blit(impact_text, impact_rect)
            y_offset += 25
        
        # Duration
        duration_text = f"Duration: {self.current_event.duration} games"
        duration = FONT_SMALL.render(duration_text, True, COLORS['text_secondary'])
        duration_rect = duration.get_rect(center=(SCREEN_WIDTH // 2, box_y + 260))
        self.screen.blit(duration, duration_rect)

    def draw_result(self):
        """Draw event result"""
        pass  # Results are shown in the main simulation screen

    def draw_career_summary(self):
        """Draw season summary"""
        pass  # Career summary is handled by final summary

    def draw_button(self, text, x, y, callback, width=200, height=50):
        """Draw a button"""
        button = Button(text, x, y, width, height, callback)
        button.draw(self.screen)
        self.buttons.append(button)

class Button:
    def __init__(self, text, x, y, width, height, callback):
        self.text = text
        self.x = x - width // 2
        self.y = y - height // 2
        self.width = width
        self.height = height
        self.callback = callback
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.hovered = False

    def draw(self, screen):
        # Check hover
        mouse_pos = pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(mouse_pos)
        
        # Draw button
        color = COLORS['accent'] if self.hovered else COLORS['blue']
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, COLORS['text_primary'], self.rect, 2, border_radius=10)
        
        # Draw text
        text_surface = FONT_MEDIUM.render(self.text, True, COLORS['text_primary'])
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

def main():
    """Main function to run the game"""
    print("Starting NBA Career Game - Enhanced Game-by-Game Edition")
    print("Loading real NBA statistics...")
    
    try:
        game = NBACareerGameEnhanced()
        print("Game initialized successfully!")
        print()
        print("🎮 Enhanced Features:")
        print("• 82-game seasons with game-by-game simulation")
        print("• Random events that affect performance")
        print("• Gradual stat development within seasons")
        print("• Speed controls (← → to adjust simulation speed)")
        print()
        print("Controls:")
        print("• Mouse - Click buttons and make selections")
        print("• SPACE - Pause/Resume simulation")
        print("• N - Advance to next game")
        print("• ESC - Back to menu")
        print()
        
        game.run()
        print("Game ended. Thank you for playing!")
        
    except Exception as e:
        print(f"❌ Error starting game: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()