import requests
from config import settings

class ReverseSearchAdapter:
    """
    Reverse Image Search Adapter.
    Integrates external reverse search APIs (SerpApi / Google Lens / Google Vision)
    and normalizes results into a unified internal format.
    """

    def search_by_url(self, image_url: str) -> list:
        if not settings.SERP_API_KEY:
            # Fallback mock results for offline/development environment
            return [
                {
                    "source_url": "https://example.com/art/digital-illustration-sample",
                    "page_title": "Digital Art Portfolio Showcase",
                    "thumbnail_url": image_url,
                    "match_confidence": 0.96,
                    "domain_name": "example.com"
                },
                {
                    "source_url": "https://stockphotos.org/preview/nature-view-102",
                    "page_title": "High Resolution Landscape Photography",
                    "thumbnail_url": image_url,
                    "match_confidence": 0.88,
                    "domain_name": "stockphotos.org"
                },
                {
                    "source_url": "https://socialmedia.com/post/982347192",
                    "page_title": "Viral Post Discussion Thread",
                    "thumbnail_url": image_url,
                    "match_confidence": 0.79,
                    "domain_name": "socialmedia.com"
                }
            ]

        try:
            params = {
                "engine": "google_lens",
                "url": image_url,
                "api_key": settings.SERP_API_KEY
            }
            response = requests.get("https://serpapi.com/search", params=params, timeout=10)
            data = response.json()

            results = []
            for item in data.get("visual_matches", []):
                results.append({
                    "source_url": item.get("link", ""),
                    "page_title": item.get("title", "Untitled Page"),
                    "thumbnail_url": item.get("thumbnail", ""),
                    "match_confidence": 0.90,
                    "domain_name": item.get("source", "unknown")
                })
            return results
        except Exception as e:
            print(f"Reverse search error: {e}")
            return []

reverse_search_service = ReverseSearchAdapter()
