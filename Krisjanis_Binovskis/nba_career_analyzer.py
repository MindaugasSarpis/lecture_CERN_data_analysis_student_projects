"""
NBA Career Analyzer - Data-Driven Career Simulation
Uses real NBA statistics to model realistic career trajectories
"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Tuple, Optional
import warnings
import os
warnings.filterwarnings('ignore')

class NBACareerAnalyzer:
    """Main analyzer class for NBA career simulation using real data"""
    
    def __init__(self, regular_stats_path: str, playoff_stats_path: str):
        """Initialize with real NBA data"""
        try:
            # Try different encodings for CSV files
            self.regular_stats = pd.read_csv(regular_stats_path, encoding='latin-1', sep=';')
            self.playoff_stats = pd.read_csv(playoff_stats_path, encoding='latin-1', sep=';')
            
            # Standardize column names
            self.regular_stats = self._standardize_columns(self.regular_stats)
            self.playoff_stats = self._standardize_columns(self.playoff_stats)
            
            print(f"✅ Loaded {len(self.regular_stats)} regular season players")
            print(f"✅ Loaded {len(self.playoff_stats)} playoff players")
            print(f"📊 Columns found: {list(self.regular_stats.columns)}")
        except Exception as e:
            print(f"⚠️ Error reading CSV files: {e}")
            print("Creating mock data instead...")
            self.regular_stats = self._create_mock_data()
            self.playoff_stats = self.regular_stats.sample(n=min(100, len(self.regular_stats)))
        
        # Clean and prepare data
        self._clean_data()
        
    
        
        # Calculate position benchmarks
        self.position_benchmarks = self._calculate_position_benchmarks()
        
        # Define archetype characteristics
        self.archetype_profiles = {
            'Scorer': {'scoring': 1.9, 'playmaking': 0.6, 'defense': 0.6, 'athleticism': 1.2, 'clutch': 0.9},
            'Playmaker': {'scoring': 1.0, 'playmaking': 1.3, 'defense': 0.7, 'athleticism': 0.6, 'clutch': 0.8},
            'Defender': {'scoring': 0.7, 'playmaking': 0.6, 'defense': 1.3, 'athleticism': 1.0, 'clutch': 0.5},
            'All-Around': {'scoring': 1.2, 'playmaking': 1.0, 'defense': 0.7, 'athleticism': 0.9, 'clutch': 0.8},
            'Specialist': {'scoring': 1.5, 'playmaking': 0.5, 'defense': 0.9, 'athleticism': 0.5, 'clutch': 1.2},
            'Prospect': {'scoring': 0.9, 'playmaking': 0.8, 'defense': 0.8, 'athleticism': 1.3, 'clutch': 0.6}
        }
        
        print("🎯 NBA Career Analyzer initialized successfully!")
    
    def _read_csv_with_encoding(self, filepath: str) -> pd.DataFrame:
        """Try reading CSV with different encodings"""
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                return pd.read_csv(filepath, encoding=encoding)
            except UnicodeDecodeError:
                print(f"⚠️ Failed to read with {encoding} encoding, trying next...")
                continue
        
        # If all encodings fail, raise the last error
        raise UnicodeDecodeError(f"Could not read {filepath} with any encoding")
    
    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names to match expected format"""
        # Common column name mappings for NBA stats
        column_mapping = {
            # Player info
            'Player': ['Player', 'Name', 'PLAYER', 'NAME', 'player', 'name'],
            'Position': ['Position', 'Pos', 'POSITION', 'position', 'pos'],
            'Age': ['Age', 'AGE', 'age'],
            
            # Stats
            'PPG': ['PPG', 'Points', 'PTS', 'pts', 'points', 'Ppg'],
            'RPG': ['RPG', 'Rebounds', 'REB', 'reb', 'rebounds', 'Rpg'],
            'ORB': ['ORB', 'Offensive Rebounds', 'OREB', 'oreb', 'offensive_rebounds'],
            'DRB': ['DRB', 'Defensive Rebounds', 'DREB', 'dreb', 'defensive_rebounds'],
            'APG': ['APG', 'Assists', 'AST', 'ast', 'assists', 'Apg'],
            'MPG': ['MPG', 'Minutes', 'MIN', 'min', 'minutes', 'Mpg'],
            'G': ['G', 'Games', 'GP', 'gp', 'games', 'games_played'],
            
            # Shooting percentages
            'FG%': ['FG%', 'FG_PCT', 'fg_pct', 'Field_Goal_Pct'],
            '3P%': ['3P%', '3P_PCT', 'three_point_pct', 'Three_Pt_Pct']
        }
        
        # Create a mapping dictionary for existing columns
        rename_dict = {}
        for standard_name, possible_names in column_mapping.items():
            for col in df.columns:
                if col in possible_names:
                    rename_dict[col] = standard_name
                    break
        
        # Rename columns
        df = df.rename(columns=rename_dict)
        
        if 'RPG' not in df.columns and 'ORB' in df.columns and 'DRB' in df.columns:
            df['RPG'] = df['ORB'] + df['DRB']
        # Check if we have the essential columns
        essential_columns = ['Player', 'Position', 'Age', 'PPG', 'RPG', 'APG']
        missing_columns = [col for col in essential_columns if col not in df.columns]
        
        if missing_columns:
            print(f"⚠️ Missing essential columns: {missing_columns}")
            print(f"Available columns: {list(df.columns)}")
            
            # If we're missing critical columns, this might not be an NBA stats file
            # In this case, it's better to use mock data
            raise ValueError(f"Missing essential NBA statistics columns: {missing_columns}")
        
        return df
    
    def _create_mock_data(self) -> pd.DataFrame:
        """Create mock NBA data for testing when real files are not available"""
        np.random.seed(42)
        
        positions = ['Point Guard', 'Shooting Guard', 'Small Forward', 'Power Forward', 'Center']
        players = []
        
        for i in range(300):
            position = np.random.choice(positions)
            age = np.random.randint(19, 40)
            
            # Position-specific base stats
            if position == 'Point Guard':
                ppg = np.random.normal(12, 6)
                rpg = np.random.normal(3, 1.5)
                apg = np.random.normal(5, 3)
            elif position == 'Shooting Guard':
                ppg = np.random.normal(11, 5)
                rpg = np.random.normal(3, 1.5)
                apg = np.random.normal(3, 2)
            elif position == 'Small Forward':
                ppg = np.random.normal(10, 5)
                rpg = np.random.normal(4, 2)
                apg = np.random.normal(2.5, 1.5)
            elif position == 'Power Forward':
                ppg = np.random.normal(9, 4)
                rpg = np.random.normal(5, 2.5)
                apg = np.random.normal(2, 1)
            else:  # Center
                ppg = np.random.normal(8, 4)
                rpg = np.random.normal(6, 3)
                apg = np.random.normal(1.5, 1)
            
            # Ensure non-negative stats
            ppg = max(ppg, 0)
            rpg = max(rpg, 0)
            apg = max(apg, 0)
            
            mpg = np.random.normal(20, 8)
            mpg = max(mpg, 5)
            games = np.random.randint(10, 82)
            
            players.append({
                'Player': f'Player {i+1}',
                'Position': position,
                'Age': age,
                'PPG': ppg,
                'RPG': rpg,
                'APG': apg,
                'MPG': mpg,
                'G': games,
                'FG%': np.random.normal(0.45, 0.1),
                '3P%': np.random.normal(0.35, 0.15)
            })
        
        return pd.DataFrame(players)
    
    def _clean_data(self):
        """Clean and standardize the data"""
        # Remove rows with missing key statistics
        self.regular_stats = self.regular_stats.dropna(subset=['Player', 'Position', 'Age', 'PPG', 'RPG', 'APG'])
        
        # Ensure numeric columns are properly typed
        numeric_cols = ['Age', 'PPG', 'RPG', 'APG', 'MPG', 'G']
        for col in numeric_cols:
            if col in self.regular_stats.columns:
                self.regular_stats[col] = pd.to_numeric(self.regular_stats[col], errors='coerce')
        
        # Fill any remaining NaN values
        self.regular_stats = self.regular_stats.fillna(0)
        
        print(f"📊 Cleaned data: {len(self.regular_stats)} players ready for analysis")
    
    def _calculate_position_benchmarks(self) -> Dict:
        """Calculate performance benchmarks for each position"""
        benchmarks = {}
        
        for position in self.regular_stats['Position'].unique():
            pos_data = self.regular_stats[self.regular_stats['Position'] == position]
            
            if len(pos_data) < 2:  # Skip positions with too few players
                continue
                
            benchmarks[position] = {
                'PPG': {
                    'elite': pos_data['PPG'].quantile(0.9),
                    'starter': pos_data['PPG'].quantile(0.7),
                    'average': pos_data['PPG'].median()
                },
                'RPG': {
                    'elite': pos_data['RPG'].quantile(0.9),
                    'starter': pos_data['RPG'].quantile(0.7),
                    'average': pos_data['RPG'].median()
                },
                'APG': {
                    'elite': pos_data['APG'].quantile(0.9),
                    'starter': pos_data['APG'].quantile(0.7),
                    'average': pos_data['APG'].median()
                }
            }
        
        print(f"🏀 Calculated benchmarks for {len(benchmarks)} positions")
        return benchmarks
    
    def get_performance_tier(self, position: str, ppg: float, rpg: float, apg: float) -> str:
        """Determine performance tier based on position and stats"""
        if position not in self.position_benchmarks:
            return 'Role Player'
        
        bench = self.position_benchmarks[position]
        
        # Score based on how many elite metrics player achieves
        elite_score = 0
        if ppg >= bench['PPG']['elite']:
            elite_score += 1
        if rpg >= bench['RPG']['elite']:
            elite_score += 1
        if apg >= bench['APG']['elite']:
            elite_score += 1
        
        # Score based on starter-level metrics
        starter_score = 0
        if ppg >= bench['PPG']['starter']:
            starter_score += 1
        if rpg >= bench['RPG']['starter']:
            starter_score += 1
        if apg >= bench['APG']['starter']:
            starter_score += 1
        
        # Determine tier
        if elite_score >= 2 or (elite_score == 1 and starter_score == 2):
            return 'Elite Player'
        elif starter_score >= 2:
            return 'Starter'
        elif starter_score >= 1:
            return 'Role Player'
        else:
            return 'Bench Player'
    
    def simulate_career_trajectory(self, position: str, archetype: str, starting_age: int = 22, years: int = 15) -> pd.DataFrame:
        """Simulate a career trajectory based on position, archetype, and age"""
        if position not in self.position_benchmarks:
            print(f"⚠️ Position '{position}' not found in benchmarks, using default")
            position = list(self.position_benchmarks.keys())[0]
        
        # Get archetype profile
        profile = self.archetype_profiles.get(archetype, self.archetype_profiles['All-Around'])
        
        # Base stats for starting player
        pos_bench = self.position_benchmarks[position]
        
        # Calculate starting stats based on archetype
        scoring_mult = profile['scoring']
        playmaking_mult = profile['playmaking']
        defense_mult = profile['defense']
        
        base_ppg = pos_bench['PPG']['average'] * scoring_mult
        base_rpg = pos_bench['RPG']['average'] * (scoring_mult * 0.3 + defense_mult * 0.7)
        base_apg = pos_bench['APG']['average'] * playmaking_mult
        
        # Initialize career trajectory
        trajectory = []
        
        for year in range(years):
            current_age = starting_age + year
            
            # Apply age-based development curve
            if year < 3:  # Development phase (ages 22-24)
                age_factor = 0.7 + (year * 0.15)  # 0.7 to 1.0
            elif year < 6:  # Peak phase (ages 25-27)
                age_factor = 1.0 + ((year - 3) * 0.1)  # 1.0 to 1.3
            elif year < 10:  # Prime phase (ages 28-31)
                age_factor = 1.3 - ((year - 6) * 0.05)  # 1.3 to 1.1
            elif year < 13:  # Decline phase (ages 32-34)
                age_factor = 1.1 - ((year - 10) * 0.08)  # 1.1 to 0.86
            else:  # Late career (ages 35+)
                age_factor = 0.86 - ((year - 13) * 0.06)  # 0.86 to 0.68
            
            # Calculate year stats
            year_ppg = base_ppg * age_factor * np.random.normal(1.0, 0.1)
            year_rpg = base_rpg * age_factor * np.random.normal(1.0, 0.15)
            year_apg = base_apg * age_factor * np.random.normal(1.0, 0.12)
            
            # Ensure realistic bounds
            year_ppg = max(0, min(year_ppg, 35))  # Max 35 PPG
            year_rpg = max(0, min(year_rpg, 15))  # Max 15 RPG
            year_apg = max(0, min(year_apg, 12))  # Max 12 APG
            
            # Games played (affected by age and random factors)
            games_played = int(82 * (1.0 - (year * 0.01) - np.random.exponential(0.05)))
            games_played = max(10, min(games_played, 82))
            
            # Minutes per game
            mpg = np.random.normal(32, 5) * (0.8 + (age_factor * 0.2))
            mpg = max(10, min(mpg, 40))
            
            # Determine performance tier
            tier = self.get_performance_tier(position, year_ppg, year_rpg, year_apg)
            
            trajectory.append({
                'Year': year + 1,
                'Age': current_age,
                'PPG': year_ppg,
                'RPG': year_rpg,
                'APG': year_apg,
                'MPG': mpg,
                'Games_Played': games_played,
                'Performance_Tier': tier
            })
        
        df = pd.DataFrame(trajectory)
        print(f"🎯 Simulated {years}-year career for {archetype} {position}")
        return df
    
    def get_career_summary(self, trajectory_df: pd.DataFrame) -> Dict:
        """Get comprehensive career summary statistics"""
        if trajectory_df.empty:
            return {}
        
        # Calculate career totals
        total_points = (trajectory_df['PPG'] * trajectory_df['Games_Played']).sum()
        total_rebounds = (trajectory_df['RPG'] * trajectory_df['Games_Played']).sum()
        total_assists = (trajectory_df['APG'] * trajectory_df['Games_Played']).sum()
        total_games = trajectory_df['Games_Played'].sum()
        
        # Career averages
        career_ppg = trajectory_df['PPG'].mean()
        career_rpg = trajectory_df['RPG'].mean()
        career_apg = trajectory_df['APG'].mean()
        
        # Peak performance
        peak_ppg = trajectory_df['PPG'].max()
        peak_year = trajectory_df.loc[trajectory_df['PPG'].idxmax(), 'Year']
        
        # Performance distribution
        tier_counts = trajectory_df['Performance_Tier'].value_counts()
        
        summary = {
            'Years_Played': len(trajectory_df),
            'Career_PPG': career_ppg,
            'Career_RPG': career_rpg,
            'Career_APG': career_apg,
            'Peak_PPG': peak_ppg,
            'Peak_Year': peak_year,
            'Total_Points': total_points,
            'Total_Rebounds': total_rebounds,
            'Total_Assists': total_assists,
            'Total_Games': total_games,
            'Performance_Tiers': tier_counts.to_dict(),
            'Prime_Years': len(trajectory_df[trajectory_df['Performance_Tier'].isin(['Elite Player', 'Starter'])])
        }
        
        return summary
    
    def find_similar_players(self, position: str, ppg: float, rpg: float, apg: float, tolerance: float = 0.2) -> pd.DataFrame:
        """Find players with similar statistics"""
        pos_players = self.regular_stats[self.regular_stats['Position'] == position]
        
        # Calculate similarity scores
        pos_players = pos_players.copy()
        pos_players['similarity_score'] = (
            1 - abs(pos_players['PPG'] - ppg) / max(ppg, 1) +
            1 - abs(pos_players['RPG'] - rpg) / max(rpg, 1) +
            1 - abs(pos_players['APG'] - apg) / max(apg, 1)
        ) / 3
        
        # Filter by similarity threshold
        similar = pos_players[pos_players['similarity_score'] >= (1 - tolerance)]
        
        return similar.nlargest(10, 'similarity_score')[['Player', 'Age', 'PPG', 'RPG', 'APG']]
    
    def get_position_analysis(self, position: str) -> Dict:
        """Get detailed analysis for a specific position"""
        pos_data = self.regular_stats[self.regular_stats['Position'] == position]
        
        if pos_data.empty:
            return {}
        
        analysis = {
            'position': position,
            'total_players': len(pos_data),
            'avg_age': pos_data['Age'].mean(),
            'avg_ppg': pos_data['PPG'].mean(),
            'avg_rpg': pos_data['RPG'].mean(),
            'avg_apg': pos_data['APG'].mean(),
            'avg_mpg': pos_data['MPG'].mean() if 'MPG' in pos_data.columns else 0,
            'top_performers': pos_data.nlargest(5, 'PPG')[['Player', 'Age', 'PPG', 'RPG', 'APG']].to_dict('records'),
            'benchmarks': self.position_benchmarks.get(position, {})
        }
        
        return analysis

# Test the analyzer
if __name__ == "__main__":
    # Test with mock data
    analyzer = NBACareerAnalyzer("mock_regular.csv", "mock_playoffs.csv")
    
    # Test career simulation
    trajectory = analyzer.simulate_career_trajectory("Point Guard", "Scorer", 22, 15)
    print("\n📊 Sample Career Trajectory:")
    print(trajectory.head())
    
    summary = analyzer.get_career_summary(trajectory)
    print(f"\n🏆 Career Summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    print("\n✅ NBA Career Analyzer test completed successfully!")