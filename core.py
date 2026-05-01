import socket
import hashlib
import json
import os
import math
import time
import random
from abc import ABC, abstractmethod

_REGISTRY = {}


def riddle(name):
    def decorator(cls):
        _REGISTRY[name] = cls

        return cls

    return decorator

def registry():
    return dict(_REGISTRY)

def _system_seed():
    ts = str(time.time_ns())
    pid = str(os.getpid())
    rand = os.urandom(16).hex()

    try:
        host = socket.gethostbyname(socket.gethostname())
    except Exception:
        host = '127.0.0.1'

    raw = f'{ts}:{pid}:{rand}:{host}'

    return hashlib.sha256(raw.encode()).hexdigest()

def _salted_hash(answer, salt):
    normalized = answer.strip().lower()
    payload = f'{salt}|{normalized}'

    return hashlib.blake2b(payload.encode(), digest_size=32).hexdigest()

def _entropy_score(text):
    if not text:
        return 0.0

    freq = {}

    for ch in text:
        freq[ch] = freq.get(ch, 0) + 1

    n = len(text)

    return round(-sum((c / n) * math.log2(c / n) for c in freq.values()), 4)


class BaseRiddle(ABC):
    def __init__(self):
        self._seed = _system_seed()
        self._salt = os.urandom(24).hex()
        self._born_at = time.monotonic()
        self._deadline = None
        self._answer_hash = None

    def _lock(self, canonical_answer):
        self._answer_hash = _salted_hash(canonical_answer, self._salt)

    def _elapsed(self):
        return time.monotonic() - self._born_at

    def _timed_out(self):
        return self._deadline and self._elapsed() > self._deadline

    @abstractmethod
    def generate(self):
        '''Return dict with at least {text, metadata}'''

    @abstractmethod
    def hint(self, attempt_n):
        '''Return hint string for attempt number attempt_n'''

    def validate(self, answer):
        if self._timed_out():
            return {'ok': False, 'reason': 'timeout', 'elapsed': self._elapsed()}

        if self._answer_hash is None:
            raise RuntimeError('riddle not generated yet')

        candidate = _salted_hash(answer, self._salt)
        ok = candidate == self._answer_hash

        return {
            'ok': ok,
            'elapsed': round(self._elapsed(), 4),
            'entropy': _entropy_score(answer)
        }

    def meta(self):
        return {
            'class': self.__class__.__name__,
            'seed': self._seed[:16] + '…',
            'deadline': self._deadline
        }
