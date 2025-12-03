#!/usr/bin/env python3
"""
Tournament simulator for testing MTG Draft Tournament Tracker.
Simulates multiple players with random health changes.
"""

import asyncio
import random
import argparse
import requests
import time
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class SimulatedPlayer:
    id: int
    name: str
    colors: List[str]
    current_match_id: Optional[int] = None
    current_health: int = 20

# 30 Iconic MTG Card Avatars (Scryfall art crops)
PREDEFINED_AVATARS = [
    "https://cards.scryfall.io/art_crop/front/b/d/bd8fa327-dd41-4737-8f19-2cf5eb1f7cdd.jpg",  # Black Lotus
    "https://cards.scryfall.io/art_crop/front/f/2/f29ba16f-c8fb-42fe-aabf-87089cb214a7.jpg",  # Lightning Bolt
    "https://cards.scryfall.io/art_crop/front/3/c/3cee9303-9d65-45a2-93d4-ef4aba59141b.jpg",  # Serra Angel
    "https://cards.scryfall.io/art_crop/front/1/f/1fcff1e0-2745-448d-a27b-e31719e222e9.jpg",  # Shivan Dragon
    "https://cards.scryfall.io/art_crop/front/1/b/1b73577a-8ca1-41d7-9b2b-7300286fde43.jpg",  # Counterspell
    "https://cards.scryfall.io/art_crop/front/9/5/95f27eeb-6f14-4db3-adb9-9be5ed76b34b.jpg",  # Dark Ritual
    "https://cards.scryfall.io/art_crop/front/8/b/8bbcfb77-daa1-4ce5-b5f9-48d0a8edbba9.jpg",  # Llanowar Elves
    "https://cards.scryfall.io/art_crop/front/f/e/feefe9f0-24a6-461c-9ef1-86c5a6f33b83.jpg",  # Birds of Paradise
    "https://cards.scryfall.io/art_crop/front/5/3/537d2b05-3f52-45d6-8fe3-26282085d0c6.jpg",  # Wrath of God
    "https://cards.scryfall.io/art_crop/front/c/8/c8817585-0d32-4d56-9142-0d29512e86a9.jpg",  # Jace, the Mind Sculptor
    "https://cards.scryfall.io/art_crop/front/d/1/d12c8c97-6491-452c-811d-943441a7ef9f.jpg",  # Liliana of the Veil
    "https://cards.scryfall.io/art_crop/front/6/9/69daba76-96e8-4bcc-ab79-2f00189ad8fb.jpg",  # Tarmogoyf
    "https://cards.scryfall.io/art_crop/front/e/e/ee6e5a35-fe21-4dee-b0ef-a8f2841511ad.jpg",  # Sol Ring
    "https://cards.scryfall.io/art_crop/front/8/9/89f612d6-7c59-4a7b-a87d-45f789e88ba5.jpg",  # Force of Will
    "https://cards.scryfall.io/art_crop/front/4/8/48070245-1370-4cf1-be15-d4e8a8b92ba8.jpg",  # Brainstorm
    "https://cards.scryfall.io/art_crop/front/7/d/7d839f21-68c7-47db-8407-ff3e2c3e13b4.jpg",  # Swords to Plowshares
    "https://cards.scryfall.io/art_crop/front/3/c/3c0f5411-1940-410f-96ce-6f92513f753a.jpg",  # Goblin Guide
    "https://cards.scryfall.io/art_crop/front/7/e/7e41765e-43fe-461d-baeb-ee30d13d2d93.jpg",  # Snapcaster Mage
    "https://cards.scryfall.io/art_crop/front/a/7/a7aed564-2d2d-42c4-bf11-812bc1a0284c.jpg",  # Path to Exile
    "https://cards.scryfall.io/art_crop/front/b/2/b281a308-ab6b-47b6-bec7-632c9aaecede.jpg",  # Thoughtseize
    "https://cards.scryfall.io/art_crop/front/2/4/249db4d4-2542-47ee-a216-e13ffbc2319c.jpg",  # Emrakul, the Aeons Torn
    "https://cards.scryfall.io/art_crop/front/4/0/4069e510-f3f3-4668-9f13-3546fa9bc7c3.jpg",  # Griselbrand
    "https://cards.scryfall.io/art_crop/front/5/d/5d275f04-cc60-4e3f-95cc-3d02bc916b82.jpg",  # Wurmcoil Engine
    "https://cards.scryfall.io/art_crop/front/6/d/6d5537da-112e-4679-a113-b5d7ce32a66b.jpg",  # Primeval Titan
    "https://cards.scryfall.io/art_crop/front/2/5/2520ab23-a068-4462-b261-2754409b4108.jpg",  # Dark Confidant
    "https://cards.scryfall.io/art_crop/front/c/d/cd702cf1-10ca-4448-9fb1-b6de635e839c.jpg",  # Vendilion Clique
    "https://cards.scryfall.io/art_crop/front/b/e/beda7acd-e970-4222-9577-5133765d6052.jpg",  # Thragtusk
    "https://cards.scryfall.io/art_crop/front/2/7/276f5cee-a501-4658-bd4d-7a044bf1ccbc.jpg",  # Craterhoof Behemoth
    "https://cards.scryfall.io/art_crop/front/d/6/d6bfa227-4309-40ed-952c-279595eab17e.jpg",  # Monastery Swiftspear
    "https://cards.scryfall.io/art_crop/front/6/9/6904ea20-e504-47da-95a0-08739fdde260.jpg",  # Delver of Secrets
]

