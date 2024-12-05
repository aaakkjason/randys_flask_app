from flask import Flask, render_template, request, abort, url_for, Response, send_from_directory
from datetime import datetime
import pandas as pd
import re
import logging
import random
import requests

app = Flask(__name__)

# Set the directory path for serving images
IMAGE_DIRECTORY = 'E:\\merged2'

# Load the service and location datasets
servicecats_df = pd.read_csv("servicecats.csv")
locationcats_df = pd.read_csv("locationcats.csv")
review_df = pd.read_csv("review.csv")
job_df = pd.read_csv("job.csv")

# Create a custom slug function
def create_slug(text):
    text = text.lower()
    text = text.replace(" ", "-")
    text = re.sub(r"[^a-z0-9-]", "", text)
    text = re.sub(r"-+", "-", text)
    text = text.strip("-")
    return text

# Register create_slug as a Jinja2 filter
app.jinja_env.filters['create_slug'] = create_slug

# Create and register the custom datetime formatting filter
@app.template_filter('datetimeformat')
def datetimeformat(value, format='%Y-%m-%d'):
    try:
        timestamp = int(value)
        return datetime.utcfromtimestamp(timestamp).strftime(format)
    except (ValueError, TypeError):
        return ''  # Return an empty string if the value is not a valid timestamp

# Create a list of all possible combinations with slugs
combinations = []
for _, service in servicecats_df.iterrows():
    for _, location in locationcats_df.iterrows():
        combinations.append({
            "service_name": service['name'],
            "service_slug": create_slug(service['name']),
            "service_desc": service['desc'],
            "location_name": location['location_name'],
            "location_slug": create_slug(location['location_name']),
            "county_name": location['county_name'],
            "county_slug": create_slug(location['county_name']),
            "municipality": location['municipality'],
            "area_codes": location['area_codes']
        })

# Create parent-child service structure
parent_services = {}
for _, service in servicecats_df.iterrows():
    if service['parent_main'] == 'yes':
        parent_services[service['name']] = []

# Add child services to their respective parent in the dictionary
for _, service in servicecats_df.iterrows():
    if service['parent'] in parent_services:
        parent_services[service['parent']].append({
            'name': service['name'],
            'slug': create_slug(service['name']),
            'desc': service['desc']
        })

# Inject the parent services dictionary into templates
@app.context_processor
def inject_services():
    return dict(parent_services=parent_services)

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,  # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s',  # Format for the log messages
    handlers=[
        logging.FileHandler("app.log"),  # Log messages to a file named 'app.log'
        logging.StreamHandler()  # Also log messages to the console
    ]
)

# Log a message when the application starts
logging.info("Flask application has started.")

#################            CACHING           #################################

@app.after_request
def add_cache_control_headers(response):
    if request.path.startswith('/static/'):
        response.headers['Cache-Control'] = 'public, max-age=31536000'  # Cache for 1 year
    else:
        response.headers['Cache-Control'] = 'public, max-age=3600'  # Cache for 1 hour
    return response


#################            CUSTOM JINJA SHORTCODE           #################################

# Create a custom Jinja2 shortcode for getting a random image from the API
def get_random_image(keyword):
    try:
        # API call to your service running on port 8000
        api_url = f"http://127.0.0.1:8000/filenames?keyword={keyword}"
        response = requests.get(api_url)

        if response.status_code == 200:
            filenames = response.json().get("filenames", "")
            filenames_list = filenames.split(", ")

            # Randomly select one filename
            if filenames_list:
                return filenames_list[random.randint(0, len(filenames_list) - 1)]
            else:
                return "default-image.jpg"  # Fallback if no filenames are found
        else:
            logging.error(f"API request failed with status code: {response.status_code}")
            return "default-image.jpg"
    except Exception as e:
        logging.error(f"Error fetching image from API: {e}")
        return "default-image.jpg"

# Register the get_random_image function as a Jinja2 filter
app.jinja_env.globals.update(random_image=get_random_image)


#################            ROUTES           #################################

@app.route("/")
def home():
    logging.info("Home page accessed.")
    return render_template("main.html", content_template="content/home.html")

