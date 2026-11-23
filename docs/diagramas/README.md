# Diagramas del proyecto

| Imagen | Qué muestra | Fuente editable |
|---|---|---|
| [`docs/arquitectura.png`](../arquitectura.png) | Navegador, frontend, API por capas, base de datos, Open-Meteo (con respaldo en wttr.in), entornos y CI | [`arquitectura.svg`](arquitectura.svg) (escrito a mano) |
| [`db/er.png`](../../db/er.png) | Modelo entidad-relación: 7 tablas, llaves, relaciones 1:N y N:M, restricciones | [`er.svg`](er.svg) (generado por `generar.py`) |

## Cómo se generan

Todo con un solo script que **solo usa la biblioteca estándar de Python** (no agrega dependencias al proyecto):

```powershell
python docs/diagramas/generar.py             # SVG y PNG
python docs/diagramas/generar.py --solo-svg  # solo los SVG (no necesita navegador)
```

1. **Modelo entidad-relación.** `generar.py` lee las migraciones de Alembic (`db/migrations/versions/`) con el
   módulo `ast` de Python, sin ejecutarlas ni conectarse a la base de datos. De la función `upgrade()` saca tablas,
   columnas con su tipo, `NULL`, llaves primarias y foráneas, `CHECK` y `UNIQUE` (incluidos los `CHECK` que cambian
   migraciones posteriores, como el rol lector de la 0004), y dibuja `er.svg`. Si cambia el modelo y se crea otra
   migración, se vuelve a correr el script. La posición de cada tabla está en el diccionario
   `DISPOSICION` del script.
2. **Arquitectura.** `arquitectura.svg` se edita a mano (es texto; se puede abrir en el navegador o en VS Code).
   Cada dato sale del código: puertos y servicios de `infra/docker-compose.yml`, `render.yaml`,
   `frontend/vercel.json`, los Dockerfile y `.github/workflows/ci.yml`.
3. **SVG a PNG.** El script abre cada SVG con Microsoft Edge o Google Chrome en modo `--headless` y guarda una
   captura del tamaño exacto del dibujo (2000 px de ancho). Si el navegador no está en la ruta de siempre,
   define la variable de entorno `NAVEGADOR` con la ruta del ejecutable.

## Qué revisar a mano después de cambiar algo

- Que el PNG se vea completo (nada encimado ni cortado).
- Que el diagrama de arquitectura no muestre nada que no exista en el código.
