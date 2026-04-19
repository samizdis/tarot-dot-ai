<script setup lang="ts">
import { computed, ref } from "vue";
import TarotCard from "./TarotCard.vue";
import Reading from "./Reading.vue";
import { postDraw, openReadingStream, type DrawnCard } from "../lib/api";

const POSITIONS = ["Past", "Present", "Future"];

const drawId = ref<string | null>(null);
const cards = ref<DrawnCard[]>([]);
const revealed = ref<boolean[]>([false, false, false]);
const drawing = ref(false);
const readingText = ref("");
const streaming = ref(false);
const error = ref<string | null>(null);
let abort: (() => void) | null = null;

const allRevealed = computed(
  () => cards.value.length === 3 && revealed.value.every(Boolean),
);
const showReadingButton = computed(
  () => allRevealed.value && !streaming.value && !readingText.value,
);

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

function flip(i: number) {
  revealed.value[i] = true;
}

function getReading() {
  if (!drawId.value) return;
  resetReading();
  streaming.value = true;
  abort = openReadingStream(drawId.value, {
    onToken: (t) => (readingText.value += t),
    onDone: () => (streaming.value = false),
    onError: (msg) => {
      error.value = msg;
      streaming.value = false;
    },
  });
}

function resetReading() {
  abort?.();
  abort = null;
  readingText.value = "";
  streaming.value = false;
  error.value = null;
}

async function copy() {
  await navigator.clipboard.writeText(readingText.value);
}
</script>

<template>
  <div class="spread">
    <TarotCard
      v-for="(pos, i) in POSITIONS"
      :key="i"
      :drawn="cards[i] ?? null"
      :position="pos"
      :face-up="revealed[i]"
      @flip="flip(i)"
    />
  </div>

  <div class="controls">
    <button @click="draw" :disabled="drawing || streaming">
      {{ cards.length ? "Draw Again" : "Draw 3 Cards" }}
    </button>
    <button v-if="showReadingButton" @click="getReading">Get Reading</button>
    <button v-if="readingText && !streaming" @click="copy">Copy Reading</button>
  </div>

  <p v-if="cards.length && !allRevealed" class="subtitle" style="margin-top: 1.5rem">
    Click each card to reveal it.
  </p>

  <Reading
    v-if="readingText || streaming || error"
    :text="readingText"
    :streaming="streaming"
    :error="error"
  />
</template>
