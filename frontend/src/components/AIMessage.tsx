"use client";

import type { ReactNode } from "react";

interface Props {
  role: "user" | "ai";
  children: ReactNode;
}

// A conversational bubble. AI messages sit on the left with the Cartiva mark.
export function AIMessage({ role, children }: Props) {
  if (role === "user") {
    return (
      <div className="flex animate-fade-up justify-end">
        <div className="max-w-[85%] rounded-2xl rounded-br-md bg-primary px-4 py-2.5 text-sm text-white shadow-soft">
          {children}
        </div>
      </div>
    );
  }

  return (
    <div className="flex animate-fade-up gap-2.5">
      <span className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-primary text-xs font-extrabold text-white">
        C
      </span>
      <div className="max-w-[90%] space-y-3">{children}</div>
    </div>
  );
}

// Animated "typing" indicator shown while Cartiva is thinking.
export function TypingBubble() {
  return (
    <div className="flex gap-2.5">
      <span className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-primary text-xs font-extrabold text-white">
        C
      </span>
      <div className="flex items-center gap-1 rounded-2xl rounded-bl-md border border-line bg-card px-4 py-3">
        <span className="h-2 w-2 animate-typing rounded-full bg-muted [animation-delay:0ms]" />
        <span className="h-2 w-2 animate-typing rounded-full bg-muted [animation-delay:200ms]" />
        <span className="h-2 w-2 animate-typing rounded-full bg-muted [animation-delay:400ms]" />
      </div>
    </div>
  );
}
