<script setup lang="ts">
const { addStructuredData, buildWebsiteSchema } = useSeo()

addStructuredData(buildWebsiteSchema(), 'website')
</script>

<template>
  <NuxtLoadingIndicator color="var(--a-color)" :height="3" />
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>
