"use client"

import { useApp } from "@/lib/app-context"
import {
  Heart,
  Settings,
  Share2,
  LogOut,
  Sparkles,
  ShoppingBag,
  TrendingUp,
  Camera,
  Edit3,
  Crown,
  X,
} from "lucide-react"
import { useState, useEffect } from "react"

const STATS = [
  { label: "Outfits Saved", icon: Heart },
  { label: "Looks Generated", icon: Sparkles },
]

const STYLE_TAGS = [
  "Streetwear",
  "Minimalist",
  "Y2K",
  "Dark Academia",
  "Coastal",
]

export function ProfilePage() {
  const { savedOutfits, toggleSaveOutfit, setCurrentPage, currentUser, logout, authToken } = useApp()
  const [activeTab, setActiveTab] = useState<"saved" | "history">("saved")
  const [historyItems, setHistoryItems] = useState<any[]>([])
  const [historyCount, setHistoryCount] = useState(0)

  // Fetch history when tab is clicked or component mounts
  useEffect(() => {
    if (!authToken) return
    fetch("http://localhost:8000/v1/history", {
      headers: { Authorization: `Bearer ${authToken}` },
    })
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (data && data.entries) {
          setHistoryItems(data.entries)
          setHistoryCount(data.entries.length)
        }
      })
      .catch((err) => console.error("Failed to fetch history:", err))
  }, [authToken])

  const displayName = currentUser?.displayName || currentUser?.email?.split('@')[0] || "User"
  const handleSignOut = () => {
    logout()
    setCurrentPage("home")
  }

  return (
    <div className="mx-auto max-w-4xl px-4 pt-20 pb-24 md:pt-24">
      {/* Profile Header */}
      <div className="glass mb-8 overflow-hidden rounded-3xl">
        {/* Banner */}
        <div className="relative h-32 bg-gradient-to-r from-primary/30 via-accent/20 to-primary/10 md:h-40">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_50%,var(--glow),transparent_70%)]" />
        </div>

        <div className="relative px-6 pb-6">
          {/* Avatar */}
          <div className="relative -mt-14 mb-4 inline-block">
            <div className="relative h-24 w-24 overflow-hidden rounded-3xl border-4 border-background bg-secondary flex items-center justify-center shadow-xl md:h-28 md:w-28 text-4xl text-primary font-bold">
              {displayName.charAt(0).toUpperCase()}
            </div>
            <button
              className="absolute -right-1 -bottom-1 flex h-8 w-8 items-center justify-center rounded-xl bg-primary text-primary-foreground shadow-lg"
              aria-label="Change photo"
            >
              <Camera className="h-4 w-4" />
            </button>
            <div className="absolute -top-1 -left-1 flex h-7 w-7 items-center justify-center rounded-lg bg-amber-500 text-white shadow-lg">
              <Crown className="h-3.5 w-3.5" />
            </div>
          </div>

          <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
            <div>
              <div className="flex items-center gap-2">
                <h1
                  className="text-2xl font-bold text-foreground"
                  style={{ fontFamily: "var(--font-display)" }}
                >
                  {displayName}
                </h1>
                <span className="rounded-lg bg-primary/15 px-2 py-0.5 text-xs font-semibold text-primary">
                  PRO
                </span>
              </div>
              <p className="mt-1 text-sm text-muted-foreground">
                @{displayName.toLowerCase().replace(/\s+/g, '')} &middot; Fashion enthusiast & trendsetter
              </p>
              <div className="mt-3 flex flex-wrap gap-1.5">
                {currentUser?.gender && (
                  <span className="rounded-lg bg-primary/20 px-2.5 py-1 text-xs font-semibold text-primary capitalize">
                    {currentUser.gender.replace("-", " ")}
                  </span>
                )}
                {STYLE_TAGS.map((tag) => (
                  <span
                    key={tag}
                    className="rounded-lg bg-secondary px-2.5 py-1 text-xs font-medium text-secondary-foreground"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>
            <div className="flex gap-2">
              <button className="glass flex items-center gap-2 rounded-xl px-4 py-2 text-sm font-medium text-foreground transition-colors hover:border-primary/50">
                <Edit3 className="h-4 w-4" />
                Edit Profile
              </button>
              <button
                className="flex h-10 w-10 items-center justify-center rounded-xl bg-secondary text-muted-foreground transition-colors hover:text-foreground"
                aria-label="Settings"
              >
                <Settings className="h-4 w-4" />
              </button>
              <button
                className="flex h-10 w-10 items-center justify-center rounded-xl bg-secondary text-muted-foreground transition-colors hover:text-foreground"
                aria-label="Share profile"
              >
                <Share2 className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="mb-8 grid grid-cols-3 gap-3">
        {STATS.map((stat) => {
          const Icon = stat.icon
          return (
            <div
              key={stat.label}
              className="glass flex flex-col items-center gap-2 rounded-2xl px-4 py-5"
            >
              <Icon className="h-5 w-5 text-primary" />
              <span
                className="text-2xl font-bold text-foreground"
                style={{ fontFamily: "var(--font-display)" }}
              >
                {stat.label === "Outfits Saved" ? savedOutfits.length : historyCount}
              </span>
              <span className="text-xs text-muted-foreground">{stat.label}</span>
            </div>
          )
        })}
      </div>

      {/* Tabs */}
      <div className="mb-6 flex gap-1 rounded-2xl bg-secondary p-1">
        <button
          onClick={() => setActiveTab("saved")}
          className={`flex-1 rounded-xl px-4 py-2.5 text-sm font-semibold transition-all ${activeTab === "saved"
            ? "bg-background text-foreground shadow-sm"
            : "text-muted-foreground hover:text-foreground"
            }`}
        >
          <Heart className="mr-2 inline-block h-4 w-4" />
          Saved ({savedOutfits.length})
        </button>
        <button
          onClick={() => setActiveTab("history")}
          className={`flex-1 rounded-xl px-4 py-2.5 text-sm font-semibold transition-all ${activeTab === "history"
            ? "bg-background text-foreground shadow-sm"
            : "text-muted-foreground hover:text-foreground"
            }`}
        >
          <Sparkles className="mr-2 inline-block h-4 w-4" />
          History
        </button>
      </div>

      {/* Saved Outfits Grid */}
      {activeTab === "saved" ? (
        savedOutfits.length > 0 ? (
          <div className="grid grid-cols-2 gap-3 md:grid-cols-3">
            {savedOutfits.map((outfit) => (
              <div
                key={outfit.id}
                className="glass group relative overflow-hidden rounded-2xl"
              >
                <div className="relative aspect-[3/4] overflow-hidden">
                  <img
                    src={outfit.image}
                    alt={outfit.name}
                    className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-background/80 to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100" />
                  <div className="absolute right-2 bottom-2 left-2 translate-y-4 opacity-0 transition-all duration-300 group-hover:translate-y-0 group-hover:opacity-100">
                    <p className="text-sm font-semibold text-foreground">
                      {outfit.name}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {outfit.items.length} pieces
                    </p>
                  </div>
                  <button
                    onClick={() => toggleSaveOutfit(outfit)}
                    className="absolute top-2 right-2 flex h-8 w-8 items-center justify-center rounded-lg bg-background/60 text-red-500 opacity-0 backdrop-blur-sm transition-all duration-200 group-hover:opacity-100"
                    aria-label="Remove from saved"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center gap-4 rounded-2xl bg-secondary/50 py-16">
            <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-muted">
              <Heart className="h-8 w-8 text-muted-foreground" />
            </div>
            <div className="text-center">
              <p className="font-semibold text-foreground">No saved outfits yet</p>
              <p className="mt-1 text-sm text-muted-foreground">
                Start generating looks and save your favorites!
              </p>
            </div>
            <button
              onClick={() => setCurrentPage("home")}
              className="rounded-xl bg-primary px-6 py-2.5 text-sm font-semibold text-primary-foreground"
            >
              Generate Outfits
            </button>
          </div>
        )
      ) : (
        <div className="space-y-3">
          {historyItems.length > 0 ? (
            historyItems.map((entry: any, i: number) => {
              const outfit = entry.payload
              const date = new Date(entry.created_at).toLocaleDateString()
              return (
                <div
                  key={i}
                  className="glass flex items-center justify-between rounded-2xl px-4 py-4"
                >
                  <div className="flex items-center gap-3">
                    {outfit?.image && (
                      <div className="h-12 w-12 flex-shrink-0 overflow-hidden rounded-lg bg-secondary">
                        <img src={outfit.image} alt={outfit.name} className="h-full w-full object-cover" />
                      </div>
                    )}
                    <div>
                      <p className="text-sm font-semibold text-foreground">
                        {outfit?.name || "Generated Outfit"}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {date} &middot; {outfit?.vibe || "Custom"} vibe
                      </p>
                    </div>
                  </div>
                  <ShoppingBag className="h-5 w-5 text-muted-foreground" />
                </div>
              )
            })
          ) : (
            <div className="flex flex-col items-center justify-center gap-4 rounded-2xl bg-secondary/50 py-16">
              <div className="text-center">
                <p className="font-semibold text-foreground">No history yet</p>
                <p className="mt-1 text-sm text-muted-foreground">
                  Your generated outfits will appear here.
                </p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Sign Out */}
      <div className="mt-10 flex justify-center">
        <button
          onClick={handleSignOut}
          className="flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-destructive"
        >
          <LogOut className="h-4 w-4" />
          Sign Out
        </button>
      </div>
    </div>
  )
}
