from melo.poc import update_matches_outcome
import pandas as pd




# TODO: Use pytest fixtures for more cases.
def test_update_matches_outcome():
    df = pd.DataFrame({"player": ["yass", "theo", "gaetan", "thomas", "polo"], "games": [0, 0, 0, 0, 0],
                       "win": [0, 0, 0, 0, 0],
                       "loss": [0, 0, 0, 0, 0],
                       "draw": [0, 0, 0, 0, 0]})
    state = "WIN"
    team_1_players = ["yass", "theo", "polo"]
    team_2_players = ["gaetan", "thomas"]
    outcome_df = update_matches_outcome(df, state, team_1_players, team_2_players)
    # More games have been played after this game
    assert outcome_df["games"].sum() > df["games"].sum()