class TournamentSimulator:
    def __init__(
        self,
        api_url: str,
        num_players: int,
        speed: str = "medium",
        manual_player: Optional[str] = None,
        admin_password: str = "admin"
    ):
        self.api_url = api_url.rstrip('/')
        self.num_players = num_players
        self.speed = speed
        self.manual_player = manual_player
        self.admin_password = admin_password
        self.players: List[SimulatedPlayer] = []
        self.tournament_id: Optional[int] = None
        self.admin_token: Optional[str] = None

        # Speed configurations (seconds)
        self.speed_config = {
            "slow": (5, 10),
            "medium": (3, 5),
            "fast": (1, 3),
            "fastest": (0.3, 1)
        }

        self.running = True

    def log(self, message: str):
        """Print timestamped log message."""
        print(f"[{time.strftime('%H:%M:%S')}] {message}")

    def admin_login(self, password: str = "admin"):
        """Login as admin and get token."""
        self.log(f"Logging in as admin...")

        response = requests.post(
            f"{self.api_url}/api/admin/login",
            json={"password": password}
        )

        if response.status_code != 200:
            raise Exception(f"Failed to login as admin: {response.text}")

        self.admin_token = response.json()["token"]
        self.log("✓ Admin login successful")

    def delete_existing_tournaments(self):
        """Delete all existing tournaments to start fresh."""
        self.log("Cleaning up existing tournaments...")
        
        try:
            # Get tournament history
            response = requests.get(
                f"{self.api_url}/api/admin/tournaments/history",
                headers={"Authorization": f"Bearer {self.admin_token}"}
            )
            
            if response.status_code == 200:
                tournaments = response.json().get("tournaments", [])
                
                for t in tournaments:
                    delete_response = requests.delete(
                        f"{self.api_url}/api/admin/tournament/{t['id']}",
                        headers={"Authorization": f"Bearer {self.admin_token}"}
                    )
                    if delete_response.status_code == 200:
                        self.log(f"  ✓ Deleted tournament: {t['name']}")
                    else:
                        self.log(f"  ! Could not delete tournament {t['id']}")
                
                if tournaments:
                    self.log(f"✓ Cleaned up {len(tournaments)} tournament(s)")
                else:
                    self.log("✓ No existing tournaments to clean up")
            else:
                self.log("! Could not fetch tournament history")
        except Exception as e:
            self.log(f"! Error cleaning up: {e}")

    def create_tournament(self) -> int:
        """Create a new tournament."""
        self.log("Creating tournament...")

        response = requests.post(
            f"{self.api_url}/api/admin/tournament",
            json={
                "name": f"Simulated Tournament {int(time.time())}",
                "max_players": self.num_players + (1 if self.manual_player else 0),
                "starting_life": 20
            },
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )

        if response.status_code != 200:
            raise Exception(f"Failed to create tournament: {response.text}")

        tournament_id = response.json()["tournament_id"]
        self.log(f"✓ Tournament created: ID {tournament_id}")
        return tournament_id

    def generate_player_name(self, index: int) -> str:
        """Generate random player name."""
        first_names = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank",
                       "Grace", "Henry", "Iris", "Jack", "Kate", "Leo",
                       "Maya", "Noah", "Olivia", "Paul", "Quinn", "Ruby"]

        if index < len(first_names):
            return f"{first_names[index]} (Bot)"
        return f"Player{index} (Bot)"

    def generate_random_colors(self) -> List[str]:
        """Generate 1-3 random Magic colors."""
        all_colors = ["W", "U", "B", "R", "G"]
        num_colors = random.randint(1, 3)
        return random.sample(all_colors, num_colors)

    def register_players(self):
        """Register all simulated players."""
        self.log(f"Registering {self.num_players} bot players...")

        for i in range(self.num_players):
            name = self.generate_player_name(i)
            colors = self.generate_random_colors()
            avatar_url = random.choice(PREDEFINED_AVATARS)

            response = requests.post(
                f"{self.api_url}/api/players/join",
                json={
                    "tournament_id": self.tournament_id,
                    "name": name
                }
            )

            if response.status_code != 200:
                self.log(f"Failed to register {name}: {response.text}")
                continue

            player_data = response.json()
            player_id = player_data["player_id"]

            # Update profile with colors and avatar
            import json
            requests.put(
                f"{self.api_url}/api/players/{player_id}/profile",
                data={
                    "colors": json.dumps(colors),
                    "avatar_url": avatar_url
                }
            )

            player = SimulatedPlayer(
                id=player_id,
                name=name,
                colors=colors
            )
            self.players.append(player)

            self.log(f"✓ Registered: {name} (ID: {player_id}, Colors: {colors})")

    def generate_schedule(self):
        """Generate tournament schedule."""
        self.log("Generating round-robin schedule...")

        response = requests.post(
            f"{self.api_url}/api/admin/tournament/{self.tournament_id}/generate-schedule",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )

        if response.status_code != 200:
            raise Exception(f"Failed to generate schedule: {response.text}")

        data = response.json()
        self.log(f"✓ Schedule generated: {data['rounds_created']} rounds, {data['total_matches']} matches")

    def get_current_round_matches(self) -> List[Dict]:
        """Get matches for current round."""
        response = requests.get(
            f"{self.api_url}/api/tournament/{self.tournament_id}/current-round"
        )

        if response.status_code != 200:
            return []

        return response.json().get("matches", [])

    def join_match(self, player: SimulatedPlayer, match_id: int):
        """Player joins their assigned match."""
        response = requests.post(
            f"{self.api_url}/api/matches/{match_id}/join",
            json={"player_id": player.id}
        )

        if response.status_code == 200:
            player.current_match_id = match_id
            player.current_health = 20
            self.log(f"✓ {player.name} joined match {match_id}")
            return True
        return False

    def update_health(self, player: SimulatedPlayer, change: int):
        """Update player health."""
        if player.current_match_id is None:
            return

        response = requests.put(
            f"{self.api_url}/api/matches/{player.current_match_id}/health",
            json={
                "player_id": player.id,
                "health_change": change
            }
        )

        if response.status_code == 200:
            player.current_health += change
            self.log(f"  {player.name}: {change:+d} HP → {player.current_health} HP")

    def confirm_defeat(self, player: SimulatedPlayer):
        """Player confirms defeat."""
        if player.current_match_id is None:
            return

        response = requests.post(
            f"{self.api_url}/api/matches/{player.current_match_id}/defeat",
            json={"player_id": player.id}
        )

        if response.status_code == 200:
            self.log(f"✓ {player.name} confirmed defeat in match {player.current_match_id}")
            player.current_match_id = None
            player.current_health = 20

    async def simulate_player_actions(self, player: SimulatedPlayer):
        """Simulate a single player's actions."""
        while self.running:
            if player.current_match_id is not None:
                # Player is in a match
                if player.current_health > 0:
                    # Random health change (more likely to lose health)
                    change = random.choice([-5, -3, -2, -1, -1, 1, 2])

                    # Don't go negative
                    if player.current_health + change < 0:
                        change = -player.current_health

                    self.update_health(player, change)

                    # Check if defeated
                    if player.current_health <= 0:
                        await asyncio.sleep(2)  # Brief pause before confirming
                        self.confirm_defeat(player)
                else:
                    # Already at 0, confirm defeat
                    self.confirm_defeat(player)

            # Wait before next action
            min_delay, max_delay = self.speed_config[self.speed]
            await asyncio.sleep(random.uniform(min_delay, max_delay))

    async def run_round(self):
        """Run one round of matches."""
        matches = self.get_current_round_matches()

        if not matches:
            self.log("No matches found for current round")
            return False

        self.log(f"Starting round with {len(matches)} matches...")

        # Assign players to their matches
        for match in matches:
            match_id = match["match_id"]

            # Find players for this match
            p1_name = match["player1"]["name"]
            p2_name = match["player2"]["name"]

            player1 = next((p for p in self.players if p.name == p1_name), None)
            player2 = next((p for p in self.players if p.name == p2_name), None)

            if player1:
                self.join_match(player1, match_id)
            if player2:
                self.join_match(player2, match_id)

        # Start simulating all players concurrently
        tasks = [asyncio.create_task(self.simulate_player_actions(player)) for player in self.players]

        # Wait until all matches are complete
        while True:
            matches = self.get_current_round_matches()

            if not matches:
                break

            in_progress = sum(1 for m in matches if m["status"] == "in_progress")
            completed = sum(1 for m in matches if m["status"] == "completed")

            if in_progress == 0:
                self.log(f"✓ Round complete! {completed} matches finished")
                break

            await asyncio.sleep(2)

        # Cancel player simulation tasks
        for task in tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        return True

    async def run_tournament(self):
        """Run the entire tournament simulation."""
        try:
            # Admin login
            self.admin_login(self.admin_password)

            # Delete existing tournaments to start fresh
            self.delete_existing_tournaments()

            # Create tournament
            self.tournament_id = self.create_tournament()

            # Register bot players
            self.register_players()

            # Manual player can join now
            if self.manual_player:
                self.log(f"\n{'='*60}")
                self.log(f"MANUAL PLAYER INFO:")
                self.log(f"  1. Open: http://localhost:8000/player.html")
                self.log(f"  2. Join tournament with name: {self.manual_player}")
                self.log(f"  3. Tournament ID: {self.tournament_id}")
                self.log(f"{'='*60}\n")
                self.log("Waiting 30 seconds for manual player to join...")
                await asyncio.sleep(30)

            # Generate schedule
            self.generate_schedule()

            # Get total rounds
            response = requests.get(f"{self.api_url}/api/tournament/{self.tournament_id}/schedule")
            total_rounds = len(response.json().get("rounds", []))

            self.log(f"Tournament has {total_rounds} rounds")

            # Run each round
            for round_num in range(1, total_rounds + 1):
                self.log(f"\n{'='*60}")
                self.log(f"ROUND {round_num} of {total_rounds}")
                self.log(f"{'='*60}\n")

                success = await self.run_round()

                if not success:
                    break

                if round_num < total_rounds:
                    self.log(f"Pausing 10 seconds before next round...")
                    await asyncio.sleep(10)

            self.log(f"\n{'='*60}")
            self.log("TOURNAMENT COMPLETE!")
            self.log(f"{'='*60}\n")

            # Display final standings
            response = requests.get(f"{self.api_url}/api/tournament/{self.tournament_id}/standings")
            standings = response.json().get("standings", [])

            self.log("Final Standings:")
            for player in standings:
                self.log(f"  {player['rank']}. {player['name']}: {player['wins']}W-{player['losses']}L ({player['points']} pts)")

        except KeyboardInterrupt:
            self.log("\nSimulation interrupted by user")
            self.running = False
        except Exception as e:
            self.log(f"Error: {e}")
            import traceback
            traceback.print_exc()
            raise

