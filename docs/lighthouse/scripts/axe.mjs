// Revisión con axe-core (reglas WCAG 2.x A/AA + buenas prácticas) en varias pantallas y estados. Uso: node axe.mjs <etiqueta>
import fs from 'node:fs'
import path from 'node:path'
import { createRequire } from 'node:module'
import { fileURLToPath } from 'node:url'
import puppeteer from 'puppeteer-core'

const require = createRequire(import.meta.url)
const axeSrc = fs.readFileSync(require.resolve('axe-core/axe.min.js'), 'utf8')
const aqui = path.dirname(fileURLToPath(import.meta.url))
const etiqueta = process.argv[2] || 'antes'
const base = 'http://localhost:5173'
const env = Object.fromEntries(
  fs.readFileSync(process.env.ENVFILE, 'utf8').split(/\r?\n/).filter((l) => l && !l.startsWith('#')).map((l) => [l.slice(0, l.indexOf('=')), l.slice(l.indexOf('=') + 1)]),
)

const browser = await puppeteer.launch({
  executablePath: 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
  headless: 'new',
  userDataDir: path.join(aqui, `profile-axe-${etiqueta}`),
})
const page = await browser.newPage()
const lecturas = []

async function revisar(nombre, ancho) {
  await page.evaluate(axeSrc)
  const r = await page.evaluate(async () => {
    // eslint-disable-next-line no-undef
    const res = await axe.run(document, {
      runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa', 'best-practice'] },
    })
    const encabezados = [...document.querySelectorAll('h1,h2,h3,h4,h5,h6')].map((h) => h.tagName + ':' + h.textContent.trim().slice(0, 30))
    const tablas = [...document.querySelectorAll('table')].map((t) => ({
      caption: !!t.querySelector('caption'),
      thSinScope: [...t.querySelectorAll('th')].filter((th) => !th.getAttribute('scope')).length,
    }))
    return {
      titulo: document.title,
      violaciones: res.violations.map((v) => ({ id: v.id, impacto: v.impact, nodos: v.nodes.map((n) => n.target.join(' ') + ' :: ' + (n.failureSummary || '').split('\n').slice(1, 3).join(' | ')).slice(0, 4) })),
      revisar: res.incomplete.map((v) => ({ id: v.id, n: v.nodes.length })),
      encabezados,
      tablas,
    }
  })
  console.log(`\n== ${nombre} (${ancho}px) -- ${r.titulo}`)
  console.log('  encabezados:', r.encabezados.join(' > '))
  if (r.tablas.length) console.log('  tablas:', JSON.stringify(r.tablas))
  console.log('  violaciones:', r.violaciones.length ? JSON.stringify(r.violaciones, null, 1) : 'ninguna')
  console.log('  por revisar:', JSON.stringify(r.revisar))
  lecturas.push({ nombre, ancho, titulo: r.titulo, violaciones: r.violaciones.map((v) => v.id), revisar: r.revisar })
}

async function ir(ruta, ancho) {
  await page.setViewport({ width: ancho, height: 900 })
  await page.goto(base + ruta, { waitUntil: 'networkidle0' })
}

// Públicas, con y sin errores de validación
for (const ancho of [1280, 320]) {
  await ir('/login', ancho)
  await page.evaluate(() => localStorage.clear())
  await ir('/login', ancho)
  await revisar('/login', ancho)
  await page.click('button[type=submit]')
  await new Promise((r) => setTimeout(r, 300))
  await revisar('/login con errores', ancho)
  await ir('/registro', ancho)
  await revisar('/registro', ancho)
  await page.click('button[type=submit]')
  await new Promise((r) => setTimeout(r, 300))
  await revisar('/registro con errores', ancho)
  await ir('/ruta-que-no-existe', ancho)
  await revisar('/404', ancho)
}

// Sesión
const res = await fetch('http://localhost:8000/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: new URLSearchParams({ username: env.SEED_ADMIN_CORREO, password: env.SEED_ADMIN_PASSWORD }),
})
const { access_token } = await res.json()
await page.evaluate((t) => localStorage.setItem('extra-liebres-token', t), access_token)
const alumnos = await (await fetch('http://localhost:8000/api/alumnos', { headers: { Authorization: 'Bearer ' + access_token } })).json()
const lista = Array.isArray(alumnos) ? alumnos : alumnos.items || alumnos.datos || []
const nocontrol = lista[0]?.nocontrol ?? lista[0]?.no_control
console.log('nocontrol de prueba:', nocontrol, 'alumnos:', lista.length)

const rutas = ['/', '/alumnos', '/alumnos/nuevo', `/alumnos/${nocontrol}`, `/alumnos/${nocontrol}/editar`, '/grupos', '/grupos/nuevo', '/grupos/1', '/grupos/1/editar', '/consultas', '/catalogos', '/usuarios']
for (const ancho of [1280, 320]) {
  for (const ruta of rutas) {
    await ir(ruta, ancho)
    await new Promise((r) => setTimeout(r, 500))
    await revisar(ruta, ancho)
  }
}
fs.mkdirSync(path.join(aqui, 'out', etiqueta), { recursive: true })
fs.writeFileSync(path.join(aqui, 'out', etiqueta, 'axe.json'), JSON.stringify(lecturas, null, 1))
await browser.close()
