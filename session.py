import importlib
import json
import os
import sys
import time
import random
from core import registry

_RIDDLE_DIR = os.path.join(os.path.dirname(__file__), 'riddles')


def _load_all():
    sys.path.insert(0, os.path.dirname(__file__))

    for fname in os.listdir(_RIDDLE_DIR):
        if fname.endswith('.py') and not fname.startswith('_'):
            importlib.import_module(f'riddles.{fname[:-3]}')


class RiddlerSession:
    def __init__(self, riddle_type=None):
        _load_all()

        reg = registry()

        if not reg:
            raise RuntimeError('no riddles registered')

        cls = reg.get(riddle_type) if riddle_type else random.choice(list(reg.values()))

        if cls is None:
            raise ValueError(f'unknown riddle type: {riddle_type!r}')

        self._riddle = cls()
        self._attempts = 0
        self._log = []

    def start(self):
        data = self._riddle.generate()

        self._log.append({'event': 'start', 'ts': time.time(), 'type': data['type']})

        return data

    def attempt(self, answer):
        self._attempts += 1

        result = self._riddle.validate(answer)

        self._log.append({'event': 'attempt', 'ts': time.time(),
                          'answer_len': len(answer), 'ok': result.get('ok')})

        return result

    def get_hint(self):
        return self._riddle.hint(self._attempts)

    def dump_log(self):
        return json.dumps(self._log, indent=2)

    def meta(self):
        return self._riddle.meta()

def _banner():
    print('\n'
          '  ██████╗ ██╗██████╗ ██████╗ ██╗     ███████╗██████╗ \n'
          '  ██╔══██╗██║██╔══██╗██╔══██╗██║     ██╔════╝██╔══██╗\n'
          '  ██████╔╝██║██║  ██║██║  ██║██║     █████╗  ██████╔╝\n'
          '  ██╔══██╗██║██║  ██║██║  ██║██║     ██╔══╝  ██╔══██╗\n'
          '  ██║  ██║██║██████╔╝██████╔╝███████╗███████╗██║  ██║\n'
          '  ╚═╝  ╚═╝╚═╝╚═════╝ ╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝\n'
          '                         — can you outsmart the machine? —\n')


def run_cli(riddle_type=None):
    _banner()
    _load_all()
    available = list(registry().keys())

    print(f'  Available riddle types: {available}\n')

    if riddle_type is None:
        riddle_type = input('  Choose type (or Enter for random): ').strip() or None

    session = RiddlerSession(riddle_type)
    data = session.start()

    print('\n' + data['text'] + '\n')

    if data.get('metadata'):
        print(f'  [meta] {data["metadata"]}\n')

    deadline = session._riddle._deadline

    if deadline:
        print(f'  ⏱  You have {deadline} seconds total.\n')

    while True:
        raw = input('  Your answer (or "hint" / "quit"): ').strip()

        if not raw:
            continue

        if raw.lower() == 'quit':
            print('\n  Session aborted.\n')

            break

        if raw.lower() == 'hint':
            print(f'\n  💡  {session.get_hint()}\n')

            continue

        result = session.attempt(raw)

        if result.get('reason') == 'timeout':
            print(f'\n  ⌛  Time expired after {result["elapsed"]:.1f}s.\n')

            break

        if result.get('ok') is None and result.get('phase') == 2:
            print(f'\n{result["prompt"]}\n')

            continue

        if not result['ok']:
            note = result.get('note') or result.get('reason') or ''

            print(f'\n  ❌  Wrong.  {note}  (elapsed={result["elapsed"]:.2f}s)\n')

            continue

        print(f'\n  ✅  CORRECT — {result["elapsed"]:.2f}s  entropy={result["entropy"]}\n')

        break


if __name__ == '__main__':
    run_cli(sys.argv[1] if len(sys.argv) > 1 else None)
