# Degens Slots Game Skeleton (Magic Slots Clone)

## 1. Overview
This document details the technical specifications for implementing "Degens Slots," a game inspired by the "Magic Slots" from RuneChat, but re-themed with OSRS elements. The goal is to replicate the engaging animations, payout logic, and bonus rounds while providing extensive user customization options for autoplay and cashout thresholds.

## 2. Core Game Mechanics

### 2.1. Slot Grid and Symbols
*   **Grid Layout:** The game will feature a standard slot grid, either 3x3 or 5x3, to be determined based on visual appeal and complexity.
*   **OSRS-Themed Symbols:**
    *   **High Value:** Partyhats (various colors), Godswords (Saradomin, Zamorak, Bandos, Armadyl), Third-Age items, Dragonfire Shield.
    *   **Medium Value:** Rune equipment, Dragon equipment, Abyssal Whip.
    *   **Low Value:** Various OSRS skill icons (Attack, Strength, Defence, etc.), common resources (Logs, Ores).
    *   **Wild Symbol:** A special symbol (e.g., a "Wildy" skull) that substitutes for other symbols to form winning combinations.
    *   **Scatter Symbol:** A unique symbol (e.g., a "Clue Scroll") that triggers bonus rounds or free spins regardless of its position on the payline.

### 2.2. Payout Lines and Combinations
*   **Configurable Paylines:** The game will support multiple configurable paylines (e.g., 10, 20, 25 lines) across the grid.
*   **Winning Combinations:** Payouts will be awarded for matching symbols on active paylines, typically from left to right.
*   **Payout Table:** A detailed payout table will define the multipliers for each winning combination, varying by symbol and number of matches.

### 2.3. Payout Logic, Multipliers, and Bonus Rounds
*   **Base Payouts:** Each symbol combination will have a predefined multiplier applied to the player's bet per line.
*   **Wild Multipliers:** Wild symbols may also apply a multiplier to wins they contribute to.
*   **Bonus Rounds (Triggered by Scatter):**
    *   **Free Spins:** A set number of free spins with potential for increased multipliers or sticky wild symbols.
    *   **Pick-Me Bonus:** Players choose from a selection of hidden items (e.g., treasure chests, mystery boxes) to reveal instant cash prizes or additional multipliers.
    *   **Mini-Game Bonus:** A simple OSRS-themed mini-game (e.g., a simplified "Barrows" chest opening) for extra rewards.
*   **Progressive Jackpot (Optional Future Feature):** A small percentage of each bet contributes to a growing jackpot, awarded randomly or through a specific rare combination.

## 3. User Customization & Variables

### 3.1. Autoplay Features
*   **Number of Autospins:** Users can set a specific number of spins to play automatically.
*   **Stop on Win:** Autoplay pauses if a win exceeds a user-defined amount.
*   **Stop on Loss:** Autoplay pauses if the session balance drops below a certain threshold or total losses exceed an amount.
*   **Stop on Bonus Round:** Autoplay pauses when a bonus round is triggered, allowing manual interaction.
*   **Bet Amount per Spin:** Configurable bet amount for autoplay sessions.

### 3.2. Cashout/Thresholds
*   **Auto-Cashout on Big Win:** Automatically transfer winnings above a certain threshold to the main account balance.
*   **Session Loss Limit:** Automatically stop playing if the total amount lost in a single session reaches a user-defined limit.
*   **Session Win Limit:** Automatically stop playing if the total amount won in a single session reaches a user-defined limit, encouraging profit-taking.

### 3.3. UI/UX Considerations
*   **High-Quality Animations:** Smooth and engaging animations for spinning reels, winning combinations, and bonus triggers, replicating the RuneChat Magic Slots feel.
*   **Sound Effects:** OSRS-style sound effects for spins, wins, and bonus events.
*   **Real-time Feedback:** Clear display of current bet, balance, last win, and active paylines.
*   **Dynamic Payout Table:** An interactive payout table that highlights winning lines and potential payouts.

## 4. Technical Implementation Notes
*   **Backend (FastAPI):**
    *   Endpoints for initiating spins, handling bets, and processing payouts (`/api/degensslots/spin`).
    *   Random number generation (RNG) for reel outcomes, ensuring fairness and provability.
    *   Logic for evaluating winning combinations, applying multipliers, and triggering bonus rounds.
    *   Storage of user game settings (autoplay, thresholds) in MongoDB.
    *   Integration with the platform's central balance and transaction system.
*   **Frontend (React):**
    *   Interactive slot machine interface with animated reels and symbols.
    *   User-friendly controls for setting bet amounts, activating autospins, and configuring thresholds.
    *   Visual effects for wins, bonus triggers, and special events.
    *   Display of game history and current session statistics.

## 5. Future Enhancements
*   **Themed Events:** Limited-time events with special symbols or increased payouts.
*   **Leaderboards:** Track biggest wins, most spins, etc.
*   **Achievements:** In-game achievements for reaching milestones or rare combinations.
*   **Customizable Skins:** Allow VIP users to change the appearance of the slot machine or symbols.
