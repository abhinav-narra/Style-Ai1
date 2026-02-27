"use client"

import { useCallback, useRef, useState } from "react"
import { useApp } from "@/lib/app-context"
import {
  Upload,
  Camera,
  Sparkles,
  ArrowRight,
  Zap,
  Star,
  Heart,
  Flame,
  Sun as SunIcon,
  Cloud,
  Glasses,
  PartyPopper,
  Briefcase,
  Dumbbell,
  Music,
  GraduationCap,
  X,
  Image as ImageIcon,
} from "lucide-react"

const vibes = [
  { id: "streetwear", label: "Streetwear", icon: Flame, color: "from-orange-500 to-red-500" },
  { id: "minimalist", label: "Minimal", icon: Star, color: "from-zinc-400 to-zinc-600" },
  { id: "y2k", label: "Y2K", icon: Sparkles, color: "from-pink-400 to-fuchsia-500" },
  { id: "cottagecore", label: "Cottagecore", icon: SunIcon, color: "from-amber-400 to-orange-400" },
  { id: "dark-academia", label: "Dark Academia", icon: Glasses, color: "from-stone-500 to-stone-700" },
  { id: "coquette", label: "Coquette", icon: Heart, color: "from-rose-300 to-pink-400" },
  { id: "grunge", label: "Grunge", icon: Zap, color: "from-gray-500 to-gray-700" },
  { id: "coastal", label: "Coastal", icon: Cloud, color: "from-sky-400 to-blue-500" },
]

const occasions = [
  { id: "party", label: "Night Out", icon: PartyPopper },
  { id: "work", label: "Work", icon: Briefcase },
  { id: "gym", label: "Gym", icon: Dumbbell },
  { id: "concert", label: "Concert", icon: Music },
  { id: "date", label: "Date Night", icon: Heart },
  { id: "school", label: "School", icon: GraduationCap },
]

const MOCK_RESULTS = [
  {
    id: "1",
    name: "Urban Edge Look",
    image: "/images/outfit-1.jpg",
    vibe: "streetwear",
    occasion: "concert",
    items: [
      { name: "Oversized Graphic Tee", brand: "Stussy", price: "$65" },
      { name: "Wide Leg Cargo Pants", brand: "Carhartt WIP", price: "$128" },
      { name: "Chunky Platform Sneakers", brand: "New Balance", price: "$145" },
      { name: "Gold Chain Layered Set", brand: "Mejuri", price: "$88" },
    ],
    matchScore: 97,
    saved: false,
  },
  {
    id: "2",
    name: "Elegant Evening",
    image: "/images/outfit-2.jpg",
    vibe: "minimalist",
    occasion: "date",
    items: [
      { name: "Silk Slip Dress", brand: "Reformation", price: "$218" },
      { name: "Strappy Heeled Sandals", brand: "Steve Madden", price: "$99" },
      { name: "Structured Clutch", brand: "Mansur Gavriel", price: "$295" },
      { name: "Pearl Drop Earrings", brand: "Mejuri", price: "$68" },
    ],
    matchScore: 94,
    saved: false,
  },
  {
    id: "3",
    name: "Sport Luxe",
    image: "/images/outfit-3.jpg",
    vibe: "minimalist",
    occasion: "gym",
    items: [
      { name: "Cropped Hoodie", brand: "Nike", price: "$85" },
      { name: "High-Waist Leggings", brand: "Alo Yoga", price: "$118" },
      { name: "Retro Running Shoes", brand: "Asics", price: "$130" },
      { name: "Minimal Baseball Cap", brand: "Aritzia", price: "$38" },
    ],
    matchScore: 91,
    saved: false,
  },
  {
    id: "4",
    name: "Boho Dreamer",
    image: "/images/outfit-4.jpg",
    vibe: "cottagecore",
    occasion: "school",
    items: [
      { name: "Floral Midi Dress", brand: "Free People", price: "$148" },
      { name: "Woven Leather Sandals", brand: "Madewell", price: "$88" },
      { name: "Straw Tote Bag", brand: "Lack of Color", price: "$125" },
      { name: "Layered Boho Necklaces", brand: "Anthropologie", price: "$58" },
    ],
    matchScore: 88,
    saved: false,
  },
]

