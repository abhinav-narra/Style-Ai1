"use client"

import { createContext, useContext, useEffect, useState, type ReactNode } from "react"

export type AppPage = "home" | "results" | "profile" | "chat" | "login" | "signup"

export interface OutfitResult {
  id: string
  name: string
  image: string
  vibe: string
  occasion: string
  items: { name: string; brand: string; price: string; image?: string }[]
  matchScore: number
  saved: boolean
  // Optional fields returned by the backend / used by results-page
  title?: string
  score?: number
  vibe_images?: string[]
  vibe_image?: string
  vibeImage?: string
  images?: string[]
  color_palette?: string[]
}

interface AppState {
  currentPage: AppPage
  setCurrentPage: (page: AppPage) => void
  selectedVibe: string | null
  setSelectedVibe: (vibe: string | null) => void
  selectedOccasion: string | null
  setSelectedOccasion: (occasion: string | null) => void
  selectedCulture: string | null
  setSelectedCulture: (culture: string | null) => void
  selectedGender: string | null
  setSelectedGender: (gender: string | null) => void
  uploadedPhoto: string | null
  setUploadedPhoto: (photo: string | null) => void
  outfitResults: OutfitResult[]
  setOutfitResults: (results: OutfitResult[]) => void
  savedOutfits: OutfitResult[]
  toggleSaveOutfit: (outfit: OutfitResult) => void
  isGenerating: boolean
  setIsGenerating: (gen: boolean) => void
  authToken: string | null
  currentUser: { id: string; email: string; displayName?: string | null; gender?: string | null } | null
  setAuthToken: (token: string | null) => void
  setCurrentUser: (user: { id: string; email: string; displayName?: string | null; gender?: string | null } | null) => void
  logout: () => void
}

const AppContext = createContext<AppState | null>(null)

export function AppProvider({ children }: { children: ReactNode }) {
  const [currentPage, setCurrentPage] = useState<AppPage>("home")
  const [selectedVibe, setSelectedVibe] = useState<string | null>(null)
  const [selectedOccasion, setSelectedOccasion] = useState<string | null>(null)
  const [selectedCulture, setSelectedCulture] = useState<string | null>(null)
  const [selectedGender, setSelectedGender] = useState<string | null>(null)
  const [uploadedPhoto, setUploadedPhoto] = useState<string | null>(null)
  const [outfitResults, setOutfitResults] = useState<OutfitResult[]>([])
  const [savedOutfits, setSavedOutfits] = useState<OutfitResult[]>([])
  const [isGenerating, setIsGenerating] = useState(false)
  const [authToken, setAuthTokenState] = useState<string | null>(null)
  const [currentUser, setCurrentUserState] = useState<{ id: string; email: string; displayName?: string | null; gender?: string | null } | null>(null)

  useEffect(() => {
    if (typeof window === "undefined") return
    const token = window.localStorage.getItem("drip-token")
    if (token) {
      setAuthTokenState(token)
      // Try to hydrate current user
      fetch("http://localhost:8000/v1/auth/me", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
        .then((res) => (res.ok ? res.json() : null))
        .then((data) => {
          if (data && data.id && data.email) {
            setCurrentUserState({
              id: data.id,
              email: data.email,
              displayName: data.display_name ?? null,
              gender: data.gender ?? null,
            })
            // Hydrate saved outfits from the backend
            fetch("http://localhost:8000/v1/saved-outfits", {
              headers: { Authorization: `Bearer ${token}` },
            })
              .then((r) => (r.ok ? r.json() : []))
              .then((rows: any[]) => {
                const outfits: OutfitResult[] = rows.map((r) => ({
                  ...r.payload,
                  id: r.payload?.id ?? r.outfit_id,
                  saved: true,
                }))
                setSavedOutfits(outfits)
              })
              .catch(() => { })
          }
        })
        .catch(() => {
          // ignore, user will login again
        })
    }
  }, [])

  const setAuthToken = (token: string | null) => {
    setAuthTokenState(token)
    if (typeof window !== "undefined") {
      if (token) {
        window.localStorage.setItem("drip-token", token)
      } else {
        window.localStorage.removeItem("drip-token")
      }
    }
  }

  const setCurrentUser = (user: { id: string; email: string; displayName?: string | null; gender?: string | null } | null) => {
    setCurrentUserState(user)
  }

  const logout = () => {
    setAuthToken(null)
    setCurrentUser(null)
    setSavedOutfits([])
  }

  const toggleSaveOutfit = (outfit: OutfitResult) => {
    setSavedOutfits((prev) => {
      const exists = prev.find((o) => o.id === outfit.id)
      if (exists) {
        // Unsave — fire DELETE to backend
        if (authToken) {
          fetch(`http://localhost:8000/v1/delete-outfit/${encodeURIComponent(outfit.id)}`, {
            method: "DELETE",
            headers: { Authorization: `Bearer ${authToken}` },
          }).catch(() => { })
        }
        return prev.filter((o) => o.id !== outfit.id)
      }
      // Save — fire POST to backend
      if (authToken) {
        fetch("http://localhost:8000/v1/save-outfit", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${authToken}`,
          },
          body: JSON.stringify(outfit),
        }).catch(() => { })
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
        selectedCulture,
        setSelectedCulture,
        selectedGender,
        setSelectedGender,
        uploadedPhoto,
        setUploadedPhoto,
        outfitResults,
        setOutfitResults,
        savedOutfits,
        toggleSaveOutfit,
        isGenerating,
        setIsGenerating,
        authToken,
        currentUser,
        setAuthToken,
        setCurrentUser,
        logout,
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
