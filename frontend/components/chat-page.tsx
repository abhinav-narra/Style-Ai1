"use client"

import { useState, useRef, useEffect } from "react"
import { useApp } from "@/lib/app-context"
import {
  Send,
  Sparkles,
  ImageIcon,
  Paperclip,
  ArrowLeft,
  Bot,
  User,
  Shirt,
  Palette,
  ThumbsUp,
} from "lucide-react"

interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: Date
  suggestions?: string[]
  outfitPreview?: {
    name: string
    image: string
    items: string[]
  }
  // Full structured response from stylist engine
  recommended_outfit?: any
  alternatives?: any[]
}

const INITIAL_MESSAGES: Message[] = [
  {
    id: "1",
    role: "assistant",
    content:
      "Hey bestie! I'm your AI stylist, fully wired into the fashion brain. Tell me your vibe, occasion, budget, or ask for accessories and I'll pull real outfit ideas for you.",
    timestamp: new Date(),
    suggestions: [
      "Party outfit under 3k",
      "Style me for a date",
      "Casual everyday look",
      "Add accessories to my last outfit",
    ],
  },
]

type StylistRecommendResponse = {
  user_id: string
  created_at: string
  recommendation_text: string
  outfits: {
    outfit: {
      outfit_id: string
      items: {
        category: string
        name: string
        colors?: string[]
        tags?: string[]
      }[]
      palette?: string[]
      tags?: string[]
    }
    score: number
    reasons?: string[]
    diversity_penalty?: number
  }[]
}

type ParsedIntent = {
  occasion?: string | null
  stylePreferences: string[]
  budget?: string | null
  isBudgetFollowup: boolean
  isAccessoriesFollowup: boolean
}

const DEFAULT_OUTFIT_IMAGE = "/images/outfit-1.jpg"

function parseIntent(input: string, lastIntent?: ParsedIntent | null): ParsedIntent {
  const text = input.toLowerCase()

  let occasion: string | null = null
  if (text.includes("party")) occasion = "party"
  else if (text.includes("date")) occasion = "date"
  else if (text.includes("casual")) occasion = "casual"
  else if (text.includes("work") || text.includes("office") || text.includes("interview")) occasion = "work"
  else if (text.includes("college") || text.includes("school") || text.includes("class"))
    occasion = "casual"
  else if (text.includes("beach") || text.includes("vacation"))
    occasion = "casual"

  const stylePreferences: string[] = []
  if (text.includes("streetwear")) stylePreferences.push("streetwear")
  if (text.includes("minimal") || text.includes("minimalist")) stylePreferences.push("minimalist")
  if (text.includes("formal")) stylePreferences.push("formal")
  if (text.includes("casual")) stylePreferences.push("casual")
  if (text.includes("college") || text.includes("school")) stylePreferences.push("everyday")
  if (text.includes("beach") || text.includes("vacation")) stylePreferences.push("coastal")
  if (text.includes("interview")) stylePreferences.push("classic")
  if (text.includes("confident")) {
    stylePreferences.push("modern")
    stylePreferences.push("elevated")
  }
  if (text.includes("accessor")) stylePreferences.push("accessories")
  if (text.includes("cheap") || text.includes("budget") || text.includes("affordable")) {
    stylePreferences.push("budget-friendly")
  }

  // Budget parsing: "under 3k", "under 3000", "budget", "cheap"
  let budget: string | null = null
  const underMatch = text.match(/under\s+([\d,.]+k?)/)
  if (underMatch) {
    budget = `under ${underMatch[1]}`
  } else if (text.includes("cheap") || text.includes("budget") || text.includes("affordable")) {
    budget = "low"
  }

  const isBudgetFollowup =
    !!lastIntent &&
    (text.includes("cheap version") ||
      text.includes("cheaper") ||
      text.includes("budget version") ||
      text.includes("make it cheaper") ||
      (text.includes("cheap") || text.includes("budget") || text.includes("affordable")))

  const isAccessoriesFollowup =
    !!lastIntent &&
    (text.includes("add accessories") ||
      text.includes("accessories") ||
      text.includes("jewelry") ||
      text.includes("earrings") ||
      text.includes("bag") ||
      text.includes("belt"))

  return {
    occasion: occasion ?? lastIntent?.occasion ?? null,
    stylePreferences: stylePreferences.length ? stylePreferences : lastIntent?.stylePreferences ?? [],
    budget: budget ?? lastIntent?.budget ?? null,
    isBudgetFollowup,
    isAccessoriesFollowup,
  }
}

