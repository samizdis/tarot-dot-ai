<script setup lang="ts">
import { computed } from "vue";
import { marked } from "marked";

const props = defineProps<{
  text: string;
  streaming: boolean;
  error: string | null;
}>();

const html = computed(() => marked.parse(props.text || "") as string);
</script>

<template>
  <div class="reading">
    <div v-html="html"></div>
    <span v-if="streaming" class="cursor"></span>
    <div v-if="error" class="error">{{ error }}</div>
  </div>
</template>
