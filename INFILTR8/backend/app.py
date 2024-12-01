import os
from flask import Flask, make_response, jsonify, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from flask_cors import CORS
from dotenv import dotenv_values
from classes import database, analysis, parser
from flask import send_file
from logs.logmanager import LogManager
from classes import user_service, project, nessus_upload, result
import bcrypt
from flask_session import Session
import subprocess
import json
from datetime import datetime, timezone
import secrets

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
    # nessus_upload.getDataExploits(driver, 'test-erik', 2)
    # testCreateProjectMany()
    temp = project.countFiles(driver, 'Test', 2)
    return jsonify({'info': 'Test to makes sure everything is working', 'data': temp})

@app.route("/flask-api/test2")
def test2():
    records = neo4j.run_query("MATCH (n:Person) RETURN n LIMIT 25")
    names = []
    for record in records:
        names.append(record[0]['name'])
    return jsonify({'test':names})

@app.route("/flask-api/create-project", methods=['POST'])
def createProject():
    data = request.form  # Use `form` to handle multipart form data
    projectName = data.get('name')
    fileNames = data.getlist('files')  # `getlist` handles multiple files
    ips = data.get('ips')
    status = 'created'

    if 'username' not in session:
        print("User not authenticated - 'username' not in session")
        return jsonify({'error': 'User not authenticated'}), 401

    print(f"Creating project for user: {session['username']}")
    
    # Ensure files are properly formatted into a comma-separated string
    filePaths = ','.join(fileNames)
    
    try:
        newProId = project.createProject(driver, session['username'], projectName, filePaths, status, ips, ['All'])
        session['currentProject'] = newProId
        return jsonify({'message': 'Project has been created', 'projectId': newProId})
    except Exception as e:
        print(f"Error during project creation: {e}")
        return jsonify({'error': str(e)}), 500

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


@app.route("/flask-api/set-currentProject", methods=['POST'])
def setCurrentProject():
    try:
        project_id = request.json.get("projectID")
        if not project_id:
            return jsonify({"message": "Missing 'projectID' in request body"})
        
        session['currentProject'] = project_id

        return jsonify({"message": f"Current project set successfully id:{project_id}" })
    except Exception as e:
         return jsonify({"error": f"An error occurred: {str(e)}"}), 500
 ### Nessus Routes ###
@app.route("/flask-api/nessus-upload", methods=['POST'])
def nessusFileUpload():
    if 'files' not in request.files:
        return jsonify({'info': 'No files uploaded'}), 400

    files = request.files.getlist('files')
    project_id = request.form.get('project_id')

    if not project_id:
        return jsonify({'info': 'Project ID is required'}), 400

    saved_files = []
    for file in files:
        if file.filename.endswith('.nessus'):
            filename = secure_filename(file.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)
            saved_files.append(filename)
        else:
            return jsonify({'info': f"Invalid file type for file: {file.filename}"}), 400

    print(f"Files uploaded for project {project_id}: {saved_files}")
    return jsonify({'message': 'Files uploaded successfully', 'files': saved_files}), 200

# Handles the uploading of the file
#@app.route("/flask-api/nessus-upload", methods=['POST'])
#def nessusFileUpload():
    # Makes sure the POST is tagged that is a file and nothing else
    #if 'file' not in request.files:
     #   return jsonify({'info':'Need to be told it is file upload'})
    
    #file = request.files['file']
    # Checks that a file was upload (could be removed becase frontend handles this)
    #if file.filename == '':
      #  print('No selected file')
     #   return jsonify({'message':'no file'})
    #if file:
        # security stuff
    #    filename = secure_filename(file.filename)
        # Saves it based on the give file path and uses the upload file name
   #     file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
  #      print(os.path.exists(app.config['UPLOAD_FOLDER']+'/'+filename))
 #       return jsonify({'message':'file was sent and has been saved on server'})

@app.route("/flask-api/process-nessus", methods=["POST"])
def processNessus():
    data = request.json
    if not data:
        return jsonify({'message': 'No data provided'}), 400
    
    disallowedIps = data.get("disallowedIps")
    archetypesAllowed = data.get("archetypes")
    print(disallowedIps)
    analysis.disallowed_ips = disallowedIps
    analysis.analyze_nessus_file(driver, session['currentProject'], session['username'])
    nessus_upload.processAndUpload(driver, session['username'], session['currentProject'])
    return jsonify({'message': 'Result files have been uploaded'})

