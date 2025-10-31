/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: ['arxiv.org'],
  },
  env: {
    REPORTER_URL: process.env.REPORTER_URL || 'https://reporter-cfskbkrt4a-ez.a.run.app',
    ANALYZER_URL: process.env.ANALYZER_URL || 'https://analyzer-cfskbkrt4a-ez.a.run.app',
    SUMMARIZER_URL: process.env.SUMMARIZER_URL || 'https://summarizer-cfskbkrt4a-ez.a.run.app',
    GCP_PROJECT: process.env.GCP_PROJECT || 'echo-476821',
  },
}

module.exports = nextConfig
