"use client"

import { AppProvider, useApp } from "@/lib/app-context"
import { AppNavbar } from "@/components/app-navbar"
import { HomePage } from "@/components/home-page"
import { ResultsPage } from "@/components/results-page"
import { ProfilePage } from "@/components/profile-page"
import { ChatPage } from "@/components/chat-page"
import { LoginPage } from "@/components/login-page"
import { SignupPage } from "@/components/signup-page"

function AppContent() {
  const { currentPage, currentUser } = useApp()

  if (currentPage === "login") return <LoginPage />
  if (currentPage === "signup") return <SignupPage />
  if (currentPage === "chat") {
    if (!currentUser) {
      return <LoginPage />
    }
    return <ChatPage />
  }

  return (
    <div className="relative min-h-[100dvh]">
      {/* Ambient background effects */}
      <div className="pointer-events-none fixed inset-0 overflow-hidden" aria-hidden="true">
        <div className="absolute -top-40 -right-40 h-96 w-96 rounded-full bg-primary/5 blur-3xl" />
        <div className="absolute top-1/3 -left-40 h-80 w-80 rounded-full bg-accent/5 blur-3xl" />
        <div className="absolute -right-20 bottom-20 h-72 w-72 rounded-full bg-primary/3 blur-3xl" />
      </div>

      <AppNavbar />
      <main className="relative z-10">
        {currentPage === "home" && <HomePage />}
        {currentPage === "results" && (currentUser ? <ResultsPage /> : <LoginPage />)}
        {currentPage === "profile" && (currentUser ? <ProfilePage /> : <LoginPage />)}
      </main>
    </div>
  )
}

export default function Page() {
  return (
    <AppProvider>
      <AppContent />
    </AppProvider>
  )
}
