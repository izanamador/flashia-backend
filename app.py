import os
from flask import Flask, request, redirect, url_for, render_template, send_from_directory
from werkzeug.utils import secure_filename

# Initialize Flask app
app = Flask(__name__)

# Folder to store uploaded files
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed extensions for uploaded files
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Function to check if the uploaded file is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Ensure the upload directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Route to render the main page with upload form
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle file uploads
@app.route('/upload', methods=['POST'])
def upload_image():
    # Check if the POST request has a file
    if 'file' not in request.files:
        return "No file part", 400

    file = request.files['file']

    # If no file is selected
    if file.filename == '':
        return "No selected file", 400

    # If file is valid, save it to the upload folder
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        print(f"File saved to: {filepath}")  # Debugging line

        # Redirect to the view page to display the uploaded image
        return redirect(url_for('view_image', filename=filename))

    return "Invalid file type", 400

# Route to display the uploaded image
@app.route('/view/<filename>')
def view_image(filename):
    return render_template('view.html', filename=filename)

# Route to serve the uploaded image
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Run the app locally
if __name__ == '__main__':
    app.run(debug=True)
