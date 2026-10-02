# Guía de contribución

Gracias por tu interés en Sys-Monitor. Esta guía cubre el entorno, el flujo de trabajo y los
criterios de calidad. Para detalles de arquitectura y convenciones de código, consulta
[CLAUDE.md](CLAUDE.md).

## 1. Preparar el entorno

```sh
git clone https://github.com/DiegoTepichin/sys-monitor.git
cd sys-monitor

python -m venv venv && source venv/bin/activate
pip install -r requirements-dev.txt
pre-commit install

cp .env.example .env          # define tu propio API_KEY

cd frontend && npm ci && cd ..
```

Requisitos: Python 3.11+, Node 22+, Docker (opcional).

## 2. Ejecutar en local

| Terminal | Comando                      | Resultado                            |
| -------- | ---------------------------- | ------------------------------------ |
| 1        | `python app.py`              | API en `http://127.0.0.1:5002`       |
| 2        | `python agent.py`            | Envía métricas cada `POLL_INTERVAL`  |
| 3        | `cd frontend && npm run dev` | Dashboard en `http://localhost:3000` |

## 3. Flujo de trabajo con Git

1. Crea una rama desde `main`: `feat/descripcion-corta`, `fix/…`, `docs/…`.
2. Haz commits atómicos siguiendo [Conventional Commits](https://www.conventionalcommits.org/):

   | Tipo       | Uso                                            |
   | ---------- | ---------------------------------------------- |
   | `feat`     | Nueva funcionalidad                            |
   | `fix`      | Corrección de bug                              |
   | `refactor` | Cambio interno sin alterar comportamiento      |
   | `perf`     | Mejora de rendimiento                          |
   | `test`     | Tests nuevos o corregidos                      |
   | `docs`     | Solo documentación                             |
   | `build`    | Dependencias, Docker, empaquetado              |
   | `ci`       | GitHub Actions                                 |
   | `chore`    | Mantenimiento que no toca código de producción |

   Ejemplo: `fix(api): reject out-of-range percent values`

3. Si un hook de pre-commit reformatea archivos, vuelve a hacer `git add` y repite el commit.
4. Abre un Pull Request hacia `main`. El CI debe pasar en verde.

## 4. Antes de abrir un PR

```sh
ruff check . && ruff format --check .
pytest
cd frontend && npm run lint && npm run build
```

Checklist:

- [ ] Los tests cubren el comportamiento nuevo o corregido.
- [ ] Los colectores nuevos devuelven siempre un `dict` con clave `error` y nunca lanzan.
- [ ] Ningún secreto en el código (usa `.env`, que está en `.gitignore`).
- [ ] README / CLAUDE.md actualizados si cambian comandos, variables o endpoints.

## 5. Reportar bugs

Abre un issue con: pasos para reproducir, resultado esperado vs. obtenido, sistema operativo,
versión de Python y logs relevantes de `logs/app.log`.
