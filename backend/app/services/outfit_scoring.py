from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Iterable

from ..models.schemas import Outfit, OutfitItem, ScoredOutfit, SkinTone

if TYPE_CHECKING:
    from .user_memory import UserProfile
from ..utils.hashing import stable_hash


@dataclass(frozen=True)
class ScoringContext:
    occasion: str | None
    style_preferences: list[str]
    budget: str | None
    skin_tone: SkinTone | None
    color_palette: list[str]
    vibe: str | None
    palette_temperature: str | None  # "warm" | "cool" | None
    culture: str | None = None
    gender: str | None = None
    user_profile: UserProfile | None = None


class OutfitCatalog:
    """
    Expanded in-memory catalog with 30+ outfits covering all vibes and occasions.
    """

    def list_candidates(self) -> list[Outfit]:
        return [
            # ── STREETWEAR ──────────────────────────────────────────
            _mk("Oversized Graphic Tee", "Stussy", "₹2,800", "top", ["black"], ["streetwear", "bold"],
                 "Wide Leg Cargo Pants", "Carhartt WIP", "₹5,500", "bottom", ["olive"], ["streetwear"],
                 "Chunky Platform Sneakers", "New Balance 550", "₹6,200", "shoes", ["white"], ["clean"],
                 tags=["street", "streetwear", "modern", "concert", "party"],
                 image="https://images.unsplash.com/photo-1520975916090-3105956dac38?w=1200&auto=format",
                 trend=0.85, tier="mid", gender="unisex"),
            _mk("Black Bomber Jacket", "Alpha Industries", "₹8,900", "top", ["black"], ["streetwear", "edgy"],
                 "Distressed Slim Jeans", "Levi's", "₹3,200", "bottom", ["charcoal"], ["street"],
                 "High-top Sneakers", "Nike Dunk", "₹7,500", "shoes", ["white", "black"], ["hype"],
                 tags=["street", "streetwear", "edgy", "concert", "party"],
                 image="https://images.unsplash.com/photo-1520975693413-35c5a271c6b4?w=1200&auto=format",
                 trend=0.80, tier="mid", gender="male"),
            _mk("Tie-Dye Hoodie", "Stussy", "₹4,500", "top", ["pastel-blue", "white"], ["street", "casual"],
                 "Relaxed Joggers", "Nike", "₹3,000", "bottom", ["grey"], ["athleisure"],
                 "Retro Runners", "Asics Gel", "₹5,800", "shoes", ["white", "grey"], ["retro"],
                 tags=["street", "streetwear", "casual", "everyday", "school"],
                 image="https://images.unsplash.com/photo-1518310383802-640c2de311b2?w=1200&auto=format",
                 trend=0.75, tier="budget", gender="unisex"),
            # ── MINIMALIST ──────────────────────────────────────────
            _mk("White Linen Shirt", "COS", "₹3,900", "top", ["white"], ["breathable", "classic"],
                 "Navy Chinos", "Uniqlo", "₹2,200", "bottom", ["navy"], ["smart-casual"],
                 "Brown Loafers", "Clarks", "₹4,800", "shoes", ["brown"], ["leather"],
                 tags=["minimal", "classic", "smart-casual", "office", "work", "date"],
                 image="https://images.unsplash.com/photo-1539008835657-9e8e9680c956?w=1200&auto=format",
                 trend=0.60, tier="mid", gender="male"),
            _mk("Black Crew-neck Tee", "Muji", "₹1,200", "top", ["black"], ["minimal"],
                 "Light-wash Jeans", "Levi's", "₹2,800", "bottom", ["light-blue"], ["everyday"],
                 "White Sneakers", "Common Projects", "₹8,500", "shoes", ["white"], ["clean"],
                 tags=["minimal", "casual", "everyday", "clean", "school"],
                 image="https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=1200&auto=format",
                 trend=0.70, tier="mid", gender="unisex"),
            _mk("Camel Turtleneck", "COS", "₹4,200", "top", ["tan"], ["elegant"],
                 "Charcoal Wool Trousers", "Zara", "₹3,500", "bottom", ["charcoal"], ["tailored"],
                 "Black Chelsea Boots", "Dr. Martens", "₹9,200", "shoes", ["black"], ["winter"],
                 tags=["minimal", "elevated", "date", "winter", "classic"],
                 image="https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=1200&auto=format",
                 trend=0.55, tier="premium", gender="unisex"),
            _mk("Charcoal Blazer", "H&M", "₹3,800", "top", ["charcoal"], ["tailored"],
                 "White Tee + Grey Trousers", "Uniqlo", "₹2,000", "bottom", ["white", "grey"], ["clean"],
                 "Black Loafers", "Aldo", "₹3,500", "shoes", ["black"], ["leather"],
                 tags=["minimal", "work", "office", "clean", "cool"],
                 image="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=1200&auto=format",
                 trend=0.62, tier="mid", gender="male"),
            # ── Y2K ─────────────────────────────────────────────────
            _mk("Butterfly Crop Top", "Shein", "₹800", "top", ["pink", "white"], ["y2k", "playful"],
                 "Low-rise Flare Jeans", "Zara", "₹2,500", "bottom", ["light-blue"], ["y2k"],
                 "Platform Sandals", "Steve Madden", "₹4,200", "shoes", ["white"], ["y2k"],
                 tags=["y2k", "party", "playful", "concert"],
                 image="https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=1200&auto=format",
                 trend=0.90, tier="budget", gender="female"),
            _mk("Metallic Halter Top", "ASOS", "₹1,500", "top", ["silver"], ["y2k", "bold"],
                 "Mini Pleated Skirt", "H&M", "₹1,200", "bottom", ["pink"], ["y2k"],
                 "Chunky Platform Heels", "Dolls Kill", "₹3,800", "shoes", ["silver"], ["party"],
                 tags=["y2k", "party", "concert", "bold"],
                 image="https://images.unsplash.com/photo-1529139574466-a303027c1d8b?w=1200&auto=format",
                 trend=0.88, tier="budget", gender="female"),
            _mk("Velvet Track Jacket", "Juicy Couture", "₹5,200", "top", ["pink"], ["y2k", "retro"],
                 "Matching Velvet Pants", "Juicy Couture", "₹4,800", "bottom", ["pink"], ["y2k"],
                 "White Platform Sneakers", "Fila", "₹3,500", "shoes", ["white"], ["retro"],
                 tags=["y2k", "casual", "school", "retro"],
                 image="https://images.unsplash.com/photo-1509631179647-0177331693ae?w=1200&auto=format",
                 trend=0.82, tier="mid", gender="female"),
            # ── COTTAGECORE ─────────────────────────────────────────
            _mk("Floral Midi Dress", "Free People", "₹6,500", "top", ["beige", "pink"], ["cottagecore"],
                 "Woven Leather Sandals", "Madewell", "₹3,800", "shoes", ["tan"], ["earthy"],
                 "Straw Tote Bag", "Lack of Color", "₹2,500", "accessory", ["beige"], ["boho"],
                 tags=["cottagecore", "casual", "school", "warm", "earthy", "date"],
                 image="https://images.unsplash.com/photo-1523381210434-271e8be1f52b?w=1200&auto=format",
                 trend=0.65, tier="mid", gender="female"),
            _mk("Puff-sleeve Blouse", "& Other Stories", "₹3,200", "top", ["white"], ["cottagecore", "romantic"],
                 "Linen Wide-leg Pants", "Zara", "₹2,800", "bottom", ["beige"], ["breathable"],
                 "Espadrille Wedges", "Soludos", "₹4,500", "shoes", ["tan"], ["summer"],
                 tags=["cottagecore", "date", "school", "romantic"],
                 image="https://images.unsplash.com/photo-1612336307429-8a898d10e223?w=1200&auto=format",
                 trend=0.58, tier="mid", gender="female"),
            _mk("Knit Cardigan", "Mango", "₹2,800", "top", ["olive"], ["cozy", "cottagecore"],
                 "Corduroy A-line Skirt", "Uniqlo", "₹1,800", "bottom", ["brown"], ["vintage"],
                 "Ankle Boots", "Clarks", "₹5,500", "shoes", ["dark-brown"], ["leather"],
                 tags=["cottagecore", "school", "cozy", "winter"],
                 image="https://images.unsplash.com/photo-1509631179647-0177331693ae?w=1200&auto=format&sat=-10",
                 trend=0.52, tier="budget", gender="female"),
            # ── DARK ACADEMIA ───────────────────────────────────────
            _mk("Tweed Blazer", "Ralph Lauren", "₹12,000", "top", ["brown", "charcoal"], ["tailored", "academic"],
                 "Pleated Trousers", "Massimo Dutti", "₹4,800", "bottom", ["charcoal"], ["classic"],
                 "Oxford Brogues", "Dr. Martens", "₹8,500", "shoes", ["dark-brown"], ["leather"],
                 tags=["dark-academia", "classic", "work", "office", "school"],
                 image="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=1200&auto=format&sat=-30",
                 trend=0.68, tier="premium", gender="male"),
            _mk("Merino Wool Vest", "COS", "₹5,500", "top", ["charcoal"], ["layered", "academic"],
                 "White Oxford Shirt", "Brooks Brothers", "₹4,200", "top", ["white"], ["classic"],
                 "Slim Wool Trousers", "Zara", "₹3,200", "bottom", ["navy"], ["tailored"],
                 tags=["dark-academia", "school", "classic", "work"],
                 image="https://images.unsplash.com/photo-1516826957135-700dedea698c?w=1200&auto=format",
                 trend=0.60, tier="mid", gender="male"),
            _mk("Turtleneck Sweater", "H&M", "₹1,800", "top", ["deep-green"], ["cozy", "academic"],
                 "Plaid Wool Skirt", "Zara", "₹2,500", "bottom", ["brown", "charcoal"], ["classic"],
                 "Knee-high Boots", "Aldo", "₹6,800", "shoes", ["dark-brown"], ["leather"],
                 tags=["dark-academia", "school", "winter", "date"],
                 image="https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=1200&auto=format&sat=-20",
                 trend=0.56, tier="budget", gender="female"),
            # ── COQUETTE ────────────────────────────────────────────
            _mk("Satin Bow Blouse", "Reformation", "₹7,200", "top", ["pink"], ["coquette", "romantic"],
                 "High-waist Mini Skirt", "Zara", "₹1,800", "bottom", ["white"], ["delicate"],
                 "Strappy Kitten Heels", "Steve Madden", "₹4,200", "shoes", ["pink"], ["feminine"],
                 tags=["coquette", "date", "party", "romantic"],
                 image="https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=1200&auto=format",
                 trend=0.85, tier="mid", gender="female"),
            _mk("Lace Cami Top", "& Other Stories", "₹2,500", "top", ["white"], ["coquette", "delicate"],
                 "Silk Midi Skirt", "H&M", "₹2,200", "bottom", ["pastel-blue"], ["elegant"],
                 "Pearl-strap Sandals", "Zara", "₹2,800", "shoes", ["white"], ["feminine"],
                 tags=["coquette", "date", "school", "delicate"],
                 image="https://images.unsplash.com/photo-1529139574466-a303027c1d8b?w=1200&auto=format&sat=-10",
                 trend=0.78, tier="budget", gender="female"),
            _mk("Ruffle Wrap Dress", "Reformation", "₹9,500", "top", ["pink", "white"], ["coquette"],
                 "Ankle-strap Heels", "Jimmy Choo", "₹15,000", "shoes", ["beige"], ["premium"],
                 "Quilted Chain Bag", "Chanel", "₹25,000", "accessory", ["pink"], ["luxury"],
                 tags=["coquette", "party", "date", "elevated"],
                 image="https://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=1200&auto=format",
                 trend=0.80, tier="premium", gender="female"),
            # ── GRUNGE ──────────────────────────────────────────────
            _mk("Oversized Flannel Shirt", "Thrift", "₹900", "top", ["charcoal", "red"], ["grunge"],
                 "Ripped Black Jeans", "Levi's", "₹2,800", "bottom", ["black"], ["distressed"],
                 "Combat Boots", "Dr. Martens", "₹9,800", "shoes", ["black"], ["edgy"],
                 tags=["grunge", "concert", "party", "edgy"],
                 image="https://images.unsplash.com/photo-1520975693413-35c5a271c6b4?w=1200&auto=format&sat=-20",
                 trend=0.72, tier="budget", gender="unisex"),
            _mk("Band Graphic Tee", "Vintage", "₹1,200", "top", ["black"], ["grunge", "vintage"],
                 "Studded Leather Belt", "AllSaints", "₹3,500", "accessory", ["black"], ["edgy"],
                 "Platform Doc Martens", "Dr. Martens", "₹12,000", "shoes", ["black"], ["grunge"],
                 tags=["grunge", "concert", "street", "edgy"],
                 image="https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=1200&auto=format&sat=-30",
                 trend=0.68, tier="mid", gender="unisex"),
            _mk("Leather Moto Jacket", "AllSaints", "₹18,000", "top", ["black"], ["edgy", "grunge"],
                 "Fishnet Tights + Mini Skirt", "Zara", "₹1,500", "bottom", ["black"], ["bold"],
                 "Ankle Boots", "Steve Madden", "₹5,500", "shoes", ["black"], ["edgy"],
                 tags=["grunge", "party", "concert", "night-out"],
                 image="https://images.unsplash.com/photo-1518310383802-640c2de311b2?w=1200&auto=format&sat=-40",
                 trend=0.76, tier="premium", gender="female"),
            # ── COASTAL ─────────────────────────────────────────────
            _mk("Linen Camp Shirt", "Tommy Bahama", "₹4,200", "top", ["pastel-blue"], ["coastal", "breathable"],
                 "Khaki Shorts", "Uniqlo", "₹1,500", "bottom", ["tan"], ["casual"],
                 "Leather Slide Sandals", "Birkenstock", "₹4,500", "shoes", ["brown"], ["relaxed"],
                 tags=["coastal", "casual", "everyday", "warm"],
                 image="https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1200&auto=format",
                 trend=0.60, tier="mid", gender="male"),
            _mk("Striped Breton Tee", "Saint James", "₹3,800", "top", ["navy", "white"], ["coastal", "classic"],
                 "White Linen Pants", "Mango", "₹2,800", "bottom", ["white"], ["breathable"],
                 "White Espadrilles", "Soludos", "₹3,200", "shoes", ["white"], ["summer"],
                 tags=["coastal", "date", "casual", "clean"],
                 image="https://images.unsplash.com/photo-1523381210434-271e8be1f52b?w=1200&auto=format&hue=200",
                 trend=0.58, tier="mid", gender="unisex"),
            _mk("Oversized Gauze Shirt", "Zara", "₹1,800", "top", ["white"], ["coastal", "relaxed"],
                 "Denim Cut-off Shorts", "Levi's", "₹2,000", "bottom", ["light-blue"], ["summer"],
                 "Canvas Slip-ons", "Vans", "₹2,500", "shoes", ["white"], ["casual"],
                 tags=["coastal", "casual", "school", "everyday"],
                 image="https://images.unsplash.com/photo-1509631179647-0177331693ae?w=1200&auto=format&sat=10",
                 trend=0.55, tier="budget", gender="female"),
            # ── GYM / ATHLEISURE ────────────────────────────────────
            _mk("Cropped Hoodie", "Nike", "₹3,500", "top", ["grey"], ["athleisure", "cozy"],
                 "High-Waist Leggings", "Alo Yoga", "₹5,200", "bottom", ["black"], ["stretch"],
                 "Retro Running Shoes", "Asics Gel-1130", "₹5,800", "shoes", ["white", "grey"], ["retro"],
                 tags=["casual", "athleisure", "gym", "everyday"],
                 image="https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=1200&auto=format",
                 trend=0.72, tier="mid", gender="female"),
            _mk("Mesh Tank Top", "Under Armour", "₹1,800", "top", ["black"], ["sporty"],
                 "Training Shorts", "Nike", "₹2,200", "bottom", ["charcoal"], ["stretch"],
                 "Cross-training Shoes", "Reebok Nano", "₹6,500", "shoes", ["black"], ["performance"],
                 tags=["gym", "sporty", "athleisure"],
                 image="https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=1200&auto=format",
                 trend=0.55, tier="budget", gender="male"),
            # ── WORK / OFFICE ───────────────────────────────────────
            _mk("Pastel Blue Oxford", "Brooks Brothers", "₹4,500", "top", ["pastel-blue"], ["preppy"],
                 "Stone Chinos", "Dockers", "₹2,500", "bottom", ["stone"], ["clean"],
                 "Tan Derby Shoes", "Clarks", "₹5,200", "shoes", ["tan"], ["leather"],
                 tags=["office", "work", "preppy", "clean"],
                 image="https://images.unsplash.com/photo-1539008835657-9e8e9680c956?w=1200&auto=format&sat=10",
                 trend=0.58, tier="mid", gender="male"),
            _mk("Navy Button-down", "Ralph Lauren", "₹5,800", "top", ["navy"], ["classic"],
                 "Grey Pleated Trousers", "Massimo Dutti", "₹4,200", "bottom", ["grey"], ["elevated"],
                 "White Leather Sneakers", "Common Projects", "₹8,500", "shoes", ["white"], ["clean"],
                 tags=["work", "date", "classic", "elevated"],
                 image="https://images.unsplash.com/photo-1516826957135-700dedea698c?w=1200&auto=format",
                 trend=0.60, tier="premium", gender="male"),
            # ── DATE NIGHT ──────────────────────────────────────────
            _mk("Silk Slip Dress", "Reformation", "₹9,800", "top", ["deep-green"], ["elegant"],
                 "Strappy Heeled Sandals", "Stuart Weitzman", "₹8,500", "shoes", ["gold"], ["premium"],
                 "Structured Clutch", "Mansur Gavriel", "₹12,000", "accessory", ["black"], ["luxury"],
                 tags=["date", "elevated", "party", "elegant"],
                 image="https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=1200&auto=format&sat=10",
                 trend=0.75, tier="premium", gender="female"),
            _mk("Olive Bomber Jacket", "Alpha Industries", "₹7,500", "top", ["olive"], ["streetwear"],
                 "Beige Turtleneck", "COS", "₹3,200", "top", ["beige"], ["warm"],
                 "Black Tapered Trousers", "Zara", "₹2,800", "bottom", ["black"], ["sleek"],
                 tags=["street", "layered", "modern", "party", "date"],
                 image="https://images.unsplash.com/photo-1520975693413-35c5a271c6b4?w=1200&auto=format&sat=10",
                 trend=0.78, tier="mid", gender="male"),
            _mk("Deep Green Knit Sweater", "COS", "₹4,800", "top", ["deep-green"], ["cozy"],
                 "Charcoal Wool Trousers", "Massimo Dutti", "₹4,200", "bottom", ["charcoal"], ["tailored"],
                 "Dark Brown Boots", "Timberland", "₹7,500", "shoes", ["dark-brown"], ["winter"],
                 tags=["date", "winter", "cozy", "elevated"],
                 image="https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=1200&auto=format&sat=10",
                 trend=0.52, tier="mid", gender="male"),
            # ── BUDGET-FRIENDLY ─────────────────────────────────────
            _mk("Basic V-neck Tee", "H&M", "₹599", "top", ["white"], ["minimal", "budget"],
                 "Slim-fit Chinos", "Decathlon", "₹999", "bottom", ["navy"], ["everyday"],
                 "Canvas Sneakers", "Bata", "₹899", "shoes", ["white"], ["clean"],
                 tags=["casual", "everyday", "school", "minimal", "budget"],
                 image="https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=1200&auto=format&sat=-10",
                 trend=0.50, tier="budget", gender="male"),
            _mk("Denim Jacket", "H&M", "₹1,999", "top", ["light-blue"], ["casual"],
                 "Black Slim Jeans", "Zara", "₹1,800", "bottom", ["black"], ["everyday"],
                 "White Low-tops", "Converse", "₹2,500", "shoes", ["white"], ["classic"],
                 tags=["casual", "school", "street", "everyday", "budget"],
                 image="https://images.unsplash.com/photo-1520975916090-3105956dac38?w=1200&auto=format&sat=-10",
                 trend=0.65, tier="budget", gender="unisex"),

            # ── INDIAN ─────────────────────────────────────────────────
            _mk("Embroidered Kurta", "FabIndia", "₹2,200", "top", ["beige", "gold"], ["ethnic", "festive"],
                 "Churidar Pants", "Manyavar", "₹1,500", "bottom", ["white"], ["ethnic"],
                 "Mojari Juttis", "Needledust", "₹1,800", "shoes", ["gold", "brown"], ["ethnic"],
                 tags=["festive", "party", "date", "indian", "ethnic"],
                 image="https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=1200&auto=format",
                 trend=0.80, tier="mid", culture="indian", gender="male"),
            _mk("Silk Kurta Set", "Manyavar", "₹4,500", "top", ["navy", "gold"], ["festive", "wedding"],
                 "Dhoti Pants", "Manyavar", "₹2,200", "bottom", ["navy"], ["ethnic"],
                 "Kolhapuri Chappals", "Metro", "₹1,200", "shoes", ["brown"], ["ethnic", "classic"],
                 tags=["festive", "wedding", "party", "indian", "ethnic", "premium"],
                 image="https://images.unsplash.com/photo-1583391733981-8b530c480725?w=1200&auto=format",
                 trend=0.85, tier="premium", culture="indian", gender="male"),
            _mk("Banarasi Silk Saree", "FabIndia", "₹8,500", "top", ["deep-green", "gold"], ["festive", "wedding"],
                 "Silk Blouse", "Sabyasachi", "₹3,500", "bottom", ["deep-green"], ["ethnic"],
                 "Gold Heeled Sandals", "Inc.5", "₹2,800", "shoes", ["gold"], ["festive"],
                 tags=["festive", "wedding", "party", "indian", "saree", "premium"],
                 image="https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=1200&auto=format&sat=20",
                 trend=0.90, tier="premium", culture="indian", gender="female"),
            _mk("Printed Cotton Kurta", "W", "₹1,200", "top", ["olive", "white"], ["casual", "everyday"],
                 "Palazzo Pants", "Global Desi", "₹999", "bottom", ["white"], ["comfort"],
                 "Kolhapuri Flats", "Bata", "₹899", "shoes", ["brown", "tan"], ["ethnic"],
                 tags=["casual", "school", "everyday", "indian", "comfort", "budget"],
                 image="https://images.unsplash.com/photo-1583391733981-8b530c480725?w=1200&auto=format&sat=-10",
                 trend=0.70, tier="budget", culture="indian", gender="female"),

            # ── KOREAN ─────────────────────────────────────────────────
            _mk("Oversized Boxy Tee", "Ader Error", "₹3,800", "top", ["white"], ["korean", "oversized"],
                 "Wide-leg Trousers", "8Seconds", "₹2,800", "bottom", ["charcoal"], ["korean", "minimal"],
                 "Chunky Dad Sneakers", "Fila Disruptor", "₹4,500", "shoes", ["white"], ["korean"],
                 tags=["street", "korean", "minimal", "casual", "everyday"],
                 image="https://images.unsplash.com/photo-1520975916090-3105956dac38?w=1200&auto=format&hue=200",
                 trend=0.88, tier="mid", culture="korean", gender="unisex"),
            _mk("Layered Shirt Jacket", "Gentle Monster", "₹5,500", "top", ["beige", "stone"], ["korean", "layered"],
                 "Straight-fit Slacks", "8Seconds", "₹2,200", "bottom", ["charcoal"], ["korean"],
                 "Leather Loafers", "Common Projects", "₹6,500", "shoes", ["black"], ["minimal"],
                 tags=["dark-academia", "korean", "layered", "work", "date"],
                 image="https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=1200&auto=format&hue=150",
                 trend=0.82, tier="premium", culture="korean", gender="male"),
            _mk("Cropped Cardigan", "Cos", "₹3,200", "top", ["pastel-blue", "white"], ["korean", "soft"],
                 "High-waist Pleated Skirt", "Stylenanda", "₹2,500", "bottom", ["white"], ["korean", "feminine"],
                 "Platform Mary Janes", "Dr. Martens", "₹5,800", "shoes", ["black"], ["korean"],
                 tags=["coquette", "korean", "school", "date", "feminine"],
                 image="https://images.unsplash.com/photo-1539008835657-9e8e9680c956?w=1200&auto=format&hue=250",
                 trend=0.85, tier="mid", culture="korean", gender="female"),

            # ── MIDDLE EASTERN ─────────────────────────────────────────
            _mk("Embroidered Kaftan", "Raishma", "₹6,500", "top", ["white", "gold"], ["modest", "elegant"],
                 "Flowing Palazzo", "Aab", "₹3,200", "bottom", ["white"], ["modest"],
                 "Embellished Sandals", "Aldo", "₹3,500", "shoes", ["gold"], ["festive"],
                 tags=["festive", "modest", "party", "middle-eastern", "elegant"],
                 image="https://images.unsplash.com/photo-1539008835657-9e8e9680c956?w=1200&auto=format&sat=15",
                 trend=0.80, tier="premium", culture="middle_eastern", gender="female"),
            _mk("Structured Abaya", "Hanayen", "₹5,800", "top", ["black", "gold"], ["modest", "formal"],
                 "Wide-leg Trousers", "Aab", "₹2,500", "bottom", ["black"], ["modest"],
                 "Pointed Heels", "Jimmy Choo", "₹12,000", "shoes", ["black", "gold"], ["premium"],
                 tags=["work", "formal", "modest", "middle-eastern", "premium"],
                 image="https://images.unsplash.com/photo-1518310383802-640c2de311b2?w=1200&auto=format&sat=5",
                 trend=0.78, tier="premium", culture="middle_eastern", gender="female"),
            _mk("Linen Thobe Tunic", "Marks & Spencer", "₹3,500", "top", ["white", "beige"], ["modest", "relaxed"],
                 "Cotton Drawstring Pants", "Uniqlo", "₹1,800", "bottom", ["beige"], ["comfort"],
                 "Leather Slides", "Birkenstock", "₹4,200", "shoes", ["brown"], ["casual"],
                 tags=["casual", "everyday", "modest", "middle-eastern", "comfort"],
                 image="https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=1200&auto=format&sat=-5",
                 trend=0.72, tier="mid", culture="middle_eastern", gender="male"),

            # ── FUSION (Indo-Western & Cross-Cultural) ─────────────────
            _mk("Nehru Jacket", "Raymond", "₹4,500", "top", ["navy", "gold"], ["fusion", "festive"],
                 "Slim Chinos", "Zara", "₹2,200", "bottom", ["beige"], ["smart-casual"],
                 "Oxford Brogues", "Hush Puppies", "₹3,800", "shoes", ["brown"], ["classic"],
                 tags=["festive", "party", "date", "fusion", "indo-western"],
                 image="https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=1200&auto=format&sat=10",
                 trend=0.85, tier="mid", culture="fusion", gender="male"),
            _mk("Short Kurta", "FabIndia", "₹1,800", "top", ["white", "beige"], ["casual", "fusion"],
                 "Blue Denim Jeans", "Levi's", "₹2,500", "bottom", ["navy"], ["casual"],
                 "White Sneakers", "Nike Court", "₹4,000", "shoes", ["white"], ["clean"],
                 tags=["casual", "everyday", "school", "fusion", "indo-western"],
                 image="https://images.unsplash.com/photo-1583391733981-8b530c480725?w=1200&auto=format&sat=-5",
                 trend=0.80, tier="mid", culture="fusion", gender="unisex"),
            _mk("Draped Saree Gown", "Indya", "₹5,500", "top", ["deep-green", "gold"], ["fusion", "festive"],
                 "Fitted Blazer", "Zara", "₹4,000", "bottom", ["deep-green"], ["modern"],
                 "Stiletto Heels", "Aldo", "₹3,800", "shoes", ["gold"], ["glamour"],
                 tags=["party", "wedding", "date", "fusion", "glamour"],
                 image="https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=1200&auto=format&sat=25",
                 trend=0.88, tier="premium", culture="fusion", gender="female"),
            _mk("Korean-Western Layered Blazer", "Cos", "₹6,200", "top", ["charcoal", "white"], ["korean", "fusion"],
                 "Tapered Trousers", "Massimo Dutti", "₹3,800", "bottom", ["charcoal"], ["smart"],
                 "Minimal Leather Boots", "Common Projects", "₹8,500", "shoes", ["black"], ["premium"],
                 tags=["work", "date", "korean", "fusion", "minimal"],
                 image="https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=1200&auto=format&sat=5",
                 trend=0.82, tier="premium", culture="fusion", gender="male"),
            _mk("Modern Modest Tunic", "Aab", "₹3,800", "top", ["stone", "beige"], ["modest", "fusion"],
                 "Wide Culottes", "Uniqlo", "₹1,800", "bottom", ["charcoal"], ["comfort"],
                 "Block-heel Mules", "Charles & Keith", "₹2,800", "shoes", ["beige"], ["modern"],
                 tags=["casual", "work", "modest", "fusion", "comfort"],
                 image="https://images.unsplash.com/photo-1518310383802-640c2de311b2?w=1200&auto=format&sat=-5",
                 trend=0.75, tier="mid", culture="fusion", gender="female"),
        ]


