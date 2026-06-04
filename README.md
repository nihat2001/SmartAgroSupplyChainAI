# 🌾 SmartAgroSupplyChainAI

SmartAgroSupplyChainAI is a full-stack platform for managing agricultural product inventory and shipments, powered by **Groq AI (LLaMA 3.3-70b)** and **AI Tool Calling**.

---

## 🚀 Key Features
| Feature | Description |
| :--- | :--- |
| **🤖 AI Tool Calling** | LLaMA 3.3-70b automatically selects and executes the right tool from a set of 4 |
| **🌾 Inventory Management** | Add, view, and deduct warehouse stock |
| **🚚 Shipment Tracking** | Create shipments and track status (In Transit → Delivered) |
| **⚡ Redis Caching** | /inventory/ and /shipments/ endpoints cached for 1 hour with auto-invalidation |
| **🧹 Data Cleaning** | Regex pipeline strips URLs, HTML, emails, and special characters |
| **📊 Streamlit Dashboard** | 4-page interactive dashboard: Dashboard, Inventory, Shipments, AI Assistant |
| **🐳 Docker Compose** | 4 services (backend, frontend, postgres, redis) orchestrated with healthchecks |
| **✅ Pydantic Validation** | Field(gt=0) prevents negative quantity inputs |

---

## 📂 Project Structure
| File/Folder | Description |
| :--- | :--- |
| `backend.py` | FastAPI app — endpoints + AI Tool Calling logic |
| `tools.py` | 5 async tool functions (inventory & shipment operations) |
| `validation.py` | SQLAlchemy models (Inventory, Shipment) + Pydantic schemas |
| `database.py` | Async PostgreSQL engine + Redis cache setup |
| `data_clean.py` | Regex-based text sanitization |
| `frontend.py` | Streamlit dashboard (4 pages, Plotly charts) |
| `dockerfile` | python:3.11-slim → starts backend via uvicorn |
| `docker-compose.yml` | postgres + redis + backend + frontend services |
| `.env` | API keys and secrets (excluded from git) |
| `requirements.txt` | All Python dependencies |

---

## 🛠️ Tech Stack
| Layer | Technologies |
| :--- | :--- |
| **Backend** | Python 3.11, FastAPI 0.104, AsyncGroq, SQLAlchemy 2.0, Asyncpg, Pydantic 2.5 |
| **AI** | Groq Cloud API (LLaMA-3.3-70b-versatile), AI Tool Calling (tool_choice="auto") |
| **Data Layer** | PostgreSQL 15, Redis 7 (redis.asyncio), Regex (re) |
| **Frontend** | Streamlit, Plotly, Pandas, httpx |
| **Infrastructure** | Docker, Docker Compose, .dockerignore, .gitignore |

---

## 🔌 API Endpoints
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **POST** | `/inventory/` | Add a new product or increase existing stock |
| **GET** | `/inventory/` | Retrieve all stock (Redis cached) |
| **POST** | `/shipment/` | Create a new shipment, deduct from stock |
| **GET** | `/shipments/` | Retrieve all shipments (Redis cached) |
| **PATCH** | `/shipment/{id}/deliver` | Mark a shipment as Delivered |
| **POST** | `/ai-task/` | Natural language → AI Tool Calling |

---

## 📊 Streamlit Dashboard Pages
| Page | Functionality |
| :--- | :--- |
| **Dashboard** | Real-time KPI cards, stock bar chart, status donut chart, last 10 shipments |
| **Inventory** | Stock levels bar chart, data table, and product management form |
| **Shipments** | New shipment form, destination bar chart, and delivery status updates |
| **AI Assistant** | Natural language input → AI tool execution + quick-example buttons |

---

## 📦 Requirements
| Dependency | Version |
| :--- | :--- |
| `fastapi` | 0.104.1 |
| `uvicorn` | 0.24.0 |
| `sqlalchemy` | 2.0.23 |
| `asyncpg` | 0.29.0 |
| `redis` | 5.0.1 |
| `groq` | >=0.9.0 |
| `python-dotenv` | 1.0.0 |
| `pydantic` | 2.5.0 |
| `httpx` | 0.27.0 |

---

## ⚠️ Disclaimer
*This application is intended for demonstration and informational purposes only. For production use, authentication, rate limiting, and additional security measures are strongly recommended.*
