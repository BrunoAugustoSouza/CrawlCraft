# Airbnb Scraping - Automated Listings Scraper

<div align="center">
  <img src="../../gifs/airbnb_demo.gif" alt="Airbnb Scraping Demo" width="600"/>
</div>

---

## 📝 Project Description

This project automates scraping of Airbnb listings using **Python** and **Flask**.
It is **containerized with Docker** for easy deployment, and the API runs on **port 5000** to serve listing data.

The scraper collects key information such as:

* Listing title and description
* Price
* Availability
* URL links

The project is modularized in `src/` for scalability and maintainability.

---

## 📂 Project Structure

```
airbnb_scraping/
│
├── src/               # Python source code
│   └── ...
├── Dockerfile         # Container definition
├── requirements.txt   # Python dependencies
├── data/              # Optional: sample or output data
└── README.md          # Project documentation
```

---

## 🚀 How to Run

### 1️⃣ Run Locally

1. Create a virtual environment (optional but recommended):

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the Flask app:

```bash
python src/main.py
```

4. Access the app in your browser:

```
http://127.0.0.1:5000
```

---

### 2️⃣ Run with Docker

1. Build the Docker image:

```bash
docker build -t airbnb-scraper .
```

2. Run the container **exposing port 5000**:

```bash
docker run --rm -p 5000:5000 airbnb-scraper
```

3. Open your browser at:

```
http://localhost:5000
```

> The `-p 5000:5000` flag maps the container's Flask port to your machine, making the app accessible outside the container.

---

## 🛠️ Tech Stack

Python | Flask | Docker | Playwright | Pandas | SQLite

---

## 🔗 Contact / More Info

* GitHub: [Bruno Augusto](https://github.com/yourusername)
* LinkedIn: [brunoaugustosouza](https://www.linkedin.com/in/brunoaugustosouza/)

---

<div align="center">
  <img src="../../gifs/airbnb_demo.gif" alt="Airbnb Demo" width="400"/>
</div>
