"use client"

import { useState, useEffect } from "react"
import { useApp, type OutfitResult } from "@/lib/app-context"
import {
  Sparkles,
  Heart,
  Share2,
  ChevronDown,
  ChevronUp,
  ArrowLeft,
  Loader2,
  ShoppingBag,
  TrendingUp,
} from "lucide-react"

function LoadingScreen() {
  const tips = [
    "Analyzing your style DNA...",
    "Scanning latest trends...",
    "Curating perfect fits...",
    "Matching colors & textures...",
    "Almost there, bestie...",
  ]
  const [tipIndex, setTipIndex] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => {
      setTipIndex((prev) => (prev + 1) % tips.length)
    }, 600)
    return () => clearInterval(interval)
  }, [tips.length])

  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center gap-6">
      <div className="relative">
        <div className="flex h-20 w-20 items-center justify-center rounded-3xl bg-primary/15 animate-pulse-glow">
          <Sparkles className="h-10 w-10 text-primary animate-float" />
        </div>
      </div>
      <div className="text-center">
        <h2
          className="mb-2 text-2xl font-bold text-foreground"
          style={{ fontFamily: "var(--font-display)" }}
        >
          Creating Your Looks
        </h2>
        <p className="text-muted-foreground transition-all duration-300">
          {tips[tipIndex]}
        </p>
      </div>
      <div className="flex gap-1.5">
        {[0, 1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className={`h-2 rounded-full transition-all duration-500 ${i <= tipIndex ? "w-8 bg-primary" : "w-2 bg-muted"
              }`}
          />
        ))}
      </div>
    </div>
  )
}

