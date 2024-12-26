import hashlib
import requests

class BloomFilter:
    def __init__(self, size, hash_count):
        self.size = size
        self.hash_count = hash_count
        self.bit_array = [0] * size

    def _hashes(self, item):
        hashes = []
        for i in range(self.hash_count):
            digest = hashlib.sha256((item + str(i)).encode()).hexdigest()
            index = int(digest, 16) % self.size
            hashes.append(index)
        return hashes

    def add(self, item):
        for hash_index in self._hashes(item):
            self.bit_array[hash_index] = 1

    def __contains__(self, item):
        return all(self.bit_array[hash_index] for hash_index in self._hashes(item))


class CacheWithCustomBloomFilter:
    def __init__(self, bloom_size=1000, hash_count=5):
        self.bloom_filter = BloomFilter(size=bloom_size, hash_count=hash_count)
        self.cache = {}

    def fetch_page(self, url):
        if url in self.cache:
            print("Страница найдена в кэше.")
            return self.cache[url]

        if url in self.bloom_filter:
            print("URL найден в фильтре Блума. Загружаем и кэшируем страницу.")
            html = self._fetch_from_internet(url)
            if html:
                self.cache[url] = html
            return html

        print("URL не найден в фильтре Блума. Добавляем в фильтр.")
        self.bloom_filter.add(url)
        return self._fetch_from_internet(url)

    def _fetch_from_internet(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            print("Страница загружена из интернета.")
            return response.text
        except requests.RequestException as e:
            print(f"Ошибка при загрузке страницы: {e}")
            return None


if __name__ == "__main__":
    cache_system = CacheWithCustomBloomFilter(bloom_size=1000, hash_count=3)

    url1 = "https://www.example.com"
    url2 = "https://www.python.org"

    print("\nПервый запрос к url1:")
    print(cache_system.fetch_page(url1))

    print("\nВторой запрос к url1:")
    print(cache_system.fetch_page(url1))

    print("\nПервый запрос к url2:")
    print(cache_system.fetch_page(url2))

    print("\nВторой запрос к url2:")
    print(cache_system.fetch_page(url2))
