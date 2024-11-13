import os
from flask import Flask, make_response, jsonify, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from flask_cors import CORS
from dotenv import dotenv_values
from classes import database, analysis, parser
from flask import send_file
from logs.logmanager import LogManager
from classes import user_service, project, nessus_upload
import bcrypt
from flask_session import Session
import subprocess
import json
from datetime import datetime, timezone








# Gets all the env variables
config = dotenv_values(".env")
URI = config['URI']
AUTH = (config['USERNAME'], config['PASSWORD'])

# Used to know where to save the files ones uploaded
UPLOAD_FOLDER = "./nessus-drop"
ALLOWED_EXTENSIONS = {'nessus'} # not used but might be

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = os.urandom(12).hex() # Needed to sign session cookies and what not
# CORS(app, supports_credentials=True, resources={r"/flask-api/*": {"origins": "http://localhost:5173"}}) # have to have or nothing works

# Flask-Session configuration
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './flask_session'  
app.config['SESSION_PERMANENT'] = False  # Disable permanent sessions
app.config['SESSION_USE_SIGNER'] = True  # To add an extra layer of security
Session(app)

# Makes the database object can be used anywhere
neo4j = database.DataBase(URI, AUTH)
driver = neo4j.driver_make()

### TEST ROUTES ###

@app.route("/flask-api/test")
def test():
    return jsonify({'info': 'Test to makes sure everything is working'})

@app.route("/flask-api/test2")
def test2():
    records = neo4j.run_query("MATCH (n:Person) RETURN n LIMIT 25")
    names = []
    for record in records:
        names.append(record[0]['name'])
    return jsonify({'test':names})

### Project Routes ###

@app.route("/flask-api/create-project", methods=['POST'])
def createProject():
    data = request.get_json()
    projectName = data.get('name')
    fileName = data.get('fileName')
    ips = data.get('ips')
    status = 'scheduled'
    
    if 'username' not in session:
        print("User not authenticated - 'username' not in session")
        return jsonify({'error': 'User not authenticated'}), 401  # Return a 401 Unauthorized if no username in session
    
    print(f"Creating project for user: {session['username']}")
    newProId = project.createProject(driver, session['username'], projectName, fileName, status, ips, ['All'])
    session['currentProject'] = newProId
    return jsonify({'message': 'Poject has been created', 'projectId': newProId})

@app.route("/flask-api/all-projects")
def allProject():
    result = project.allProjectInfo(driver, session['username'])
    print("Projects fetched from database:", result)
    return jsonify({'data': result})


@app.route("/flask-api/total-project")
def something():
    result = project.countProjects(driver, session['username'])
    return jsonify({'data': result})

@app.route("/flask-api/current-project-info")
def getCurrentProjectInfo():
    result = project.getProjectInfomation(driver, session['username'], session['currentProject'])
    return jsonify({'data': result})

@app.route("/flask-api/get-all-project-info")
def getAllProjectsInfo():
    result = project.allProjectInfo(driver, session['username'])
    return jsonify({'data': result})

### Nessus Routes ###

# Handles the uploading of the file
@app.route("/flask-api/nessus-upload", methods=['POST'])
def nessusFileUpload():
    # Makes sure the POST is tagged that is a file and nothing else
    if 'file' not in request.files:
        return jsonify({'info':'Need to be told it is file upload'})
    
    file = request.files['file']
    # Checks that a file was upload (could be removed becase frontend handles this)
    if file.filename == '':
        print('No selected file')
        return jsonify({'message':'no file'})
    if file:
        # security stuff
        filename = secure_filename(file.filename)
        # Saves it based on the give file path and uses the upload file name
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        print(os.path.exists(app.config['UPLOAD_FOLDER']+'/'+filename))
        return jsonify({'message':'file was sent and has been saved on server'})

@app.route("/flask-api/process-nessus")
def processNessus():
    result = nessus_upload.processAndUpload(driver, session['currentProject'],  session['username'])
    return jsonify({'message': 'File has been uploaded'})
    

# Sends the entry points
@app.route("/flask-api/ranked-entry-points")
def rankedEntryPoints():
    return
