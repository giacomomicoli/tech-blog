<template>
  <div class="site">
    <header class="site-header">
      <NavBar />
    </header>
    <main class="site-main">
      <slot />
    </main>
    <footer class="site-footer">
      <p>{{ $t('footer.text', { year: new Date().getFullYear() }) }}</p>
    </footer>
  </div>
</template>

<style scoped>
.site {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.site-header {
  padding-block: var(--space-sm);
  margin-block-end: var(--space-md);
  border-bottom: 1px solid var(--border-color);
}

.site-main {
  flex: 1;
  padding-block: var(--space-sm);
}

.site-footer {
  padding-block: var(--space-md);
  margin-block-start: var(--space-lg);
  border-top: 1px solid var(--border-color);
  font-size: var(--font-size-sm);
  color: var(--font-color-muted);
  text-align: center;
}

@media screen and (min-width: 1024px) {
  .site-main {
    padding-block: var(--space-md);
  }
}
</style>
