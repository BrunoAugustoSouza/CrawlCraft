import io, csv
from flask import Flask, render_template, request, send_file, redirect, url_for
import pandas as pd
from common.db import Session, HomesUrl, Price
from common.pipeline import run_scraper

app = Flask(__name__)

# --- Rotas do Flask ---
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        action = request.form.get("action")

        # pega os valores do formulário
        city = request.form.get("city")
        checkin = request.form.get("checkin")
        checkout = request.form.get("checkout")
        adults = request.form.get("adults", type=int)
        currency = request.form.get("currency")

        if action == "run_scraper":
            # mapeia cidade -> nome/país
            mapping = {
                "new-york-usa": ("New York", "USA"),
                "rio-de-janeiro-brazil": ("Rio de Janeiro", "Brazil"),
                "dubai-uae": ("Dubai", "United Arab Emirates"),
                "paris-france": ("Paris", "France"),
                "london-uk": ("London", "UK"),
                "tokyo-japan": ("Tokyo", "Japan"),
                "barcelona-spain": ("Barcelona", "Spain"),
                "rome-italy": ("Rome", "Italy"),
                "bali-indonesia": ("Bali", "Indonesia"),
                "sydney-australia": ("Sydney", "Australia"),
            }
            city_name, country = mapping.get(city, (None, None))

            if not city_name or not country:
                return render_template("index.html", message="Cidade inválida")

            scraped_data = run_scraper(country, city_name, checkin, checkout, adults, currency)

            if scraped_data is not None and not scraped_data.empty:
                scrape_job_id = scraped_data['scrapeJobId'].iloc[0] if 'scrapeJobId' in scraped_data.columns else None
                return redirect(url_for("show_results", scrape_job_id=scrape_job_id))
            else:
                return render_template("index.html", message="No data scraped or an error occurred.", data=[])

        elif action == "save_data":
            # aqui você poderia só salvar os dados no banco ou sessão
            return render_template("index.html", message="Dados salvos. Agora clique em Run Scraper.")

    return render_template("index.html")


@app.route('/results/<scrape_job_id>')
def show_results(scrape_job_id):
    session = Session()
    try:
        scraped_data = session.query(Price).filter_by(scrapeJobId=scrape_job_id).all()
        # Convert SQLAlchemy objects to dictionaries for easier template rendering
        data_for_template = [
            {
                'isPropertyAvailable': item.isPropertyAvailable,
                'productId': item.productId,
                'priceTotal': item.priceTotal,
                'priceNightTotal': item.priceNightTotal,
                'checkIn': item.checkIn,
                'checkOut': item.checkOut,
                'currency': item.currency,
                'url': item.url
            }
            for item in scraped_data
        ]
        currency = data_for_template[0].get('currency', '-')
        if not data_for_template:
            return "No data found for this scrape job ID.", 404
        return render_template('results.html', 
                               data=data_for_template, 
                               scrape_job_id=scrape_job_id,
                               currency=currency)
    finally:
        session.close()

@app.route('/download_csv/<scrape_job_id>', methods=['GET'])
def download_csv(scrape_job_id):
    session = Session()
    try:
        data_to_csv = session.query(Price).filter_by(scrapeJobId=scrape_job_id).all()
        
        if not data_to_csv:
            return "Nenhum dado para exportar para este ID de job.", 400

        # pega dinamicamente todas as colunas do modelo Price
        fieldnames = [col.name for col in Price.__table__.columns]

        si = io.StringIO()
        writer = csv.DictWriter(si, fieldnames=fieldnames)
        writer.writeheader()
        
        for item in data_to_csv:
            row_dict = {col: getattr(item, col) for col in fieldnames}
            writer.writerow(row_dict)
        
        output = io.BytesIO(si.getvalue().encode('utf-8'))
        output.seek(0)

        return send_file(
            output,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'scraped_data_{scrape_job_id}.csv'
        )
    finally:
        session.close()

if __name__ == '__main__':
    app.run(debug=True)