#gets ips from the analysis
@app.route('/flask-api/get-ips', methods=['POST'])
def receive_ips():
    ips = request.json
    analysis.disallowed_ips=[]
    # Run analysis.py with the data as a JSON command-line argument
    for ip in ips:
        analysis.disallowed_ips.append(ip['ip'])
    
    analysis.analyze_nessus_file(driver, session['currentProject'] ,session['username'])

    try:
        data = request.get_json(force=True)
        if data is None or not isinstance(data, dict):
            return jsonify({"error": "Invalid JSON format"}), 400

        # Check for required fields
        project_id = data.get("project_id")
        ips = data.get("ips")
        exploits = data.get("exploits")

        # Validate types of each field
        if not isinstance(project_id, int):
            return jsonify({"error": "Invalid project_id: must be an integer"}), 400
        if not isinstance(ips, str):
            return jsonify({"error": "Invalid ips: must be a string"}), 400
        if not isinstance(exploits, list):
            return jsonify({"error": "Invalid exploits: must be a list"}), 400

        ip_list = ips.split(",") if ips else []

        response_data = {
            "project_id": project_id,
            "ips_count": len(ip_list),
            "exploits_count": len(exploits),
            "status": "Analysis started"
        }
        return jsonify(response_data), 200

    except Exception as e:
        print(f"Error in /get-ips: {e}")
        return jsonify({"error": str(e)}), 500

#gets unqiue ips from the file
@app.route("/flask-api/get-all-ips", methods=['POST'])
def get_all_ips():
    data = request.get_json()
    fileName = data.get('name')
    try:
        all_ips = parser.parserFile(fileName)
        print("All IPs:", all_ips)  # Debugging print
        return jsonify(all_ips.tolist())
    except Exception as e:
        print("Error:", e)  # Log the error for debugging
        return jsonify({"error": str(e)}), 500

### Logging fuctions ###

# Log user action from frontend
@app.route("/flask-api/log-action", methods=['POST'])
def log_action():
    data = request.json
    username = data.get('username', 'Anonymous')
    action = data.get('action', 'No action specified')
    details = data.get('details', 'No details provided')

    logger = LogManager()
    logger.log_action(username, action, details)
    
    return jsonify({"message": f"Action logged for {username}: {action} with details: {details}"})


# Download logs 
@app.route("/flask-api/download-logs/<date>", methods=['GET'])
def download_logs(date):
    current_utc_date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    print(f"Server's current UTC date: {current_utc_date}")
    
    log_file_path = os.path.join(app.root_path, 'logs', f'logs_{date}.log')
    print(f"Looking for log file at: {log_file_path}")  # Debug

    try:
        return send_file(log_file_path, as_attachment=True)
    except FileNotFoundError:
        return jsonify({'error': 'Log file not found'}), 404

### Login and Create User ###

# creates user in the db
@app.route('/flask-api/create_user', methods=['POST'])
def create_user_route():
    data = request.get_json()
    first_name = data['first_name']
    last_name = data['last_name']
    username = data['username']
    password = data['password']

    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    with driver.session() as session:
        session.write_transaction(user_service.create_user, username, first_name, last_name, hashed_password.decode('utf-8'))
    
    return jsonify({"status": "User created successfully"})

# checks login information 
@app.route('/flask-api/login', methods=['POST'])
def login_route():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if user_service.login_user(driver, username, password):
        session['username'] = username  # Store username in session
        session_id = session.sid
        return jsonify({"status": "Login successful", "session_id": session_id})
    else:
        return jsonify({"status": "Invalid username or password"}), 401

# clears session and deletes all session files
@app.route('/flask-api/logout', methods=['POST'])
def logout_route():
    session.pop('username', None)
    session.clear()

    # List session files for debugging
    session_files = os.listdir(app.config['SESSION_FILE_DIR'])
    print(f"Session files after logout: {session_files}")

    # Optionally manually delete files if they are not cleared
    for file in session_files:
        file_path = os.path.join(app.config['SESSION_FILE_DIR'], file)
        os.remove(file_path)

    return jsonify({"status": "Logged out successfully"})

#checks whether the session contains the username
@app.route('/flask-api/check_session', methods=['GET'])
def check_session_route():
    if 'username' in session:
        return jsonify({"status": "Logged in", "logged_in": True, "username": session['username'], "session_id": session.sid})
    else:
        return jsonify({"status": "Not Logged in", "logged_in": False, "username": ''})


#Log Manager 
@app.route("/flask-api/log_export", methods=['POST'])
def log_export():
    data = request.json
    ip_addresses = data.get("ip_addresses", [])
    export_format = data.get("export_format", "unknown")

    logger = LogManager()  # Create a LogManager instance
    for ip in ip_addresses:
        logger.log_action("User", "Export", f"Exporting IP: {ip} in format {export_format}")

    return jsonify({"message": "Export logged successfully"}), 200 