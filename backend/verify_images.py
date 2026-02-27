import asyncio
from app.services.stylist import StylistService
from app.models.schemas import RecommendRequest
from app.core.config import Settings
from app.repositories.history import HistoryRepository

async def main():
    s = Settings()
    h = HistoryRepository('test_db.sqlite')
    await h.init()
    
    svc = StylistService(s, h)
    
    # Fake request
    req = RecommendRequest(
        user_id='test',
        style_preferences=['streetwear'],
        occasion='party'
    )
    req.gender = 'male'
    
    res = await svc.recommend(req)
    outfits = res.outfits
    
    for i, o in enumerate(outfits):
        print(f"Outfit {i+1}:")
        print(f"  Vibe: {o.outfit.tags}")
        print(f"  Color Palette: {o.outfit.palette}")
        print(f"  Dynamic Image: {o.outfit.image}")

asyncio.run(main())
