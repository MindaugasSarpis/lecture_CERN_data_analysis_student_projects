#!/usr/bin/env python3
"""
NBA Career Game Enhanced Launcher
Launches the game-by-game simulation with events
"""

import sys
import os

# Add current directory to path
sys.path.append('.')

print("🏀 NBA Career Game - Enhanced Game-by-Game Edition")
print("=" * 55)
print()
print("Loading real NBA statistics from 2021-2022 season...")
print("Analyzing 628 regular season players...")
print()

try:
    # Import and run the enhanced game
    from nba_career_game_enhanced import NBACareerGameEnhanced
    
    print("✅ Game modules loaded successfully!")
    print()
    print("🎮 NEW Enhanced Features:")
    print("• 82-game seasons with game-by-game simulation")
    print("• Random events affecting performance (hot streaks, slumps, etc.)")
    print("• Gradual stat development within seasons")
    print("• Speed controls (← → to adjust simulation speed)")
    print("• Real-time event system with visual notifications")
    print()
    print("🎯 Event Examples:")
    print("• Positive: Hot Streak, Training Breakthrough, Team Chemistry")
    print("• Negative: Shooting Slump, Injuries, Fatigue, Trade Rumors")
    print("• Neutral: Role Changes, System Changes")
    print()
    print("🕹️  Controls:")
    print("• Mouse - Click buttons and make selections")
    print("• SPACE - Pause/Resume simulation")
    print("• N - Advance to next game")
    print("• ← → - Adjust simulation speed")
    print("• ESC - Back to main menu")
    print()
    print("📊 How It Works:")
    print("• Each season has 82 games with realistic stat progression")
    print("• Events can last multiple games and affect different stats")
    print("• Performance modifiers stack when multiple events are active")
    print("• Season averages update after each game")
    print()
    
    # Start the enhanced game
    game = NBACareerGameEnhanced()
    print("🚀 Starting enhanced game...")
    game.run()
    
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    print()
    print("Please ensure all dependencies are installed:")
    print("pip install pygame pandas numpy scikit-learn")
    
except Exception as e:
    print(f"❌ Error starting game: {e}")
    import traceback
    traceback.print_exc()