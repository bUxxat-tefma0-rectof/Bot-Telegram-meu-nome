from threading import Lock
from datetime import datetime, timedelta
from typing import Any, Optional, Dict

class CacheService:
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._cache = {}
            cls._instance._expiracoes = {}
        return cls._instance
    
    def set(self, chave: str, valor: Any, ttl_segundos: int = 300) -> bool:
        with self._lock:
            self._cache[chave] = valor
            self._expiracoes[chave] = datetime.now() + timedelta(seconds=ttl_segundos)
            return True
    
    def get(self, chave: str, default: Any = None) -> Optional[Any]:
        with self._lock:
            if chave in self._expiracoes:
                if datetime.now() > self._expiracoes[chave]:
                    self.delete(chave)
                    return default
            return self._cache.get(chave, default)
    
    def delete(self, chave: str) -> bool:
        with self._lock:
            self._cache.pop(chave, None)
            self._expiracoes.pop(chave, None)
            return True
    
    def clear(self) -> bool:
        with self._lock:
            self._cache.clear()
            self._expiracoes.clear()
            return True
    
    def has(self, chave: str) -> bool:
        return self.get(chave) is not None
    
    def get_all(self) -> Dict:
        with self._lock:
            return dict(self._cache)
    
    def limpar_expirados(self) -> int:
        count = 0
        agora = datetime.now()
        with self._lock:
            for chave in list(self._expiracoes.keys()):
                if agora > self._expiracoes[chave]:
                    self.delete(chave)
                    count += 1
        return count

cache = CacheService()
