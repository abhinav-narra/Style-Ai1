"use client"

import { FormEvent, useState } from "react"
import { useApp } from "@/lib/app-context"

export function SignupPage() {
  const { setCurrentPage, setAuthToken, setCurrentUser } = useApp()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [name, setName] = useState("")
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    if (!email || !password) return
    setIsLoading(true)
    try {
      const res = await fetch("http://localhost:8000/v1/auth/signup", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password, display_name: name || null }),
      })
      if (!res.ok) {
        throw new Error("Signup failed")
      }
      const data = await res.json()
      if (data.access_token) {
        setAuthToken(data.access_token)
        const meRes = await fetch("http://localhost:8000/v1/auth/me", {
          headers: {
            Authorization: `Bearer ${data.access_token}`,
          },
        })
        if (meRes.ok) {
          const me = await meRes.json()
          setCurrentUser({
            id: me.id,
            email: me.email,
            displayName: me.display_name ?? null,
          })
        }
        setCurrentPage("home")
      }
    } catch (err) {
      console.error(err)
      alert("Signup failed. Try a different email.")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="mx-auto flex min-h-[100dvh] max-w-md flex-col items-center justify-center px-4">
      <div className="w-full rounded-2xl border border-border/60 bg-background/80 p-6 shadow-xl backdrop-blur">
        <h1 className="mb-2 text-2xl font-bold text-foreground">Create your account</h1>
        <p className="mb-6 text-sm text-muted-foreground">
          Save outfits, track your history, and get personalized styling.
        </p>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="mb-1 block text-xs font-medium text-muted-foreground">
              Name (optional)
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="h-10 w-full rounded-xl border border-input bg-background/60 px-3 text-sm text-foreground placeholder:text-muted-foreground focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
              placeholder="How should DRIP AI call you?"
            />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-muted-foreground">
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="h-10 w-full rounded-xl border border-input bg-background/60 px-3 text-sm text-foreground placeholder:text-muted-foreground focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
              placeholder="you@example.com"
              required
            />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-muted-foreground">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="h-10 w-full rounded-xl border border-input bg-background/60 px-3 text-sm text-foreground placeholder:text-muted-foreground focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
              placeholder="At least 6 characters"
              required
            />
          </div>
          <button
            type="submit"
            disabled={isLoading}
            className="mt-2 inline-flex w-full items-center justify-center rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground shadow-lg transition-colors hover:bg-primary/90 disabled:cursor-not-allowed disabled:opacity-70"
          >
            {isLoading ? "Creating account..." : "Sign up"}
          </button>
        </form>
        <p className="mt-4 text-center text-xs text-muted-foreground">
          Already have an account?{" "}
          <button
            type="button"
            onClick={() => setCurrentPage("login")}
            className="font-medium text-primary hover:underline"
          >
            Sign in
          </button>
        </p>
      </div>
    </div>
  )
}

