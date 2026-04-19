export interface Card {
  id: string;
  name: string;
  arcana: "major" | "minor";
  suit: "wands" | "cups" | "swords" | "pentacles" | null;
  number: number;
  keywords_upright: string[];
  keywords_reversed: string[];
  short_upright: string;
  short_reversed: string;
}

export interface DrawnCard {
  card: Card;
  position: string;
  reversed: boolean;
}

export interface DrawResponse {
  draw_id: string;
  cards: DrawnCard[];
}

export async function postDraw(): Promise<DrawResponse> {
  const r = await fetch("/api/draw", { method: "POST" });
  if (!r.ok) throw new Error(`draw failed: ${r.status}`);
  return r.json();
}

export interface ReadingHandlers {
  onToken: (text: string) => void;
  onDone: () => void;
  onError: (msg: string) => void;
}

export type Section = "past" | "present" | "future" | "synthesis";

// Open an SSE stream for one section of the reading. Returns an abort function.
export function openReadingStream(
  drawId: string,
  section: Section,
  handlers: ReadingHandlers,
): () => void {
  const qs = new URLSearchParams({ draw_id: drawId, section });
  const es = new EventSource(`/api/reading?${qs}`);

  es.addEventListener("token", (ev) => {
    // Backend escapes \n as "\\n" so we restore it here.
    handlers.onToken((ev as MessageEvent).data.replaceAll("\\n", "\n"));
  });
  es.addEventListener("done", () => {
    handlers.onDone();
    es.close();
  });
  es.addEventListener("error", (ev) => {
    const data = (ev as MessageEvent).data;
    handlers.onError(data ?? "stream error");
    es.close();
  });

  return () => es.close();
}
