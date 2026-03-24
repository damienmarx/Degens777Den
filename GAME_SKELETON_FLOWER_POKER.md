# Flower Poker Game Skeleton

## 1. Overview
This document outlines the technical specifications for implementing an OSRS-style Flower Poker game within the Degens777Den platform. The game will replicate the core mechanics, visual elements, and betting structure of the traditional RuneScape Flower Poker, with added features for enhanced user experience and customization.

## 2. Core Game Mechanics

### 2.1. Game Flow
1.  **Player vs. Player (PvP):** Two players agree on a bet amount.
2.  **Flower Planting:** Each player plants a "Mithril Seed" (or equivalent in-game item/action).
3.  **Flower Growth:** Five flowers grow for each player, revealing their 
color.
4.  **Hand Evaluation:** The combination of five flower colors determines the player's hand.
5.  **Winner Determination:** The player with the higher-ranked hand wins the pot.
6.  **Pot Distribution:** The winner takes the total bet, minus a small house rake.

### 2.2. Flower Colors and Hand Rankings
Based on OSRS Flower Poker, the hand rankings are as follows (from lowest to highest):

| Rank             | Description                                                                 | Example                                     |
| :--------------- | :-------------------------------------------------------------------------- | :------------------------------------------ |
| **No Pair**      | Five different colored flowers.                                             | Red, Blue, Green, Yellow, Purple            |
| **One Pair**     | Two flowers of the same color, three other different colors.                | Red, Red, Blue, Green, Yellow               |
| **Two Pair**     | Two sets of two flowers of the same color, one other different color.       | Red, Red, Blue, Blue, Green                 |
| **Three of a Kind** | Three flowers of the same color, two other different colors.                | Red, Red, Red, Blue, Green                  |
| **Full House**   | Three flowers of one color, and two flowers of another color.               | Red, Red, Red, Blue, Blue                   |
| **Four of a Kind** | Four flowers of the same color, one other different color.                  | Red, Red, Red, Red, Blue                    |
| **Five of a Kind** | All five flowers are the same color. This is the highest possible hand.     | Red, Red, Red, Red, Red                     |

**Tie-breaking:** In case of a tie (e.g., both players have a Full House), the highest-ranked color within the hand (e.g., the color of the three-of-a-kind in a Full House) determines the winner. If still tied, the pot is split.

### 2.3. Betting System
*   **Peer-to-Peer:** Players initiate challenges with a specified bet amount.
*   **House Rake:** A small percentage (e.g., 1-3%) of the total pot is taken as a house rake.
*   **Minimum/Maximum Bets:** Configurable limits to prevent abuse and manage risk.

## 3. User Customization & Variables

### 3.1. Autoplay Features
*   **Auto-Accept Challenges:** Users can set a threshold to automatically accept challenges from other players if the bet amount is within a specified range.
*   **Auto-Plant:** Automatically plant seeds when a challenge is accepted or initiated.
*   **Auto-Replay:** Automatically initiate a new game with the same opponent and bet amount after a game concludes.

### 3.2. Cashout/Thresholds
*   **Win Threshold Auto-Cashout:** Automatically cash out winnings to the main balance if a single win exceeds a user-defined amount.
*   **Loss Threshold Auto-Stop:** Automatically stop playing if total losses within a session exceed a user-defined amount.
*   **Session Limit:** Set a maximum number of games to play in a single session.

### 3.3. UI/UX Considerations
*   **Visual Feedback:** Clear animations for planting, growing, and revealing flowers. Distinct visual cues for winning/losing hands.
*   **Real-time Updates:** Instant updates on opponent's actions, pot amount, and game status.
*   **History Log:** A personal game history log showing past bets, wins, losses, and opponents.

## 4. Technical Implementation Notes
*   **Backend (FastAPI):**
    *   Endpoint for initiating challenges (`/api/flowerpoker/challenge`).
    *   Endpoint for planting seeds (`/api/flowerpoker/plant`).
    *   Game state management (MongoDB) for active games, player hands, and pot.
    *   Logic for hand evaluation and winner determination.
    *   Integration with user balance system for betting and payouts.
    *   WebSockets for real-time game updates.
*   **Frontend (React):**
    *   Game lobby for finding opponents or initiating challenges.
    *   Interactive game table displaying flowers, bets, and results.
    *   User settings panel for autoplay and threshold configurations.
    *   Animations for game actions.

## 5. Future Enhancements
*   **Spectator Mode:** Allow users to watch ongoing games.
*   **Leaderboards:** Track top players by wins, biggest pots, etc.
*   **Tournaments:** Implement multi-player tournaments.
*   **Customizable Seeds/Animations:** Allow VIP users to unlock unique seed planting animations or flower designs.
