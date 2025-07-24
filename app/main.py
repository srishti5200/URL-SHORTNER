# app/main.py
import os
from flask import Flask, jsonify, request, redirect, render_template, url_for
# Import URLManager and validate_url from utils.py
from app.utils import URLManager, validate_url
# Import ShortenedURL for type hinting/understanding, though not directly creating instances here
from app.models import ShortenedURL

app = Flask(__name__)
# Initialize the URLManager. In a real application, this would connect to a database.
url_manager = URLManager()

@app.route('/')
def index():
    """
    Renders the main HTML page for the URL shortener.
    """
    return render_template('index.html')

@app.route('/health')
def health_check():
    """
    Health check endpoint for the application.
    """
    return jsonify({
        "status": "healthy",
        "service": "URL Shortener API"
    })

@app.route('/api/health')
def api_health():
    """
    API health check endpoint.
    """
    return jsonify({
        "status": "ok",
        "message": "URL Shortener API is running"
    })

@app.route('/api/shorten', methods=['POST'])
def shorten_url():
    """
    API endpoint to shorten a given URL.
    Expects a JSON payload with 'original_url'.
    """
    data = request.get_json()
    original_url = data.get('original_url')

    if not original_url:
        return jsonify({"error": "No URL provided"}), 400

    # Validate URL using the utility function
    if not validate_url(original_url):
        return jsonify({"error": "Invalid URL format. Please include http:// or https://"}), 400

    try:
        shortened_url_obj = url_manager.add_url(original_url)
        # Construct the full short URL that the user can click
        short_url = url_for('redirect_to_original', short_code=shortened_url_obj.short_code, _external=True)
        return jsonify({
            "original_url": original_url,
            "short_code": shortened_url_obj.short_code,
            "short_url": short_url,
            "click_count": shortened_url_obj.click_count # Include click count in response
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        # Catch any other unexpected errors
        app.logger.error(f"Error shortening URL: {e}")
        return jsonify({"error": "An internal server error occurred"}), 500

@app.route('/api/urls', methods=['GET'])
def list_urls():
    """
    API endpoint to list all currently shortened URLs.
    Each URL dictionary now includes the 'click_count'.
    """
    all_urls = [url_obj.to_dict() for url_obj in url_manager.get_all_urls()]
    return jsonify(all_urls), 200

@app.route('/<short_code>')
def redirect_to_original(short_code):
    """
    Endpoint to redirect from a short code to the original URL.
    Also increments the click count for the accessed short URL.
    """
    original_url = url_manager.get_original_url(short_code)
    if original_url:
        # Increment the click count for this short code
        url_manager.increment_click(short_code)
        return redirect(original_url)
    else:
        # You can render a custom 404 page or simply return a JSON error
        return jsonify({"error": "Short URL not found"}), 404

if __name__ == '__main__':
    # Use environment variable for PORT, default to 5000 for local development
    # Also set debug=False for production best practice
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)