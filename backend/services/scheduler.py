from typing import List, Tuple, Optional
from models import Player


def generate_round_robin_schedule(players: List[Player]) -> List[List[Tuple[Player, Player]]]:
    """
    Generates a round-robin tournament schedule.
    If odd number of players, one player gets a bye each round (represented as None).

    Args:
        players: List of Player objects

    Returns:
        List of rounds, where each round is a list of (player1, player2) tuples
    """
    players_list = players.copy()
    n = len(players_list)

    # Handle bye for odd number of players
    has_bye = n % 2 == 1
    if has_bye:
        players_list.append(None)  # Bye placeholder
        n += 1

    rounds = []
    num_rounds = n - 1
    half = n // 2

    for round_num in range(num_rounds):
        round_matches = []

        for i in range(half):
            player1 = players_list[i]
            player2 = players_list[n - 1 - i]

            # Skip matches where either player is None (bye)
            if player1 is not None and player2 is not None:
                round_matches.append((player1, player2))

        rounds.append(round_matches)

        # Rotate players (keep first player fixed, rotate the rest)
        players_list = [players_list[0]] + [players_list[-1]] + players_list[1:-1]

    return rounds
