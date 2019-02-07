# -*- coding: utf-8 -*-

import unittest

import pandas as pd

from melo.poc import update_matches_outcome

# TODO: Use pytest fixtures for more cases.


class MELOBaseTestCase(unittest.TestCase):

    def test_update_matches_outcome(self):
        df = pd.DataFrame({"player": ["yass", "theo", "gaetan", "thomas", "polo"], "games": [0, 0, 0, 0, 0],
                           "win": [0, 0, 0, 0, 0],
                           "loss": [0, 0, 0, 0, 0],
                           "draw": [0, 0, 0, 0, 0]})
        state = "WIN"
        team_1_players = ["yass", "theo", "polo"]
        team_2_players = ["gaetan", "thomas"]
        number_of_players = len(team_1_players + team_2_players)
        outcome_df = update_matches_outcome(df, state, team_1_players, team_2_players)
        # More games have been played after this game
        assert outcome_df["games"].sum() == number_of_players + df["games"].sum()
        # Winners have won a game, losers have lost a game.
        winners_df = outcome_df.loc[outcome_df["player"].isin(team_1_players)]
        losers_df = outcome_df.loc[outcome_df["player"].isin(team_2_players)]
        assert all(winners_df.loc[:, ['win']])
        assert all(~winners_df.loc[:, ['loss']])
        assert all(losers_df.loc[:, ['loss']])
        assert all(~losers_df.loc[:, ['win']])
        outcome_df = update_matches_outcome(outcome_df, state, team_1_players, team_2_players)
        # Even more games have been played after this game
        assert outcome_df["games"].sum() == 2 * number_of_players + df["games"].sum()
