<template>
  <NuxtLoadingIndicator color="var(--a-color)" :height="3" />
  <NuxtLayout>
    <NuxtPage :page-key="route => route.path" />
  </NuxtLayout>
</template>
