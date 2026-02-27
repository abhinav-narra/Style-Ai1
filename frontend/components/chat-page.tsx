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
}

const INITIAL_MESSAGES: Message[] = [
  {
    id: "1",
    role: "assistant",
    content:
      "Hey bestie! I'm your AI stylist. Tell me what you're looking for today -- a full outfit, accessory recs, or style advice? I got you.",
    timestamp: new Date(),
    suggestions: [
      "Style me for a date night",
      "What shoes go with wide-leg jeans?",
      "Build me a capsule wardrobe",
      "Trending colors this season",
    ],
  },
]

const AI_RESPONSES: Record<string, Message> = {
  "Style me for a date night": {
    id: "",
    role: "assistant",
    content:
      "Ooh date night! Love that for you. I'd go with something that's effortlessly chic but still makes a statement. Think a satin midi skirt with a fitted top and strappy heels. Add a dainty gold necklace for that extra sparkle. Here's a look I put together:",
    timestamp: new Date(),
    outfitPreview: {
      name: "Date Night Elegance",
      image: "/images/outfit-2.jpg",
      items: ["Silk Cami Top - Aritzia", "Satin Midi Skirt - Reformation", "Strappy Heels - Steve Madden", "Gold Pendant - Mejuri"],
    },
    suggestions: ["Show me more options", "Make it more casual", "Add a jacket"],
  },
  "What shoes go with wide-leg jeans?": {
    id: "",
    role: "assistant",
    content:
      "Wide-leg jeans are SO versatile! Here are my top picks:\n\n1. Platform sneakers -- keeps it casual but adds height\n2. Pointed-toe mules -- instant polish\n3. Chunky loafers -- the it-girl choice rn\n4. Ankle boots -- perfect for fall/winter\n\nThe key is to make sure the hem hits right at the shoe. Want me to style a full look with any of these?",
    timestamp: new Date(),
    suggestions: ["Style with platform sneakers", "Show loafer outfits", "Best brands for wide-leg jeans"],
  },
  "Build me a capsule wardrobe": {
    id: "",
    role: "assistant",
    content:
      "A capsule wardrobe? You're speaking my language! Here's the foundation you need -- 15 essential pieces that mix and match into 50+ outfits:\n\nTops: White tee, black bodysuit, striped button-down, knit sweater\nBottoms: Dark wash jeans, tailored trousers, midi skirt\nOuters: Blazer, leather jacket, trench coat\nShoes: White sneakers, black boots, heeled sandals\nBags: Crossbody, structured tote\n\nWant me to build specific outfits from these pieces?",
    timestamp: new Date(),
    suggestions: ["Build outfits from these", "Affordable brands for these", "Add trendy pieces"],
  },
  "Trending colors this season": {
    id: "",
    role: "assistant",
    content:
      "The color forecast is giving main character energy this season! Here are the top trending shades:\n\nButter Yellow -- the new neutral, works in everything\nCherry Red -- bold, confident, statement pieces\nSlate Blue -- sophisticated and calming\nEspresso Brown -- rich and luxurious\nSoft Sage -- nature-inspired, super wearable\n\nMy hot take? Pair butter yellow with espresso brown for a combo that'll stop people in their tracks. Want me to style some color combos for you?",
    timestamp: new Date(),
    suggestions: ["Style butter yellow looks", "How to wear cherry red", "Color combos for my skin tone"],
  },
}

const DEFAULT_RESPONSE: Message = {
  id: "",
  role: "assistant",
  content:
    "Great question! Let me think about that... I'd recommend exploring some trending styles right now. The fashion scene is really moving toward effortless layering and bold accessories. Want me to put together a specific look for you based on your vibe?",
  timestamp: new Date(),
  suggestions: ["Show me street style", "Formal outfit ideas", "Accessory recommendations"],
}

export function ChatPage() {
  const { setCurrentPage } = useApp()
  const [messages, setMessages] = useState<Message[]>(INITIAL_MESSAGES)
  const [input, setInput] = useState("")
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

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

    setTimeout(() => {
      const response = AI_RESPONSES[content] || DEFAULT_RESPONSE
      const aiMessage: Message = {
        ...response,
        id: (Date.now() + 1).toString(),
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, aiMessage])
      setIsTyping(false)
    }, 1500)
  }

  return (
    <div className="flex h-[100dvh] flex-col">
      {/* Chat Header */}
      <div className="glass-strong fixed top-0 right-0 left-0 z-50 border-b border-border/50">
        <div className="mx-auto flex h-14 max-w-3xl items-center gap-3 px-4 md:h-16">
          <button
            onClick={() => setCurrentPage("home")}
            className="flex h-9 w-9 items-center justify-center rounded-xl text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground md:hidden"
            aria-label="Go back"
          >
            <ArrowLeft className="h-5 w-5" />
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
                  className={`flex gap-3 ${
                    message.role === "user" ? "flex-row-reverse" : "flex-row"
                  }`}
                >
                  {/* Avatar */}
                  <div
                    className={`flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-xl ${
                      message.role === "assistant"
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
                    className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                      message.role === "user"
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
                      className={`mt-1.5 text-[10px] ${
                        message.role === "user"
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
              className={`flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl transition-all ${
                input.trim()
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
