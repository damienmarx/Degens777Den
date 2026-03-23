// Rule-based Chatbot - No external dependencies
// Handles common casino and OSRS degen site questions

const CHATBOT_RESPONSES = {
  // Greetings
  hello: {
    keywords: ['hello', 'hi', 'hey', 'greetings', 'sup', 'yo'],
    responses: [
      '🐺 Yo degen! Welcome to Degens♧Den! What can I help you with?',
      '♧ Wassup! Ready to lose some money? Just kidding... or am I? 😎',
      '🎰 Hey there! Looking to play some games or have questions?',
    ],
  },

  // About the site
  about: {
    keywords: ['about', 'what is', 'tell me about', 'who are you', 'what do you do'],
    responses: [
      '♧ Degens♧Den is the ultimate crypto casino for OSRS players and crypto degenerates. We offer provably fair games, OSRS GP trading, and a wolf pack community. 🐺',
      '🎰 We\'re a provably fair crypto casino with games like Dice, Keno, and Crash. Plus, you can trade OSRS gold!',
    ],
  },

  // Games
  games: {
    keywords: ['games', 'what games', 'play', 'how to play', 'game rules'],
    responses: [
      '🎮 We have: Dice (guess higher/lower), Keno (pick numbers), and Crash (cash out before crash). All provably fair!',
      '♧ Check out our game selection: Dice, Keno, Crash. Each has different odds and strategies. Which one interests you?',
    ],
  },

  // Dice game
  dice: {
    keywords: ['dice', 'dice game', 'how to play dice'],
    responses: [
      '🎲 Dice: Pick your target number (0-100), choose over/under, set your bet. Win if the roll hits your target!',
      '♧ Dice is simple: Set a number, pick over or under, and watch it roll. Higher odds = lower win chance. Classic!',
    ],
  },

  // Keno game
  keno: {
    keywords: ['keno', 'keno game', 'how to play keno', 'quick pick'],
    responses: [
      '🎰 Keno: Pick 1-40 numbers, place your bet, and watch 20 numbers draw. More matches = bigger payout! Use Quick Pick for random selection.',
      '♧ Keno is like lottery: Pick your lucky numbers, bet, and see how many match. The paytable shows your potential winnings.',
    ],
  },

  // Crash game
  crash: {
    keywords: ['crash', 'crash game', 'how to play crash'],
    responses: [
      '🚀 Crash: Place your bet, watch the multiplier climb. Cash out before it crashes to win! The longer you wait, the bigger the payout... but risky!',
      '♧ Crash is high-risk, high-reward: Set your bet and cash out target. If you cash out in time, you win. If it crashes first, you lose.',
    ],
  },

  // Deposits
  deposit: {
    keywords: ['deposit', 'how to deposit', 'add funds', 'fund account', 'payment'],
    responses: [
      '💰 Click the Deposit button in the header. We accept crypto and OSRS GP. Choose your currency and follow the instructions.',
      '♧ Deposits are easy: Click Deposit, select your currency (crypto or OSRS), and send funds to your wallet address. Instant!',
    ],
  },

  // Withdrawals
  withdraw: {
    keywords: ['withdraw', 'how to withdraw', 'cash out', 'get money out'],
    responses: [
      '💸 Go to your account, click Withdraw, enter the amount, and confirm. Funds go to your wallet. Fast and secure!',
      '♧ Withdrawals: Click Withdraw, pick your currency, enter amount, and boom - funds on their way to your wallet!',
    ],
  },

  // OSRS GP
  osrs: {
    keywords: ['osrs', 'runescape', 'gp', 'old school', 'gold'],
    responses: [
      '🎮 We support OSRS GP deposits and withdrawals! Trade your gold for crypto or vice versa. Rates are fair and transparent.',
      '♧ OSRS players can deposit/withdraw GP directly. Perfect for grinding and gambling! Check current rates in the currency selector.',
    ],
  },

  // Provably fair
  provably: {
    keywords: ['provably fair', 'fair', 'rigged', 'trust', 'verify'],
    responses: [
      '✅ All games are provably fair! You can verify every result with our hash system. No house manipulation - just pure RNG.',
      '♧ Provably fair means you can verify every game result. We use cryptographic hashing so you know it\'s legit. No scams here!',
    ],
  },

  // VIP/Rewards
  vip: {
    keywords: ['vip', 'rewards', 'loyalty', 'points', 'level', 'tier'],
    responses: [
      '👑 Play more, earn more! Our VIP system rewards loyal players with better odds, higher limits, and exclusive perks.',
      '♧ The more you play, the higher your VIP level. Better odds, higher bet limits, and special rewards await!',
    ],
  },

  // Chat/Community
  chat: {
    keywords: ['chat', 'community', 'talk', 'message', 'tip', 'rain'],
    responses: [
      '💬 Use the chat panel to connect with other degens! Tip players, participate in rain events, and share your wins (or losses 😅).',
      '♧ Chat is where the wolf pack hangs out! Tip your fellow degens, celebrate wins, and build the community.',
    ],
  },

  // Limits
  limits: {
    keywords: ['limit', 'max bet', 'minimum bet', 'restrictions'],
    responses: [
      '📊 Bet limits vary by game and VIP level. Check each game for min/max bets. Higher VIP = higher limits!',
      '♧ Minimum bets are low to start, but max bets increase with your VIP level. No limits for high rollers!',
    ],
  },

  // Fees
  fees: {
    keywords: ['fee', 'charge', 'cost', 'commission', 'rake'],
    responses: [
      '💵 We charge minimal fees on deposits/withdrawals. Game house edge is standard industry rates. Check the game details for specifics.',
      '♧ Fees are transparent and minimal. We make money on the house edge, not hidden charges. Fair and square!',
    ],
  },

  // Security
  security: {
    keywords: ['security', 'safe', 'hack', 'secure', 'privacy', 'kyc'],
    responses: [
      '🔒 Your funds and data are secure. We use industry-standard encryption and cold storage for crypto. Play with confidence!',
      '♧ Security is our priority. Encrypted connections, secure wallets, and transparent operations. Your money is safe with us.',
    ],
  },

  // Support
  support: {
    keywords: ['support', 'help', 'contact', 'issue', 'problem', 'bug'],
    responses: [
      '🆘 Having issues? Check our FAQ or contact support. We\'re here to help 24/7!',
      '♧ Need help? Reach out to our support team. We respond fast and solve problems quickly.',
    ],
  },

  // Odds/Math
  odds: {
    keywords: ['odds', 'probability', 'math', 'payout', 'rtp', 'house edge'],
    responses: [
      '📈 Each game has different odds. Dice: 49% win chance (standard). Keno: Varies by matches. Crash: Depends on multiplier. Check paytables!',
      '♧ Odds are fair and transparent. Lower risk = lower reward. Higher risk = higher reward. That\'s the game!',
    ],
  },

  // Account
  account: {
    keywords: ['account', 'profile', 'settings', 'password', 'login'],
    responses: [
      '👤 Access your account from the header. View balance, history, VIP level, and settings. Keep your password safe!',
      '♧ Your account shows everything: balance, history, stats, and settings. Update your profile anytime.',
    ],
  },

  // Referrals
  referral: {
    keywords: ['referral', 'refer', 'friend', 'bonus', 'commission'],
    responses: [
      '🤝 Refer friends and earn commission! Share your link, they sign up, you both get rewards. Win-win!',
      '♧ Referral program: Share your code, earn commission on their losses. Build your wolf pack!',
    ],
  },

  // Promotions
  promotion: {
    keywords: ['promotion', 'promo', 'bonus', 'offer', 'deal', 'special'],
    responses: [
      '🎁 Check our promotions page for current offers! We run regular bonuses, contests, and special events.',
      '♧ We always have something going on. Bonuses, contests, rain events - stay tuned!',
    ],
  },

  // Mobile
  mobile: {
    keywords: ['mobile', 'app', 'phone', 'ios', 'android'],
    responses: [
      '📱 Degens♧Den works perfectly on mobile! Responsive design, touch-optimized, and full functionality. Play anywhere!',
      '♧ Mobile-first design means you can gamble on the go. All games work great on your phone!',
    ],
  },

  // Joke/Fun
  joke: {
    keywords: ['joke', 'funny', 'laugh', 'meme', 'lol', 'haha'],
    responses: [
      '😂 Why did the degen go to the casino? Because the ATM was too close! 🎰',
      '♧ What\'s the difference between a degen and a casino? The casino has a business plan! 😅',
      '🎲 A degen walks into a casino... and doesn\'t walk out. That\'s not a joke, that\'s a lifestyle! 🐺',
    ],
  },

  // Luck
  luck: {
    keywords: ['luck', 'lucky', 'win', 'blessed', 'fortune', 'god'],
    responses: [
      '🍀 Luck is for casuals. We\'re all about that provably fair RNG, baby! 🎰',
      '♧ Luck is just statistics in disguise. Play smart, manage your bankroll, and the odds will smile on you!',
    ],
  },

  // Default
  default: {
    responses: [
      '♧ I didn\'t quite catch that. Ask me about games, deposits, OSRS, VIP, security, or anything else!',
      '🤔 Hmm, not sure about that one. Try asking about Dice, Keno, Crash, or how to deposit!',
      '♧ I\'m just a chatbot, but I know a lot about Degens♧Den! What else can I help with?',
    ],
  },
};

export const getChatbotResponse = (userMessage) => {
  if (!userMessage || userMessage.trim().length === 0) {
    return '♧ Say something! Ask me anything about Degens♧Den.';
  }

  const message = userMessage.toLowerCase().trim();

  // Find matching category
  for (const [category, data] of Object.entries(CHATBOT_RESPONSES)) {
    if (category === 'default') continue;

    const keywords = data.keywords || [];
    if (keywords.some(keyword => message.includes(keyword))) {
      const responses = data.responses || [];
      return responses[Math.floor(Math.random() * responses.length)];
    }
  }

  // Default response if no match
  const defaultResponses = CHATBOT_RESPONSES.default.responses;
  return defaultResponses[Math.floor(Math.random() * defaultResponses.length)];
};

export const isUserMessage = (message) => {
  return message && message.trim().length > 0;
};

export const formatBotMessage = (text) => {
  return {
    user: 'Degens♧Bot',
    text: text,
    isBot: true,
    timestamp: new Date().toISOString(),
  };
};
