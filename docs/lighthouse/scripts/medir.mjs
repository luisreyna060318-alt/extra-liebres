// Mide con Lighthouse (móvil y escritorio) las pantallas públicas y privadas. Uso: node medir.mjs <etiqueta>
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import puppeteer from 'puppeteer-core'
import lighthouse from 'lighthouse'
import desktopConfig from 'lighthouse/core/config/desktop-config.js'

const aqui = path.dirname(fileURLToPath(import.meta.url))
const etiqueta = process.argv[2] || 'antes'
const base = 'http://localhost:5173'
const salida = path.join(aqui, 'out', etiqueta)
fs.mkdirSync(salida, { recursive: true })
const env = Object.fromEntries(
  fs.readFileSync(process.env.ENVFILE, 'utf8').split(/\r?\n/).filter((l) => l && !l.startsWith('#')).map((l) => [l.slice(0, l.indexOf('=')), l.slice(l.indexOf('=') + 1)]),
)

const browser = await puppeteer.launch({
  executablePath: 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
  headless: 'new',
  args: ['--no-sandbox'],
  userDataDir: path.join(aqui, `profile-${etiqueta}`),
})
const port = Number(new URL(browser.wsEndpoint()).port)
console.log('Chrome', await browser.version())

const publicas = ['/login', '/registro']
const privadas = ['/', '/alumnos', '/grupos', '/grupos/1', '/consultas', '/catalogos', '/usuarios']
const resumen = []

async function medir(ruta, modo) {
  const r = await lighthouse(
    base + ruta,
    { port, output: ['json', 'html'], logLevel: 'error', disableStorageReset: true, onlyCategories: ['performance', 'accessibility', 'best-practices', 'seo'] },
    modo === 'escritorio' ? desktopConfig : undefined,
  )
  const nombre = (ruta === '/' ? 'inicio' : ruta.slice(1).replace(/\//g, '-')) + '-' + modo
  fs.writeFileSync(path.join(salida, nombre + '.json'), r.report[0])
  fs.writeFileSync(path.join(salida, nombre + '.html'), r.report[1])
  const lhr = r.lhr
  const fila = { ruta, modo, version: lhr.lighthouseVersion, chrome: lhr.environment.hostUserAgent, finalUrl: lhr.finalDisplayedUrl }
  for (const [k, c] of Object.entries(lhr.categories)) fila[k] = Math.round(c.score * 100)
  fila.fallos = lhr.categories.accessibility.auditRefs.filter((x) => lhr.audits[x.id].score === 0).map((x) => x.id)
  resumen.push(fila)
  console.log(JSON.stringify(fila))
}

const page = await browser.newPage()
await page.goto(base + '/login')
await page.evaluate(() => localStorage.clear())
for (const ruta of publicas) for (const modo of ['movil', 'escritorio']) await medir(ruta, modo)

// Sesión: se pide el token a la API y se guarda donde lo busca la app (la contraseña no se escribe en ningún archivo)
const res = await fetch('http://localhost:8000/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: new URLSearchParams({ username: env.SEED_ADMIN_CORREO, password: env.SEED_ADMIN_PASSWORD }),
})
const { access_token } = await res.json()
await page.evaluate((t) => localStorage.setItem('extra-liebres-token', t), access_token)
for (const ruta of privadas) for (const modo of ['movil', 'escritorio']) await medir(ruta, modo)

fs.writeFileSync(path.join(salida, 'resumen.json'), JSON.stringify(resumen, null, 1))
await browser.close()
