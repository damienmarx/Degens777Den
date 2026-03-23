import React, { useState, useEffect, useRef } from 'react';
import { Spades, Hearts, Diamonds, Clubs, RotateCcw, Zap } from 'lucide-react';
import { toast } from 'sonner';

const BlackjackGame = ({ api, user, selectedCurrency, refreshWallet }) => {
  const [gameState, setGameState] = useState('betting'); // betting, playing, dealer, result
  const [betAmount, setBetAmount] = useState(0.0001);
  const [playerHand, setPlayerHand] = useState([]);
  const [dealerHand, setDealerHand] = useState([]);
  const [playerScore, setPlayerScore] = useState(0);
  const [dealerScore, setDealerScore] = useState(0);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [doubleDown, setDoubleDown] = useState(false);
  const animationRef = useRef(null);

  const suits = ['♠', '♥', '♦', '♣'];
  const ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K'];

  const calculateScore = (hand) => {
    let score = 0;
    let aces = 0;
    
    hand.forEach(card => {
      if (card.rank === 'A') {
        aces += 1;
        score += 11;
      } else if (['J', 'Q', 'K'].includes(card.rank)) {
        score += 10;
      } else {
        score += parseInt(card.rank);
      }
    });

    while (score > 21 && aces > 0) {
      score -= 10;
      aces -= 1;
    }

    return score;
  };

  const placeBet = async () => {
    if (!user) {
      toast.error('Please login to play');
      return;
    }
    if (betAmount <= 0) {
      toast.error('Invalid bet amount');
      return;
    }

    setIsProcessing(true);
    try {
      const res = await api.post('/games/bet', {
        game_type: 'blackjack',
        amount: betAmount,
        currency: selectedCurrency,
        params: { action: 'initial_deal' }
      });

      setPlayerHand(res.data.result.player_hand);
      setDealerHand(res.data.result.dealer_hand);
      setPlayerScore(calculateScore(res.data.result.player_hand));
      setDealerScore(calculateScore([res.data.result.dealer_hand[0]])); // Only show first dealer card
      setGameState('playing');
      setResult(null);
      setDoubleDown(false);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Bet failed');
    } finally {
      setIsProcessing(false);
    }
  };

  const hit = async () => {
    setIsProcessing(true);
    try {
      const res = await api.post('/games/bet', {
        game_type: 'blackjack',
        amount: betAmount,
        currency: selectedCurrency,
        params: { action: 'hit' }
      });

      const newHand = [...playerHand, res.data.result.new_card];
      setPlayerHand(newHand);
      const newScore = calculateScore(newHand);
      setPlayerScore(newScore);

      if (newScore > 21) {
        setGameState('result');
        setResult({ won: false, message: 'BUST! You went over 21.' });
        setHistory(prev => [{ action: 'bust', payout: 0 }, ...prev.slice(0, 9)]);
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Hit failed');
    } finally {
      setIsProcessing(false);
    }
  };

  const stand = async () => {
    setIsProcessing(true);
    try {
      const res = await api.post('/games/bet', {
        game_type: 'blackjack',
        amount: betAmount * (doubleDown ? 2 : 1),
        currency: selectedCurrency,
        params: { action: 'stand', double_down: doubleDown }
      });

      setDealerHand(res.data.result.dealer_hand);
      setDealerScore(calculateScore(res.data.result.dealer_hand));
      setGameState('result');

      const gameResult = res.data.result;
      setResult({
        won: gameResult.won,
        message: gameResult.message,
        payout: gameResult.payout
      });

      setHistory(prev => [
        { action: gameResult.message, payout: gameResult.payout },
        ...prev.slice(0, 9)
      ]);

      refreshWallet();

      if (gameResult.won) {
        toast.success(`Won ${gameResult.payout.toFixed(8)} ${selectedCurrency.toUpperCase()}!`);
      } else {
        toast.error('Dealer wins!');
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Stand failed');
    } finally {
      setIsProcessing(false);
    }
  };

  const doubleDownAction = async () => {
    if (playerHand.length !== 2) {
      toast.error('Can only double down on initial hand');
      return;
    }
    setDoubleDown(true);
    await hit();
  };

  const resetGame = () => {
    setGameState('betting');
    setPlayerHand([]);
    setDealerHand([]);
    setPlayerScore(0);
    setDealerScore(0);
    setResult(null);
    setDoubleDown(false);
  };

  const CardComponent = ({ card, hidden = false }) => {
    if (hidden) {
      return (
        <div className="card card-hidden">
          <div className="card-back">
            <div className="card-pattern"></div>
          </div>
        </div>
      );
    }

    const suitColor = ['♠', '♣'].includes(card.suit) ? 'black' : 'red';
    return (
      <div className={`card card-${suitColor}`}>
        <div className="card-rank">{card.rank}</div>
        <div className="card-suit">{card.suit}</div>
      </div>
    );
  };

  return (
    <div className="blackjack-game">
      <div className="blackjack-header">
        <h2>🎰 BLACKJACK SIDE TABLE</h2>
        <p>Professional Casino Experience</p>
      </div>

      <div className="blackjack-container">
        {/* Dealer Area */}
        <div className="dealer-area">
          <div className="area-label">DEALER</div>
          <div className="cards-display">
            {gameState === 'betting' ? (
              <div className="empty-state">Ready to deal</div>
            ) : (
              <>
                {dealerHand.map((card, idx) => (
                  <CardComponent
                    key={idx}
                    card={card}
                    hidden={gameState === 'playing' && idx === 1}
                  />
                ))}
              </>
            )}
          </div>
          {gameState !== 'betting' && (
            <div className="score-display">
              Score: <span className="score-value">{gameState === 'playing' ? dealerScore : dealerScore}</span>
            </div>
          )}
        </div>

        {/* Player Area */}
        <div className="player-area">
          <div className="area-label">PLAYER</div>
          <div className="cards-display">
            {gameState === 'betting' ? (
              <div className="empty-state">Place your bet</div>
            ) : (
              <>
                {playerHand.map((card, idx) => (
                  <CardComponent key={idx} card={card} />
                ))}
              </>
            )}
          </div>
          {gameState !== 'betting' && (
            <div className="score-display">
              Score: <span className={`score-value ${playerScore > 21 ? 'bust' : ''}`}>
                {playerScore}
              </span>
            </div>
          )}
        </div>

        {/* Result Display */}
        {result && (
          <div className={`result-display ${result.won ? 'win' : 'loss'}`}>
            <div className="result-message">{result.message}</div>
            {result.payout > 0 && (
              <div className="result-payout">
                +{result.payout.toFixed(8)} {selectedCurrency.toUpperCase()}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Betting Controls */}
      <div className="betting-section">
        {gameState === 'betting' && (
          <>
            <div className="bet-input-group">
              <label>Bet Amount</label>
              <input
                type="number"
                value={betAmount}
                onChange={(e) => setBetAmount(parseFloat(e.target.value) || 0)}
                placeholder="0.0001"
                step="0.0001"
                min="0.0001"
              />
            </div>
            <button
              className="btn btn-primary btn-large"
              onClick={placeBet}
              disabled={isProcessing}
            >
              <Zap size={20} />
              DEAL
            </button>
          </>
        )}

        {gameState === 'playing' && (
          <div className="action-buttons">
            <button
              className="btn btn-secondary"
              onClick={hit}
              disabled={isProcessing}
            >
              HIT
            </button>
            <button
              className="btn btn-secondary"
              onClick={stand}
              disabled={isProcessing}
            >
              STAND
            </button>
            {playerHand.length === 2 && (
              <button
                className="btn btn-secondary"
                onClick={doubleDownAction}
                disabled={isProcessing || doubleDown}
              >
                DOUBLE DOWN
              </button>
            )}
          </div>
        )}

        {gameState === 'result' && (
          <button
            className="btn btn-primary btn-large"
            onClick={resetGame}
          >
            <RotateCcw size={20} />
            NEW HAND
          </button>
        )}
      </div>

      {/* History */}
      <div className="game-history">
        <h3>Recent Hands</h3>
        <div className="history-list">
          {history.slice(0, 5).map((hand, idx) => (
            <div key={idx} className={`history-item ${hand.payout > 0 ? 'win' : 'loss'}`}>
              <span>{hand.action}</span>
              <span className="payout">
                {hand.payout > 0 ? '+' : ''}{hand.payout.toFixed(4)}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default BlackjackGame;
