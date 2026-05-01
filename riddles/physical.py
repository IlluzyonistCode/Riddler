import hashlib
import time
import random
from core import BaseRiddle, riddle, _salted_hash

def _derive_target(hour, minute, temp, rolls, rng):
    op1 = rng.choice(['+', '*', '^'])
    op2 = rng.choice(['+', '-', '*'])

    base = hour * minute if minute else hour + 1

    if op1 == '+':
        v1 = base + temp

    elif op1 == '*':
        v1 = base * (temp % 13 + 1)

    else:
        v1 = (base ^ temp)

    roll_sum = sum(rolls)

    if op2 == '+':
        v2 = v1 + roll_sum

    elif op2 == '-':
        v2 = abs(v1 - roll_sum)

    else:
        v2 = v1 * (roll_sum % 7 + 1)

    return v2, op1, op2, base, roll_sum

def _build_puzzle(T, rng):
    k1 = rng.randint(2, 9)
    k2 = rng.randint(11, 37)
    k3 = rng.randint(3, 8)

    a = T * k1
    b = a + k2
    c = b - (T * (k1 - 1))
    d = c * k3
    answer = d // k3

    steps = (
        f'Let X = your derived target T (computed from your local data).\n'
        f'\n'
        f'  Step 1: Multiply X by {k1}.             Call this A.\n'
        f'  Step 2: Add {k2} to A.                  Call this B.\n'
        f'  Step 3: Subtract (X × {k1 - 1}) from B. Call this C.\n'
        f'  Step 4: Multiply C by {k3}.             Call this D.\n'
        f'  Step 5: Integer-divide D by {k3}.       This is your final answer.\n'
    )

    return steps, str(answer)


@riddle('physical')
class PhysicalRiddle(BaseRiddle):
    def __init__(self):
        super().__init__()

        self._phase = 1
        self._n_rolls = None
        self._unit = None
        self._pending_rng = None

    def generate(self):
        self._deadline = 180

        rng = random.Random(self._seed)

        self._n_rolls = rng.randint(3, 5)
        self._unit = rng.choice(['°C', '°F'])
        self._pending_rng = rng
        self._phase = 1

        text = '\n'.join([
            '┌─ PHYSICAL CONTEXT ENGINE ─────────────────────────────────────────┐',
            '│  This riddle is anchored to YOUR physical environment right now.   │',
            '│  No AI, search engine, or database can answer for you.             │',
            '│                                                                     │',
            '│  Before the puzzle is revealed, provide three data points:         │',
            '│                                                                     │',
            f'│  A) Your current local time in HH:MM format (24-hour clock).      │',
            f'│  B) The temperature outside your window right now, in {self._unit:3s}.      │',
            f'│  C) Roll a standard 6-sided die {self._n_rolls} times.                       │',
            f'│     Enter the results as a sequence, e.g.: 3 1 4 1 5             │',
            '│                                                                     │',
            '│  Format your answer EXACTLY as:                                    │',
            '│    TIME=HH:MM TEMP=N ROLLS=d1 d2 d3 ...                           │',
            '│  Example:  TIME=14:37 TEMP=22 ROLLS=3 1 4                         │',
            '│                                                                     │',
            f'│  ⏱  {self._deadline}s total for both phases.                              │',
            '└─────────────────────────────────────────────────────────────────────┘'
        ])

        return {
            'text':  text,
            'type':  'physical',
            'phase': 1,
            'metadata': {
                'n_rolls': self._n_rolls,
                'unit':    self._unit
            }
        }

    def _parse_phase1(self, raw):
        parts = {}

        for token in raw.upper().split():
            if '=' in token:
                k, _, v = token.partition('=')
                parts[k.strip()] = v.strip()

        if 'TIME' not in parts:
            raise ValueError('missing TIME=')

        if 'TEMP' not in parts:
            raise ValueError('missing TEMP=')

        time_raw = parts['TIME']

        if ':' not in time_raw:
            raise ValueError('TIME must be HH:MM')

        h, m = time_raw.split(':', 1)
        hour, minute = int(h), int(m)

        temp = int(parts['TEMP'])

        rolls_part = raw.upper().split('ROLLS=', 1)

        if len(rolls_part) < 2:
            raise ValueError('missing ROLLS=')

        rolls = [int(x) for x in rolls_part[1].split() if x.isdigit()]

        if len(rolls) != self._n_rolls:
            raise ValueError(f'expected {self._n_rolls} die rolls, got {len(rolls)}')

        for r in rolls:
            if not 1 <= r <= 6:
                raise ValueError(f'die value {r} out of range 1-6')

        return hour, minute, temp, rolls

    def validate(self, answer):
        if self._timed_out():
            return {'ok': False, 'reason': 'timeout', 'elapsed': self._elapsed()}

        if self._phase == 1:
            try:
                hour, minute, temp, rolls = self._parse_phase1(answer)
            except Exception as e:
                return {
                    'ok': False,
                    'reason': f'parse error: {e}',
                    'elapsed': round(self._elapsed(), 4)
                }

            rng = self._pending_rng
            T, op1, op2, base, roll_sum = _derive_target(hour, minute, temp, rolls, rng)
            steps, final_answer = _build_puzzle(T, rng)

            self._lock(final_answer)
            self._phase = 2

            unit = self._unit

            text = '\n'.join([
                '┌─ PHYSICAL CONTEXT ENGINE — PHASE 2 ───────────────────────────────┐',
                '│  Local data received.  Computing your personal target T...         │',
                '│                                                                     │',
                f'│  Your inputs:  time={hour:02d}:{minute:02d}  temp={temp}{unit}  '
                f'rolls={" ".join(str(r) for r in rolls)}',
                '│                                                                     │',
                f'│  Derivation of T (session-specific formula):                      │',
                f'│    base = hour × minute =  {hour} × {minute} =  {base}      │',
                f'│    v1 = base  {op1}  temp =  {base} {op1} {temp}           │',
                f'│    roll_sum = {roll_sum}  (sum of your die rolls)                  │',
                f'│    T = v1  {op2}  roll_sum                                  │',
                '│                                                                     │',
                '│  Now solve this procedure using YOUR value of T:                   │',
                '│                                                                     │',
                *[f'│  {l}' for l in steps.split('\n')],
                '│                                                                     │',
                '│  Answer with the final integer only.                               │',
                '└─────────────────────────────────────────────────────────────────────┘'
            ])

            return {
                'ok': None,
                'phase': 2,
                'prompt': text,
                'elapsed': round(self._elapsed(), 4)
            }

        result = super().validate(answer)

        if not result['ok']:
            cleaned = answer.strip().rstrip('.')

            if _salted_hash(cleaned, self._salt) == self._answer_hash:
                result['ok'] = True

        return result

    def hint(self, attempt_n):
        if self._phase == 1:
            return f'Format: TIME=HH:MM TEMP=N ROLLS=d1 d2 ... ({self._n_rolls} dice values 1-6)'

        return [
            'Compute T from the derivation shown, then run the 5 steps on paper.',
            'Each step must use the exact T you derived — not an estimate.',
            'Integer division in Step 5 means discard any remainder.'
        ][min(attempt_n, 2)]
