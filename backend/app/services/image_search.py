import logging
import random
import time
from typing import Dict, List, Optional
import httpx
from pydantic import BaseModel

from ..core.config import Settings

logger = logging.getLogger(__name__)

class ImageResult(BaseModel):
    url: str
    source: str
    photographer: Optional[str] = None

class ImageCache:
    def __init__(self):
        self._cache: Dict[str, Dict] = {}
        self._used_urls: set = set()
    
    def get(self, key: str) -> Optional[List[ImageResult]]:
        item = self._cache.get(key)
        if item and time.time() - item["timestamp"] < 600: # 10 minute cache
            return item["results"]
        return None
        
    def set(self, key: str, results: List[ImageResult]):
        self._cache[key] = {
            "timestamp": time.time(),
            "results": results
        }

    def mark_used(self, url: str):
        self._used_urls.add(url)
        
    def is_used(self, url: str) -> bool:
        return url in self._used_urls

# Global cache instance for the app lifecycle
_image_cache = ImageCache()

class ImageSearchService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.unsplash_key = settings.unsplash_access_key
        self.pexels_key = settings.pexels_api_key
        self.cache = _image_cache

    async def search_outfit_images(self, query: str) -> Optional[ImageResult]:
        """
        Search for an outfit image matching the query.
        Returns a single ImageResult, avoiding recently used images if possible.
        """
        logger.info(f"Searching for outfit image: '{query}'")
        
        # 1. Check cache for this exact query
        results = self.cache.get(query)
        
        # 2. If no cache, fetch from APIs
        if results is None:
            results = await self._fetch_from_apis(query)
            if results:
                self.cache.set(query, results)
                
        if not results:
            logger.warning(f"No images found for query: '{query}'")
            return None
            
        # 3. Pick an unused image if possible
        unused = [r for r in results if not self.cache.is_used(r.url)]
        
        if unused:
            chosen = random.choice(unused)
        else:
            # All cached images for this query were already used, just pick a random one
            chosen = random.choice(results)
            
        self.cache.mark_used(chosen.url)
        return chosen

    async def _fetch_from_apis(self, query: str) -> List[ImageResult]:
        results = []
        
        if self.unsplash_key:
            results = await self._search_unsplash(query)
            
        if not results and self.pexels_key:
            logger.info(f"Unsplash failed or returned nothing for '{query}', falling back to Pexels")
            results = await self._search_pexels(query)
            
        return results

    async def _search_unsplash(self, query: str) -> List[ImageResult]:
        url = "https://api.unsplash.com/search/photos"
        params = {
            "query": query,
            "per_page": 10,
            "orientation": "portrait"
        }
        headers = {
            "Authorization": f"Client-ID {self.unsplash_key}",
            "Accept-Version": "v1"
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, params=params, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                
                results = []
                for item in data.get("results", []):
                    results.append(ImageResult(
                        url=item["urls"]["regular"],
                        source="unsplash",
                        photographer=item["user"]["name"]
                    ))
                return results
        except Exception as e:
            logger.error(f"Unsplash API error: {e}")
            return []

    async def _search_pexels(self, query: str) -> List[ImageResult]:
        url = "https://api.pexels.com/v1/search"
        params = {
            "query": query,
            "per_page": 10,
            "orientation": "portrait"
        }
        headers = {
            "Authorization": self.pexels_key
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, params=params, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                
                results = []
                for item in data.get("photos", []):
                    results.append(ImageResult(
                        url=item["src"]["large"],
                        source="pexels",
                        photographer=item["photographer"]
                    ))
                return results
        except Exception as e:
            logger.error(f"Pexels API error: {e}")
            return []
