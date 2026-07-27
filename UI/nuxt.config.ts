// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  ssr: false,
  devtools: { enabled: true },
  devServer: {
    port: 5000,
    host: "0.0.0.0",
  },
  vite: {
    server: {
      allowedHosts: true,
      hmr: { clientPort: 443, protocol: "wss" },
    },
  },
  modules: [
    "@bg-dev/nuxt-naiveui",
    "@vueuse/nuxt",
    "@nuxtjs/tailwindcss",
    "@nuxt/content",
    "nuxt-icon",
    "@pinia/nuxt",
    "@unocss/nuxt",
    "@nuxtjs/i18n",
    "nuxt-lodash",
  ],
  css: ["~/assets/scss/main.scss"],
  tailwindcss: {
    exposeConfig: {
      write: true,
    },
  },
  content: {
    markdown: {
      anchorLinks: false,
    },
  },
  i18n: {
    locales: [
      {
        code: "en",
        file: "en-US.json",
      },
    ],
    lazy: true,
    langDir: "locales",
    defaultLocale: "en",
  },
  runtimeConfig: {
    public: {
      pexelsApiKey: process.env.PEXELS_API_KEY,
    },
  },
});
