"use client"

import { useState, useEffect } from "react"
import { useApp } from "@/lib/app-context"
import { useTheme } from "next-themes"
import {
  Home,
  Sparkles,
  User,
  MessageCircle,
  Sun,
  Moon,
  Flame,
} from "lucide-react"

const navItems = [
  { id: "home" as const, label: "Home", icon: Home },
  { id: "results" as const, label: "Style", icon: Sparkles },
  { id: "chat" as const, label: "Chat", icon: MessageCircle },
  { id: "profile" as const, label: "Profile", icon: User },
]

export function AppNavbar() {
  const { currentPage, setCurrentPage, currentUser, logout } = useApp()
  const { theme, setTheme, resolvedTheme } = useTheme()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  return (
    <>
      {/* Desktop top nav */}
      <header className="glass-strong fixed top-0 right-0 left-0 z-50 hidden md:block">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">
          <button
            onClick={() => setCurrentPage("home")}
            className="flex items-center gap-2"
          >
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-primary">
              <Flame className="h-5 w-5 text-primary-foreground" />
            </div>
            <span className="text-xl font-bold tracking-tight text-foreground" style={{ fontFamily: 'var(--font-display)' }}>
              DRIP AI
            </span>
          </button>

          <nav className="flex items-center gap-1">
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = currentPage === item.id
              return (
                <button
                  key={item.id}
                  onClick={() => setCurrentPage(item.id)}
                  className={`flex items-center gap-2 rounded-xl px-4 py-2 text-sm font-medium transition-all duration-200 ${
                    isActive
                      ? "bg-primary text-primary-foreground shadow-lg"
                      : "text-muted-foreground hover:bg-secondary hover:text-foreground"
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  {item.label}
                </button>
              )
            })}
            {currentUser ? (
              <button
                onClick={logout}
                className="ml-2 flex items-center gap-2 rounded-xl px-3 py-2 text-xs font-medium text-muted-foreground hover:bg-secondary hover:text-foreground"
              >
                <span className="hidden md:inline">Logout</span>
              </button>
            ) : (
              <button
                onClick={() => setCurrentPage("login")}
                className="ml-2 flex items-center gap-2 rounded-xl bg-primary px-3 py-2 text-xs font-semibold text-primary-foreground shadow-lg hover:bg-primary/90"
              >
                Login
              </button>
            )}
          </nav>

          <button
            onClick={() => setTheme(resolvedTheme === "dark" ? "light" : "dark")}
            className="flex h-10 w-10 items-center justify-center rounded-xl text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
            aria-label="Toggle theme"
          >
            {mounted ? (
              resolvedTheme === "dark" ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />
            ) : (
              <span className="h-5 w-5" />
            )}
          </button>
        </div>
      </header>

      {/* Mobile top bar */}
      <header className="glass-strong fixed top-0 right-0 left-0 z-50 md:hidden">
        <div className="flex h-14 items-center justify-between px-4">
          <button
            onClick={() => setCurrentPage("home")}
            className="flex items-center gap-2"
          >
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
              <Flame className="h-4 w-4 text-primary-foreground" />
            </div>
            <span className="text-lg font-bold tracking-tight text-foreground" style={{ fontFamily: 'var(--font-display)' }}>
              DRIP AI
            </span>
          </button>
          <button
            onClick={() => setTheme(resolvedTheme === "dark" ? "light" : "dark")}
            className="flex h-9 w-9 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-secondary"
            aria-label="Toggle theme"
          >
            {mounted ? (
              resolvedTheme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />
            ) : (
              <span className="h-4 w-4" />
            )}
          </button>
        </div>
      </header>

      {/* Mobile bottom nav */}
      <nav className="glass-strong fixed right-0 bottom-0 left-0 z-50 pb-[env(safe-area-inset-bottom)] md:hidden">
        <div className="flex h-16 items-center justify-around px-2">
          {navItems.map((item) => {
            const Icon = item.icon
            const isActive = currentPage === item.id
            return (
              <button
                key={item.id}
                onClick={() => setCurrentPage(item.id)}
                className={`flex flex-col items-center gap-0.5 rounded-xl px-4 py-1.5 transition-all duration-200 ${
                  isActive
                    ? "text-primary"
                    : "text-muted-foreground"
                }`}
              >
                <div className={`flex h-8 w-8 items-center justify-center rounded-xl transition-all duration-200 ${
                  isActive ? "bg-primary/15 scale-110" : ""
                }`}>
                  <Icon className="h-5 w-5" />
                </div>
                <span className="text-[10px] font-medium">{item.label}</span>
              </button>
            )
          })}
          <button
            onClick={() => setCurrentPage(currentUser ? "profile" : "login")}
            className="flex flex-col items-center gap-0.5 rounded-xl px-4 py-1.5 text-muted-foreground"
          >
            <div className="flex h-8 w-8 items-center justify-center rounded-xl">
              <User className="h-5 w-5" />
            </div>
            <span className="text-[10px] font-medium">
              {currentUser ? "Account" : "Login"}
            </span>
          </button>
        </div>
      </nav>
    </>
  )
}
