import urllib.request
import json
import random
from core import BaseRiddle, riddle, _system_seed

_COINS = ['bitcoin', 'ethereum', 'solana', 'dogecoin', 'ripple']


def _fetch_prices(coins):
    ids = ','.join(coins)
    url = f'https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd'

    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Riddler/1.0'})

        with urllib.request.urlopen(req, timeout=5) as r:
            return json.loads(r.read())
    except Exception:
        rng = random.Random(_system_seed())

        base = {
            'bitcoin': 60000,
            'ethereum': 3000,
            'solana': 140,
            'dogecoin': 0.14,
            'ripple': 0.55
        }

        return {k: {'usd': round(v * rng.uniform(0.9, 1.1), 2)} for k, v in base.items()}


@riddle('market')
class MarketRiddle(BaseRiddle):
    def generate(self):
        self._deadline = 45

        prices = _fetch_prices(_COINS)
        rng = random.Random(self._seed)

        swings = {coin: round(rng.uniform(-8, 15), 2) for coin in _COINS}
        gains = {
            coin: round(prices[coin]['usd'] * (1 + swings[coin] / 100), 2)
            for coin in _COINS
        }

        winner = max(gains, key=gains.__getitem__)

        self._lock(winner)

        display = _COINS[:]
        rng.shuffle(display)
        lines = [
            f'  {c.upper():10s}  ${prices[c]["usd"]:>10,.2f}   {swings[c]:+.2f}%'
            for c in display
        ]

        text = (
            '┌─ MARKET ORACLE ──────────────────────────────────────────────┐\n'
            '│  Equal USD value held in each asset.  Market moves.          │\n'
            '│                                                               │\n'
            '│  Asset         Price (USD)     Shift                         │\n'
            + '\n'.join(f'│{l}  │' for l in lines)
            + '\n│                                                               │\n'
            '│  Which coin ends with the highest absolute USD value?        │\n'
            '│  Answer with the full lowercase name.                        │\n'
            '└───────────────────────────────────────────────────────────────┘'
        )

        return {
            'text': text,
            'type': 'market',
            'metadata': {'prices': {c: prices[c]['usd'] for c in _COINS}, 'swings': swings}
        }

    def hint(self, attempt_n):
        return [
            'Think in absolute dollar values, not percentages.',
            'Multiply base price by (1 + shift/100) for each coin.',
            'A small % on a large price often beats a large % on a tiny price.'
        ][min(attempt_n, 2)]
