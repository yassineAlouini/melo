# -*- coding: utf-8 -*-

# A POC implementation


import os
from pathlib import Path

import pandas as pd

import elo
import emoji
from melo.conf import BASE_K_FACTOR
from slacker import Slacker
from tabulate import tabulate


def compute_score(state, team_1_score, team_2_score, points_difference):
    """
    State contains the outcome of the game between team_1 and team_2.
    It is "WIN" if player 1 wins, "LOSS" if he looses and "DRAW" otherwise.
    """
    # +1 to avoid having a k_factor of 0 when there is a DRAW.
    elo.setup(k_factor=BASE_K_FACTOR * (points_difference + 1))
    if state == "WIN":
        scores = elo.rate_1vs1(team_1_score, team_2_score)
    elif state == "LOSS":
        scores = elo.rate_1vs1(team_2_score, team_1_score)[::-1]
    else:
        scores = elo.rate_1vs1(team_1_score, team_2_score, drawn=True)
    return scores


def get_game_state():
    team_1_players = input(
        "Enter the players' names from team 1 (names space-separated): ").split(" ")
    team_2_players = input(
        "Enter the players' names from team 2 (names space-separated):  ").split(" ")
    points_difference = input(
        "Please enter the points difference between team 1 and team 2 (in absolute value): ")
    if not team_1_players or not team_2_players:
        raise Exception(
            "You haven't entred players' names for either team 1 or team 2")
    if len(set(team_1_players)) != len(team_1_players):
        raise Exception(
            "You have entred the name of a player many times for team 1.")
    if len(set(team_2_players)) != len(team_2_players):
        raise Exception(
            "You have entred the name of a player many times for team 2.")
    if set(team_1_players) & set(team_2_players):
        raise Exception(
            "There shouldn't be any commong players between the two teams. Please enter the names again.")
    winning_team = input(
        "Enter the name of the winning team. Space character if it is a draw.")
    if winning_team not in ["team_1", "team_2", " "]:
        raise Exception(
            "The winning team should be either 'team_1', 'team_2' or a ' ' if a draw.")
    if winning_team == "team_1":
        state = "WIN"
    elif winning_team == "team_2":
        state = "LOSS"
    else:
        state = "DRAW"
    return state, team_1_players, team_2_players, int(points_difference)


def update_matches_outcome(input_df, state, team_1_players, team_2_players):
    df = input_df.copy()
    # Update the number of games
    players = team_1_players + team_2_players
    df.loc[lambda df: df.player.isin(players), 'games'] += 1
    # Update the game outcome (win, loss, draw)
    if state == "WIN":
        df.loc[lambda df: df.player.isin(team_1_players), 'win'] += 1
        df.loc[lambda df: df.player.isin(team_2_players), 'loss'] += 1

    elif state == "LOSS":
        df.loc[lambda df: df.player.isin(team_1_players), 'loss'] += 1
        df.loc[lambda df: df.player.isin(team_2_players), 'win'] += 1

    elif state == "DRAW":
        df.loc[lambda df: df.player.isin(team_1_players), 'draw'] += 1
        df.loc[lambda df: df.player.isin(team_2_players), 'draw'] += 1
    else:
        raise Exception("You have provided a state that isn't available!")
    return df


def get_results_msg(df, team_1_players, team_1_new_score, team_1_scores, team_2_players, team_2_new_score,
                    team_2_scores):
    formatted_data = tabulate(df, headers='keys', tablefmt='psql')
    team_1_deltas = team_1_new_score - team_1_scores
    team_2_deltas = team_2_new_score - team_2_scores
    assert len(team_1_deltas) == len(team_2_deltas)
    msg = ' '.join([u'{} got {}. \n'.format(player, delta)
                    for player, delta in zip(team_1_players, team_1_deltas)])
    msg = msg + ' '.join([u'{} got {}. \n'.format(player, delta)
                          for player, delta in zip(team_2_players, team_2_deltas)])
    msg = msg + \
        u'The new melos are:\n ```{}```Well played :wink2:'.format(
            formatted_data)
    return emoji.emojize(msg)


def slack_results_msg(msg, game_type):
    slack = Slacker(SLACK_API_KEY)
    if game_type == "test":
        slack.chat.post_message(SLACK_USER, msg, as_user=False)
    else:
        slack.chat.post_message(CHANNEL, msg)


def main(game_type):
    # TODO: Add some documentation
    path = PATHS.get(game_type, PATHS["test"])
    game_df = pd.read_csv(path)
    state, team_1_players, team_2_players = get_game_state()
    game_df = update_matches_outcome(
        game_df, state, team_1_players, team_2_players)
    team_1_scores = game_df.loc[lambda df: df.player.isin(
        team_1_players), 'elo']
    team_2_scores = game_df.loc[lambda df: df.player.isin(
        team_2_players), 'elo']
    # TODO: Using the mean for now. Make this more generalizable.
    team_1_score = float(team_1_scores.mean())
    team_2_score = float(team_2_scores.mean())
    team_1_new_score, team_2_new_score = compute_score(
        state, team_1_score, team_2_score)
    # Update the score
    game_df.loc[lambda df: df.player.isin(
        team_1_players), 'elo'] = team_1_new_score
    game_df.loc[lambda df: df.player.isin(
        team_2_players), 'elo'] = team_2_new_score
    game_df = game_df.sort_values(
        'score', ascending=False).reset_index(drop=True)
    # 1 based index
    game_df.index += 1
    game_df.to_csv(path, index=False)
    msg = get_results_msg(game_df, team_1_players, team_1_new_score, team_1_scores, team_2_players,
                          team_2_new_score, team_2_scores)
    slack_results_msg(msg, game_type)


if __name__ == '__main__':
    main("test")
