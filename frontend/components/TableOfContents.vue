<script setup lang="ts">
import type { TocEntry } from '~/types/blog'

defineProps<{ entries: TocEntry[] }>()

const { t } = useI18n()
</script>

<template>
  <nav v-if="entries.length" class="toc">
    <h3 class="toc-title">{{ t('toc.title') }}</h3>
    <ul class="toc-list">
      <li
        v-for="entry in entries"
        :key="entry.id"
        :class="`toc-item toc-level-${entry.level}`"
      >
        <a :href="`#${entry.id}`" class="toc-link">{{ entry.text }}</a>
      </li>
    </ul>
  </nav>
</template>

<style scoped>
.toc {
  position: sticky;
  top: var(--space-lg);
  padding: var(--space-sm) var(--space-md);
  border: 1px solid var(--border-color);
  border-radius: var(--space-xs);
  background: var(--surface-color);
}

.toc-title {
  font-size: var(--font-size-xs);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--font-color-muted);
  margin: 0 0 var(--space-sm);
}

.toc-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.toc-item {
  margin: var(--space-xs) 0;
}

.toc-level-2 {
  padding-left: 0;
}

.toc-level-3 {
  padding-left: var(--space-sm);
}

.toc-link {
  font-size: var(--font-size-xs);
  color: var(--font-color-muted);
  text-decoration: none;
  line-height: var(--line-height-base);
  transition: color var(--transition-fast);
}

.toc-link:hover {
  color: var(--a-color);
}
</style>
