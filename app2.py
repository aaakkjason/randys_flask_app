from flask import Flask, render_template, request, abort, url_for, Response, send_from_directory
import pandas as pd
import re

app = Flask(__name__)

# Determine if the app is in production mode (set to True for production)
IS_PRODUCTION = False  # Set to True to switch to CDN paths for production

# Define paths based on environment
LOCAL_IMAGE_PATH = "/static/images/"
CDN_IMAGE_PATH = "https://static.randyspro.com/images/" if IS_PRODUCTION else LOCAL_IMAGE_PATH

# Function to generate image URLs dynamically based on environment
def get_image_url(filename):
    return f"{CDN_IMAGE_PATH}{filename}"

# Set the directory path for serving images in development mode
IMAGE_DIRECTORY = 'E:\\merged2'

# Load the service and location datasets
servicecats_df = pd.read_csv("servicecats.csv")
locationcats_df = pd.read_csv("locationcats.csv")

# Create a custom slug function
def create_slug(text):
    text = text.lower()
    text = text.replace(" ", "-")
    text = re.sub(r"[^a-z0-9-]", "", text)
    text = re.sub(r"-+", "-", text)
    text = text.strip("-")
    return text

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

# Filter parent and child services based on 'parent_main'
for _, service in servicecats_df.iterrows():
    # If the service is a parent service, add it to the parent_services dictionary
    if service['parent_main'] == 'yes':
        parent_services[service['name']] = []  # Initialize with an empty list for children

# Add child services to their respective parent in the dictionary
for _, service in servicecats_df.iterrows():
    if service['parent'] in parent_services:
        parent_services[service['parent']].append({
            'name': service['name'],
            'slug': create_slug(service['name']),
            'desc': service['desc']
        })

# Inject the parent services dictionary and image URL function into templates
@app.context_processor
def inject_services():
    return dict(parent_services=parent_services, get_image_url=get_image_url)


# Route for serving images from the local directory (for development mode only)
@app.route('/images/<filename>')
def serve_image(filename):
    if IS_PRODUCTION:
        # In production, this route should not be used
        abort(404)
    else:
        # Serve images from the local directory in development mode
        return send_from_directory(IMAGE_DIRECTORY, filename)


# Homepage route
@app.route("/")
def home():
    return render_template("main.html", content_template="content/home.html")


# Example route to display all service-location combinations
@app.route("/combinations")
def show_combinations():
    return render_template("main.html", content_template="content/combinations.html", combinations=combinations)


# Dynamic route for specific service and location combinations using slugs
@app.route("/<county_slug>-county/<location_slug>/<service_slug>")
def show_combination_detail(service_slug, location_slug, county_slug):
    for combination in combinations:
        if (combination['service_slug'] == service_slug and
            combination['location_slug'] == location_slug and
            combination['county_slug'] == county_slug):
            return render_template("main.html", content_template="content/combination_detail.html", combination=combination)
    
    # If no match found, return a 404 error page
    abort(404)


# Form submission route for contact form
@app.route("/submit_contact", methods=["POST"])
def submit_contact():
    # Retrieve form data
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    message = request.form.get("message")

    # Pass the form data to the template to display it on the new page
    return render_template("main.html", content_template="content/submit_contact.html", 
                           first_name=first_name, last_name=last_name, email=email, 
                           phone=phone, message=message)


# Create a sitemap route that displays all possible pages/routes
@app.route("/sitemap.xml", methods=["GET"])
def sitemap():
    # List of static routes
    static_routes = [
        {"loc": url_for('home', _external=True)},
        {"loc": url_for('show_combinations', _external=True)}
    ]

    # List of dynamic routes based on combinations
    dynamic_routes = []
    for combination in combinations:
        dynamic_routes.append({
            "loc": url_for('show_combination_detail', 
                           county_slug=combination['county_slug'], 
                           location_slug=combination['location_slug'], 
                           service_slug=combination['service_slug'], 
                           _external=True)
        })

    # Render the sitemap as XML
    sitemap_template = render_template("sitemap.xml", static_routes=static_routes, dynamic_routes=dynamic_routes)
    return Response(sitemap_template, mimetype="application/xml")


if __name__ == "__main__":
    app.run(debug=not IS_PRODUCTION)
