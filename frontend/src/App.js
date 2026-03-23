import { useState, useEffect, createContext, useContext, useRef, useCallback } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, Link, useNavigate, Navigate, useLocation } from "react-router-dom";
import axios from "axios";
import { Toaster, toast } from "sonner";
import {
  Wallet, Menu, X, User, LogOut, Settings, MessageSquare, Send,
  ChevronRight, ChevronDown, Coins, Dices, Target, Trophy, Shield,
  Flame, Zap, Gift, TrendingUp, Clock, Users, Copy, Check, RefreshCw,
  Volume2, VolumeX, Eye, EyeOff, ArrowUp, ArrowDown, Circle, Play,
  Pause, RotateCcw, Home, Rocket, Star, Crown, Diamond
} from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// ==================== CONTEXTS ====================
const AuthContext = createContext(null);
const WalletContext = createContext(null);
const ChatContext = createContext(null);
const useAuth = () => useContext(AuthContext);
const useWallet = () => useContext(WalletContext);
const useChat = () => useContext(ChatContext);

// ==================== API ====================
const api = axios.create({ baseURL: API });
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// ==================== CONSTANTS ====================
const CURRENCIES = [
  { id: "btc", name: "Bitcoin", symbol: "BTC", icon: "₿", color: "#F7931A" },
  { id: "eth", name: "Ethereum", symbol: "ETH", icon: "Ξ", color: "#627EEA" },
  { id: "ltc", name: "Litecoin", symbol: "LTC", icon: "Ł", color: "#BFBBBB" },
  { id: "usdc", name: "USD Coin", symbol: "USDC", icon: "$", color: "#2775CA" },
  { id: "usdt", name: "Tether", symbol: "USDT", icon: "₮", color: "#26A17B" },
  { id: "osrs_gp", name: "OSRS Gold", symbol: "GP", icon: "🪙", color: "#FFC800" },
];

const VIP_TIERS = [
  { level: 0, name: "Bronze", color: "#CD7F32", wager: 0 },
  { level: 1, name: "Silver", color: "#C0C0C0", wager: 1000 },
  { level: 2, name: "Gold", color: "#FFD700", wager: 10000 },
  { level: 3, name: "Platinum", color: "#E5E4E2", wager: 50000 },
  { level: 4, name: "Dragon", color: "#FF2346", wager: 250000 },
];

// ==================== UTILITY FUNCTIONS ====================
const formatBalance = (balance, currency) => {
  if (currency === "osrs_gp") {
    if (balance >= 1000000000) return (balance / 1000000000).toFixed(2) + "B";
    if (balance >= 1000000) return (balance / 1000000).toFixed(2) + "M";
    if (balance >= 1000) return (balance / 1000).toFixed(2) + "K";
    return balance.toFixed(0);
  }
  return balance.toFixed(8);
};

const copyToClipboard = (text) => {
  navigator.clipboard.writeText(text);
  toast.success("Copied to clipboard");
};

