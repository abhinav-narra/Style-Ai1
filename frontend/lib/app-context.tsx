"use client"

import { createContext, useContext, useState, type ReactNode } from "react"

export type AppPage = "home" | "results" | "profile" | "chat"

export interface OutfitResult {
  id: string
  name: string
  image: string
  vibe: string
  occasion: string
  items: { name: string; brand: string; price: string }[]
  matchScore: number
  saved: boolean
}

interface AppState {
  currentPage: AppPage
  setCurrentPage: (page: AppPage) => void
  selectedVibe: string | null
  setSelectedVibe: (vibe: string | null) => void
  selectedOccasion: string | null
  setSelectedOccasion: (occasion: string | null) => void
  uploadedPhoto: string | null
  setUploadedPhoto: (photo: string | null) => void
  outfitResults: OutfitResult[]
  setOutfitResults: (results: OutfitResult[]) => void
  savedOutfits: OutfitResult[]
  toggleSaveOutfit: (outfit: OutfitResult) => void
  isGenerating: boolean
  setIsGenerating: (gen: boolean) => void
}

const AppContext = createContext<AppState | null>(null)

export function AppProvider({ children }: { children: ReactNode }) {
  const [currentPage, setCurrentPage] = useState<AppPage>("home")
  const [selectedVibe, setSelectedVibe] = useState<string | null>(null)
  const [selectedOccasion, setSelectedOccasion] = useState<string | null>(null)
  const [uploadedPhoto, setUploadedPhoto] = useState<string | null>(null)
  const [outfitResults, setOutfitResults] = useState<OutfitResult[]>([])
  const [savedOutfits, setSavedOutfits] = useState<OutfitResult[]>([])
  const [isGenerating, setIsGenerating] = useState(false)

  const toggleSaveOutfit = (outfit: OutfitResult) => {
    setSavedOutfits((prev) => {
      const exists = prev.find((o) => o.id === outfit.id)
      if (exists) {
        return prev.filter((o) => o.id !== outfit.id)
      }
      return [...prev, { ...outfit, saved: true }]
    })
  }

  return (
    <AppContext.Provider
      value={{
        currentPage,
        setCurrentPage,
        selectedVibe,
        setSelectedVibe,
        selectedOccasion,
        setSelectedOccasion,
        uploadedPhoto,
        setUploadedPhoto,
        outfitResults,
        setOutfitResults,
        savedOutfits,
        toggleSaveOutfit,
        isGenerating,
        setIsGenerating,
      }}
    >
      {children}
    </AppContext.Provider>
  )
}

export function useApp() {
  const context = useContext(AppContext)
  if (!context) throw new Error("useApp must be used within AppProvider")
  return context
}