# Test route for analysis
@app.route("/flask-api/analysis-test")
def testAnalysis():
    analysis.analyze_nessus_file(driver, session['currentProject'], session['username'])
    nessus_upload.processAndUpload(driver, session['username'], session['currentProject'])
    return jsonify({'name': session['username'], 'proid': session['currentProject'], })
    
# Sends the entry points
@app.route("/flask-api/data-with-exploits")
def dataExploits():
    dataEx = result.getResult(driver, 'dataExploits', session['currentProject'], session['username'])
    return jsonify({'message': 'success', 'data': dataEx})

@app.route("/flask-api/ranked-entry-points")
def rankedEntryPoints():
    rankedEntry = result.getResult(driver, 'rankedEntry', session['currentProject'], session['username'])
    return jsonify({'message': 'success', 'data': rankedEntry})

@app.route("/flask-api/entry-most-info")
def entryMostInfo():
    mostInfo = result.getResult(driver, 'mostInfo', session['currentProject'], session['username'])
    return jsonify({'message': 'success', 'data': mostInfo})

@app.route("/flask-api/port-0-entries")
def portZeroEntries():
    zeroEntries = result.getResult(driver, 'portZero', session['currentProject'], session['username'])
    return jsonify({'message': 'success', 'data': zeroEntries})

#gets ips from the analysis
@app.route('/flask-api/get-scope', methods=['POST'])
def receive_ips():

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
@app.route("/flask-api/get-ips-from-nessus", methods=['POST'])
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
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    # Generate a secure, random key for account recovery
    recovery_key = secrets.token_urlsafe(16)

    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    try:
        with driver.session() as session:
            user_created = session.write_transaction(
                user_service.create_user, username, hashed_password, recovery_key
            )

        if user_created:
            return jsonify({
                "status": "User created successfully",
                "recovery_key": recovery_key
            }), 201
        else:
            return jsonify({"error": "User already exists"}), 409

    except Exception as e:
        print(f"Error creating user: {e}")
        return jsonify({"error": "Failed to create user"}), 500


@app.route('/flask-api/verify_recovery_key', methods=['POST'])
def verify_recovery_key():
    data = request.get_json()
    recovery_key = data.get('recovery_key')

    if not recovery_key:
        return jsonify({"error": "Recovery key is required"}), 400

    with driver.session() as session:
        result = session.run(
            """
            MATCH (a:Analyst {recovery_key: $recovery_key})
            RETURN a.username AS username
            """,
            recovery_key=recovery_key
        )

        record = result.single()
        
        if record:
            return jsonify({"status": "Recovery key valid", "username": record["username"]}), 200
        else:
            return jsonify({"error": "Invalid recovery key"}), 404

@app.route('/flask-api/password-reset-status', methods=['POST'])
def password_reset_status():
    data = request.get_json()
    username = data.get('username')
    
    try:
        with driver.session() as session:
            result = session.run(
                "MATCH (r:PasswordResetRequest {username: $username}) RETURN r.status AS status, r.timestamp AS timestamp",
                username=username
            ).single()
            
            if result:
                # If `status` is None, assume it is "active"
                status = result['status'] if result['status'] is not None else "Pending"
                return jsonify({
                    "status": status,
                    "timestamp": result['timestamp']
                }), 200
            else:
                return jsonify({"error": "No pending password reset request found"}), 404
    except Exception as e:
        print(f"Error checking password reset status: {e}")
        return jsonify({"error": "Failed to check password reset status"}), 500

@app.route('/flask-api/get-password-reset-requests', methods=['GET'])
def get_password_reset_requests():
    # Ensure the session contains the username
    # username = session.get('username')  # Check if the username is in session
    print("Session username: ", session['username'])  # Debug: Log the session username

    # Allow access only to the admin user
    if session['username'] != "admin":
        print("Access denied: User is not an admin.")  # Debug log for access check
        return jsonify({"error": "Access denied. Admins only."}), 403

    try:
        # Use a session to interact with the database
        with driver.session() as neo4j_session:
            # Run the query and process the result immediately within the transaction
            result = neo4j_session.run("MATCH (r:PasswordResetRequest) RETURN r")
            requests = [
                {
                    "id": record["r"]["id"],
                    "username": record["r"]["username"],
                    "timestamp": record["r"]["timestamp"]
                }
                for record in result  # Process each record within the transaction
            ]
        
        print(f"Fetched reset requests: {requests}")  # Debug: Log fetched requests
        return jsonify({"requests": requests}), 200

    except Exception as e:
        print(f"Error fetching password reset requests: {e}")  # Debug: Log errors
        return jsonify({"error": "Failed to fetch password reset requests"}), 500
    