function OutfitCard({
  outfit,
  index,
}: {
  outfit: OutfitResult
  index: number
}) {
  const { savedOutfits, toggleSaveOutfit } = useApp()
  const [expanded, setExpanded] = useState(false)
  const [mainImageError, setMainImageError] = useState(false)
  const isSaved = savedOutfits.some((o) => o.id === outfit.id)

  // Get the best available main image
  const getMainImage = () => {
    if (!mainImageError) {
      // Try vibe_images array (new backend)
      if (outfit.vibe_images && outfit.vibe_images.length > 0) {
        return outfit.vibe_images[0]
      }
      // Try vibeImage (alternative field name)
      if (outfit.vibeImage) {
        return outfit.vibeImage
      }
      // Try vibe_image (another alternative)
      if (outfit.vibe_image) {
        return outfit.vibe_image
      }
      // Try images array
      if (outfit.images && outfit.images.length > 0) {
        return outfit.images[0]
      }
      // Try first item image
      if (outfit.items && outfit.items.length > 0 && outfit.items[0].image) {
        return outfit.items[0].image
      }
      // Fallback to old image field
      if (outfit.image) {
        return outfit.image
      }
    }
    // Ultimate fallback - fashion image
    return "https://images.unsplash.com/photo-1520975916090-3105956dac38?w=800"
  }

  return (
    <div
      className="glass animate-slide-up overflow-hidden rounded-2xl"
      style={{ animationDelay: `${index * 200}ms`, animationFillMode: "both" }}
    >
      {/* VIBE IMAGE (instead of uploaded face) */}
      <div className="relative aspect-[4/5] overflow-hidden">

        {/* Main image with fallback */}
        <img
          src={getMainImage()}
          alt={outfit.name}
          className="h-full w-full object-cover animate-reveal"
          style={{ animationDelay: `${index * 200 + 300}ms`, animationFillMode: "both" }}
          onError={() => setMainImageError(true)}
        />

        <div className="absolute inset-0 bg-gradient-to-t from-background/90 via-background/20 to-transparent" />

        {/* Match Score */}
        <div className="absolute top-3 left-3 flex items-center gap-1.5 rounded-xl bg-primary px-3 py-1.5 text-sm font-bold text-primary-foreground shadow-lg">
          <TrendingUp className="h-3.5 w-3.5" />
          {Math.round(outfit.score || outfit.matchScore || 90)}% Match
        </div>

        {/* Actions */}
        <div className="absolute top-3 right-3 flex gap-2">
          <button
            onClick={() => toggleSaveOutfit(outfit)}
            className={`glass flex h-10 w-10 items-center justify-center rounded-xl transition-all duration-200 ${isSaved ? "text-red-500" : "text-foreground hover:text-red-400"
              }`}
            aria-label={isSaved ? "Unsave outfit" : "Save outfit"}
          >
            <Heart className={`h-5 w-5 ${isSaved ? "fill-current" : ""}`} />
          </button>
          <button
            className="glass flex h-10 w-10 items-center justify-center rounded-xl text-foreground transition-colors hover:text-primary"
            aria-label="Share outfit"
          >
            <Share2 className="h-5 w-5" />
          </button>
        </div>

        {/* Title overlay */}
        <div className="absolute right-3 bottom-3 left-3">
          <h3
            className="mb-1 text-xl font-bold text-foreground"
            style={{ fontFamily: "var(--font-display)" }}
          >
            {outfit.title || outfit.name}
          </h3>
          <p className="text-sm text-muted-foreground">
            {outfit.items?.length || 0} pieces curated for you
          </p>
        </div>
      </div>

      {/* Items */}
      <div className="p-4">
        <button
          onClick={() => setExpanded(!expanded)}
          className="flex w-full items-center justify-between py-1 text-sm font-medium text-foreground"
        >
          <span className="flex items-center gap-2">
            <ShoppingBag className="h-4 w-4 text-primary" />
            View Items
          </span>
          {expanded ? (
            <ChevronUp className="h-4 w-4 text-muted-foreground" />
          ) : (
            <ChevronDown className="h-4 w-4 text-muted-foreground" />
          )}
        </button>

        {expanded && (
          <div className="mt-3 space-y-2">
            {outfit.items?.map((item, i) => (
              <div
                key={i}
                className="flex items-center gap-3 rounded-xl bg-secondary/50 px-3 py-2.5"
              >
                {/* product image with error handling */}
                <div className="h-12 w-12 flex-shrink-0 rounded-lg bg-secondary overflow-hidden">
                  <img
                    src={item.image || "https://via.placeholder.com/60x60?text=Product"}
                    alt={item.name}
                    className="h-full w-full object-cover"
                    onError={(e) => {
                      e.currentTarget.src = "https://via.placeholder.com/60x60?text=Product"
                    }}
                  />
                </div>

                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-foreground truncate">
                    {item.name}
                  </p>
                  <p className="text-xs text-muted-foreground truncate">
                    {item.brand}
                  </p>
                </div>

                <span className="text-sm font-semibold text-primary whitespace-nowrap">
                  {item.price}
                </span>
              </div>
            ))}
            <button className="mt-2 flex w-full items-center justify-center gap-2 rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground transition-colors hover:bg-primary/90">
              <ShoppingBag className="h-4 w-4" />
              Shop This Look
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export function ResultsPage() {
  const { outfitResults, isGenerating, setCurrentPage } = useApp()

  // DEBUG: Log the first outfit to see its structure (remove after fixing)
  useEffect(() => {
    if (outfitResults.length > 0) {
      console.log("First outfit data:", outfitResults[0])
      console.log("Vibe images:", outfitResults[0].vibe_images)
      console.log("Color palette:", outfitResults[0].color_palette)
    }
  }, [outfitResults])

  return (
    <div className="mx-auto max-w-5xl px-4 pt-20 pb-24 md:pt-24">
      {/* Back button */}
      <button
        onClick={() => setCurrentPage("home")}
        className="mb-6 flex items-center gap-2 text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to Style Lab
      </button>

      {isGenerating ? (
        <LoadingScreen />
      ) : (
        <>
          <div className="mb-8 text-center">
            <h1
              className="mb-2 text-3xl font-bold text-foreground md:text-4xl"
              style={{ fontFamily: "var(--font-display)" }}
            >
              Your Styled Looks
            </h1>
            <p className="text-muted-foreground">
              {outfitResults.length} outfits curated just for you
            </p>
          </div>

          {/* COLOR PALETTE - Show if available */}
          {outfitResults?.[0]?.color_palette && outfitResults[0].color_palette.length > 0 && (
            <div className="mb-8 flex flex-col items-center">
              <p className="mb-3 text-sm text-muted-foreground">Your best colors</p>
              <div className="flex gap-3 flex-wrap justify-center">
                {outfitResults[0].color_palette.map((c: string, i: number) => (
                  <div
                    key={i}
                    className="h-10 w-10 rounded-full border-2 border-white shadow-lg"
                    style={{ background: c }}
                    title={c}
                  />
                ))}
              </div>
            </div>
          )}

          {outfitResults.length > 0 ? (
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              {outfitResults.map((outfit, index) => (
                <OutfitCard key={outfit.id} outfit={outfit} index={index} />
              ))}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center gap-4 py-20">
              <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-muted">
                <Sparkles className="h-8 w-8 text-muted-foreground" />
              </div>
              <p className="text-center text-muted-foreground">
                No outfits generated yet. Head back to the Style Lab!
              </p>
              <button
                onClick={() => setCurrentPage("home")}
                className="rounded-xl bg-primary px-6 py-2.5 text-sm font-semibold text-primary-foreground"
              >
                Go to Style Lab
              </button>
            </div>
          )}

          {outfitResults.length > 0 && (
            <div className="mt-10 flex justify-center">
              <button
                onClick={() => setCurrentPage("home")}
                className="glass flex items-center gap-2 rounded-2xl px-8 py-3 text-sm font-semibold text-foreground transition-all hover:border-primary/50"
              >
                <Loader2 className="h-4 w-4" />
                Generate More Looks
              </button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
