import asyncio
from app.services.outfit_scoring import OutfitCatalog, OutfitScoringEngine, ScoringContext

catalog = OutfitCatalog()
engine = OutfitScoringEngine()

def test_case(f, gender, vibe, occasion, culture=""):
    ctx = ScoringContext(
        occasion=occasion,
        style_preferences=[vibe],
        budget="mid",
        skin_tone=None,
        color_palette=[],
        vibe=vibe,
        palette_temperature="warm",
        culture=culture,
        gender=gender
    )
    results = engine.score(catalog.list_candidates(), ctx)
    f.write(f"\n--- {gender.upper()} + {vibe.upper()} + {occasion.upper()} + {culture.upper()} ---\n")
    if results:
        for r in results[:2]:
            f.write(f"[{r.score}] {r.outfit.items[0].name} (Tags: {r.outfit.tags}) (Culture: {r.outfit.culture})\n")
    else:
        f.write("NO OUTFITS FOUND\n")

with open('out_clean.txt', 'w', encoding='utf-8') as f:
    test_case(f, "male", "minimal", "work", "")
    test_case(f, "female", "party", "party", "")
    test_case(f, "male", "minimal", "work", "indian")
