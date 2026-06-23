# Sys-Monitor

Sistema de monitoreo de métricas de sistema (CPU, RAM, Disco) distribuido.

## Arquitectura

Este repositorio está estructurado como un monorepo que contiene tres componentes principales:

- `agent/`: Script de Python (psutil) que recolecta y envía las métricas de los servidores.
- `backend/`: API RESTful con FastAPI que procesa y guarda las métricas.
- `frontend/`: Dashboard en React para visualización en tiempo real.

## Desarrollo

Ver las carpetas de cada componente para instrucciones específicas.