def main():
    parser = argparse.ArgumentParser(
        description="Simulate MTG Draft Tournament with bot players"
    )
    parser.add_argument(
        "--players",
        type=int,
        default=8,
        help="Number of simulated players (2-20)"
    )
    parser.add_argument(
        "--speed",
        choices=["slow", "medium", "fast", "fastest"],
        default="medium",
        help="Simulation speed"
    )
    parser.add_argument(
        "--manual-player",
        type=str,
        help="Reserve slot for human player with this name"
    )
    parser.add_argument(
        "--api-url",
        default="http://localhost:8000",
        help="Backend API URL"
    )
    parser.add_argument(
        "--password",
        type=str,
        default="admin",
        help="Admin password (default: admin)"
    )

    args = parser.parse_args()

    # Validate player count
    if args.players < 2 or args.players > 20:
        print("Error: Players must be between 2 and 20")
        return

    # Adjust for manual player
    num_bots = args.players - (1 if args.manual_player else 0)

    print(f"""
╔══════════════════════════════════════════════════════════╗
║      MTG Draft Tournament Simulator                      ║
╚══════════════════════════════════════════════════════════╝

Configuration:
  - Bot Players: {num_bots}
  - Manual Player: {args.manual_player or 'None'}
  - Speed: {args.speed}
  - API: {args.api_url}
  - Password: {args.password}

Starting simulation...
    """)

    simulator = TournamentSimulator(
        api_url=args.api_url,
        num_players=num_bots,
        speed=args.speed,
        manual_player=args.manual_player,
        admin_password=args.password
    )

    asyncio.run(simulator.run_tournament())

if __name__ == "__main__":
    main()
