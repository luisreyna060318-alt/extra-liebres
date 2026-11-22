// Revisa con axe estados que Lighthouse no ve (paneles de confirmación, diálogo, pestañas, errores de formulario),
// el contraste del anillo de foco y el desbordamiento horizontal. Uso: node estados.mjs <etiqueta>
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
const esperar = (ms) => new Promise((r) => setTimeout(r, ms))

const browser = await puppeteer.launch({
  executablePath: 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
  headless: 'new',
  userDataDir: path.join(aqui, `profile-estados-${etiqueta}`),
})
const page = await browser.newPage()
const salida = []

async function axe(nombre) {
  await page.evaluate(axeSrc)
  const r = await page.evaluate(async () => {
    // eslint-disable-next-line no-undef
    const res = await axe.run(document, { runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa', 'best-practice'] } })
    return {
      v: res.violations.map((x) => x.id + ' [' + x.nodes.map((n) => n.target.join(' ')).slice(0, 3).join(' ; ') + ']'),
      i: res.incomplete.map((x) => x.id + ' x' + x.nodes.length),
      h: [...document.querySelectorAll('h1,h2,h3,h4')].map((h) => h.tagName + ':' + h.textContent.trim().slice(0, 25)).join(' > '),
    }
  })
  console.log(`${nombre}\n   encabezados: ${r.h}\n   violaciones: ${r.v.length ? r.v.join(' | ') : 'ninguna'}\n   por revisar: ${r.i.join(', ') || '-'}`)
  salida.push({ nombre, violaciones: r.v, revisar: r.i })
}

async function clic(selector, texto) {
  const ok = await page.evaluate(
    (sel, tx) => {
      const el = [...document.querySelectorAll(sel)].find((e) => !tx || e.textContent.trim().startsWith(tx) || (e.getAttribute('aria-label') || '').startsWith(tx))
      if (!el) return false
      el.click()
      return true
    },
    selector,
    texto,
  )
  if (!ok) console.log('   (no se encontró)', selector, texto)
  await esperar(500)
}

const res = await fetch('http://localhost:8000/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: new URLSearchParams({ username: env.SEED_ADMIN_CORREO, password: env.SEED_ADMIN_PASSWORD }),
})
const { access_token } = await res.json()
await page.goto(base + '/login')
await page.evaluate((t) => localStorage.setItem('extra-liebres-token', t), access_token)

for (const ancho of [1280, 360]) {
  await page.setViewport({ width: ancho, height: 900 })
  const p = `(${ancho}px) `
  await page.goto(base + '/alumnos', { waitUntil: 'networkidle0' })
  await clic('button', 'Dar de baja')
  await axe(p + 'alumnos: diálogo de baja abierto')

  await page.goto(base + '/usuarios', { waitUntil: 'networkidle0' })
  await clic('button', 'Suspender')
  await axe(p + 'usuarios: confirmación de suspender')

  await page.goto(base + '/catalogos', { waitUntil: 'networkidle0' })
  await clic('button', 'Nuevo')
  await axe(p + 'catálogos/promotores: panel de formulario')
  await clic('button[type=submit]', 'Guardar')
  await axe(p + 'catálogos/promotores: formulario con errores')
  await clic('button', 'Eliminar')
  await axe(p + 'catálogos/promotores: confirmación de eliminar')
  for (const pestana of ['Actividades', 'Semestres']) {
    await page.goto(base + '/catalogos', { waitUntil: 'networkidle0' })
    await clic('[role=tab]', pestana)
    await axe(p + 'catálogos/' + pestana)
    await clic('button', 'Nuev')
    await axe(p + 'catálogos/' + pestana + ': panel de formulario')
  }

  await page.goto(base + '/alumnos/nuevo', { waitUntil: 'networkidle0' })
  await clic('button[type=submit]', '')
  await axe(p + 'alumnos/nuevo: errores')
  await page.goto(base + '/grupos/nuevo', { waitUntil: 'networkidle0' })
  await clic('button[type=submit]', '')
  await axe(p + 'grupos/nuevo: errores')
  await page.goto(base + '/consultas', { waitUntil: 'networkidle0' })
  await axe(p + 'consultas')

  // Desbordamiento horizontal (reflujo) en cada pantalla
  const rutas = ['/login', '/registro', '/', '/alumnos', '/grupos', '/grupos/1', '/consultas', '/catalogos', '/usuarios']
  const desbordan = []
  for (const r of rutas) {
    await page.goto(base + r, { waitUntil: 'networkidle0' })
    const d = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth)
    if (d > 0) desbordan.push(r + ' (+' + d + 'px)')
  }
  console.log(p + 'desbordamiento horizontal:', desbordan.join(', ') || 'ninguno')
}

// Foco: se recorre la página con Tab y se calcula el contraste del anillo contra el fondo real
await page.setViewport({ width: 1280, height: 900 })
const luz = (rgb) => {
  const c = rgb.map((v) => v / 255).map((v) => (v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4))
  return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
}
const contraste = (a, b) => (Math.max(luz(a), luz(b)) + 0.05) / (Math.min(luz(a), luz(b)) + 0.05)
for (const ruta of ['/alumnos', '/alumnos/nuevo']) {
  await page.goto(base + ruta, { waitUntil: 'networkidle0' })
  const peores = []
  for (let i = 0; i < 30; i++) {
    await page.keyboard.press('Tab')
    const info = await page.evaluate(() => {
      const el = document.activeElement
      if (!el || el === document.body) return null
      const cs = getComputedStyle(el)
      // Fondo contra el que se ve el contorno: lo que hay justo afuera del elemento (4 px a la izquierda), el primer fondo opaco
      const r = el.getBoundingClientRect()
      const x = Math.max(1, r.left - 4)
      const y = r.top + r.height / 2
      let fondo = 'rgb(255, 255, 255)'
      for (const e of document.elementsFromPoint(x, y)) {
        if (e === el) continue
        const b = getComputedStyle(e).backgroundColor
        if (b !== 'rgba(0, 0, 0, 0)' && b !== 'transparent') {
          fondo = b
          break
        }
      }
      return { n: el.tagName + '.' + el.className + (el.getAttribute('aria-label') ? '[' + el.getAttribute('aria-label') + ']' : ''), color: cs.outlineColor, estilo: cs.outlineStyle, ancho: cs.outlineWidth, fondo }
    })
    if (!info) continue
    const num = (s) => s.match(/[\d.]+/g).slice(0, 3).map(Number)
    const c = contraste(num(info.color), num(info.fondo))
    peores.push({ ...info, c: Number(c.toFixed(2)) })
  }
  peores.sort((a, b) => a.c - b.c)
  console.log(`foco ${ruta}: elementos recorridos ${peores.length}; peor contraste del anillo = ${peores[0]?.c}:1 (${peores[0]?.n}, fondo ${peores[0]?.fondo}); mejor = ${peores.at(-1)?.c}:1`)
}

fs.mkdirSync(path.join(aqui, 'out', etiqueta), { recursive: true })
fs.writeFileSync(path.join(aqui, 'out', etiqueta, 'estados.json'), JSON.stringify(salida, null, 1))
await browser.close()