def _mk(
    name1: str, brand1: str, price1: str, cat1: str, colors1: list[str], tags1: list[str],
    name2: str, brand2: str, price2: str, cat2: str, colors2: list[str], tags2: list[str],
    name3: str, brand3: str, price3: str, cat3: str, colors3: list[str], tags3: list[str],
    *,
    tags: list[str],
    image: str,
    trend: float,
    tier: str = "mid",
    culture: str = "western",
    gender: str = "unisex",
) -> Outfit:
    """Build an Outfit from 3 items with full product details."""
    outfit_items = [
        OutfitItem(category=cat1, name=name1, colors=colors1, tags=tags1, brand=brand1, price=price1,
                   image=f"https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=200&auto=format"),
        OutfitItem(category=cat2, name=name2, colors=colors2, tags=tags2, brand=brand2, price=price2,
                   image=f"https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=200&auto=format"),
        OutfitItem(category=cat3, name=name3, colors=colors3, tags=tags3, brand=brand3, price=price3,
                   image=f"https://images.unsplash.com/photo-1549298916-b41d501d3772?w=200&auto=format"),
    ]
    palette: list[str] = []
    for it in outfit_items:
        for c in it.colors:
            if c not in palette:
                palette.append(c)
    payload = {"items": [it.model_dump() for it in outfit_items], "tags": tags, "palette": palette, "image": image}
    outfit_id = stable_hash(payload)
    return Outfit(
        outfit_id=outfit_id, image=image, items=outfit_items,
        palette=palette, tags=tags, trend_score=trend, price_tier=tier,
        culture=culture, gender=gender,
    )