function mapBackendToChatMessage(
  data: StylistRecommendResponse,
  intent: ParsedIntent
): { message: string; recommended_outfit?: any; alternatives?: any[]; outfitPreview?: Message["outfitPreview"] } {
  const text = data.recommendation_text || "Here's a look I pulled for you."
  const outfits = data.outfits || []
  const top = outfits[0]
  const alts = outfits.slice(1, 3)

  const recommended_outfit = top?.outfit
  const alternatives = alts.map((o) => o.outfit)

  let outfitPreview: Message["outfitPreview"] | undefined
  if (recommended_outfit) {
    let itemNames: string[] = []

    if (intent.isAccessoriesFollowup) {
      const items = (recommended_outfit.items || []) as any[]
      const shoesItem =
        items.find((i) => typeof i.category === "string" && i.category.toLowerCase().includes("shoe")) ||
        items.find((i) => typeof i.category === "string" && i.category.toLowerCase().includes("sneaker"))
      const palette: string[] = (recommended_outfit.palette || []) as string[]
      const primaryColor = (palette[0] || "black") as string

      itemNames = [
        `Shoes: ${shoesItem?.name || "clean white sneakers to ground the look"}`,
        `Watch: slim ${primaryColor} or metal watch to keep it polished`,
        `Bag: structured ${primaryColor} bag to pull everything together`,
      ]
    } else {
      itemNames =
        recommended_outfit.items?.map((i: any) => `${i.name} (${i.category})`) || []
    }

    outfitPreview = {
      name:
        intent.isBudgetFollowup && intent.budget === "low"
          ? "Budget-Friendly Version"
          : intent.isAccessoriesFollowup
            ? "Accessories: shoes, watch, bag"
            : "Styled Outfit",
      image: DEFAULT_OUTFIT_IMAGE,
      items: itemNames,
    }
  }

  // Conversational wrapper
  const intro = intent.isBudgetFollowup
    ? "Got you, let's make this more wallet-friendly.\n\n"
    : intent.isAccessoriesFollowup
      ? "Love that you're thinking about accessories.\n\n"
      : ""

  const message = `${intro}${text}`

  return { message, recommended_outfit, alternatives, outfitPreview }
}

