# A POC implementation


import elo
import pandas as pd
from slacker import Slacker
from tabulate import tabulate
import emoji

# TODO: Replace these with env variables. 
slack = Slacker('SLACK_API_KEY')  # API key
test = False
game = True
K_FACTOR = 40
CHANNEL = 'SLACK_CHANNEL'
SLACK_USER = '@cat'

elo.setup(k_factor=K_FACTOR)


def compute_score(state, team_1_score, team_2_score):
    """
    State contains the outcome of the game between player 1 and 2.
    It is "WIN" if player 1 wins, "LOSS" if he looses and "DRAW" otherwise.
    Notice that in the case of multiple players, it is the mean that is taken 
    into account.
    """
    if state == "WIN":
        scores = elo.rate_1vs1(team_1_score, team_2_score)
    elif state == "LOSS":
        scores = elo.rate_1vs1(player_2_score, team_1_score)[::-1]
    else:
        scores = elo.rate_1vs1(team_1_score, team_2_score, drawn=True)
    return scores

# TODO: Some refactoring...
def get_game_state():
    team_1_players = raw_input("Enter the players' names from team 1 (names space-separated): ").split(" ")
    team_2_players = raw_input("Enter the players' names from team 2 (names space-separated):  ").split(" ")
    if not team_1_players or not team_2_players:
        raise Exception("You haven't entred players' names for either team 1 or team 2")
    if len(set(team_1_players)) != len(team_1_players):
        raise Exception("You have entred the name of a player many times for team 1."
    if len(set(team_2_players)) != len(team_2_players):
        raise Exception("You have entred the name of a player many times for team 2."       
    if set(team_1_players) & set(team2_players):
        raise Exception("There shouldn't be any commong players between the two teams. Please enter the names again.")
    winning_team = raw_input("Enter the name of the winning team. Space character if it is a draw.")
    if winning_team not in ["team_1", "team_2", " "]:
        raise Exception("The winning team should be either 'team_1', 'team_2' or a ' ' if a draw.") 
    if winning_team == "team_1":
        state = "WIN"
    elif winning_team == "team_2":
        state = "LOSS"
    else:
        state = "DRAW"
    return state, team_1_players, team_2_players


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
    return df


if __name__ == '__main__':
    if not test:
        SCORES_PATH = 'scores.csv'
    else:
        SCORES_PATH = 'test_scores.csv'
    game_df = pd.read_csv(SCORES_PATH)
    if game:
        state, team_1_players, team_2_players = get_game_state()
        game_df = update_matches_outcome(game_df, state, team_1_players, team_2_players)
        team_1_scores = game_df.loc[lambda df: df.player.isin(team_1_players), 'score']
        team_2_scores = game_df.loc[lambda df: df.player.isin(team_2_players), 'score']
        # Use the mean for now
        team_1_score = float(team_1_scores.mean())
        team_2_score = float(team_2_scores.mean())
        team_1_new_score, team_2_new_score = compute_score(
            state, team_1_score, team_2_score)
        # Update the score
        game_df.loc[lambda df: df.player.isin(team_1_players), 'score'] = team_1_new_score
        game_df.loc[lambda df: df.player.isin(team_2_players), 'score'] = team_2_new_score
        game_df = game_df.sort_values('score', ascending=False).reset_index(drop=True)
        # 1 based index
        game_df.index += 1
        start_bold = "\033[1m"
        end_bold = "\033[0;0m"
        print start_bold + end_bold
        # TODO: Update this for the multiplayers setting
        # previous_world_champion = str(data.loc[lambda df: df.world_champ == 1, 'player'].values[0])
        # world_champion = previous_world_champion
        # if (state == "WIN") and (previous_world_champion == player_2):
        #     world_champion = player_1
        # elif (state == "LOSS") and (previous_world_champion == player_1):
        #    world_champion = player_2
        # data.loc[lambda df: df.player == world_champion, 'world_champ'] = 1
        # data.loc[lambda df: df.player != world_champion, 'world_champ'] = 0
        game_df.to_csv(SCORES_PATH, index=False)
    formatted_data = tabulate(game_df, headers='keys', tablefmt='psql')
    team_1_deltas = team_1_new_score - team_1_scores
    team_2_deltas = team_2_new_score - team_2_scores
    msg = ''.join([u'{} got {}. \n'.format(player, delta) for player, delta in zip(team_1_players, team_1_deltas)
    msg = msg + ''.join(u'{} got {}. \n'.format(player, delta) for player, delta in zip(team_2_players, team_2_deltas)
    # TODO: Finish this.
    # if previous_world_champion != world_champion:
    #     msg = msg + u'{} is the new world champion :king_black:. The previous one was {}. Congratulations!\n'.format(
    #         world_champion, previous_world_champion)
    msg = msg + u'The new scores are:\n ```{}```. Well played :wink2:'.format(formatted_data)
    msg = emoji.emojize(msg)
    if test:
        slack.chat.post_message(SLACK_USER, msg, as_user=False)
    else:
        slack.chat.post_message(CHANNEL, msg)