@app.route("/<page>")
def render_page(page):
    allowed_pages = ["about", "services", "service-area", "permits", "contact", "our-work", "estimate"]
    if page in allowed_pages:
        logging.info(f"Page '{page}' accessed.")
        return render_template("main.html", content_template=f"content/{page}.html")
    else:
        logging.warning(f"Attempted access to non-existent page: {page}")
        abort(404)

@app.route("/jobs")
def show_jobs():
    jobs = job_df.to_dict(orient='records')
    logging.info("Jobs page accessed.")
    return render_template("main.html", content_template="content/jobs.html", jobs=jobs)

@app.route("/job/<job_slug>")
def show_job_detail(job_slug):
    try:
        for _, job in job_df.iterrows():
            if create_slug(job['Title']) == job_slug:
                job_photos = job['wpcf-job-photos'].split('|') if pd.notna(job['wpcf-job-photos']) else []
                logging.info(f"Displaying details for job: {job['Title']}")
                return render_template("main.html", content_template="content/job_detail.html", job=job, job_photos=job_photos)
        logging.warning(f"No job found for slug: {job_slug}")
        abort(404)
    except Exception as e:
        logging.error(f"Error displaying job details for slug {job_slug}: {e}")
        abort(500)

@app.route("/reviews")
def show_reviews():
    reviews = review_df.to_dict(orient='records')
    logging.info("Reviews page accessed.")
    return render_template("main.html", content_template="content/reviews.html", reviews=reviews)

@app.route('/images/<filename>')
def serve_image(filename):
    logging.info(f"Serving image: {filename}")
    return send_from_directory(IMAGE_DIRECTORY, filename)

@app.route("/combinations")
def show_combinations():
    logging.info("Combinations page accessed.")
    return render_template("main.html", content_template="content/combinations.html", combinations=combinations)

@app.route("/<county_slug>-county/<location_slug>/<service_slug>")
def show_combination_detail(service_slug, location_slug, county_slug):
    for combination in combinations:
        if (combination['service_slug'] == service_slug and
            combination['location_slug'] == location_slug and
            combination['county_slug'] == county_slug):
            logging.info(f"Displaying combination details: {county_slug} - {location_slug} - {service_slug}")
            return render_template("main.html", content_template="content/combination_detail.html", combination=combination)
    logging.warning(f"No combination found for slugs: {county_slug}, {location_slug}, {service_slug}")
    abort(404)

@app.route("/submit_contact", methods=["POST"])
def submit_contact():
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    message = request.form.get("message")
    logging.info(f"Contact form submitted by: {first_name} {last_name} - Email: {email}, Phone: {phone}")
    return render_template("main.html", content_template="content/submit_contact.html", 
                           first_name=first_name, last_name=last_name, email=email, 
                           phone=phone, message=message)


#################            SITEMAP           #################################

@app.route("/sitemap.xml", methods=["GET"])
def sitemap():
    static_routes = [
        {"loc": url_for('home', _external=True)},
        {"loc": url_for('render_page', page='about', _external=True)},
        {"loc": url_for('render_page', page='services', _external=True)},
        {"loc": url_for('render_page', page='service-area', _external=True)},
        {"loc": url_for('render_page', page='permits', _external=True)},
        {"loc": url_for('render_page', page='contact', _external=True)},
        {"loc": url_for('render_page', page='our-work', _external=True)},
        {"loc": url_for('show_reviews', _external=True)},
        {"loc": url_for('show_combinations', _external=True)},
        {"loc": url_for('show_jobs', _external=True)}
    ]

    dynamic_routes = []
    for combination in combinations:
        dynamic_routes.append({
            "loc": url_for('show_combination_detail',
                           county_slug=combination['county_slug'],
                           location_slug=combination['location_slug'],
                           service_slug=combination['service_slug'],
                           _external=True)
        })

    for _, job in job_df.iterrows():
        dynamic_routes.append({
            "loc": url_for('show_job_detail', job_slug=create_slug(job['Title']), _external=True)
        })

    sitemap_template = render_template("sitemap.xml", static_routes=static_routes, dynamic_routes=dynamic_routes)
    logging.info("Sitemap accessed and generated.")
    return Response(sitemap_template, mimetype="application/xml")


#################            ERROR HANDLERS           #################################

@app.errorhandler(404)
def page_not_found(e):
    logging.warning(f"Page not found: {request.url}")
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_server_error(e):
    logging.error(f"Server error at {request.url}: {e}")
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.run(debug=True)
