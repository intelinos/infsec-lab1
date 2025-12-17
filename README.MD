# Secure REST API (FastAPI) — Lab

## Overview
Minimal secure REST API implemented with FastAPI, SQLAlchemy, JWT authentication, password hashing (bcrypt), and basic protections (XSS escaping, CORS). Tests are intentionally NOT included.

## Requirements
- Python 3.10+
- pip

## Setup (local)
1. Copy `.env.example` to `.env` and fill values (especially `JWT_SECRET`).
2. Create venv and install:
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Unix
# source .venv/bin/activate
pip install -r requirements.txt
