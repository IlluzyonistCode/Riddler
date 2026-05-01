import random
from core import BaseRiddle, riddle

def _make_chain(rng):
    names = rng.sample(['Ava', 'Bram', 'Cleo', 'Dex', 'Ezra', 'Fay', 'Gil', 'Hana'], 5)
    items = rng.sample(['a RED box', 'a BLUE sphere', 'a GREEN cube',
                        'a YELLOW prism', 'a WHITE cylinder'], 5)
    assignment = dict(zip(names, items))

    directly_pinned = {names[1], names[2]}

    clues = [
        f'{names[0]} does not have {items[1]}.',
        f'{names[1]} has the item that is not {items[0].split()[-1].lower()} and not {items[2].split()[-1].lower()}.',
        f'{names[2]} has {items[2]}.',
        f'The person with {items[0]} is not {names[3]}.',
        f'{names[3]} and {names[4]} both have items that are NOT {items[3].split()[-1].lower()}.'
    ]

    noise = [
        f'Somewhere in the room there is a {rng.choice(["clock", "mirror", "lamp"])}.',
        f'The temperature is {"mild" if rng.random() > .5 else "cool"}.',
        f'{rng.choice(names)} once owned a different item in a past session.',
        f'This statement has {"exactly" if rng.random() > .5 else "approximately"} {rng.randint(6, 12)} words.'
    ]

    all_clues = clues + rng.sample(noise, 2)
    rng.shuffle(all_clues)

    safe_targets = [n for n in names if n not in directly_pinned]
    target = rng.choice(safe_targets)
    correct_item = assignment[target]

    return all_clues, target, correct_item, assignment


@riddle('deduction')
class DeductionRiddle(BaseRiddle):
    def generate(self):
        self._deadline = 120

        rng = random.Random(self._seed)
        clues, target, answer, _ = _make_chain(rng)

        self._lock(answer)

        clue_block = '\n'.join(
            f'│  [{i+1:02d}]  {c:<56}│' for i, c in enumerate(clues)
        )

        text = (
            f'┌─ DEDUCTION ENGINE ──────────────────────────────────────────────┐\n'
            f'│  Five individuals each hold exactly one unique item.             │\n'
            f'│  Some clues below are genuine.  Some are noise.                 │\n'
            f'│                                                                   │\n'
            + clue_block
            + f'\n│                                                                   │\n'
            f'│  ❓  What item does {target.upper():<10} hold?                     │\n'
            f'│  Answer with the full description  (e.g. "a RED box").           │\n'
            f'└─────────────────────────────────────────────────────────────────┘'
        )

        return {
            'text': text,
            'type': 'deduction',
            'target': target,
            'metadata': {'n_noise_clues': 2, 'n_real_clues': 5},
        }

    def hint(self, attempt_n):
        return [
            'Identify noise clues first — they reference the environment or time.',
            'Use elimination: start with the clue that pins exactly one person/item.',
            'Noise clues often reference "the room", temperature, or past sessions.'
        ][min(attempt_n, 2)]