export function HomePage() {
  const {
    selectedVibe,
    setSelectedVibe,
    selectedOccasion,
    setSelectedOccasion,
    uploadedPhoto,
    setUploadedPhoto,
    setCurrentPage,
    setOutfitResults,
    setIsGenerating,
  } = useApp()

  const fileInputRef = useRef<HTMLInputElement>(null)
  const [isDragOver, setIsDragOver] = useState(false)

  const handleFileUpload = useCallback(
    (file: File) => {
      if (file && file.type.startsWith("image/")) {
        const reader = new FileReader()
        reader.onload = (e) => {
          setUploadedPhoto(e.target?.result as string)
        }
        reader.readAsDataURL(file)
      }
    },
    [setUploadedPhoto]
  )

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setIsDragOver(false)
      const file = e.dataTransfer.files[0]
      if (file) handleFileUpload(file)
    },
    [handleFileUpload]
  )

  const handleGenerate = async () => {
  if (!uploadedPhoto) {
    alert("Upload photo first")
    return
  }

  setIsGenerating(true)
  setCurrentPage("results")

  try {
    // convert base64 preview to file
    const imgRes = await fetch(uploadedPhoto)
    const blob = await imgRes.blob()
    const file = new File([blob], "photo.jpg", { type: blob.type })

    const formData = new FormData()
    formData.append("file", file)

    const res = await fetch("http://127.0.0.1:8000/v1/analyze", {
      method: "POST",
      body: formData,
    })

    if (!res.ok) {
      throw new Error("Backend error")
    }

    const data = await res.json()
    console.log("AI RESPONSE:", data)

    // Format result for UI (temporary)
    const formatted = MOCK_RESULTS.map((item, i) => ({
  ...item,
  id: "ai-" + i,
  image: uploadedPhoto,
  vibe: selectedVibe || item.vibe,
  occasion: selectedOccasion || item.occasion,
}))

    setOutfitResults(formatted)
  } catch (err) {
    console.error(err)
    alert("Backend connection failed")
  }

  setIsGenerating(false)
}

  const canGenerate = selectedVibe && selectedOccasion

  return (
    <div className="mx-auto max-w-4xl px-4 pt-20 pb-24 md:pt-24">
      {/* Hero */}
      <div className="mb-10 text-center">
        <div className="mb-4 inline-flex items-center gap-2 rounded-full bg-primary/10 px-4 py-1.5 text-sm font-medium text-primary">
          <Sparkles className="h-3.5 w-3.5" />
          AI-Powered Fashion
        </div>
        <h1
          className="mb-3 text-4xl font-bold tracking-tight text-balance text-foreground md:text-5xl lg:text-6xl"
          style={{ fontFamily: "var(--font-display)" }}
        >
          Your AI Stylist
          <br />
          <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
            Awaits
          </span>
        </h1>
        <p className="mx-auto max-w-lg text-base text-pretty text-muted-foreground md:text-lg">
          Upload a photo, choose your vibe, pick the occasion, and watch AI
          curate your perfect outfit in seconds.
        </p>
      </div>

      {/* Upload Section */}
      <section className="mb-10">
        <h2 className="mb-3 text-sm font-semibold tracking-wider text-muted-foreground uppercase">
          Step 1 &middot; Upload Your Photo
        </h2>
        <div
          onDragOver={(e) => {
            e.preventDefault()
            setIsDragOver(true)
          }}
          onDragLeave={() => setIsDragOver(false)}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`glass group relative cursor-pointer overflow-hidden rounded-2xl transition-all duration-300 ${
            isDragOver
              ? "border-primary ring-4 ring-primary/20"
              : "hover:border-primary/50"
          } ${uploadedPhoto ? "p-0" : "p-8 md:p-12"}`}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            className="hidden"
            onChange={(e) => {
              const file = e.target.files?.[0]
              if (file) handleFileUpload(file)
            }}
          />

          {uploadedPhoto ? (
            <div className="relative aspect-[3/2] w-full">
              <img
                src={uploadedPhoto}
                alt="Your uploaded photo"
                className="h-full w-full object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-background/80 to-transparent" />
              <div className="absolute right-3 bottom-3 left-3 flex items-center justify-between">
                <span className="glass rounded-lg px-3 py-1.5 text-sm font-medium text-foreground">
                  Photo uploaded
                </span>
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    setUploadedPhoto(null)
                  }}
                  className="flex h-8 w-8 items-center justify-center rounded-lg bg-destructive/80 text-destructive-foreground transition-colors hover:bg-destructive"
                  aria-label="Remove photo"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-4 text-center">
              <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10 transition-transform duration-300 group-hover:scale-110">
                <Upload className="h-7 w-7 text-primary" />
              </div>
              <div>
                <p className="mb-1 text-base font-semibold text-foreground">
                  Drag & drop your photo here
                </p>
                <p className="text-sm text-muted-foreground">
                  or click to browse &middot; JPG, PNG up to 10MB
                </p>
              </div>
              <div className="flex gap-3">
                <span className="glass inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium text-muted-foreground">
                  <Camera className="h-3.5 w-3.5" />
                  Take Photo
                </span>
                <span className="glass inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium text-muted-foreground">
                  <ImageIcon className="h-3.5 w-3.5" />
                  Gallery
                </span>
              </div>
            </div>
          )}
        </div>
      </section>

      {/* Vibe Selector */}
      <section className="mb-10">
        <h2 className="mb-3 text-sm font-semibold tracking-wider text-muted-foreground uppercase">
          Step 2 &middot; Choose Your Vibe
        </h2>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          {vibes.map((vibe) => {
            const Icon = vibe.icon
            const isSelected = selectedVibe === vibe.id
            return (
              <button
                key={vibe.id}
                onClick={() =>
                  setSelectedVibe(isSelected ? null : vibe.id)
                }
                className={`glass group relative flex flex-col items-center gap-2 rounded-2xl px-3 py-5 transition-all duration-300 ${
                  isSelected
                    ? "border-primary ring-2 ring-primary/30 shadow-lg"
                    : "hover:border-primary/40 hover:scale-[1.02]"
                }`}
              >
                <div
                  className={`flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br ${vibe.color} transition-transform duration-300 ${
                    isSelected ? "scale-110" : "group-hover:scale-105"
                  }`}
                >
                  <Icon className="h-5 w-5 text-white" />
                </div>
                <span className="text-sm font-medium text-foreground">
                  {vibe.label}
                </span>
                {isSelected && (
                  <div className="absolute -top-1 -right-1 flex h-5 w-5 items-center justify-center rounded-full bg-primary">
                    <Sparkles className="h-3 w-3 text-primary-foreground" />
                  </div>
                )}
              </button>
            )
          })}
        </div>
      </section>

      {/* Occasion Selector */}
      <section className="mb-10">
        <h2 className="mb-3 text-sm font-semibold tracking-wider text-muted-foreground uppercase">
          Step 3 &middot; What's the Occasion?
        </h2>
        <div className="grid grid-cols-3 gap-3 sm:grid-cols-6">
          {occasions.map((occ) => {
            const Icon = occ.icon
            const isSelected = selectedOccasion === occ.id
            return (
              <button
                key={occ.id}
                onClick={() =>
                  setSelectedOccasion(isSelected ? null : occ.id)
                }
                className={`glass group flex flex-col items-center gap-2 rounded-2xl px-2 py-4 transition-all duration-300 ${
                  isSelected
                    ? "border-primary ring-2 ring-primary/30 shadow-lg"
                    : "hover:border-primary/40 hover:scale-[1.02]"
                }`}
              >
                <Icon
                  className={`h-6 w-6 transition-colors ${
                    isSelected
                      ? "text-primary"
                      : "text-muted-foreground group-hover:text-foreground"
                  }`}
                />
                <span className="text-xs font-medium text-foreground">
                  {occ.label}
                </span>
              </button>
            )
          })}
        </div>
      </section>

      {/* Generate Button */}
      <div className="flex justify-center">
        <button
          onClick={handleGenerate}
          disabled={!canGenerate}
          className={`group flex items-center gap-3 rounded-2xl px-10 py-4 text-base font-semibold transition-all duration-300 ${
            canGenerate
              ? "bg-primary text-primary-foreground shadow-xl hover:shadow-2xl hover:scale-[1.02] animate-pulse-glow"
              : "cursor-not-allowed bg-muted text-muted-foreground"
          }`}
        >
          <Sparkles
            className={`h-5 w-5 transition-transform ${
              canGenerate ? "group-hover:rotate-12" : ""
            }`}
          />
          Generate Outfits
          <ArrowRight
            className={`h-5 w-5 transition-transform ${
              canGenerate ? "group-hover:translate-x-1" : ""
            }`}
          />
        </button>
      </div>

      {!canGenerate && (
        <p className="mt-3 text-center text-sm text-muted-foreground">
          Select a vibe and occasion to unlock the magic
        </p>
      )}
    </div>
  )
}
