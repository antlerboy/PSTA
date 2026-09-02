import { defineConfig } from 'vite'

export default defineConfig({
  root: 'deploy',
  base: '/',
  server: {
    host: '0.0.0.0',
    allowedHosts: ['terminal.local'],
  },
  plugins: [
    {
      name: 'psta-github-pages-base',
      configureServer(server) {
        server.middlewares.use((request, _response, next) => {
          if (request.url === '/PSTA') {
            request.url = '/'
          } else if (request.url?.startsWith('/PSTA/')) {
            request.url = request.url.slice('/PSTA'.length)
          }
          next()
        })
      },
    },
  ],
})
