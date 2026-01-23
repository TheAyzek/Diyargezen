"""
Performans optimizasyon modülü
Lazy loading, caching, memory management
"""
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional, Callable, Tuple
from threading import Lock


class LRUCache:
    """LRU (Least Recently Used) cache implementasyonu"""
    
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.cache: Dict[str, Tuple[Any, float]] = {}
        self.lock = Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """Cache'den değer al"""
        with self.lock:
            if key in self.cache:
                value, _ = self.cache[key]
                # Son erişim zamanını güncelle
                self.cache[key] = (value, time.time())
                return value
        return None
    
    def set(self, key: str, value: Any) -> None:
        """Cache'e değer ekle"""
        with self.lock:
            # Eğer cache doluysa, en eski öğeyi sil
            if len(self.cache) >= self.max_size and key not in self.cache:
                # En eski öğeyi bul
                oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][1])
                del self.cache[oldest_key]
            
            self.cache[key] = (value, time.time())
    
    def clear(self) -> None:
        """Cache'i temizle"""
        with self.lock:
            self.cache.clear()
    
    def size(self) -> int:
        """Cache boyutunu döndür"""
        return len(self.cache)


class LazyDataLoader:
    """Lazy loading ile veri yükleme"""
    
    def __init__(self, loader_func: Callable[[], Dict[str, Any]]):
        self.loader_func = loader_func
        self._data: Optional[Dict[str, Any]] = None
        self._lock = Lock()
    
    def get(self) -> Dict[str, Any]:
        """Veriyi yükle (sadece ilk çağrıda)"""
        if self._data is None:
            with self._lock:
                if self._data is None:
                    self._data = self.loader_func()
        return self._data
    
    def clear(self) -> None:
        """Yüklenen veriyi temizle"""
        with self._lock:
            self._data = None
    
    def is_loaded(self) -> bool:
        """Veri yüklenmiş mi?"""
        return self._data is not None


# Global cache instance
_global_cache = LRUCache(max_size=200)


def cached_load_json(path: Path, use_cache: bool = True) -> Dict[str, Any]:
    """
    JSON dosyasını cache ile yükle
    
    Args:
        path: JSON dosya yolu
        use_cache: Cache kullanılsın mı?
    
    Returns:
        JSON verisi
    """
    cache_key = f"json:{path}"
    
    if use_cache:
        cached = _global_cache.get(cache_key)
        if cached is not None:
            return cached
    
    # Dosyayı yükle
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    
    if use_cache:
        _global_cache.set(cache_key, data)
    
    return data


def clear_cache() -> None:
    """Global cache'i temizle"""
    _global_cache.clear()


def get_cache_stats() -> Dict[str, Any]:
    """Cache istatistiklerini döndür"""
    return {
        "size": _global_cache.size(),
        "max_size": _global_cache.max_size
    }


class PerformanceMonitor:
    """Performans izleme sınıfı"""
    
    def __init__(self):
        self.timings: Dict[str, list] = {}
        self.lock = Lock()
    
    def start_timer(self, operation: str) -> float:
        """Zamanlayıcı başlat"""
        return time.time()
    
    def end_timer(self, operation: str, start_time: float) -> float:
        """Zamanlayıcı bitir ve süreyi kaydet"""
        duration = time.time() - start_time
        with self.lock:
            if operation not in self.timings:
                self.timings[operation] = []
            self.timings[operation].append(duration)
        return duration
    
    def get_average_time(self, operation: str) -> Optional[float]:
        """Ortalama süreyi döndür"""
        with self.lock:
            if operation not in self.timings or not self.timings[operation]:
                return None
            return sum(self.timings[operation]) / len(self.timings[operation])
    
    def get_stats(self) -> Dict[str, Any]:
        """Tüm istatistikleri döndür"""
        with self.lock:
            stats = {}
            for operation, timings in self.timings.items():
                if timings:
                    stats[operation] = {
                        "count": len(timings),
                        "average": sum(timings) / len(timings),
                        "min": min(timings),
                        "max": max(timings),
                        "total": sum(timings)
                    }
            return stats
    
    def clear(self) -> None:
        """İstatistikleri temizle"""
        with self.lock:
            self.timings.clear()


# Global performance monitor
_performance_monitor = PerformanceMonitor()


def monitor_performance(operation: str):
    """Decorator: Fonksiyon performansını izle"""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            start_time = _performance_monitor.start_timer(operation)
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                _performance_monitor.end_timer(operation, start_time)
        return wrapper
    return decorator


def get_performance_stats() -> Dict[str, Any]:
    """Performans istatistiklerini döndür"""
    return _performance_monitor.get_stats()


def clear_performance_stats() -> None:
    """Performans istatistiklerini temizle"""
    _performance_monitor.clear()


class MemoryManager:
    """Memory yönetimi"""
    
    @staticmethod
    def cleanup_weak_references() -> int:
        """Zayıf referansları temizle"""
        # Python'ın garbage collector'ı otomatik yönetir
        # Bu fonksiyon sadece manuel temizleme için
        import gc
        collected = gc.collect()
        return collected
    
    @staticmethod
    def get_memory_usage() -> Dict[str, Any]:
        """Memory kullanımını döndür"""
        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
            mem_info = process.memory_info()
            return {
                "rss": mem_info.rss,  # Resident Set Size (bytes)
                "vms": mem_info.vms,  # Virtual Memory Size (bytes)
                "percent": process.memory_percent()
            }
        except ImportError:
            return {"error": "psutil not available"}


def optimize_json_parsing(data: str) -> Dict[str, Any]:
    """
    JSON parsing optimizasyonu
    Büyük dosyalar için daha hızlı parsing
    """
    # Python'ın json modülü zaten optimize edilmiş
    # Ancak büyük dosyalar için streaming parser kullanılabilir
    return json.loads(data)


def batch_process(items: list, batch_size: int = 100, 
                  processor: Callable = None) -> list:
    """
    Büyük listeleri batch'ler halinde işle
    
    Args:
        items: İşlenecek öğeler
        batch_size: Batch boyutu
        processor: İşleme fonksiyonu
    
    Returns:
        İşlenmiş öğeler
    """
    if processor is None:
        return items
    
    results = []
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        batch_results = [processor(item) for item in batch]
        results.extend(batch_results)
    
    return results