class OutfitScoringEngine:
    def score(self, candidates: Iterable[Outfit], ctx: ScoringContext) -> list[ScoredOutfit]:
        scored: list[ScoredOutfit] = []
        prefs = [p.strip().lower() for p in ctx.style_preferences if p.strip()]
        occasion = (ctx.occasion or "").strip().lower()
        desired_palette = [c.strip().lower() for c in (ctx.color_palette or []) if isinstance(c, str) and c.strip()]

        filtered = list(candidates)
        filtered = _apply_filters(filtered, desired_palette=desired_palette, vibe=ctx.vibe, occasion=occasion, culture=ctx.culture, gender=ctx.gender)

        for outfit in filtered:
            reasons: list[str] = []

            # Components (0..1)
            color_match = _color_match(desired_palette, outfit.palette, palette_temperature=ctx.palette_temperature)
            vibe_match = _vibe_match(ctx.vibe, outfit, prefs)
            occasion_match = _occasion_match(occasion, outfit)
            trend = float(outfit.trend_score or 0.5)
            hist_affinity = _history_affinity(outfit, ctx.user_profile)

            # Weighted score (0..100)
            score = 100.0 * (
                0.30 * color_match
                + 0.20 * vibe_match
                + 0.15 * occasion_match
                + 0.15 * max(0.0, min(1.0, trend))
                + 0.20 * hist_affinity
            )

            if desired_palette:
                reasons.append(f"Palette match: {int(round(color_match * 100))}%")
            if ctx.vibe:
                reasons.append(f"Vibe match: {int(round(vibe_match * 100))}%")
            if occasion:
                reasons.append(f"Occasion fit: {int(round(occasion_match * 100))}%")
            reasons.append(f"Trend score: {int(round(max(0.0, min(1.0, trend)) * 100))}%")
            if ctx.user_profile and ctx.user_profile.has_history:
                reasons.append(f"Style affinity: {int(round(hist_affinity * 100))}%")

            # Skin tone harmony (kept, small nudge)
            if ctx.skin_tone:
                tone = ctx.skin_tone.tone
                palette = [c.lower() for c in outfit.palette]
                if tone in ("deep", "tan") and any(c in palette for c in ("white", "pastel-blue", "stone", "beige")):
                    score += 2.5
                if tone in ("very_light", "light") and any(c in palette for c in ("navy", "charcoal", "deep-green", "olive")):
                    score += 2.5

            scored.append(ScoredOutfit(outfit=outfit, score=round(score, 2), reasons=_dedupe(reasons)))

        scored.sort(key=lambda s: s.score, reverse=True)
        return scored



