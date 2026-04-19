<script setup lang="ts">
import { computed } from "vue";
import type { DrawnCard } from "../lib/api";

const props = defineProps<{
  drawn: DrawnCard | null;
  position: string;
  faceUp: boolean;
}>();

const emit = defineEmits<{ (e: "flip"): void }>();

const ascii = computed(() => {
  if (!props.drawn) return "";
  // Generic frame; the user can swap in per-card ASCII later by id.
  const lines = [
    "╔══════════╗",
    "║          ║",
    "║    ✦     ║",
    "║          ║",
    "║   " + (props.drawn.reversed ? "↯" : "★") + "      ║",
    "║          ║",
    "║    ✦     ║",
    "║          ║",
    "╚══════════╝",
  ];
  return lines.join("\n");
});

function onClick() {
  if (!props.faceUp && props.drawn) emit("flip");
}
</script>

<template>
  <div class="card-slot" @click="onClick">
    <div class="card" :class="{ 'face-up': faceUp, 'reversed': drawn?.reversed && faceUp }">
      <div class="face back">
        <div class="back-pattern">✦</div>
      </div>
      <div class="face front">
        <pre class="art">{{ ascii }}</pre>
        <div class="meta">
          <div class="name">{{ drawn?.card.name }}</div>
          <div v-if="drawn?.reversed" class="reversed-badge">Reversed ↯</div>
        </div>
      </div>
    </div>
    <div class="position-label">{{ position }}</div>
  </div>
</template>

<style scoped>
.card-slot {
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  user-select: none;
}

.card {
  width: 100%;
  aspect-ratio: 2 / 3;
  position: relative;
  transform-style: preserve-3d;
  transition: transform 0.7s cubic-bezier(0.4, 0.1, 0.3, 1);
}

.card.face-up {
  transform: rotateY(180deg);
}

.face {
  position: absolute;
  inset: 0;
  backface-visibility: hidden;
  border: 1px solid var(--accent-dim);
  background: var(--panel);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow);
}

.back {
  background: var(--card-back);
  background-image:
    radial-gradient(circle at 30% 30%, rgba(201, 169, 107, 0.1) 0%, transparent 60%),
    radial-gradient(circle at 70% 70%, rgba(201, 169, 107, 0.08) 0%, transparent 60%);
}

.back-pattern {
  font-size: 3rem;
  color: var(--accent);
  opacity: 0.5;
}

.front {
  transform: rotateY(180deg);
  padding: 0.75rem;
  gap: 0.5rem;
}

.card.reversed .art,
.card.reversed .meta {
  transform: rotate(180deg);
}

.art {
  font-family: ui-monospace, "SF Mono", monospace;
  color: var(--ink);
  font-size: 0.75rem;
  line-height: 1.1;
  margin: 0;
}

.meta {
  text-align: center;
}

.name {
  color: var(--accent);
  font-size: 0.85rem;
  letter-spacing: 0.05em;
}

.reversed-badge {
  color: var(--ink-dim);
  font-size: 0.7rem;
  font-style: italic;
  margin-top: 0.2rem;
}

.position-label {
  margin-top: 0.6rem;
  color: var(--ink-dim);
  font-size: 0.85rem;
  letter-spacing: 0.15em;
  text-transform: uppercase;
}
</style>
