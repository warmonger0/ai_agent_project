// File: /frontend/src/__tests__/commandPanel/ChatMessageList.test.tsx

import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import ChatMessageList from "@/components/planning/ChatPanel/ChatMessageList";
import type { ChatMessage } from "@/types";

describe("ChatMessageList", () => {
  const messages: ChatMessage[] = [
    { role: "user", content: "Hello from user" },
    { role: "assistant", content: "Hello from assistant" },
  ];

  it("renders all messages in the list", () => {
    render(<ChatMessageList messages={messages} />);

    expect(screen.getByText("Hello from user")).toBeInTheDocument();
    expect(screen.getByText("Hello from assistant")).toBeInTheDocument();
  });

  it("renders an empty state when there are no messages", () => {
    render(<ChatMessageList messages={[]} />);
    // Optionally test for absence or a fallback message
    expect(screen.queryByText(/hello/i)).not.toBeInTheDocument();
  });
});