def _dedupe(xs: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for x in xs:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def _all_item_tags(outfit: Outfit) -> set[str]:
    tags: set[str] = set()
    for it in outfit.items:
        tags.update(t.lower() for t in it.tags)
    return tags


def _apply_filters(outfits: list[Outfit], desired_palette: list[str], vibe: str | None, occasion: str, culture: str | None = None, gender: str | None = None) -> list[Outfit]:
    # ── 1. Gender filter (Strict absolute) ──
    base = outfits
    if gender:
        g = gender.strip().lower()
        if g in ("male", "female"):
            base = [o for o in base if o.gender in (g, "unisex")]
        else:
            base = [o for o in base if o.gender == "unisex"]
            
    if not base:
        return []

    # Helper for checking multiple valid tags
    def has_tags(o: Outfit, allowed: set[str]) -> bool:
        if not allowed: return True
        return any(t.lower() in allowed for t in o.tags) or any(t.lower() in allowed for t in _all_item_tags(o))

    # Compile valid tags for vibe + occasion
    vibe_l = (vibe.strip().lower() if vibe else "")
    occ = (occasion.strip().lower() if occasion else "")
    
    vibe_synonyms = {
        "streetwear": {"street", "streetwear", "modern", "edgy"},
        "minimal": {"minimal", "clean", "classic", "formal"},
        "cozy": {"cozy", "warm", "winter", "knit"},
        "classic": {"classic", "elevated", "formal", "tailored"},
        "party": {"party", "bold", "trendy", "glamour", "edgy"},
        "work": {"work", "office", "formal", "smart-casual", "clean", "preppy"},
        "aesthetic": {"aesthetic", "y2k", "cottagecore", "coquette", "dark-academia", "grunge", "coastal"},
        "edgy": {"edgy", "grunge", "bold"},
        "retro": {"retro", "vintage", "y2k"}
    }
    allowed_vibe = vibe_synonyms.get(vibe_l, {vibe_l}) if vibe_l else set()
    
    occ_mapping = {
        "party": {"party", "modern", "street", "edgy", "festive", "glamour"},
        "date": {"date", "elevated", "classic", "modern", "romantic"},
        "casual": {"casual", "everyday", "street", "minimal", "comfort", "relaxed"},
        "work": {"work", "office", "clean", "smart-casual", "preppy", "formal", "tailored"},
        "school": {"school", "casual", "everyday"},
        "gym": {"gym", "athleisure", "sporty", "performance"},
        "wedding": {"wedding", "festive", "elegant", "premium"}
    }
    allowed_occ = occ_mapping.get(occ, {occ}) if occ else set()
    culture_l = culture.strip().lower().replace(" ", "_").replace("-", "_") if culture else ""

    # Phase 1: Perfect match (Gender + Vibe + Occasion + Culture)
    l1 = [o for o in base if 
          (not culture_l or o.culture.lower().replace("-", "_") == culture_l) and
          (not allowed_vibe or has_tags(o, allowed_vibe)) and 
          (not allowed_occ or has_tags(o, allowed_occ))]
    
    if l1:
        current = l1
    else:
        # Phase 2: Gender + Vibe + Occasion (Drop Culture if it overrides the aesthetic)
        l2 = [o for o in base if 
              (not allowed_vibe or has_tags(o, allowed_vibe)) and 
              (not allowed_occ or has_tags(o, allowed_occ))]
        if l2:
            current = l2
        else:
            # Phase 3: Closest Match - Gender + Vibe (Drop occasion)
            l3 = [o for o in base if not allowed_vibe or has_tags(o, allowed_vibe)]
            if l3:
                current = l3
            else:
                # Phase 4: Fallback to gender bounds only
                current = base

    # ── 5. Hard palette filter (Softish, won't drop if list becomes empty) ──
    if desired_palette:
        compatible = [
            o for o in current
            if _palette_overlap(desired_palette, o.palette) > 0.0 and not _colors_clash(desired_palette, o.palette)
        ]
        if compatible:
            current = compatible

    return current


def _palette_overlap(desired: list[str], outfit_palette: list[str]) -> float:
    d = {c.lower() for c in desired}
    o = {c.lower() for c in outfit_palette}
    if not d:
        return 0.0
    return len(d & o) / max(1, len(d))


# ── Colors that clash with each undertone family ──
_WARM_CLASH = {"pastel-blue", "light-blue", "lavender", "powder-blue", "mint", "cobalt"}
_COOL_CLASH = {"olive", "brown", "tan", "stone", "beige", "deep-green", "peach"}


def _colors_clash(desired_palette: list[str], outfit_palette: list[str]) -> bool:
    """Return True if the outfit contains colors that clash with the user's palette."""
    dp = {c.lower() for c in desired_palette}
    op = {c.lower() for c in outfit_palette}

    # Detect the palette's temperature from colors present
    warm_palette_markers = {"beige", "olive", "brown", "tan", "stone", "deep-green"}
    cool_palette_markers = {"navy", "charcoal", "grey", "pastel-blue", "light-blue", "cobalt"}

    is_warm = len(dp & warm_palette_markers) >= 2
    is_cool = len(dp & cool_palette_markers) >= 2

    if is_warm and not is_cool:
        # Warm palette: reject outfits dominated by cool clash colors
        clash_count = len(op & _WARM_CLASH)
        compatible_count = len(op & dp)
        return clash_count > compatible_count
    elif is_cool and not is_warm:
        # Cool palette: reject outfits dominated by warm clash colors
        clash_count = len(op & _COOL_CLASH)
        compatible_count = len(op & dp)
        return clash_count > compatible_count

    return False


def _color_match(desired: list[str], outfit_palette: list[str], palette_temperature: str | None) -> float:
    base = _palette_overlap(desired, outfit_palette)

    # Penalty for clashing colors
    if _colors_clash(desired, outfit_palette):
        return max(0.0, base - 0.3)

    # Temperature boost: warm -> earthy, cool -> blue/grey/white
    warm_set = {"beige", "tan", "brown", "olive", "deep-green", "dark-brown", "stone"}
    cool_set = {"white", "grey", "charcoal", "navy", "pastel-blue", "light-blue"}
    op = {c.lower() for c in outfit_palette}
    if palette_temperature == "warm":
        boost = 0.2 if len(op & warm_set) >= 2 else 0.0
        return min(1.0, base + boost)
    if palette_temperature == "cool":
        boost = 0.2 if len(op & cool_set) >= 2 else 0.0
        return min(1.0, base + boost)
    return base


def _vibe_match(vibe: str | None, outfit: Outfit, prefs: list[str]) -> float:
    # Prefer explicit vibe; otherwise infer from prefs
    vibe_l = (vibe or "").strip().lower()
    if not vibe_l:
        for p in prefs:
            if p in ("streetwear", "street"):
                vibe_l = "street"
                break
            if p in ("minimal", "minimalist"):
                vibe_l = "minimal"
                break
            if p in ("classic", "timeless"):
                vibe_l = "classic"
                break
            if p in ("preppy",):
                vibe_l = "preppy"
                break
            if p in ("cozy", "warm"):
                vibe_l = "cozy"
                break

    if not vibe_l:
        return 0.4  # neutral when no vibe requested

    tags = {t.lower() for t in outfit.tags} | _all_item_tags(outfit)
    if vibe_l in tags:
        return 1.0
    # loose mapping
    synonyms = {
        "streetwear": {"street", "streetwear", "modern"},
        "street": {"street", "streetwear", "modern"},
        "minimal": {"minimal", "clean", "classic"},
        "minimalist": {"minimal", "clean"},
        "cozy": {"cozy", "warm", "winter"},
        "classic": {"classic", "smart-casual", "elevated"},
    }
    for key, syns in synonyms.items():
        if vibe_l == key and (tags & syns):
            return 0.75
    return 0.0


def _occasion_match(occasion: str, outfit: Outfit) -> float:
    if not occasion:
        return 0.4
    occ = occasion.lower()
    tags = {t.lower() for t in outfit.tags} | _all_item_tags(outfit)

    mapping = {
        "party": {"party", "modern", "street", "edgy"},
        "date": {"date", "elevated", "classic", "modern"},
        "casual": {"casual", "everyday", "street", "minimal"},
        "work": {"work", "office", "clean", "smart-casual", "preppy"},
        "office": {"work", "office", "clean", "smart-casual", "preppy"},
    }

    for k, req in mapping.items():
        if k in occ:
            inter = len(tags & req)
            return min(1.0, inter / max(1, min(3, len(req))))
    return 0.25


def _history_affinity(outfit: Outfit, profile: UserProfile | None) -> float:
    """Score how well an outfit matches the user's historical preferences (0..1)."""
    if profile is None or not profile.has_history:
        return 0.5  # neutral for new users

    outfit_colors = {c.lower() for c in outfit.palette}
    outfit_tags = {t.lower() for t in outfit.tags}
    for item in outfit.items:
        outfit_tags.update(t.lower() for t in item.tags)
        outfit_colors.update(c.lower() for c in item.colors)

    # Color overlap with user's frequent colours
    fav_colors = set(profile.frequent_colors)
    color_overlap = len(outfit_colors & fav_colors) / max(1, len(fav_colors)) if fav_colors else 0.0

    # Vibe/tag overlap with user's frequent vibes
    fav_vibes = set(profile.frequent_vibes)
    vibe_overlap = len(outfit_tags & fav_vibes) / max(1, len(fav_vibes)) if fav_vibes else 0.0

    # Bonus if user explicitly liked this outfit before
    liked_bonus = 0.15 if outfit.outfit_id in profile.liked_outfit_ids else 0.0

    # Penalty if already recommended recently
    repeat_penalty = 0.1 if outfit.outfit_id in profile.past_outfit_ids else 0.0

    return min(1.0, max(0.0, 0.45 * color_overlap + 0.40 * vibe_overlap + liked_bonus - repeat_penalty))
