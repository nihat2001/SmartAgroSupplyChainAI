** 🌾 SmartAgroSupplyChainAI **

📌 About
SmartAgroSupplyChainAI is a full-stack platform for managing agricultural product inventory and shipments, powered by Groq AI (LLaMA 3.3-70b) and AI Tool Calling.
Users can issue commands in plain natural language ("Send 50 tons wheat to Baku") — the AI automatically selects the correct tool and executes the operation against the database. The system is fully controllable via both a REST API and a visual Streamlit dashboard.

🚀 Key Features
FeatureDescription🤖 AI Tool CallingLLaMA 3.3-70b automatically selects and executes the right tool from a set of 4🌾 Inventory ManagementAdd, view, and deduct warehouse stock🚚 Shipment TrackingCreate shipments and track status (In Transit → Delivered)⚡ Redis Caching/inventory/ and /shipments/ endpoints cached for 1 hour with auto-invalidation🧹 Data CleaningRegex pipeline strips URLs, HTML tags, emails, and special characters before DB writes📊 Streamlit Dashboard4-page interactive dashboard: Dashboard, Inventory, Shipments, AI Assistant🐳 Docker Compose4 services (backend, frontend, postgres, redis) orchestrated with healthchecks✅ Pydantic ValidationField(gt=0) prevents negative quantity inputs

📂 Project Structure
SmartAgroSupplyChainAI/
│
├── backend.py          # FastAPI app — endpoints + AI Tool Calling logic
├── tools.py            # 5 async tool functions (inventory & shipment operations)
├── validation.py       # SQLAlchemy models (Inventory, Shipment) + Pydantic schemas
├── database.py         # Async PostgreSQL engine + Redis cache setup
├── data_clean.py       # Regex-based text sanitization
├── frontend.py         # Streamlit dashboard (4 pages, Plotly charts)
│
├── 🐳 dockerfile          # python:3.11-slim → starts backend via uvicorn
├── 🐳 docker-compose.yml  # postgres + redis + backend + frontend services
├── 🙈 .dockerignore       # .env, .git, __pycache__
├── 🔒 .env                # API keys and secrets (excluded from git)
├── 📦 requirements.txt    # All Python dependencies
└── 📖 README.md

🛠️ Tech Stack
Backend
Python 3.11        → Core application logic
FastAPI 0.104      → Async REST API (lifespan, Depends)
AsyncGroq          → Groq AI async client
SQLAlchemy 2.0     → Async ORM (create_async_engine, AsyncSession)
Asyncpg            → Async PostgreSQL driver
Pydantic 2.5       → Request validation and SQLAlchemy schemas
AI
Groq Cloud API     → LLaMA-3.3-70b-versatile inference engine
AI Tool Calling    → 4 dynamic tools: log_shipment, check_inventory,
                     add_inventory, get_shipments
tool_choice="auto" → Model selects the correct tool automatically
Data Layer
PostgreSQL 15      → inventory + shipments tables
Redis 7            → Async caching (redis.asyncio), TTL: 3600s
Regex (re)         → URL, HTML tag, email, and special character sanitization
Frontend
Streamlit          → 4-page interactive web dashboard
Plotly             → Bar charts (stock levels, shipments) + Donut chart (status)
Pandas             → DataFrame processing and display
httpx              → Async HTTP communication with the backend
Infrastructure
Docker             → python:3.11-slim image
Docker Compose     → 4 services + healthchecks + depends_on
.dockerignore      → Excludes .env, .git, __pycache__ from build context
.gitignore         → Excludes .env from version control

🔌 API Endpoints
REST Endpoints
MethodEndpointDescriptionPOST/inventory/Add a new product or increase existing stockGET/inventory/Retrieve all stock (Redis cached)POST/shipment/Create a new shipment, deduct from stockGET/shipments/Retrieve all shipments (Redis cached)PATCH/shipment/{id}/deliverMark a shipment as DeliveredPOST/ai-task/Natural language → AI Tool Calling

📊 Streamlit Dashboard Pages
▦ Dashboard
Real-time overview: 4 KPI cards (product types, total stock, shipments, in-transit count), stock bar chart, shipment status donut chart, last 10 shipments table.
◫ Inventory
Stock levels bar chart + data table. Right panel: product name + quantity form → POST /inventory/.
◎ Shipments
New shipment form, bar chart by destination, full shipment list, "Mark as Delivered" dropdown for in-transit shipments.
◇ AI Assistant
Natural language input → POST /ai-task/ → AI selects the right tool → result displayed. Includes 4 quick-example buttons for common operations.

📦 requirements.txt
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
asyncpg==0.29.0
redis==5.0.1
groq>=0.9.0
python-dotenv==1.0.0
pydantic==2.5.0
httpx==0.27.0

⚠️ Disclaimer
This application is intended for demonstration and informational purposes only. For production use, authentication, rate limiting, and additional security measures are strongly recommended.
