current_session = {"username": None}

def login_session(username):
    current_session["username"] = username

def logout_session():
    current_session["username"] = None

def is_logged_in():
    return current_session["username"] is not None

def get_current_user():
    return current_session["username"]