@app.route('/flask-api/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    recovery_key = data.get('recovery_key')
    new_password = data.get('new_password')

    if not recovery_key or not new_password:
        return jsonify({"error": "Recovery key and new password are required"}), 400

    # Hash the new password
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    try:
        with driver.session() as session:
            # Match user with recovery key and update their password
            result = session.run(
                """
                MATCH (a:Analyst {recovery_key: $recovery_key})
                SET a.password = $hashed_password
                RETURN a.username AS username
                """,
                recovery_key=recovery_key,
                hashed_password=hashed_password
            )

            record = result.single()
            if record:
                return jsonify({"message": "Password reset successful", "username": record["username"]}), 200
            else:
                return jsonify({"error": "Invalid recovery key"}), 404
    except Exception as e:
        print(f"Error resetting password: {e}")
        return jsonify({"error": "Failed to reset password"}), 500

# checks login information 
@app.route('/flask-api/login', methods=['POST'])
def login_route():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Call the login_user function
    login_result = user_service.login_user(driver, username, password)

    # Check if there was an error in the login process
    if "error" in login_result:
        print(f"Login failed for {username}: {login_result['error']}")
        return jsonify({"status": "Login failed", "error": login_result["error"]}), 401

    # If login is successful, store session details
    session['username'] = username
    session_id = session.sid  # Generate a session ID
    print(f"Login successful for {username}")
    return jsonify({"status": login_result["status"], "session_id": session_id})

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


# Helper function to check if a user exists in the Analyst node
def check_user_exists(tx, username):
    query = "MATCH (a:Analyst {username: $username}) RETURN a LIMIT 1"
    print("Running query to check user existence:", query)
    result = tx.run(query, username=username)
    exists = result.single() is not None
    print("User existence result:", exists)
    return exists
@app.route('/flask-api/request-password-reset', methods=['POST'])
def request_password_reset():
    data = request.get_json()
    username = data.get('username')
    
    # Debug log to confirm receiving the request
    print(f"Received password reset request for username: {username}")
    
    # Check if user exists in the Analyst table
    user_exists = False
    with driver.session() as session:
        result = session.run("MATCH (a:Analyst {username: $username}) RETURN a LIMIT 1", username=username)
        user_exists = result.single() is not None
    
    print(f"User exists check: {user_exists}")
    
    if user_exists:
        # Create the password reset request without a unique ID
        request_id = username  # Set the ID to the username or use a static string
        with driver.session() as session:
            session.write_transaction(
                lambda tx: tx.run(
                    "CREATE (r:PasswordResetRequest {id: $id, username: $username, timestamp: timestamp()})",
                    id=request_id,
                    username=username
                )
            )
        return jsonify({"status": "Password reset request created"}), 200
    else:
        # If the user does not exist
        return jsonify({"error": "User not found"}), 404
@app.route('/flask-api/approve-password-reset', methods=['POST'])
def approve_password_reset():
    if 'username' not in session or session['username'] != 'admin':
        return jsonify({"error": "Access denied: Admin only."}), 403

    data = request.get_json()
    print(f"Data received in request: {data}")  # Debugging line

    if not data:
        print("Error: No data received")
        return jsonify({"error": "Invalid data. No JSON received."}), 400

    username = data.get('username')
    action = data.get('action')

    if not username or action not in ['approve', 'deny']:
        print(f"Error: Missing or invalid 'username' or 'action' - Username: {username}, Action: {action}")
        return jsonify({"error": "Invalid input: Missing username or action."}), 400

    status = 'approved' if action == 'approve' else 'denied'

    # Update the status in the database
    with driver.session() as neo4j_session:
        result = neo4j_session.run(
            """
            MATCH (r:PasswordResetRequest {username: $username})
            SET r.status = $status
            RETURN r.username AS username, r.status AS status
            """,
            username=username, status=status
        )

        record = result.single()
        if record:
            return jsonify({"message": f"Request {status} successfully for {username}."}), 200
        else:
            return jsonify({"error": "Request not found."}), 404
