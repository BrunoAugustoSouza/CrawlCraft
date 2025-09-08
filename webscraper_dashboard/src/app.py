from flask import Flask, render_template, request, send_file, redirect, url_for
from playwright.sync_api import sync_playwright
import csv
import io
import os
import uuid # For generating unique IDs for scrape jobs

# Database imports
from sqlalchemy import create_engine, Column, String, Text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# --- Database Setup ---
# Use an in-memory SQLite database for simplicity.
# For a production application, you'd use a file-based SQLite, PostgreSQL, MySQL, etc.
DATABASE_URL = "sqlite:///scraped_data.db" # This will create a file named scraped_data.db

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()

# Define your database model
class ScrapedItem(Base):
    __tablename__ = 'scraped_items'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    scrape_job_id = Column(String, nullable=False) # To link items to a specific scrape run
    text = Column(Text, nullable=True)
    href = Column(Text, nullable=True)

    def __repr__(self):
        return f"<ScrapedItem(text='{self.text}', href='{self.href}')>"

# Create tables if they don't exist
Base.metadata.create_all(engine)

app = Flask(__name__)

# --- Função de Scraper com Playwright ---
def scrape_data_playwright(url, scrape_job_id):
    data = []
    session = Session() # Get a new database session
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url)

            elements = page.query_selector_all('a')
            for element in elements:
                text = element.text_content().strip()
                href = element.get_attribute('href')
                if text and href:
                    item_data = {'text': text, 'href': href}
                    data.append(item_data)
                    
                    # Store in database
                    scraped_item = ScrapedItem(scrape_job_id=scrape_job_id, text=text, href=href)
                    session.add(scraped_item)
            
            session.commit() # Commit all changes to the database
            browser.close()
    except Exception as e:
        session.rollback() # Rollback in case of error
        print(f"Erro ao raspar dados com Playwright: {e}")
    finally:
        session.close() # Always close the session
    return data

# --- Rotas do Flask ---
@app.route('/', methods=['GET', 'POST'])
def index():
    scraped_data = []
    scrape_job_id = None
    if request.method == 'POST':
        target_url = request.form.get('url_to_scrape')
        if target_url:
            scrape_job_id = str(uuid.uuid4()) # Generate a unique ID for this scrape job
            scraped_data = scrape_data_playwright(target_url, scrape_job_id)
            # Redirect to show results and enable download, passing the scrape_job_id
            if scraped_data:
                return redirect(url_for('show_results', scrape_job_id=scrape_job_id))
            else:
                return render_template('index.html', message="No data scraped or an error occurred.", data=[])
    
    return render_template('index.html', data=scraped_data)

@app.route('/results/<scrape_job_id>')
def show_results(scrape_job_id):
    session = Session()
    try:
        scraped_data = session.query(ScrapedItem).filter_by(scrape_job_id=scrape_job_id).all()
        # Convert SQLAlchemy objects to dictionaries for easier template rendering
        data_for_template = [{'text': item.text, 'href': item.href} for item in scraped_data]
        if not data_for_template:
            return "No data found for this scrape job ID.", 404
        return render_template('results.html', data=data_for_template, scrape_job_id=scrape_job_id)
    finally:
        session.close()

@app.route('/download_csv/<scrape_job_id>', methods=['GET'])
def download_csv(scrape_job_id):
    session = Session()
    try:
        data_to_csv = session.query(ScrapedItem).filter_by(scrape_job_id=scrape_job_id).all()
        
        if not data_to_csv:
            return "Nenhum dado para exportar para este ID de job.", 400

        si = io.StringIO()
        # Adapt CSV headers to the fields you are scraping
        fieldnames = ['text', 'href'] # Define your fieldnames explicitly
        
        writer = csv.DictWriter(si, fieldnames=fieldnames)
        writer.writeheader()
        
        for item in data_to_csv:
            writer.writerow({'text': item.text, 'href': item.href})
        
        output = io.BytesIO(si.getvalue().encode('utf-8'))
        output.seek(0)

        return send_file(output, mimetype='text/csv', as_attachment=True, download_name=f'scraped_data_{scrape_job_id}.csv')
    finally:
        session.close()

if __name__ == '__main__':
    app.run(debug=True)