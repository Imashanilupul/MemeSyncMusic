SHELL := /usr/bin/sh

BACKEND_DIR     := Backend
BACKEND_APP_DIR := Backend/app
BACKEND_VENV    := Backend/venv
BACKEND_PY      := $(BACKEND_VENV)/Scripts/python.exe
BACKEND_PIP     := $(BACKEND_VENV)/Scripts/pip.exe

FRONTEND_DIR := frontend

.PHONY: help install install-backend install-frontend backend frontend dev

help:
	@echo "make install           # install backend + frontend dependencies"
	@echo "make install-backend   # install backend deps into Backend/venv"
	@echo "make install-frontend  # npm install in frontend/"
	@echo "make backend           # run FastAPI dev server (http://localhost:8000)"
	@echo "make frontend          # run Vite dev server"
	@echo "make dev               # run backend + frontend together"

install: install-backend install-frontend

install-backend:
	$(BACKEND_PIP) install -r $(BACKEND_DIR)/requirements.txt

install-frontend:
	cd $(FRONTEND_DIR) && npm install

backend:
	cd $(BACKEND_APP_DIR) && ../venv/Scripts/python.exe -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

frontend:
	cd $(FRONTEND_DIR) && npm run dev

dev:
	$(MAKE) -j2 backend frontend