// ==================== SIDEBAR COMPONENT ====================
const Sidebar = ({ collapsed, setCollapsed }) => {
  const location = useLocation();
  const { user } = useAuth();
  
  const games = [
    { path: "/dice", name: "Dice", icon: Dices },
    { path: "/keno", name: "Keno", icon: Target },
    { path: "/crash", name: "Crash", icon: Rocket },
    { path: "/wheel", name: "Lucky Wheel", icon: Star },
    { path: "/plinko", name: "Plinko", icon: Circle },
    { path: "/limbo", name: "Limbo", icon: TrendingUp },
  ];

  return (
    <aside className={`sidebar ${collapsed ? "collapsed" : ""}`} data-testid="sidebar">
      <div className="sidebar-header">
        <Link to="/" className="logo" data-testid="logo">
          <Diamond className="logo-icon" />
          {!collapsed && <span className="logo-text">DEGEN'S DEN</span>}
        </Link>
        <button onClick={() => setCollapsed(!collapsed)} className="collapse-btn" data-testid="collapse-sidebar">
          {collapsed ? <ChevronRight /> : <X />}
        </button>
      </div>

      <nav className="sidebar-nav">
        <Link to="/" className={`nav-item ${location.pathname === "/" ? "active" : ""}`} data-testid="nav-home">
          <Home className="nav-icon" />
          {!collapsed && <span>Home</span>}
        </Link>

        <div className="nav-section">
          {!collapsed && <span className="nav-section-title">GAMES</span>}
          {games.map((game) => (
            <Link
              key={game.path}
              to={game.path}
              className={`nav-item ${location.pathname === game.path ? "active" : ""}`}
              data-testid={`nav-${game.path.slice(1)}`}
            >
              <game.icon className="nav-icon" />
              {!collapsed && <span>{game.name}</span>}
            </Link>
          ))}
        </div>

        <div className="nav-section">
          {!collapsed && <span className="nav-section-title">ACCOUNT</span>}
          <Link to="/wallet" className={`nav-item ${location.pathname === "/wallet" ? "active" : ""}`} data-testid="nav-wallet">
            <Wallet className="nav-icon" />
            {!collapsed && <span>Wallet</span>}
          </Link>
          <Link to="/referral" className={`nav-item ${location.pathname === "/referral" ? "active" : ""}`} data-testid="nav-referral">
            <Gift className="nav-icon" />
            {!collapsed && <span>Refer a Degen</span>}
          </Link>
          <Link to="/vip" className={`nav-item ${location.pathname === "/vip" ? "active" : ""}`} data-testid="nav-vip">
            <Crown className="nav-icon" />
            {!collapsed && <span>VIP Club</span>}
          </Link>
          <Link to="/provably-fair" className={`nav-item ${location.pathname === "/provably-fair" ? "active" : ""}`} data-testid="nav-fair">
            <Shield className="nav-icon" />
            {!collapsed && <span>Provably Fair</span>}
          </Link>
          <Link to="/leaderboard" className={`nav-item ${location.pathname === "/leaderboard" ? "active" : ""}`} data-testid="nav-leaderboard">
            <Trophy className="nav-icon" />
            {!collapsed && <span>Leaderboard</span>}
          </Link>
        </div>

        {user?.is_admin && (
          <div className="nav-section">
            {!collapsed && <span className="nav-section-title">ADMIN</span>}
            <Link to="/admin" className={`nav-item ${location.pathname === "/admin" ? "active" : ""}`} data-testid="nav-admin">
              <Settings className="nav-icon" />
              {!collapsed && <span>Dashboard</span>}
            </Link>
          </div>
        )}
      </nav>
    </aside>
  );
};

// ==================== HEADER COMPONENT ====================
const Header = ({ toggleChat }) => {
  const { user, logout } = useAuth();
  const { wallet, selectedCurrency, setSelectedCurrency } = useWallet();
  const [showCurrencyDropdown, setShowCurrencyDropdown] = useState(false);
  const navigate = useNavigate();

  const currentBalance = selectedCurrency === "osrs_gp" 
    ? wallet?.osrs_gp || 0 
    : wallet?.balances?.find(b => b.currency === selectedCurrency)?.balance || 0;

  const currencyData = CURRENCIES.find(c => c.id === selectedCurrency);

  return (
    <header className="header" data-testid="header">
      <div className="header-left">
        {user && (
          <div className="balance-display" data-testid="balance-display">
            <div className="currency-selector" onClick={() => setShowCurrencyDropdown(!showCurrencyDropdown)}>
              <span className="currency-icon" style={{ color: currencyData?.color }}>{currencyData?.icon}</span>
              <span className="balance-amount">{formatBalance(currentBalance, selectedCurrency)}</span>
              <ChevronDown className="dropdown-arrow" />
              
              {showCurrencyDropdown && (
                <div className="currency-dropdown" data-testid="currency-dropdown">
                  {CURRENCIES.map(curr => {
                    const bal = curr.id === "osrs_gp" 
                      ? wallet?.osrs_gp || 0 
                      : wallet?.balances?.find(b => b.currency === curr.id)?.balance || 0;
                    return (
                      <div
                        key={curr.id}
                        className={`currency-option ${selectedCurrency === curr.id ? "active" : ""}`}
                        onClick={(e) => { e.stopPropagation(); setSelectedCurrency(curr.id); setShowCurrencyDropdown(false); }}
                        data-testid={`currency-${curr.id}`}
                      >
                        <span className="currency-icon" style={{ color: curr.color }}>{curr.icon}</span>
                        <span className="currency-name">{curr.symbol}</span>
                        <span className="currency-balance">{formatBalance(bal, curr.id)}</span>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
            <button onClick={() => navigate("/wallet")} className="deposit-btn" data-testid="deposit-btn">
              <Wallet size={16} /> Deposit
            </button>
          </div>
        )}
      </div>

      <div className="header-right">
        <button onClick={toggleChat} className="chat-toggle-btn" data-testid="chat-toggle">
          <MessageSquare size={20} />
        </button>
        
        {user ? (
          <div className="user-menu">
            <Link to="/profile" className="user-info" data-testid="user-profile">
              <div className="user-avatar">{user.username[0].toUpperCase()}</div>
              <span className="user-name">{user.username}</span>
            </Link>
            <button onClick={logout} className="logout-btn" data-testid="logout-btn">
              <LogOut size={18} />
            </button>
          </div>
        ) : (
          <div className="auth-buttons">
            <Link to="/login" className="login-btn" data-testid="login-btn">Login</Link>
            <Link to="/register" className="register-btn" data-testid="register-btn">Register</Link>
          </div>
        )}
      </div>
    </header>
  );
};

// ==================== CHAT COMPONENT ====================
const ChatPanel = ({ isOpen, onClose }) => {
  const { messages, sendMessage, connected } = useChat();
  const { user } = useAuth();
  const [input, setInput] = useState("");
  const [showTip, setShowTip] = useState(false);
  const [tipAmount, setTipAmount] = useState("");
  const [tipRecipient, setTipRecipient] = useState("");
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = (e) => {
    e.preventDefault();
    if (!input.trim() || !user) return;
    sendMessage(input);
    setInput("");
  };

  const handleTip = async () => {
    if (!tipRecipient || !tipAmount) return;
    try {
      await api.post("/chat/tip", { recipient_username: tipRecipient, amount: parseFloat(tipAmount), currency: "btc" });
      toast.success("Tip sent!");
      setShowTip(false);
      setTipAmount("");
      setTipRecipient("");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Tip failed");
    }
  };

  return (
    <aside className={`chat-panel ${isOpen ? "open" : ""}`} data-testid="chat-panel">
      <div className="chat-header">
        <div className="chat-title">
          <MessageSquare size={18} />
          <span>Global Chat</span>
          <span className={`connection-status ${connected ? "online" : "offline"}`}></span>
        </div>
        <button onClick={onClose} className="close-chat" data-testid="close-chat"><X size={18} /></button>
      </div>

      <div className="chat-messages" data-testid="chat-messages">
        {messages.map((msg, i) => (
          <div key={msg.id || i} className={`chat-message ${msg.message_type}`} data-testid={`message-${i}`}>
            {msg.message_type === "rain" && <div className="rain-alert"><Gift size={16} /> RAIN!</div>}
            {msg.message_type === "tip" && <div className="tip-alert"><Coins size={16} /> TIP</div>}
            <span className="message-user">{msg.username}:</span>
            <span className="message-text">{msg.message}</span>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {user ? (
        <div className="chat-input-area">
          {showTip ? (
            <div className="tip-form">
              <input placeholder="Username" value={tipRecipient} onChange={e => setTipRecipient(e.target.value)} data-testid="tip-recipient" />
              <input placeholder="Amount (BTC)" type="number" value={tipAmount} onChange={e => setTipAmount(e.target.value)} data-testid="tip-amount" />
              <button onClick={handleTip} className="send-tip-btn" data-testid="send-tip">Send</button>
              <button onClick={() => setShowTip(false)} className="cancel-tip-btn">Cancel</button>
            </div>
          ) : (
            <form onSubmit={handleSend} className="chat-form">
              <button type="button" onClick={() => setShowTip(true)} className="tip-btn" data-testid="open-tip"><Gift size={16} /></button>
              <input
                value={input}
                onChange={e => setInput(e.target.value)}
                placeholder="Type a message..."
                maxLength={200}
                data-testid="chat-input"
              />
              <button type="submit" className="send-btn" data-testid="send-message"><Send size={16} /></button>
            </form>
          )}
        </div>
      ) : (
        <div className="chat-login-prompt">Login to chat</div>
      )}
    </aside>
  );
};

// ==================== GAME CONTROLS COMPONENT ====================
const GameControls = ({ betAmount, setBetAmount, onBet, isPlaying, disabled }) => {
  const { wallet, selectedCurrency } = useWallet();
  const currentBalance = selectedCurrency === "osrs_gp" 
    ? wallet?.osrs_gp || 0 
    : wallet?.balances?.find(b => b.currency === selectedCurrency)?.balance || 0;

  const handleHalf = () => setBetAmount(prev => Math.max(0, prev / 2));
  const handleDouble = () => setBetAmount(prev => Math.min(currentBalance, prev * 2));
  const handleMax = () => setBetAmount(currentBalance);

  return (
    <div className="game-controls" data-testid="game-controls">
      <div className="bet-input-group">
        <label>Bet Amount</label>
        <div className="bet-input-wrapper">
          <input
            type="number"
            value={betAmount}
            onChange={e => setBetAmount(Math.max(0, parseFloat(e.target.value) || 0))}
            disabled={isPlaying}
            data-testid="bet-amount-input"
          />
          <div className="bet-modifiers">
            <button onClick={handleHalf} disabled={isPlaying} data-testid="bet-half">½</button>
            <button onClick={handleDouble} disabled={isPlaying} data-testid="bet-double">2×</button>
            <button onClick={handleMax} disabled={isPlaying} data-testid="bet-max">MAX</button>
          </div>
        </div>
      </div>
      <button 
        onClick={onBet} 
        disabled={disabled || isPlaying || betAmount <= 0}
        className="bet-button"
        data-testid="bet-button"
      >
        {isPlaying ? "PLAYING..." : "BET"}
      </button>
    </div>
  );
};

// ==================== DICE GAME ====================
const DicePage = () => {
  const { user } = useAuth();
  const { selectedCurrency, refreshWallet } = useWallet();
  const navigate = useNavigate();
  
  const [betAmount, setBetAmount] = useState(0.0001);
  const [target, setTarget] = useState(50);
  const [isOver, setIsOver] = useState(true);
  const [isPlaying, setIsPlaying] = useState(false);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  
  // Auto bet state
  const [autoBetEnabled, setAutoBetEnabled] = useState(false);
  const [autoBetCount, setAutoBetCount] = useState(0);
  const [maxAutoBets, setMaxAutoBets] = useState(10);
  const [stopOnWin, setStopOnWin] = useState(0);
  const [stopOnLoss, setStopOnLoss] = useState(0);
  const [onWinIncrease, setOnWinIncrease] = useState(0);
  const [onLossIncrease, setOnLossIncrease] = useState(0);
  const autoBetRef = useRef(false);

  const multiplier = isOver ? (99 / (100 - target)).toFixed(4) : (99 / target).toFixed(4);
  const winChance = isOver ? (100 - target).toFixed(2) : target.toFixed(2);

  const placeBet = async () => {
    if (!user) { navigate("/login"); return; }
    setIsPlaying(true);
    try {
      const res = await api.post("/games/bet", {
        game_type: "dice",
        amount: betAmount,
        currency: selectedCurrency,
        params: { target, over: isOver }
      });
      setResult(res.data);
      setHistory(prev => [res.data, ...prev.slice(0, 19)]);
      refreshWallet();
      
      if (res.data.won) {
        toast.success(`Won ${res.data.payout.toFixed(8)} ${selectedCurrency.toUpperCase()}!`);
      }
      
      return res.data;
    } catch (err) {
      toast.error(err.response?.data?.detail || "Bet failed");
      return null;
    } finally {
      setIsPlaying(false);
    }
  };

  const runAutoBet = useCallback(async () => {
    if (!autoBetRef.current) return;
    
    let currentBet = betAmount;
    let totalProfit = 0;
    let count = 0;
    
    while (autoBetRef.current && count < maxAutoBets) {
      setBetAmount(currentBet);
      const res = await placeBet();
      if (!res) break;
      
      totalProfit += res.won ? res.payout - res.amount : -res.amount;
      count++;
      setAutoBetCount(count);
      
      // Stop conditions
      if (stopOnWin > 0 && totalProfit >= stopOnWin) break;
      if (stopOnLoss > 0 && totalProfit <= -stopOnLoss) break;
      
      // Adjust bet
      if (res.won && onWinIncrease > 0) {
        currentBet = currentBet * (1 + onWinIncrease / 100);
      } else if (!res.won && onLossIncrease > 0) {
        currentBet = currentBet * (1 + onLossIncrease / 100);
      }
      
      await new Promise(r => setTimeout(r, 500));
    }
    
    autoBetRef.current = false;
    setAutoBetEnabled(false);
  }, [betAmount, maxAutoBets, stopOnWin, stopOnLoss, onWinIncrease, onLossIncrease]);

  const toggleAutoBet = () => {
    if (autoBetEnabled) {
      autoBetRef.current = false;
      setAutoBetEnabled(false);
    } else {
      autoBetRef.current = true;
      setAutoBetEnabled(true);
      setAutoBetCount(0);
      runAutoBet();
    }
  };

  return (
    <div className="game-page dice-page" data-testid="dice-page">
      <div className="game-main">
        <div className="game-canvas">
          <div className="dice-display">
            <div className={`dice-result ${result?.won ? "win" : result ? "lose" : ""}`}>
              {result ? result.result.roll.toFixed(2) : "00.00"}
            </div>
            <div className="dice-slider-container">
              <input
                type="range"
                min="1"
                max="98"
                value={target}
                onChange={e => setTarget(parseInt(e.target.value))}
                className={`dice-slider ${isOver ? "over" : "under"}`}
                data-testid="dice-slider"
              />
              <div className="slider-markers">
                <span>0</span>
                <span className="target-marker" style={{ left: `${target}%` }}>{target}</span>
                <span>100</span>
              </div>
            </div>
            <div className="dice-direction">
              <button 
                className={`direction-btn ${!isOver ? "active" : ""}`} 
                onClick={() => setIsOver(false)}
                data-testid="roll-under"
              >
                <ArrowDown /> Roll Under
              </button>
              <button 
                className={`direction-btn ${isOver ? "active" : ""}`} 
                onClick={() => setIsOver(true)}
                data-testid="roll-over"
              >
                <ArrowUp /> Roll Over
              </button>
            </div>
          </div>
          
          <div className="dice-stats">
            <div className="stat-box">
              <span className="stat-label">Multiplier</span>
              <span className="stat-value">{multiplier}×</span>
            </div>
            <div className="stat-box">
              <span className="stat-label">Win Chance</span>
              <span className="stat-value">{winChance}%</span>
            </div>
          </div>
        </div>

        <div className="game-betting">
          <GameControls
            betAmount={betAmount}
            setBetAmount={setBetAmount}
            onBet={placeBet}
            isPlaying={isPlaying}
            disabled={!user}
          />
          
          <div className="auto-bet-section">
            <div className="auto-bet-header">
              <span>Auto Bet</span>
              <button 
                onClick={toggleAutoBet} 
                className={`auto-bet-toggle ${autoBetEnabled ? "active" : ""}`}
                data-testid="auto-bet-toggle"
              >
                {autoBetEnabled ? <Pause /> : <Play />}
              </button>
            </div>
            {autoBetEnabled && <div className="auto-bet-count">Bets: {autoBetCount}/{maxAutoBets}</div>}
            <div className="auto-bet-options">
              <div className="auto-bet-input">
                <label>Number of Bets</label>
                <input type="number" value={maxAutoBets} onChange={e => setMaxAutoBets(parseInt(e.target.value))} data-testid="max-auto-bets" />
              </div>
              <div className="auto-bet-input">
                <label>On Win Increase %</label>
                <input type="number" value={onWinIncrease} onChange={e => setOnWinIncrease(parseFloat(e.target.value))} data-testid="on-win-increase" />
              </div>
              <div className="auto-bet-input">
                <label>On Loss Increase %</label>
                <input type="number" value={onLossIncrease} onChange={e => setOnLossIncrease(parseFloat(e.target.value))} data-testid="on-loss-increase" />
              </div>
              <div className="auto-bet-input">
                <label>Stop on Win</label>
                <input type="number" value={stopOnWin} onChange={e => setStopOnWin(parseFloat(e.target.value))} data-testid="stop-on-win" />
              </div>
              <div className="auto-bet-input">
                <label>Stop on Loss</label>
                <input type="number" value={stopOnLoss} onChange={e => setStopOnLoss(parseFloat(e.target.value))} data-testid="stop-on-loss" />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="game-history">
        <h3>Recent Bets</h3>
        <div className="history-list">
          {history.map((bet, i) => (
            <div key={bet.id || i} className={`history-item ${bet.won ? "win" : "lose"}`}>
              <span className="history-roll">{bet.result.roll.toFixed(2)}</span>
              <span className={`history-result ${bet.won ? "win" : "lose"}`}>
                {bet.won ? `+${bet.payout.toFixed(8)}` : `-${bet.amount.toFixed(8)}`}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// ==================== KENO GAME ====================
const KenoPage = () => {
  const { user } = useAuth();
  const { selectedCurrency, refreshWallet } = useWallet();
  const navigate = useNavigate();
  
  const [betAmount, setBetAmount] = useState(0.0001);
  const [selected, setSelected] = useState([]);
  const [drawn, setDrawn] = useState([]);
  const [hits, setHits] = useState([]);
  const [isPlaying, setIsPlaying] = useState(false);
  const [result, setResult] = useState(null);

  const KENO_PAYOUTS = { 0: 0, 1: 0, 2: 1, 3: 2, 4: 5, 5: 15, 6: 50, 7: 200, 8: 500, 9: 1000, 10: 5000 };

  const toggleNumber = (num) => {
    if (isPlaying) return;
    if (selected.includes(num)) {
      setSelected(selected.filter(n => n !== num));
    } else if (selected.length < 10) {
      setSelected([...selected, num]);
    }
  };

  const clearSelection = () => { setSelected([]); setDrawn([]); setHits([]); setResult(null); };

  const quickPick = () => {
    const picks = [];
    while (picks.length < 10) {
      const num = Math.floor(Math.random() * 40) + 1;
      if (!picks.includes(num)) picks.push(num);
    }
    setSelected(picks);
  };

  const placeBet = async () => {
    if (!user) { navigate("/login"); return; }
    if (selected.length === 0) { toast.error("Select at least one number"); return; }
    
    setIsPlaying(true);
    setDrawn([]);
    setHits([]);
    
    try {
      const res = await api.post("/games/bet", {
        game_type: "keno",
        amount: betAmount,
        currency: selectedCurrency,
        params: { selected }
      });
      
      // Animate drawing
      const drawnNums = res.data.result.drawn_numbers;
      for (let i = 0; i < drawnNums.length; i++) {
        await new Promise(r => setTimeout(r, 200));
        setDrawn(prev => [...prev, drawnNums[i]]);
        if (selected.includes(drawnNums[i])) {
          setHits(prev => [...prev, drawnNums[i]]);
        }
      }
      
      setResult(res.data);
      refreshWallet();
      
      if (res.data.won) {
        toast.success(`${res.data.result.hits} hits! Won ${res.data.payout.toFixed(8)}!`);
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || "Bet failed");
    } finally {
      setIsPlaying(false);
    }
  };

  return (
    <div className="game-page keno-page" data-testid="keno-page">
      <div className="game-main">
        <div className="game-canvas">
          <div className="keno-board">
            {Array.from({ length: 40 }, (_, i) => i + 1).map(num => (
              <button
                key={num}
                onClick={() => toggleNumber(num)}
                className={`keno-cell 
                  ${selected.includes(num) ? "selected" : ""} 
                  ${drawn.includes(num) ? "drawn" : ""} 
                  ${hits.includes(num) ? "hit" : ""}`}
                disabled={isPlaying}
                data-testid={`keno-cell-${num}`}
              >
                {num}
              </button>
            ))}
          </div>
          
          <div className="keno-info">
            <div className="keno-stats">
              <div className="stat-box">
                <span className="stat-label">Selected</span>
                <span className="stat-value">{selected.length}/10</span>
              </div>
              <div className="stat-box">
                <span className="stat-label">Hits</span>
                <span className="stat-value win">{hits.length}</span>
              </div>
              <div className="stat-box">
                <span className="stat-label">Potential Win</span>
                <span className="stat-value">{(betAmount * KENO_PAYOUTS[selected.length]).toFixed(8)}</span>
              </div>
            </div>
            
            <div className="keno-actions">
              <button onClick={quickPick} disabled={isPlaying} className="quick-pick-btn" data-testid="quick-pick">
                <Zap /> Quick Pick
              </button>
              <button onClick={clearSelection} disabled={isPlaying} className="clear-btn" data-testid="clear-selection">
                <RotateCcw /> Clear
              </button>
            </div>
          </div>
        </div>

        <div className="game-betting">
          <GameControls
            betAmount={betAmount}
            setBetAmount={setBetAmount}
            onBet={placeBet}
            isPlaying={isPlaying}
            disabled={!user || selected.length === 0}
          />
          
          <div className="keno-paytable">
            <h4>Paytable (10 picks)</h4>
            <div className="paytable-grid">
              {Object.entries(KENO_PAYOUTS).map(([hits, payout]) => (
                <div key={hits} className="paytable-row">
                  <span>{hits} hits</span>
                  <span>{payout}×</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// ==================== CRASH GAME ====================
const CrashPage = () => {
  const { user } = useAuth();
  const { selectedCurrency, refreshWallet } = useWallet();
  const navigate = useNavigate();
  
  const [betAmount, setBetAmount] = useState(0.0001);
  const [cashOutTarget, setCashOutTarget] = useState(2.0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentMultiplier, setCurrentMultiplier] = useState(1.0);
  const [crashed, setCrashed] = useState(false);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const animationRef = useRef(null);

  const placeBet = async () => {
    if (!user) { navigate("/login"); return; }
    
    setIsPlaying(true);
    setCrashed(false);
    setCurrentMultiplier(1.0);
    
    try {
      const res = await api.post("/games/bet", {
        game_type: "crash",
        amount: betAmount,
        currency: selectedCurrency,
        params: { cash_out: cashOutTarget }
      });
      
      // Animate crash
      const crashPoint = res.data.result.crash_point;
      const startTime = Date.now();
      const duration = Math.min(crashPoint * 1000, 10000); // Max 10 seconds
      
      const animate = () => {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const currentMult = 1 + (crashPoint - 1) * progress;
        
        setCurrentMultiplier(parseFloat(currentMult.toFixed(2)));
        
        if (progress < 1) {
          animationRef.current = requestAnimationFrame(animate);
        } else {
          setCrashed(true);
          setResult(res.data);
          setHistory(prev => [{ multiplier: crashPoint, won: res.data.won }, ...prev.slice(0, 19)]);
          refreshWallet();
          
          if (res.data.won) {
            toast.success(`Cashed out at ${cashOutTarget}×! Won ${res.data.payout.toFixed(8)}!`);
          } else {
            toast.error(`Crashed at ${crashPoint}×`);
          }
          setIsPlaying(false);
        }
      };
      
      animationRef.current = requestAnimationFrame(animate);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Bet failed");
      setIsPlaying(false);
    }
  };

  useEffect(() => {
    return () => {
      if (animationRef.current) cancelAnimationFrame(animationRef.current);
    };
  }, []);

  return (
    <div className="game-page crash-page" data-testid="crash-page">
      <div className="game-main">
        <div className="game-canvas crash-canvas">
          <div className={`crash-display ${crashed ? "crashed" : ""}`}>
            <div className="crash-rocket">
              <Rocket className={`rocket-icon ${isPlaying && !crashed ? "flying" : ""}`} />
              {isPlaying && !crashed && <div className="rocket-flames"><Flame /><Flame /><Flame /></div>}
            </div>
            <div className={`crash-multiplier ${crashed ? "crashed" : result?.won ? "cashed" : ""}`}>
              {currentMultiplier.toFixed(2)}×
            </div>
            {crashed && <div className="crash-explosion">CRASHED!</div>}
            {result?.won && <div className="cash-out-indicator">CASHED OUT!</div>}
          </div>
          
          <div className="crash-history">
            {history.map((h, i) => (
              <span key={i} className={`crash-history-item ${h.multiplier >= 2 ? "high" : "low"}`}>
                {h.multiplier.toFixed(2)}×
              </span>
            ))}
          </div>
        </div>

        <div className="game-betting">
          <div className="cash-out-input">
            <label>Auto Cash Out At</label>
            <input
              type="number"
              value={cashOutTarget}
              onChange={e => setCashOutTarget(Math.max(1.01, parseFloat(e.target.value) || 1.01))}
              step="0.1"
              min="1.01"
              disabled={isPlaying}
              data-testid="cash-out-input"
            />
          </div>
          
          <GameControls
            betAmount={betAmount}
            setBetAmount={setBetAmount}
            onBet={placeBet}
            isPlaying={isPlaying}
            disabled={!user}
          />
          
          <div className="potential-win">
            <span>Potential Win:</span>
            <span className="win-amount">{(betAmount * cashOutTarget).toFixed(8)}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

// ==================== LUCKY WHEEL GAME ====================
const WheelPage = () => {
  const { user } = useAuth();
  const { selectedCurrency, refreshWallet } = useWallet();
  const navigate = useNavigate();
  
  const [betAmount, setBetAmount] = useState(0.0001);
  const [isSpinning, setIsSpinning] = useState(false);
  const [rotation, setRotation] = useState(0);
  const [result, setResult] = useState(null);
  
  const SEGMENTS = [0, 2, 0, 3.5, 0, 2, 0, 7, 0, 2, 0, 3.5, 0, 2, 0, 21, 0, 2, 0, 3.5];
  const SEGMENT_COLORS = SEGMENTS.map(s => s === 0 ? "#1A1A22" : s === 21 ? "#E0FF00" : s === 7 ? "#00FFA3" : s >= 3 ? "#00E0FF" : "#FF2346");

  const spin = async () => {
    if (!user) { navigate("/login"); return; }
    
    setIsSpinning(true);
    
    try {
      const res = await api.post("/games/bet", {
        game_type: "wheel",
        amount: betAmount,
        currency: selectedCurrency,
        params: {}
      });
      
      const segment = res.data.result.segment;
      const segmentAngle = 360 / SEGMENTS.length;
      const targetRotation = rotation + 1440 + (SEGMENTS.length - segment) * segmentAngle + segmentAngle / 2;
      
      setRotation(targetRotation);
      
      setTimeout(() => {
        setResult(res.data);
        setIsSpinning(false);
        refreshWallet();
        
        if (res.data.won) {
          toast.success(`${res.data.multiplier}× multiplier! Won ${res.data.payout.toFixed(8)}!`);
        } else {
          toast.error("Better luck next time!");
        }
      }, 5000);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Spin failed");
      setIsSpinning(false);
    }
  };

  return (
    <div className="game-page wheel-page" data-testid="wheel-page">
      <div className="game-main">
        <div className="game-canvas wheel-canvas">
          <div className="wheel-container">
            <div className="wheel-pointer">
              <ChevronDown size={40} />
            </div>
            <div 
              className="wheel" 
              style={{ transform: `rotate(${rotation}deg)`, transition: isSpinning ? "transform 5s cubic-bezier(0.25, 1, 0.5, 1)" : "none" }}
            >
              <div className="wheel-center">
                <Diamond className="goat-icon" />
                <Coins className="money-icon" />
              </div>
              {SEGMENTS.map((seg, i) => (
                <div
                  key={i}
                  className="wheel-segment"
                  style={{
                    transform: `rotate(${i * (360 / SEGMENTS.length)}deg)`,
                    backgroundColor: SEGMENT_COLORS[i]
                  }}
                >
                  <span className="segment-value">{seg}×</span>
                </div>
              ))}
            </div>
          </div>
          
          {result && (
            <div className={`wheel-result ${result.won ? "win" : "lose"}`}>
              {result.multiplier}×
            </div>
          )}
        </div>

        <div className="game-betting">
          <GameControls
            betAmount={betAmount}
            setBetAmount={setBetAmount}
            onBet={spin}
            isPlaying={isSpinning}
            disabled={!user}
          />
          
          <div className="wheel-legend">
            <h4>Multipliers</h4>
            <div className="legend-items">
              <span className="legend-item" style={{ color: "#E0FF00" }}>21×</span>
              <span className="legend-item" style={{ color: "#00FFA3" }}>7×</span>
              <span className="legend-item" style={{ color: "#00E0FF" }}>3.5×</span>
              <span className="legend-item" style={{ color: "#FF2346" }}>2×</span>
              <span className="legend-item" style={{ color: "#52525B" }}>0×</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// ==================== PLINKO GAME ====================
const PlinkoPage = () => {
  const { user } = useAuth();
  const { selectedCurrency, refreshWallet } = useWallet();
  const navigate = useNavigate();
  
  const [betAmount, setBetAmount] = useState(0.0001);
  const [isDropping, setIsDropping] = useState(false);
  const [ballPath, setBallPath] = useState([]);
  const [result, setResult] = useState(null);
  
  const MULTIPLIERS = [110, 41, 10, 5, 3, 1.5, 1, 0.5, 0.3, 0.5, 1, 1.5, 3, 5, 10, 41, 110];

  const dropBall = async () => {
    if (!user) { navigate("/login"); return; }
    
    setIsDropping(true);
    setBallPath([]);
    
    try {
      const res = await api.post("/games/bet", {
        game_type: "plinko",
        amount: betAmount,
        currency: selectedCurrency,
        params: {}
      });
      
      // Animate path
      const path = res.data.result.path;
      for (let i = 0; i < path.length; i++) {
        await new Promise(r => setTimeout(r, 100));
        setBallPath(prev => [...prev, path[i]]);
      }
      
      setResult(res.data);
      refreshWallet();
      
      toast.success(`Landed on ${res.data.multiplier}×! ${res.data.won ? `Won ${res.data.payout.toFixed(8)}!` : ""}`);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Drop failed");
    } finally {
      setIsDropping(false);
    }
  };

  // Calculate ball position based on path
  const getBallPosition = () => {
    let x = 50; // Start at center
    ballPath.forEach(dir => {
      x += dir === "L" ? -3 : 3;
    });
    return { x, y: ballPath.length * 6 };
  };

  const ballPos = getBallPosition();

  return (
    <div className="game-page plinko-page" data-testid="plinko-page">
      <div className="game-main">
        <div className="game-canvas plinko-canvas">
          <div className="plinko-board">
            {/* Pegs */}
            {Array.from({ length: 16 }, (_, row) => (
              <div key={row} className="plinko-row">
                {Array.from({ length: row + 3 }, (_, col) => (
                  <div key={col} className="plinko-peg" />
                ))}
              </div>
            ))}
            
            {/* Ball */}
            {isDropping && (
              <div 
                className="plinko-ball"
                style={{ left: `${ballPos.x}%`, top: `${ballPos.y}%` }}
              />
            )}
            
            {/* Buckets */}
            <div className="plinko-buckets">
              {MULTIPLIERS.map((mult, i) => (
                <div 
                  key={i} 
                  className={`plinko-bucket ${result?.result?.position === i ? "active" : ""}`}
                  style={{ 
                    backgroundColor: mult >= 10 ? "#E0FF00" : mult >= 3 ? "#00FFA3" : mult >= 1 ? "#00E0FF" : "#FF2346",
                    opacity: mult >= 1 ? 1 : 0.5
                  }}
                >
                  {mult}×
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="game-betting">
          <GameControls
            betAmount={betAmount}
            setBetAmount={setBetAmount}
            onBet={dropBall}
            isPlaying={isDropping}
            disabled={!user}
          />
        </div>
      </div>
    </div>
  );
};

// ==================== LIMBO GAME ====================
const LimboPage = () => {
  const { user } = useAuth();
  const { selectedCurrency, refreshWallet } = useWallet();
  const navigate = useNavigate();
  
  const [betAmount, setBetAmount] = useState(0.0001);
  const [targetMultiplier, setTargetMultiplier] = useState(2.0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);

  const winChance = Math.min(99, (99 / targetMultiplier)).toFixed(2);

  const placeBet = async () => {
    if (!user) { navigate("/login"); return; }
    
    setIsPlaying(true);
    
    try {
      const res = await api.post("/games/bet", {
        game_type: "limbo",
        amount: betAmount,
        currency: selectedCurrency,
        params: { target: targetMultiplier }
      });
      
      setResult(res.data);
      setHistory(prev => [res.data, ...prev.slice(0, 19)]);
      refreshWallet();
      
      if (res.data.won) {
        toast.success(`Won ${res.data.payout.toFixed(8)}!`);
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || "Bet failed");
    } finally {
      setIsPlaying(false);
    }
  };

  return (
    <div className="game-page limbo-page" data-testid="limbo-page">
      <div className="game-main">
        <div className="game-canvas limbo-canvas">
          <div className={`limbo-display ${result?.won ? "win" : result ? "lose" : ""}`}>
            <div className="limbo-result">
              {result ? result.result.target.toFixed(2) : "?.??"}×
            </div>
            <div className="limbo-target">
              Target: {targetMultiplier.toFixed(2)}×
            </div>
          </div>
          
          <div className="limbo-history">
            {history.map((h, i) => (
              <span key={i} className={`limbo-history-item ${h.won ? "win" : "lose"}`}>
                {h.result.target.toFixed(2)}×
              </span>
            ))}
          </div>
        </div>

        <div className="game-betting">
          <div className="target-input">
            <label>Target Multiplier</label>
            <input
              type="number"
              value={targetMultiplier}
              onChange={e => setTargetMultiplier(Math.max(1.01, parseFloat(e.target.value) || 1.01))}
              step="0.1"
              min="1.01"
              disabled={isPlaying}
              data-testid="target-multiplier"
            />
            <div className="target-quick-picks">
              {[1.5, 2, 5, 10, 100].map(m => (
                <button key={m} onClick={() => setTargetMultiplier(m)} disabled={isPlaying}>{m}×</button>
              ))}
            </div>
          </div>
          
          <div className="limbo-stats">
            <div className="stat-box">
              <span className="stat-label">Win Chance</span>
              <span className="stat-value">{winChance}%</span>
            </div>
            <div className="stat-box">
              <span className="stat-label">Profit on Win</span>
              <span className="stat-value">{(betAmount * (targetMultiplier - 1)).toFixed(8)}</span>
            </div>
          </div>
          
          <GameControls
            betAmount={betAmount}
            setBetAmount={setBetAmount}
            onBet={placeBet}
            isPlaying={isPlaying}
            disabled={!user}
          />
        </div>
      </div>
    </div>
  );
};

// ==================== AUTH PAGES ====================
const LoginPage = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await login(email, password);
      navigate("/");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page" data-testid="login-page">
      <div className="auth-card">
        <div className="auth-header">
          <Diamond className="auth-logo" />
          <h1>Welcome Back</h1>
          <p>Sign in to continue playing</p>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="input-group">
            <label>Email</label>
            <input type="email" value={email} onChange={e => setEmail(e.target.value)} required data-testid="login-email" />
          </div>
          <div className="input-group">
            <label>Password</label>
            <input type="password" value={password} onChange={e => setPassword(e.target.value)} required data-testid="login-password" />
          </div>
          <button type="submit" disabled={loading} className="auth-submit" data-testid="login-submit">
            {loading ? "Signing in..." : "Sign In"}
          </button>
        </form>
        <p className="auth-switch">
          Don't have an account? <Link to="/register">Create one</Link>
        </p>
      </div>
    </div>
  );
};

const RegisterPage = () => {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await register(username, email, password);
      navigate("/");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page" data-testid="register-page">
      <div className="auth-card">
        <div className="auth-header">
          <Diamond className="auth-logo" />
          <h1>Join the Den</h1>
          <p>Create your account</p>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="input-group">
            <label>Username</label>
            <input type="text" value={username} onChange={e => setUsername(e.target.value)} required data-testid="register-username" />
          </div>
          <div className="input-group">
            <label>Email</label>
            <input type="email" value={email} onChange={e => setEmail(e.target.value)} required data-testid="register-email" />
          </div>
          <div className="input-group">
            <label>Password</label>
            <input type="password" value={password} onChange={e => setPassword(e.target.value)} required data-testid="register-password" />
          </div>
          <button type="submit" disabled={loading} className="auth-submit" data-testid="register-submit">
            {loading ? "Creating account..." : "Create Account"}
          </button>
        </form>
        <p className="auth-switch">
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
      </div>
    </div>
  );
};

// ==================== WALLET PAGE ====================
const WalletPage = () => {
  const { wallet, refreshWallet } = useWallet();
  const [activeTab, setActiveTab] = useState("deposit");
  const [selectedCurrency, setSelectedCurrency] = useState("btc");
  const [amount, setAmount] = useState("");
  const [withdrawAddress, setWithdrawAddress] = useState("");
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [walletConfig, setWalletConfig] = useState(null);
  
  // OSRS GP deposit state
  const [osrsAmount, setOsrsAmount] = useState(15);
  const [osrsRsn, setOsrsRsn] = useState("");
  const [osrsDepositPending, setOsrsDepositPending] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [txRes, configRes] = await Promise.all([
          api.get("/wallet/transactions"),
          api.get("/wallet/config")
        ]);
        setTransactions(txRes.data);
        setWalletConfig(configRes.data);
      } catch (err) {
        console.error(err);
      }
    };
    fetchData();
  }, []);

  const handleDeposit = async () => {
    if (!amount || parseFloat(amount) <= 0) return;
    setLoading(true);
    try {
      await api.post("/wallet/deposit", { currency: selectedCurrency, amount: parseFloat(amount) });
      toast.success("Deposit successful!");
      refreshWallet();
      setAmount("");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Deposit failed");
    } finally {
      setLoading(false);
    }
  };

  const handleOsrsDeposit = async () => {
    if (!osrsRsn || osrsAmount < 15) {
      toast.error("Enter your RSN and minimum 15M GP");
      return;
    }
    setLoading(true);
    try {
      const res = await api.post("/wallet/deposit/osrs", {
        amount_gp: osrsAmount * 1000000,
        rsn: osrsRsn
      });
      setOsrsDepositPending(res.data);
      toast.success("Deposit request created! Follow the instructions.");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Deposit failed");
    } finally {
      setLoading(false);
    }
  };

  const handleWithdraw = async () => {
    if (!amount || !withdrawAddress) return;
    setLoading(true);
    try {
      const res = await api.post("/wallet/withdraw", { currency: selectedCurrency, amount: parseFloat(amount), address: withdrawAddress });
      toast.success(res.data.message);
      refreshWallet();
      setAmount("");
      setWithdrawAddress("");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Withdrawal failed");
    } finally {
      setLoading(false);
    }
  };

  const currentCurrency = CURRENCIES.find(c => c.id === selectedCurrency);
  const currentBalance = selectedCurrency === "osrs_gp" 
    ? wallet?.osrs_gp || 0 
    : wallet?.balances?.find(b => b.currency === selectedCurrency)?.balance || 0;
  const depositAddress = wallet?.balances?.find(b => b.currency === selectedCurrency)?.address || "";

  return (
    <div className="wallet-page" data-testid="wallet-page">
      <h1>Wallet</h1>
      
      {/* Deposit Limits Info */}
      {walletConfig && (
        <div className="wallet-limits-info">
          <div className="limit-item">
            <span>Crypto Deposit:</span>
            <span>${walletConfig.crypto?.min_deposit_usd} - ${walletConfig.crypto?.max_deposit_usd}</span>
          </div>
          <div className="limit-item">
            <span>OSRS GP Deposit:</span>
            <span>{walletConfig.osrs?.min_deposit/1000000}M - {walletConfig.osrs?.max_deposit/1000000}M</span>
          </div>
          <div className="limit-item">
            <span>Daily Withdraw Limit:</span>
            <span>${walletConfig.withdraw?.daily_limit_usd} (48h wait above)</span>
          </div>
        </div>
      )}
      
      <div className="wallet-balances">
        {CURRENCIES.map(curr => {
          const bal = curr.id === "osrs_gp" ? wallet?.osrs_gp || 0 : wallet?.balances?.find(b => b.currency === curr.id)?.balance || 0;
          return (
            <div 
              key={curr.id} 
              className={`balance-card ${selectedCurrency === curr.id ? "active" : ""}`}
              onClick={() => setSelectedCurrency(curr.id)}
              data-testid={`balance-${curr.id}`}
            >
              <span className="balance-icon" style={{ color: curr.color }}>{curr.icon}</span>
              <span className="balance-name">{curr.symbol}</span>
              <span className="balance-amount">{formatBalance(bal, curr.id)}</span>
            </div>
          );
        })}
      </div>

      <div className="wallet-tabs">
        <button className={activeTab === "deposit" ? "active" : ""} onClick={() => setActiveTab("deposit")} data-testid="tab-deposit">Deposit</button>
        <button className={activeTab === "osrs" ? "active" : ""} onClick={() => setActiveTab("osrs")} data-testid="tab-osrs">OSRS GP</button>
        <button className={activeTab === "withdraw" ? "active" : ""} onClick={() => setActiveTab("withdraw")} data-testid="tab-withdraw">Withdraw</button>
        <button className={activeTab === "history" ? "active" : ""} onClick={() => setActiveTab("history")} data-testid="tab-history">History</button>
      </div>

      <div className="wallet-content">
        {activeTab === "deposit" && (
          <div className="deposit-section">
            {selectedCurrency !== "osrs_gp" ? (
              <>
                <div className="deposit-address">
                  <label>Deposit Address ({currentCurrency?.symbol})</label>
                  <div className="address-box">
                    <code>{walletConfig?.admin_wallets?.[selectedCurrency] || depositAddress}</code>
                    <button onClick={() => copyToClipboard(walletConfig?.admin_wallets?.[selectedCurrency] || depositAddress)} data-testid="copy-address"><Copy size={16} /></button>
                  </div>
                  <p className="deposit-note">
                    Send only {currentCurrency?.name} to this address.<br/>
                    Min: ${walletConfig?.crypto?.min_deposit_usd} | Max: ${walletConfig?.crypto?.max_deposit_usd}
                  </p>
                </div>
                
                {/* Demo deposit for testing */}
                <div className="demo-deposit">
                  <h4>Demo Deposit (Testing)</h4>
                  <input 
                    type="number" 
                    value={amount} 
                    onChange={e => setAmount(e.target.value)} 
                    placeholder="Amount"
                    data-testid="deposit-amount"
                  />
                  <button onClick={handleDeposit} disabled={loading} data-testid="deposit-btn">
                    {loading ? "Processing..." : "Deposit"}
                  </button>
                </div>
              </>
            ) : (
              <div className="osrs-redirect">
                <p>For OSRS GP deposits, use the OSRS GP tab</p>
                <button onClick={() => setActiveTab("osrs")}>Go to OSRS GP Deposit</button>
              </div>
            )}
          </div>
        )}

        {activeTab === "osrs" && (
          <div className="osrs-deposit-section">
            <div className="osrs-deposit-header">
              <Coins size={32} className="osrs-icon" />
              <h2>OSRS GP Deposit</h2>
              <p>Trade your GP in-game to deposit on Degen's Den</p>
            </div>

            {osrsDepositPending ? (
              <div className="osrs-pending-deposit">
                <div className="pending-badge">PENDING</div>
                <h3>Complete Your Deposit</h3>
                <div className="deposit-instructions">
                  <div className="instruction-step">
                    <span className="step-num">1</span>
                    <div>
                      <strong>Trade to RSN:</strong>
                      <code className="rsn-display">{osrsDepositPending.trade_to_rsn}</code>
                    </div>
                  </div>
                  <div className="instruction-step">
                    <span className="step-num">2</span>
                    <div>
                      <strong>Amount:</strong>
                      <span>{(osrsDepositPending.amount_gp / 1000000).toFixed(0)}M GP</span>
                    </div>
                  </div>
                  <div className="instruction-step">
                    <span className="step-num">3</span>
                    <div>
                      <strong>Include Code in Trade:</strong>
                      <code className="code-display">{osrsDepositPending.code}</code>
                      <button onClick={() => copyToClipboard(osrsDepositPending.code)}><Copy size={14} /></button>
                    </div>
                  </div>
                </div>
                <p className="expire-note">This request expires in 1 hour. Make sure to include the code!</p>
                <button onClick={() => setOsrsDepositPending(null)} className="new-deposit-btn">
                  Create New Deposit Request
                </button>
              </div>
            ) : (
              <div className="osrs-deposit-form">
                <div className="osrs-amount-selector">
                  <label>Amount (in millions)</label>
                  <div className="amount-slider-container">
                    <input
                      type="range"
                      min="15"
                      max="750"
                      step="5"
                      value={osrsAmount}
                      onChange={e => setOsrsAmount(parseInt(e.target.value))}
                      className="osrs-slider"
                      data-testid="osrs-amount-slider"
                    />
                    <div className="amount-display">
                      <span className="amount-value">{osrsAmount}M GP</span>
                    </div>
                  </div>
                  <div className="amount-presets">
                    {[15, 50, 100, 250, 500, 750].map(val => (
                      <button 
                        key={val} 
                        onClick={() => setOsrsAmount(val)}
                        className={osrsAmount === val ? "active" : ""}
                      >
                        {val}M
                      </button>
                    ))}
                  </div>
                </div>

                <div className="input-group">
                  <label>Your RuneScape Name (RSN)</label>
                  <input
                    type="text"
                    value={osrsRsn}
                    onChange={e => setOsrsRsn(e.target.value)}
                    placeholder="Enter your in-game name"
                    maxLength={12}
                    data-testid="osrs-rsn"
                  />
                </div>

                <div className="deposit-summary">
                  <div className="summary-row">
                    <span>Deposit Amount:</span>
                    <span className="gp-amount">{osrsAmount}M GP</span>
                  </div>
                  <div className="summary-row">
                    <span>Trade To:</span>
                    <span className="rsn">{walletConfig?.osrs?.deposit_rsn || "Degens7Den"}</span>
                  </div>
                </div>

                <button 
                  onClick={handleOsrsDeposit} 
                  disabled={loading || !osrsRsn || osrsAmount < 15}
                  className="osrs-deposit-btn"
                  data-testid="osrs-deposit-btn"
                >
                  {loading ? "Creating Request..." : "Create Deposit Request"}
                </button>

                <p className="osrs-note">
                  Min: 15M GP | Max: 750M GP<br/>
                  GP will be credited after trade is verified by staff (usually within 10 minutes)
                </p>
              </div>
            )}
          </div>
        )}

        {activeTab === "withdraw" && (
          <div className="withdraw-section">
            <div className="withdraw-limits">
              <p>Daily Limit: ${walletConfig?.withdraw?.daily_limit_usd} | Above limit: {walletConfig?.withdraw?.extended_wait_hours}h processing</p>
            </div>
            <div className="input-group">
              <label>Amount</label>
              <input 
                type="number" 
                value={amount} 
                onChange={e => setAmount(e.target.value)} 
                placeholder="0.00"
                data-testid="withdraw-amount"
              />
              <span className="available">Available: {formatBalance(currentBalance, selectedCurrency)} {currentCurrency?.symbol}</span>
            </div>
            <div className="input-group">
              <label>Withdrawal Address</label>
              <input 
                type="text" 
                value={withdrawAddress} 
                onChange={e => setWithdrawAddress(e.target.value)} 
                placeholder="Enter your wallet address"
                data-testid="withdraw-address"
              />
            </div>
            <button onClick={handleWithdraw} disabled={loading || !amount || !withdrawAddress} className="withdraw-btn" data-testid="withdraw-btn">
              {loading ? "Processing..." : "Withdraw"}
            </button>
          </div>
        )}

        {activeTab === "history" && (
          <div className="transaction-history">
            {transactions.length === 0 ? (
              <p className="no-transactions">No transactions yet</p>
            ) : (
              transactions.map((tx, i) => (
                <div key={tx.id || i} className={`transaction-item ${tx.type}`}>
                  <div className="tx-info">
                    <span className="tx-type">{tx.type}</span>
                    <span className="tx-currency">{tx.currency?.toUpperCase()}</span>
                  </div>
                  <div className="tx-amount">
                    {tx.type === "deposit" || tx.type === "win" ? "+" : "-"}
                    {tx.amount}
                  </div>
                  <div className="tx-status">{tx.status}</div>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
};

// ==================== REFERRAL PAGE ====================
const ReferralPage = () => {
  const { user } = useAuth();
  const [referralInfo, setReferralInfo] = useState(null);
  const [redeemCode, setRedeemCode] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (user) {
      api.get("/referral/info").then(res => setReferralInfo(res.data)).catch(console.error);
    }
  }, [user]);

  const handleRedeem = async () => {
    if (!redeemCode.trim()) return;
    setLoading(true);
    try {
      const res = await api.post("/referral/redeem", { code: redeemCode.trim() });
      toast.success(res.data.message);
      setRedeemCode("");
      // Refresh info
      const infoRes = await api.get("/referral/info");
      setReferralInfo(infoRes.data);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Redemption failed");
    } finally {
      setLoading(false);
    }
  };

  const wagerProgress = referralInfo?.wager_required > 0 
    ? Math.min(100, (referralInfo.wager_completed / referralInfo.wager_required) * 100)
    : 0;

  return (
    <div className="referral-page" data-testid="referral-page">
      <h1>Refer a Degen</h1>
      
      <div className="referral-hero">
        <Gift size={64} className="referral-icon" />
        <h2>Get $5 FREE or 35M GP!</h2>
        <p>Share your code with friends and both of you get rewarded!</p>
      </div>

      {user && referralInfo && (
        <>
          {/* Your Referral Code */}
          <div className="referral-code-section">
            <h3>Your Referral Code</h3>
            <div className="code-box">
              <code className="referral-code">{referralInfo.referral_code}</code>
              <button onClick={() => copyToClipboard(referralInfo.referral_code)}><Copy size={18} /></button>
            </div>
            <div className="referral-link">
              <span>Share Link:</span>
              <input type="text" value={referralInfo.referral_link} readOnly />
              <button onClick={() => copyToClipboard(referralInfo.referral_link)}><Copy size={14} /></button>
            </div>
          </div>

          {/* Referral Stats */}
          <div className="referral-stats">
            <div className="stat-card">
              <Users size={24} />
              <span className="stat-value">{referralInfo.total_referrals}</span>
              <span className="stat-label">Total Referrals</span>
            </div>
            <div className="stat-card">
              <Gift size={24} />
              <span className="stat-value">${referralInfo.bonus_config?.usd_bonus || 5}</span>
              <span className="stat-label">Friend's Bonus</span>
            </div>
            <div className="stat-card">
              <Zap size={24} />
              <span className="stat-value">{referralInfo.bonus_config?.wager_multiplier || 10}x</span>
              <span className="stat-label">Wager Req</span>
            </div>
          </div>

          {/* Pending Bonus */}
          {referralInfo.bonus_pending > 0 && (
            <div className="bonus-progress-section">
              <h3>Your Bonus Progress</h3>
              <div className="bonus-info">
                <span>Bonus: ${referralInfo.bonus_pending} {referralInfo.bonus_type?.toUpperCase()}</span>
                <span>Wager: ${referralInfo.wager_completed?.toFixed(2)} / ${referralInfo.wager_required?.toFixed(2)}</span>
              </div>
              <div className="progress-bar">
                <div className="progress-fill" style={{ width: `${wagerProgress}%` }} />
              </div>
              <p className="progress-note">
                {wagerProgress >= 100 
                  ? "Congratulations! Your bonus is unlocked for withdrawal!" 
                  : `Wager $${(referralInfo.wager_required - referralInfo.wager_completed).toFixed(2)} more to unlock withdrawals`}
              </p>
            </div>
          )}

          {/* Referred Users */}
          {referralInfo.referred_users?.length > 0 && (
            <div className="referred-users-section">
              <h3>Your Referrals</h3>
              <div className="referred-list">
                {referralInfo.referred_users.map((u, i) => (
                  <div key={i} className="referred-user">
                    <span className="ref-username">{u.username}</span>
                    <span className="ref-wagered">${u.total_wagered?.toFixed(2) || 0} wagered</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}

      {/* Redeem Code Section */}
      <div className="redeem-section">
        <h3>Have a Code?</h3>
        <p>Enter a referral or promo code below:</p>
        <div className="redeem-input">
          <input
            type="text"
            value={redeemCode}
            onChange={e => setRedeemCode(e.target.value.toUpperCase())}
            placeholder="Enter code"
            maxLength={20}
            data-testid="redeem-code-input"
          />
          <button onClick={handleRedeem} disabled={loading || !redeemCode} data-testid="redeem-btn">
            {loading ? "Redeeming..." : "Redeem"}
          </button>
        </div>
        <p className="redeem-note">Codes can only be redeemed within 24 hours of registration. 10x wager requirement applies.</p>
      </div>

      {/* How It Works */}
      <div className="how-it-works">
        <h3>How It Works</h3>
        <div className="steps">
          <div className="step">
            <span className="step-num">1</span>
            <h4>Share Your Code</h4>
            <p>Give your unique referral code to friends</p>
          </div>
          <div className="step">
            <span className="step-num">2</span>
            <h4>Friend Signs Up</h4>
            <p>They register and enter your code within 24 hours</p>
          </div>
          <div className="step">
            <span className="step-num">3</span>
            <h4>Both Get Rewarded</h4>
            <p>Friend gets $5 FREE, you earn 10% of their wagers</p>
          </div>
          <div className="step">
            <span className="step-num">4</span>
            <h4>Unlock & Withdraw</h4>
            <p>Complete 10x wager requirement to withdraw bonus</p>
          </div>
        </div>
      </div>
    </div>
  );
};

// ==================== VIP PAGE ====================
const VIPPage = () => {
  const [vipStatus, setVipStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchVIP = async () => {
      try {
        const res = await api.get("/vip/status");
        setVipStatus(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchVIP();
  }, []);

  const claimRakeback = async () => {
    try {
      const res = await api.post("/vip/claim-rakeback");
      toast.success(`Claimed ${res.data.amount.toFixed(8)} BTC rakeback!`);
      setVipStatus(prev => ({ ...prev, rakeback_available: 0 }));
    } catch (err) {
      toast.error(err.response?.data?.detail || "Claim failed");
    }
  };

  const claimLossback = async () => {
    try {
      const res = await api.post("/vip/claim-lossback");
      toast.success(`Claimed ${res.data.amount.toFixed(8)} BTC lossback!`);
      setVipStatus(prev => ({ ...prev, lossback_available: 0 }));
    } catch (err) {
      toast.error(err.response?.data?.detail || "Claim failed");
    }
  };

  if (loading) return <div className="loading">Loading VIP status...</div>;

  const currentTier = VIP_TIERS.find(t => t.level === vipStatus?.level) || VIP_TIERS[0];
  const nextTier = VIP_TIERS.find(t => t.level === vipStatus?.level + 1);

  return (
    <div className="vip-page" data-testid="vip-page">
      <h1>VIP Club</h1>
      
      <div className="vip-status-card">
        <div className="vip-tier" style={{ color: currentTier.color }}>
          <Crown size={48} />
          <h2>{currentTier.name}</h2>
          <span className="vip-level">Level {vipStatus?.level}</span>
        </div>
        
        <div className="vip-progress-section">
          <div className="progress-header">
            <span>Progress to {nextTier?.name || "Max"}</span>
            <span>{vipStatus?.progress?.toFixed(1)}%</span>
          </div>
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${vipStatus?.progress || 0}%` }} />
          </div>
          <div className="progress-stats">
            <span>Wagered: ${vipStatus?.total_wagered?.toFixed(2)}</span>
            {nextTier && <span>Need: ${vipStatus?.wager_to_next?.toFixed(2)} more</span>}
          </div>
        </div>
      </div>

      <div className="vip-rewards">
        <div className="reward-card">
          <h3>Rakeback</h3>
          <div className="reward-rate">{(vipStatus?.rakeback_rate * 100).toFixed(0)}%</div>
          <div className="reward-available">
            <span>Available:</span>
            <span className="amount">{vipStatus?.rakeback_available?.toFixed(8)} BTC</span>
          </div>
          <button 
            onClick={claimRakeback} 
            disabled={!vipStatus?.rakeback_available || vipStatus?.rakeback_available <= 0}
            data-testid="claim-rakeback"
          >
            Claim Rakeback
          </button>
        </div>
        
        <div className="reward-card">
          <h3>Lossback</h3>
          <div className="reward-rate">{(vipStatus?.lossback_rate * 100).toFixed(0)}%</div>
          <div className="reward-available">
            <span>Available:</span>
            <span className="amount">{vipStatus?.lossback_available?.toFixed(8)} BTC</span>
          </div>
          <button 
            onClick={claimLossback} 
            disabled={!vipStatus?.lossback_available || vipStatus?.lossback_available <= 0}
            data-testid="claim-lossback"
          >
            Claim Lossback
          </button>
          {vipStatus?.level < 1 && <p className="unlock-note">Unlock at Silver tier</p>}
        </div>
      </div>

      <div className="vip-tiers-section">
        <h2>VIP Tiers</h2>
        <div className="tiers-grid">
          {VIP_TIERS.map(tier => (
            <div 
              key={tier.level} 
              className={`tier-card ${tier.level === vipStatus?.level ? "current" : ""} ${tier.level < vipStatus?.level ? "achieved" : ""}`}
            >
              <Crown style={{ color: tier.color }} />
              <h4>{tier.name}</h4>
              <p className="tier-wager">${tier.wager.toLocaleString()} wagered</p>
              <ul className="tier-benefits">
                <li>Rakeback: {tier.level === 0 ? "5%" : tier.level === 1 ? "10%" : tier.level === 2 ? "15%" : tier.level === 3 ? "20%" : "30%"}</li>
                <li>Lossback: {tier.level === 0 ? "0%" : tier.level === 1 ? "2%" : tier.level === 2 ? "5%" : tier.level === 3 ? "8%" : "12%"}</li>
              </ul>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// ==================== PROVABLY FAIR PAGE ====================
const ProvablyFairPage = () => {
  const { user } = useAuth();
  const [fairInfo, setFairInfo] = useState(null);
  const [newClientSeed, setNewClientSeed] = useState("");
  const [verifyData, setVerifyData] = useState({ serverSeed: "", clientSeed: "", nonce: "", gameType: "dice" });
  const [verifyResult, setVerifyResult] = useState(null);

  useEffect(() => {
    if (user) {
      api.get("/provably-fair").then(res => setFairInfo(res.data)).catch(console.error);
    }
  }, [user]);

  const rotateSeed = async () => {
    if (!newClientSeed) return;
    try {
      const res = await api.post("/provably-fair/rotate", { new_client_seed: newClientSeed });
      toast.success("Seeds rotated! Previous server seed revealed.");
      setFairInfo({
        server_seed_hash: res.data.new_server_seed_hash,
        client_seed: res.data.new_client_seed,
        nonce: 0,
        previous_server_seed: res.data.revealed_server_seed
      });
      setNewClientSeed("");
    } catch (err) {
      toast.error("Failed to rotate seeds");
    }
  };

  const verifyBet = async () => {
    try {
      const res = await api.post("/provably-fair/verify", null, {
        params: {
          server_seed: verifyData.serverSeed,
          client_seed: verifyData.clientSeed,
          nonce: parseInt(verifyData.nonce),
          game_type: verifyData.gameType
        }
      });
      setVerifyResult(res.data);
    } catch (err) {
      toast.error("Verification failed");
    }
  };

  return (
    <div className="provably-fair-page" data-testid="provably-fair-page">
      <h1>Provably Fair</h1>
      <p className="fair-intro">
        Every bet on Degen's Den is provably fair. We use cryptographic hashing to ensure results cannot be manipulated.
      </p>

      {user && fairInfo && (
        <div className="current-seeds">
          <h2>Your Current Seeds</h2>
          <div className="seed-box">
            <label>Server Seed Hash (SHA-256)</label>
            <code className="hash-display">{fairInfo.server_seed_hash}</code>
            <button onClick={() => copyToClipboard(fairInfo.server_seed_hash)}><Copy size={14} /></button>
          </div>
          <div className="seed-box">
            <label>Client Seed</label>
            <code>{fairInfo.client_seed}</code>
            <button onClick={() => copyToClipboard(fairInfo.client_seed)}><Copy size={14} /></button>
          </div>
          <div className="seed-box">
            <label>Nonce</label>
            <code>{fairInfo.nonce}</code>
          </div>
          {fairInfo.previous_server_seed && (
            <div className="seed-box revealed">
              <label>Previous Server Seed (Revealed)</label>
              <code>{fairInfo.previous_server_seed}</code>
              <button onClick={() => copyToClipboard(fairInfo.previous_server_seed)}><Copy size={14} /></button>
            </div>
          )}
          
          <div className="rotate-seed-section">
            <h3>Rotate Seeds</h3>
            <p>Rotating seeds will reveal your current server seed and generate a new one.</p>
            <div className="rotate-input">
              <input 
                type="text" 
                value={newClientSeed} 
                onChange={e => setNewClientSeed(e.target.value)}
                placeholder="Enter new client seed"
                data-testid="new-client-seed"
              />
              <button onClick={rotateSeed} disabled={!newClientSeed} data-testid="rotate-seeds">Rotate Seeds</button>
            </div>
          </div>
        </div>
      )}

      <div className="verify-section">
        <h2>Verify a Bet</h2>
        <div className="verify-form">
          <div className="input-group">
            <label>Server Seed</label>
            <input 
              value={verifyData.serverSeed} 
              onChange={e => setVerifyData(prev => ({ ...prev, serverSeed: e.target.value }))}
              placeholder="Enter revealed server seed"
              data-testid="verify-server-seed"
            />
          </div>
          <div className="input-group">
            <label>Client Seed</label>
            <input 
              value={verifyData.clientSeed} 
              onChange={e => setVerifyData(prev => ({ ...prev, clientSeed: e.target.value }))}
              placeholder="Enter client seed"
              data-testid="verify-client-seed"
            />
          </div>
          <div className="input-group">
            <label>Nonce</label>
            <input 
              type="number"
              value={verifyData.nonce} 
              onChange={e => setVerifyData(prev => ({ ...prev, nonce: e.target.value }))}
              placeholder="Enter nonce"
              data-testid="verify-nonce"
            />
          </div>
          <div className="input-group">
            <label>Game Type</label>
            <select 
              value={verifyData.gameType} 
              onChange={e => setVerifyData(prev => ({ ...prev, gameType: e.target.value }))}
              data-testid="verify-game-type"
            >
              <option value="dice">Dice</option>
              <option value="crash">Crash</option>
              <option value="keno">Keno</option>
              <option value="wheel">Wheel</option>
              <option value="plinko">Plinko</option>
              <option value="limbo">Limbo</option>
            </select>
          </div>
          <button onClick={verifyBet} className="verify-btn" data-testid="verify-btn">Verify</button>
        </div>

        {verifyResult && (
          <div className="verify-result">
            <h3>Verification Result</h3>
            <pre>{JSON.stringify(verifyResult, null, 2)}</pre>
          </div>
        )}
      </div>

      <div className="how-it-works">
        <h2>How It Works</h2>
        <ol>
          <li><strong>Server Seed:</strong> We generate a random server seed and show you its SHA-256 hash before you bet.</li>
          <li><strong>Client Seed:</strong> You can set your own client seed at any time.</li>
          <li><strong>Nonce:</strong> A counter that increases with each bet.</li>
          <li><strong>Result:</strong> Game results are calculated using: SHA256(server_seed + client_seed + nonce)</li>
          <li><strong>Verification:</strong> After rotating seeds, the old server seed is revealed so you can verify all past bets.</li>
        </ol>
      </div>
    </div>
  );
};

// ==================== LEADERBOARD PAGE ====================
const LeaderboardPage = () => {
  const [leaders, setLeaders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/leaderboard").then(res => {
      setLeaders(res.data);
      setLoading(false);
    }).catch(err => {
      console.error(err);
      setLoading(false);
    });
  }, []);

  return (
    <div className="leaderboard-page" data-testid="leaderboard-page">
      <h1>Leaderboard</h1>
      
      {loading ? (
        <div className="loading">Loading leaderboard...</div>
      ) : (
        <div className="leaderboard-table">
          <div className="leaderboard-header">
            <span>Rank</span>
            <span>Player</span>
            <span>VIP</span>
            <span>Wagered</span>
          </div>
          {leaders.map((leader, i) => {
            const tier = VIP_TIERS.find(t => t.level === leader.vip_level) || VIP_TIERS[0];
            return (
              <div key={leader.username} className={`leaderboard-row ${i < 3 ? `top-${i + 1}` : ""}`}>
                <span className="rank">
                  {i === 0 && <Trophy className="gold" />}
                  {i === 1 && <Trophy className="silver" />}
                  {i === 2 && <Trophy className="bronze" />}
                  {i > 2 && `#${leader.rank}`}
                </span>
                <span className="player">{leader.username}</span>
                <span className="vip" style={{ color: tier.color }}>{tier.name}</span>
                <span className="wagered">${leader.total_wagered.toLocaleString()}</span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

// ==================== HOME PAGE ====================
const HomePage = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [liveBets, setLiveBets] = useState([]);

  useEffect(() => {
    api.get("/games/live").then(res => setLiveBets(res.data)).catch(console.error);
  }, []);

  const games = [
    { id: "dice", name: "Dice", icon: Dices, color: "#E0FF00", description: "Classic dice with customizable odds" },
    { id: "keno", name: "Keno", icon: Target, color: "#00FFA3", description: "Pick your numbers, win big" },
    { id: "crash", name: "Crash", icon: Rocket, color: "#FF2346", description: "Ride the rocket, cash out in time" },
    { id: "wheel", name: "Lucky Wheel", icon: Star, color: "#E0FF00", description: "Spin for massive multipliers" },
    { id: "plinko", name: "Plinko", icon: Circle, color: "#00E0FF", description: "Drop the ball, hit the jackpot" },
    { id: "limbo", name: "Limbo", icon: TrendingUp, color: "#00FFA3", description: "Set your target, test your luck" },
  ];

  return (
    <div className="home-page" data-testid="home-page">
      <section className="hero-section">
        <div className="hero-content">
          <h1>DEGEN'S DEN</h1>
          <p className="hero-tagline">The Ultimate Crypto Casino for OSRS Degens</p>
          <div className="hero-features">
            <span><Shield size={16} /> Provably Fair</span>
            <span><Zap size={16} /> Instant Payouts</span>
            <span><Coins size={16} /> Multi-Crypto</span>
          </div>
          {!user && (
            <div className="hero-cta">
              <button onClick={() => navigate("/register")} className="cta-primary" data-testid="hero-register">
                Start Playing
              </button>
              <button onClick={() => navigate("/login")} className="cta-secondary" data-testid="hero-login">
                Login
              </button>
            </div>
          )}
        </div>
        <div className="hero-visual">
          <Diamond className="hero-diamond" />
        </div>
      </section>

      <section className="games-section">
        <h2>Games</h2>
        <div className="games-grid">
          {games.map(game => (
            <div 
              key={game.id} 
              className="game-card" 
              onClick={() => navigate(`/${game.id}`)}
              data-testid={`game-card-${game.id}`}
            >
              <div className="game-icon" style={{ color: game.color }}>
                <game.icon size={40} />
              </div>
              <h3>{game.name}</h3>
              <p>{game.description}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="live-bets-section">
        <h2>Live Bets</h2>
        <div className="live-bets-table">
          <div className="table-header">
            <span>Player</span>
            <span>Game</span>
            <span>Bet</span>
            <span>Multiplier</span>
            <span>Payout</span>
          </div>
          {liveBets.slice(0, 10).map((bet, i) => (
            <div key={bet.id || i} className={`table-row ${bet.won ? "win" : "lose"}`}>
              <span className="player">{bet.username}</span>
              <span className="game">{bet.game_type}</span>
              <span className="bet">{bet.amount.toFixed(6)}</span>
              <span className="multiplier">{bet.multiplier.toFixed(2)}×</span>
              <span className={`payout ${bet.won ? "win" : "lose"}`}>
                {bet.won ? `+${bet.payout.toFixed(6)}` : `-${bet.amount.toFixed(6)}`}
              </span>
            </div>
          ))}
        </div>
      </section>

      <section className="features-section">
        <div className="feature">
          <Shield size={48} />
          <h3>Provably Fair</h3>
          <p>Every bet verifiable with cryptographic proof</p>
        </div>
        <div className="feature">
          <Wallet size={48} />
          <h3>Multi-Crypto</h3>
          <p>BTC, ETH, LTC, USDC, USDT + OSRS GP</p>
        </div>
        <div className="feature">
          <Crown size={48} />
          <h3>VIP Rewards</h3>
          <p>Earn rakeback and lossback as you play</p>
        </div>
        <div className="feature">
          <Gift size={48} />
          <h3>Rain & Tips</h3>
          <p>Active community with live rewards</p>
        </div>
      </section>
    </div>
  );
};

// ==================== ADMIN PAGE ====================
const AdminPage = () => {
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [bets, setBets] = useState([]);
  const [activeTab, setActiveTab] = useState("stats");

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, usersRes, betsRes] = await Promise.all([
          api.get("/admin/stats"),
          api.get("/admin/users"),
          api.get("/admin/bets")
        ]);
        setStats(statsRes.data);
        setUsers(usersRes.data);
        setBets(betsRes.data);
      } catch (err) {
        toast.error("Failed to load admin data");
      }
    };
    fetchData();
  }, []);

  return (
    <div className="admin-page" data-testid="admin-page">
      <h1>Admin Dashboard</h1>

      <div className="admin-tabs">
        <button className={activeTab === "stats" ? "active" : ""} onClick={() => setActiveTab("stats")}>Stats</button>
        <button className={activeTab === "users" ? "active" : ""} onClick={() => setActiveTab("users")}>Users</button>
        <button className={activeTab === "bets" ? "active" : ""} onClick={() => setActiveTab("bets")}>Bets</button>
      </div>

      {activeTab === "stats" && stats && (
        <div className="admin-stats">
          <div className="stat-card">
            <Users size={32} />
            <div className="stat-value">{stats.total_users}</div>
            <div className="stat-label">Total Users</div>
          </div>
          <div className="stat-card">
            <Dices size={32} />
            <div className="stat-value">{stats.total_bets}</div>
            <div className="stat-label">Total Bets</div>
          </div>
          <div className="stat-card">
            <Coins size={32} />
            <div className="stat-value">${stats.total_wagered?.toFixed(2)}</div>
            <div className="stat-label">Total Wagered</div>
          </div>
          <div className="stat-card">
            <TrendingUp size={32} />
            <div className="stat-value">${stats.house_profit?.toFixed(2)}</div>
            <div className="stat-label">House Profit</div>
          </div>
        </div>
      )}

      {activeTab === "users" && (
        <div className="admin-users">
          {users.map(u => (
            <div key={u.id} className="user-row">
              <span>{u.username}</span>
              <span>{u.email}</span>
              <span>VIP {u.vip_level}</span>
              <span>${u.total_wagered?.toFixed(2)} wagered</span>
            </div>
          ))}
        </div>
      )}

      {activeTab === "bets" && (
        <div className="admin-bets">
          {bets.map(b => (
            <div key={b.id} className={`bet-row ${b.won ? "win" : "lose"}`}>
              <span>{b.username}</span>
              <span>{b.game_type}</span>
              <span>{b.amount}</span>
              <span>{b.multiplier}×</span>
              <span className={b.won ? "win" : "lose"}>{b.won ? `+${b.payout}` : `-${b.amount}`}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// ==================== PROTECTED ROUTE ====================
const ProtectedRoute = ({ children, adminOnly = false }) => {
  const { user, loading } = useAuth();
  
  if (loading) return <div className="loading">Loading...</div>;
  if (!user) return <Navigate to="/login" replace />;
  if (adminOnly && !user.is_admin) return <Navigate to="/" replace />;
  
  return children;
};

// ==================== MAIN APP ====================
function App() {
  const [user, setUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(true);
  const [wallet, setWallet] = useState(null);
  const [selectedCurrency, setSelectedCurrency] = useState("btc");
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [chatOpen, setChatOpen] = useState(true);
  const [chatMessages, setChatMessages] = useState([]);
  const [wsConnected, setWsConnected] = useState(false);
  const wsRef = useRef(null);

  // Load user on mount
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      api.get("/auth/me")
        .then(res => setUser(res.data))
        .catch(() => localStorage.removeItem("token"))
        .finally(() => setAuthLoading(false));
    } else {
      setAuthLoading(false);
    }
  }, []);

  // Load wallet when user changes
  const refreshWallet = useCallback(async () => {
    if (user) {
      try {
        const res = await api.get("/wallet");
        setWallet(res.data);
      } catch (err) {
        console.error(err);
      }
    }
  }, [user]);

  useEffect(() => {
    refreshWallet();
  }, [refreshWallet]);

  // Seed data and load initial chat
  useEffect(() => {
    api.post("/seed").catch(console.error);
    api.get("/chat/messages").then(res => setChatMessages(res.data)).catch(console.error);
  }, []);

  // WebSocket for chat
  useEffect(() => {
    const token = localStorage.getItem("token");
    const wsUrl = BACKEND_URL.replace("https://", "wss://").replace("http://", "ws://");
    const ws = new WebSocket(`${wsUrl}/ws/chat?token=${token || ""}`);
    
    ws.onopen = () => setWsConnected(true);
    ws.onclose = () => setWsConnected(false);
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === "chat" || data.type === "tip" || data.type === "rain") {
          setChatMessages(prev => [...prev, data.data]);
        } else if (data.type === "big_win") {
          toast.success(`${data.username} won ${data.multiplier}× on ${data.game}!`);
        }
      } catch (e) {
        console.error(e);
      }
    };
    
    wsRef.current = ws;
    
    // Ping to keep alive
    const pingInterval = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send("ping");
      }
    }, 30000);
    
    return () => {
      clearInterval(pingInterval);
      ws.close();
    };
  }, []);

  // Auth functions
  const login = async (email, password) => {
    const res = await api.post("/auth/login", { email, password });
    localStorage.setItem("token", res.data.access_token);
    setUser(res.data.user);
    toast.success("Welcome back!");
  };

  const register = async (username, email, password) => {
    const res = await api.post("/auth/register", { username, email, password });
    localStorage.setItem("token", res.data.access_token);
    setUser(res.data.user);
    toast.success("Account created!");
  };

  const logout = () => {
    localStorage.removeItem("token");
    setUser(null);
    setWallet(null);
    toast.success("Logged out");
  };

  // Chat functions
  const sendMessage = async (message) => {
    try {
      await api.post("/chat/send", { message });
    } catch (err) {
      toast.error("Failed to send message");
    }
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, loading: authLoading }}>
      <WalletContext.Provider value={{ wallet, selectedCurrency, setSelectedCurrency, refreshWallet }}>
        <ChatContext.Provider value={{ messages: chatMessages, sendMessage, connected: wsConnected }}>
          <BrowserRouter>
            <div className={`app ${sidebarCollapsed ? "sidebar-collapsed" : ""} ${chatOpen ? "chat-open" : ""}`}>
              <Toaster position="top-right" theme="dark" richColors />
              <Sidebar collapsed={sidebarCollapsed} setCollapsed={setSidebarCollapsed} />
              <main className="main-content">
                <Header toggleChat={() => setChatOpen(!chatOpen)} />
                <div className="page-content">
                  <Routes>
                    <Route path="/" element={<HomePage />} />
                    <Route path="/dice" element={<DicePage />} />
                    <Route path="/keno" element={<KenoPage />} />
                    <Route path="/crash" element={<CrashPage />} />
                    <Route path="/wheel" element={<WheelPage />} />
                    <Route path="/plinko" element={<PlinkoPage />} />
                    <Route path="/limbo" element={<LimboPage />} />
                    <Route path="/login" element={<LoginPage />} />
                    <Route path="/register" element={<RegisterPage />} />
                    <Route path="/wallet" element={<ProtectedRoute><WalletPage /></ProtectedRoute>} />
                    <Route path="/referral" element={<ProtectedRoute><ReferralPage /></ProtectedRoute>} />
                    <Route path="/vip" element={<ProtectedRoute><VIPPage /></ProtectedRoute>} />
                    <Route path="/provably-fair" element={<ProvablyFairPage />} />
                    <Route path="/leaderboard" element={<LeaderboardPage />} />
                    <Route path="/admin" element={<ProtectedRoute adminOnly><AdminPage /></ProtectedRoute>} />
                  </Routes>
                </div>
              </main>
              <ChatPanel isOpen={chatOpen} onClose={() => setChatOpen(false)} />
            </div>
          </BrowserRouter>
        </ChatContext.Provider>
      </WalletContext.Provider>
    </AuthContext.Provider>
  );
}

export default App;
