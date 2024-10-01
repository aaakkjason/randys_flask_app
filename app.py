from flask import Flask, render_template, request, abort, url_for, Response
import pandas as pd
import re

app = Flask(__name__)

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

# Inject the parent services dictionary into templates
@app.context_processor
def inject_services():
    return dict(parent_services=parent_services)

@app.route("/")
def home():
    return render_template("main.html", content_template="content/home.html")

@app.route("/about")
def about():
    return render_template("main.html", content_template="content/about.html")

@app.route("/services")
def services():
    return render_template("main.html", content_template="content/services.html")

@app.route("/service-area")
def service_area():
    return render_template("main.html", content_template="content/service-area.html")

@app.route("/permits")
def permits():
    return render_template("main.html", content_template="content/permits.html")

@app.route("/contact")
def contact():
    return render_template("main.html", content_template="content/contact.html")

@app.route("/our-work")
def our_work():
    return render_template("main.html", content_template="content/our-work.html")

# Show all combinations
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

# Contact form submission
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


from flask import Flask, render_template, request, abort, url_for, Response
import pandas as pd
import re

app = Flask(__name__)

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

# Inject the parent services dictionary into templates
@app.context_processor
def inject_services():
    return dict(parent_services=parent_services)

@app.route("/")
def home():
    return render_template("main.html", content_template="content/home.html")

@app.route("/about")
def about():
    return render_template("main.html", content_template="content/about.html")

@app.route("/services")
def services():
    return render_template("main.html", content_template="content/services.html")

@app.route("/service-area")
def service_area():
    return render_template("main.html", content_template="content/service-area.html")

@app.route("/permits")
def permits():
    return render_template("main.html", content_template="content/permits.html")

@app.route("/contact")
def contact():
    return render_template("main.html", content_template="content/contact.html")

@app.route("/our-work")
def our_work():
    return render_template("main.html", content_template="content/our-work.html")

# Show all combinations
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

# Contact form submission
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
        {"loc": url_for('about', _external=True)},
        {"loc": url_for('services', _external=True)},
        {"loc": url_for('service_area', _external=True)},
        {"loc": url_for('permits', _external=True)},
        {"loc": url_for('contact', _external=True)},
        {"loc": url_for('our_work', _external=True)},
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
    app.run(debug=True)


if __name__ == "__main__":
    app.run(debug=True)