export function ChatPage() {
  const { setCurrentPage, currentUser, authToken } = useApp()
  const [messages, setMessages] = useState<Message[]>(INITIAL_MESSAGES)
  const [input, setInput] = useState("")
  const [isTyping, setIsTyping] = useState(false)
  const [lastStylistResponse, setLastStylistResponse] = useState<{
    backend: StylistRecommendResponse
    intent: ParsedIntent
  } | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const userIdRef = useRef<string>("")

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  if (!userIdRef.current) {
    if (currentUser) {
      userIdRef.current = currentUser.id
    } else if (typeof window !== "undefined") {
      const existing = window.sessionStorage.getItem("drip-user-id")
      if (existing) {
        userIdRef.current = existing
      } else {
        const id = `web-${crypto.randomUUID?.() || Date.now().toString(36)}`
        userIdRef.current = id
        window.sessionStorage.setItem("drip-user-id", id)
      }
    }
  }

  const callStylistRecommend = async (userText: string) => {
    const intent = parseIntent(userText, lastStylistResponse?.intent)

    const requestPayload = {
      user_id: userIdRef.current || "web-anon",
      occasion: intent.occasion,
      style_preferences: intent.stylePreferences,
      budget: intent.budget,
      image_base64: null,
      extra_context: {
        user_message: userText,
        is_budget_followup: intent.isBudgetFollowup,
        is_accessories_followup: intent.isAccessoriesFollowup,
        last_outfit_id: lastStylistResponse?.backend.outfits?.[0]?.outfit?.outfit_id ?? null,
      },
    }

    const formData = new FormData()
    formData.append("request_json", JSON.stringify(requestPayload))

    const res = await fetch("http://localhost:8000/v1/recommend", {
      method: "POST",
      body: formData,
      headers: authToken
        ? {
          Authorization: `Bearer ${authToken}`,
        }
        : undefined,
    })

    if (!res.ok) {
      throw new Error("Stylist backend error")
    }

    const data: StylistRecommendResponse = await res.json()
    const mapped = mapBackendToChatMessage(data, intent)

    const aiMessage: Message = {
      id: (Date.now() + 1).toString(),
      role: "assistant",
      content: mapped.message,
      timestamp: new Date(),
      outfitPreview: mapped.outfitPreview,
      recommended_outfit: mapped.recommended_outfit,
      alternatives: mapped.alternatives,
    }

    setLastStylistResponse({ backend: data, intent })
    setMessages((prev) => [...prev, aiMessage])
  }

  // Detect if the message is an outfit request (should call /recommend)
  const isOutfitRequest = (text: string): boolean => {
    const t = text.toLowerCase()
    const outfitTriggers = [
      "style me", "outfit for", "dress me", "what to wear",
      "recommend", "suggest an outfit", "pick an outfit", "create a look",
      "show me outfits", "give me an outfit", "curate", "put together",
      "party outfit", "date outfit", "work outfit", "casual outfit",
      "outfit under", "look for", "dress for",
    ]
    return outfitTriggers.some((tr) => t.includes(tr))
  }

  // Call backend /v1/chat endpoint
  const callGroqChat = async (userMessage: string): Promise<string> => {
    // Build conversation history from recent messages
    const history = messages.slice(-10).map((m) => ({
      role: m.role,
      content: m.content,
    }))

    try {
      const res = await fetch("http://localhost:8000/v1/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: userMessage,
          history,
        }),
      })

      const data = await res.json()
      if (data.reply) return data.reply
    } catch (err) {
      console.error("Chat API error:", err)
    }

    return "Stylist is thinking... try again"
  }

  const sendMessage = (content: string) => {
    if (!content.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput("")
    setIsTyping(true)

    // If it's an outfit request, call the stylist backend
    if (isOutfitRequest(content)) {
      ; (async () => {
        try {
          await callStylistRecommend(content)
        } catch (err) {
          console.error(err)
          const fallback: Message = {
            id: (Date.now() + 2).toString(),
            role: "assistant",
            content:
              "I tried to reach the styling engine but something went wrong. Try asking again in a moment!",
            timestamp: new Date(),
          }
          setMessages((prev) => [...prev, fallback])
        } finally {
          setIsTyping(false)
        }
      })()
      return
    }

    // For all other messages, call Groq-powered chat
    ; (async () => {
      try {
        const reply = await callGroqChat(content)
        const aiMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: reply,
          timestamp: new Date(),
          suggestions: [
            "Style me for a date",
            "Party outfit under 3k",
            "What colors suit me?",
            "What's trending now?",
          ],
        }
        setMessages((prev) => [...prev, aiMessage])
      } catch (err) {
        console.error(err)
        const fallback: Message = {
          id: (Date.now() + 2).toString(),
          role: "assistant",
          content:
            "I'm having trouble connecting right now. Try again in a moment! 💫",
          timestamp: new Date(),
        }
        setMessages((prev) => [...prev, fallback])
      } finally {
        setIsTyping(false)
      }
    })()
  }

  return (
    <div className="flex h-[100dvh] flex-col">
      {/* Chat Header */}
      <div className="glass-strong fixed top-0 right-0 left-0 z-50 border-b border-border/50">
        <div className="mx-auto flex h-14 max-w-3xl items-center gap-3 px-4 md:h-16">
          <button
            onClick={() => setCurrentPage("home")}
            className="flex items-center gap-1.5 rounded-xl px-2 py-1.5 text-sm font-medium text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
            aria-label="Back to Style"
          >
            <ArrowLeft className="h-4 w-4" />
            <span className="hidden sm:inline">Back to Style</span>
          </button>
          <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-primary/15">
            <Sparkles className="h-5 w-5 text-primary" />
          </div>
          <div className="flex-1">
            <h2 className="text-sm font-semibold text-foreground">
              DRIP AI Stylist
            </h2>
            <p className="flex items-center gap-1.5 text-xs text-muted-foreground">
              <span className="h-2 w-2 rounded-full bg-emerald-500" />
              Always online
            </p>
          </div>
          <div className="hidden gap-2 md:flex">
            <button className="glass flex items-center gap-1.5 rounded-xl px-3 py-1.5 text-xs font-medium text-muted-foreground transition-colors hover:text-foreground">
              <Shirt className="h-3.5 w-3.5" />
              Outfit Help
            </button>
            <button className="glass flex items-center gap-1.5 rounded-xl px-3 py-1.5 text-xs font-medium text-muted-foreground transition-colors hover:text-foreground">
              <Palette className="h-3.5 w-3.5" />
              Color Advice
            </button>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto scrollbar-hide pt-14 pb-20 md:pt-16 md:pb-24">
        <div className="mx-auto max-w-3xl px-4 py-4">
          <div className="space-y-4">
            {messages.map((message) => (
              <div key={message.id}>
                <div
                  className={`flex gap-3 ${message.role === "user" ? "flex-row-reverse" : "flex-row"
                    }`}
                >
                  {/* Avatar */}
                  <div
                    className={`flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-xl ${message.role === "assistant"
                      ? "bg-primary/15"
                      : "bg-secondary"
                      }`}
                  >
                    {message.role === "assistant" ? (
                      <Bot className="h-4 w-4 text-primary" />
                    ) : (
                      <User className="h-4 w-4 text-muted-foreground" />
                    )}
                  </div>

                  {/* Bubble */}
                  <div
                    className={`max-w-[80%] rounded-2xl px-4 py-3 ${message.role === "user"
                      ? "bg-primary text-primary-foreground"
                      : "glass"
                      }`}
                  >
                    <p className="whitespace-pre-line text-sm leading-relaxed">
                      {message.content}
                    </p>

                    {/* Outfit Preview */}
                    {message.outfitPreview && (
                      <div className="mt-3 overflow-hidden rounded-xl border border-border/50">
                        <div className="relative aspect-[16/9] overflow-hidden">
                          <img
                            src={message.outfitPreview.image}
                            alt={message.outfitPreview.name}
                            className="h-full w-full object-cover"
                          />
                          <div className="absolute inset-0 bg-gradient-to-t from-background/80 to-transparent" />
                          <p className="absolute bottom-2 left-3 text-sm font-semibold text-foreground">
                            {message.outfitPreview.name}
                          </p>
                        </div>
                        <div className="space-y-1 px-3 py-2">
                          {message.outfitPreview.items.map((item, i) => (
                            <p
                              key={i}
                              className="text-xs text-muted-foreground"
                            >
                              {item}
                            </p>
                          ))}
                        </div>
                      </div>
                    )}

                    <p
                      className={`mt-1.5 text-[10px] ${message.role === "user"
                        ? "text-primary-foreground/60"
                        : "text-muted-foreground"
                        }`}
                    >
                      {message.timestamp.toLocaleTimeString([], {
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </p>
                  </div>
                </div>

                {/* Suggestions */}
                {message.suggestions && message.role === "assistant" && (
                  <div className="ml-11 mt-2 flex flex-wrap gap-2">
                    {message.suggestions.map((suggestion) => (
                      <button
                        key={suggestion}
                        onClick={() => sendMessage(suggestion)}
                        className="glass rounded-xl px-3 py-1.5 text-xs font-medium text-foreground transition-all hover:border-primary/50 hover:text-primary"
                      >
                        {suggestion}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ))}

            {/* Typing Indicator */}
            {isTyping && (
              <div className="flex gap-3">
                <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-xl bg-primary/15">
                  <Bot className="h-4 w-4 text-primary" />
                </div>
                <div className="glass flex items-center gap-1 rounded-2xl px-4 py-3">
                  <div className="typing-dot h-2 w-2 rounded-full bg-primary" />
                  <div className="typing-dot h-2 w-2 rounded-full bg-primary" />
                  <div className="typing-dot h-2 w-2 rounded-full bg-primary" />
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </div>
      </div>

      {/* Input */}
      <div className="glass-strong fixed right-0 bottom-0 left-0 border-t border-border/50 pb-[env(safe-area-inset-bottom)]">
        <div className="mx-auto flex max-w-3xl items-center gap-2 px-4 py-3">
          <button
            className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
            aria-label="Attach image"
          >
            <ImageIcon className="h-5 w-5" />
          </button>
          <button
            className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
            aria-label="Attach file"
          >
            <Paperclip className="h-5 w-5" />
          </button>
          <form
            onSubmit={(e) => {
              e.preventDefault()
              sendMessage(input)
            }}
            className="flex flex-1 items-center gap-2"
          >
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask me anything about style..."
              className="h-10 flex-1 rounded-xl border border-input bg-background/50 px-4 text-sm text-foreground placeholder:text-muted-foreground focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
            />
            <button
              type="submit"
              disabled={!input.trim()}
              className={`flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl transition-all ${input.trim()
                ? "bg-primary text-primary-foreground shadow-lg"
                : "bg-muted text-muted-foreground"
                }`}
              aria-label="Send message"
            >
              <Send className="h-4 w-4" />
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
