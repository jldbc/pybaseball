from pybaseball.batting_leaders import batting_stats

data = batting_stats(2023)

# Use `legacy` flag to get legacy leaderboard page data
legacy_data = batting_stats(2023, legacy=True)
