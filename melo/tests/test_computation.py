# -*- coding: utf-8 -*-

import unittest

import pandas as pd

from ddt import data, ddt, unpack
from melo.conf import BASE_K_FACTOR
from melo.poc import compute_score, update_matches_outcome


# TODO: Use pytest fixtures for more cases.


def _compute_expected_score(score_1, score_2):
    return 1 / (1 + 10 ** ((score_2 - score_1) / 400))


@ddt
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
        outcome_df = update_matches_outcome(
            df, state, team_1_players, team_2_players)
        # More games have been played after this game
        assert outcome_df["games"].sum() == number_of_players + \
            df["games"].sum()
        # Winners have won a game, losers have lost a game.
        winners_df = outcome_df.loc[outcome_df["player"].isin(team_1_players)]
        losers_df = outcome_df.loc[outcome_df["player"].isin(team_2_players)]
        assert all(winners_df.loc[:, ['win']])
        assert all(~winners_df.loc[:, ['loss']])
        assert all(losers_df.loc[:, ['loss']])
        assert all(~losers_df.loc[:, ['win']])
        outcome_df = update_matches_outcome(
            outcome_df, state, team_1_players, team_2_players)
        # Even more games have been played after this game
        assert outcome_df["games"].sum() == 2 * \
            number_of_players + df["games"].sum()

    @unpack
    @data({"team_1_score": 1100, "team_2_score": 1100, "points_difference": 10},
          {"team_1_score": 2000, "team_2_score": 1000, "points_difference": 10},
          {"team_1_score": 100, "team_2_score": 1000, "points_difference": 1})
    def test_compute_score_team_1_won(self, team_1_score, team_2_score, points_difference):
        """
        Test that the new score for team 1 has increased and decreased for team 2
        (since team 1 won). Also, check that the scores differences is correctly computed:
        using the theoretical formula, it should be 2 * K * (points_difference + 1) * (1 - E_1))
        """
        # Team 1 won scenario
        state = "WIN"
        new_team_1_score, new_team_2_score = compute_score(state, team_1_score, team_2_score,
                                                           points_difference)
        assert new_team_1_score > team_1_score
        assert new_team_2_score < team_2_score
        expected_team_1_score = _compute_expected_score(
            team_1_score, team_2_score)
        expected_scores_difference = 2 * BASE_K_FACTOR * \
            (points_difference + 1) * (1 - expected_team_1_score)
        compute_scores_difference = ((new_team_1_score - new_team_2_score) -
                                     (team_1_score - team_2_score))
        # Round since float imprecision
        assert round(compute_scores_difference, 6) == round(
            expected_scores_difference, 6)

    @unpack
    @data({"team_1_score": 1100, "team_2_score": 1100, "points_difference": 10},
          {"team_1_score": 2000, "team_2_score": 1000, "points_difference": 10},
          {"team_1_score": 100, "team_2_score": 1000, "points_difference": 1})
    def test_compute_score_team_1_lost(self, team_1_score, team_2_score, points_difference):
        """
        Test that the new score for team 1 has decreased and increased for team 2
        (since team 1 lost). Also, check that the scores differences is correctly computed:
        using the theoretical formula, it should be -2 * K * (points_difference + 1) * E_1
        """
        # Team 1 lost scenario
        state = "LOSS"
        new_team_1_score, new_team_2_score = compute_score(state, team_1_score, team_2_score,
                                                           points_difference)
        assert new_team_1_score < team_1_score
        assert new_team_2_score > team_2_score
        expected_team_1_score = _compute_expected_score(
            team_1_score, team_2_score)
        expected_scores_difference = -2 * BASE_K_FACTOR * \
            (points_difference + 1) * expected_team_1_score
        compute_scores_difference = ((new_team_1_score - new_team_2_score) -
                                     (team_1_score - team_2_score))
        # Round since float imprecision
        assert round(compute_scores_difference, 6) == round(
            expected_scores_difference, 6)

    def test_get_more_points_when_bigger_points_difference(self):
        """ Check that a team gains more points when the points difference is bigger. """
        state = "WIN"
        team_1_score = 1100
        team_2_score = 1100
        new_team_1_score_big_difference, _ = compute_score(state, team_1_score, team_2_score,
                                                           10)

        new_team_1_score_small_difference, _ = compute_score(state, team_1_score, team_2_score,
                                                             1)
        assert new_team_1_score_big_difference > new_team_1_score_small_difference

    def test_get_points_when_draw(self):
        """
        Check that a team gains some points even when the game is a draw if
        it has a lower inital score than the other one.
        """
        state = "DRAW"
        points_difference = 0
        team_1_score = 1000
        team_2_score = 2000
        new_team_1_score, _ = compute_score(
            state, team_1_score, team_2_score, points_difference)
        assert new_team_1_score - team_1_score > 0
