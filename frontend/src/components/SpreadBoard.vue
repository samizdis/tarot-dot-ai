<script setup lang="ts">
import { computed, ref, watch } from "vue";
import TarotCard from "./TarotCard.vue";
import Reading from "./Reading.vue";
import {
  postDraw,
  openReadingStream,
  type DrawnCard,
  type Section,
} from "../lib/api";

const POSITIONS = ["Past", "Present", "Future"];
const SECTIONS: Section[] = ["past", "present", "future"];

const drawId = ref<string | null>(null);
const cards = ref<DrawnCard[]>([]);
const revealed = ref<boolean[]>([false, false, false]);
const drawing = ref(false);
const readingText = ref("");
const streaming = ref(false);
const error = ref<string | null>(null);
const readingsOn = ref(false);
const sectionsDone = ref<Section[]>([]);
const catchingUp = ref(false);
let abort: (() => void) | null = null;

const allRevealed = computed(
  () => cards.value.length === 3 && revealed.value.every(Boolean),
);
const nextToFlip = computed(() => {
  if (cards.value.length !== 3) return -1;
  return revealed.value.findIndex((r) => !r);
});

async function draw() {
  resetReading();
  drawing.value = true;
  error.value = null;
  try {
    const r = await postDraw();
    drawId.value = r.draw_id;
    cards.value = r.cards;
    revealed.value = [false, false, false];
  } catch (e) {
    error.value = String(e);
  } finally {
    drawing.value = false;
  }
}

async function flip(i: number) {
  revealed.value[i] = true;
  await catchUp();
}

// Stream any sections owed given current toggle + revealed state.
// Re-entrant-safe via catchingUp guard; bails mid-loop if readings are toggled off.
async function catchUp() {
  if (!readingsOn.value || !drawId.value || catchingUp.value) return;
  catchingUp.value = true;
  try {
    for (let i = 0; i < 3; i++) {
      if (!readingsOn.value) return;
      if (revealed.value[i] && !sectionsDone.value.includes(SECTIONS[i])) {
        await runSection(SECTIONS[i]);
      }
    }
    if (!readingsOn.value) return;
    if (allRevealed.value && !sectionsDone.value.includes("synthesis")) {
      await runSection("synthesis");
    }
  } finally {
    catchingUp.value = false;
  }
}

function runSection(section: Section): Promise<void> {
  return new Promise((resolve) => {
    if (!drawId.value) return resolve();
    if (readingText.value) readingText.value += "\n\n";
    streaming.value = true;
    error.value = null;
    abort = openReadingStream(drawId.value, section, {
      onToken: (t) => (readingText.value += t),
      onDone: () => {
        sectionsDone.value.push(section);
        streaming.value = false;
        resolve();
      },
      onError: (msg) => {
        error.value = msg;
        streaming.value = false;
        resolve();
      },
    });
  });
}

watch(readingsOn, (on) => {
  if (on) catchUp();
});

function resetReading() {
  abort?.();
  abort = null;
  readingText.value = "";
  streaming.value = false;
  error.value = null;
  sectionsDone.value = [];
}

async function copy() {
  await navigator.clipboard.writeText(readingText.value);
}
</script>

<template>
  <div class="top-bar">
    <label class="toggle">
      <input type="checkbox" v-model="readingsOn" />
      <span>Claude reading</span>
    </label>
  </div>

  <p v-if="!cards.length" class="hint">
    Draw three cards, then click each one in turn to reveal it.
  </p>
  <p v-else-if="!allRevealed && !streaming" class="hint">
    Click <strong>{{ POSITIONS[nextToFlip] }}</strong> to reveal it.
  </p>

  <div class="spread">
    <TarotCard
      v-for="(pos, i) in POSITIONS"
      :key="i"
      :drawn="cards[i] ?? null"
      :position="pos"
      :face-up="revealed[i]"
      :can-flip="i === nextToFlip && !streaming"
      @flip="flip(i)"
    />
  </div>

  <div class="controls">
    <button @click="draw" :disabled="drawing || streaming">
      {{ cards.length ? "Draw Again" : "Draw 3 Cards" }}
    </button>
    <button v-if="readingText && !streaming && allRevealed" @click="copy">
      Copy Reading
    </button>
  </div>

  <Reading
    v-if="readingText || streaming || error"
    :text="readingText"
    :streaming="streaming"
    :error="error"
  />
</template>
