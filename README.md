# YieldX ⚡

<div align="center">
  <p><strong>Real-time financial dashboard and API tracking Vietnamese market data.</strong></p>
</div>

YieldX is a centralized platform designed to track and compare yield opportunities across various financial markets in Vietnam. It features a Python backend that scrapes live market data and an elegant, responsive React dashboard for data visualization.

---

## ✨ Features
*   **🥇 Gold Prices:** Real-time buying and selling prices from major Vietnamese brands (SJC, DOJI, PNJ, BTMC), including spread calculation.
*   **🏦 Bank Interest Rates:** Browse and compare deposit interest rates across multiple terms (1-36 months) from Vietnamese banks, featuring visual rate bars.
*   **💱 Forex Rates:** Exchange rates for major currency pairs and local banks.
*   **₿ Cryptocurrency:** Live market tracking of top cryptocurrencies by market cap with fast symbol indexing.

---

## 🛠 Tech Stack

**Frontend**
<br>
![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)
![Vite](https://img.shields.io/badge/vite-%23646CFF.svg?style=for-the-badge&logo=vite&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white)
![Zustand](https://img.shields.io/badge/zustand-%2320232a.svg?style=for-the-badge&logo=react&logoColor=white)

**Backend / Database**
<br>
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![PostgreSQL](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)

---

## 🚀 Installation & Setup

### Prerequisites
*   [Node.js](https://nodejs.org/) (v18+)
*   [Python](https://www.python.org/) (v3.10+)
*   PostgreSQL database (Cloud like Supabase, or locally hosted)

### 1. Clone the repository
```bash
git clone https://github.com/vovanhai2005/YieldX.git
cd YieldX
```

### 2. Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   Create a `.env` file in the `backend/` directory with your database credentials:
   ```env
   DB_HOST=your_db_host
   DB_PORT=5432
   DB_NAME=postgres
   DB_USER=your_user
   DB_PASSWORD=your_password
   ```
5. Run the FastAPI server:
   ```bash
   uvicorn main:app --reload --port 8000
   ```
   *The API will be available at `http://localhost:8000` and Swagger UI docs at `http://localhost:8000/docs`.*

### 3. Frontend Setup
Open a **new terminal window/tab** to run the frontend server parallel to the backend.

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install NodeJS dependencies:
   ```bash
   npm install
   ```
3. Run the Vite development server:
   ```bash
   npm run dev
   ```
   *The dashboard will be available at `http://localhost:5173`.*