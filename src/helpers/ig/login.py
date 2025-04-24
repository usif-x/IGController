from instagrapi import Client
import config
import json
import os

class InstagramHelper:
    def __init__(self):
        self.client = Client()
        self.session_file = os.path.join(os.path.dirname(__file__), '../../../data/session.json')
        self.ensure_data_dir()
        
    def ensure_data_dir(self):
        """Ensure the data directory exists"""
        data_dir = os.path.dirname(self.session_file)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
    def load_session(self):
        """Load session from JSON file if it exists"""
        if os.path.exists(self.session_file):
            try:
                with open(self.session_file, 'r') as f:
                    session_data = json.load(f)
                
                # Set session data to client
                self.client.set_settings(session_data)
                
                # Verify the session is still valid
                try:
                    self.client.get_timeline_feed()
                    return True, "Session loaded successfully"
                except Exception:
                    return False, "Saved session expired"
            except Exception as e:
                return False, f"Error loading session: {str(e)}"
        return False, "No saved session found"
    
    def save_session(self):
        """Save current session to JSON file"""
        try:
            session_data = self.client.get_settings()
            
            with open(self.session_file, 'w') as f:
                json.dump(session_data, f)
            
            return True, "Session saved successfully"
        except Exception as e:
            return False, f"Error saving session: {str(e)}"
    
    def login(self):
        """Login to Instagram, first try to load session"""
        # Try to load existing session first
        success, message = self.load_session()
        if success:
            return True, message
        
        # If no session or expired, login with credentials
        try:
            self.client.login(config.ig_username, config.ig_password)
            # Save the new session
            self.save_session()
            return True, "Successfully logged in and saved session"
        except Exception as e:
            return False, f"Login error: {str(e)}"
    
    def check_status(self):
        """Check if currently logged in"""
        try:
            self.client.get_timeline_feed()
            return True
        except Exception:
            return False
    
    def get_account_info(self):
        """Get account information"""
        try:
            return self.client.account_info()
        except Exception as e:
            print(f"Error getting account info: {str(e)}")
            return None