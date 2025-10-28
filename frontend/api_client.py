import streamlit as st
import requests
import os

API_BASE_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

class ApiClient:
    def __init__(self, token=None):
        self.base_url = API_BASE_URL
        self.headers = {"accept": "application/json"}
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

    def _handle_response(self, response):
        """Centralized error handling."""
        try:
            response.raise_for_status() # Raise HTTPError for bad responses
            return response.json()
        except requests.exceptions.HTTPError as e:
            # Try to get the API's specific error detail
            detail = e.response.json().get('detail', e.response.text)
            st.error(f"API Error: {detail}")
            return None
        except requests.exceptions.RequestException as e:
            st.error(f"Connection Error: {e}")
            return None

    def login(self, username, password):
        login_data = {"username": username, "password": password}
        # Note: Login uses 'data' (form data), not 'json'
        try:
            response = requests.post(
                f"{self.base_url}/login", 
                data=login_data,
                headers={"accept": "application/json"}
            )
            response.raise_for_status()
            return response.json().get("access_token")
        except:
            return None

    def register(self, username, password):
        reg_data = {"username": username, "password": password}
        response = requests.post(
            f"{self.base_url}/register", 
            headers=self.headers, 
            json=reg_data
        )
        return self._handle_response(response)

    def get_tasks(self):
        response = requests.get(f"{self.base_url}/tasks/", headers=self.headers)
        return self._handle_response(response)

    def create_task(self, title, description):
        payload = {"title": title, "description": description}
        response = requests.post(
            f"{self.base_url}/tasks/", 
            headers=self.headers, 
            json=payload
        )
        return self._handle_response(response)

    def update_task(self, task_id, is_complete):
        payload = {"is_complete": is_complete}
        response = requests.put(
            f"{self.base_url}/tasks/{task_id}", 
            headers=self.headers, 
            json=payload
        )
        return self._handle_response(response)

    def delete_task(self, task_id):
        response = requests.delete(
            f"{self.base_url}/tasks/{task_id}", 
            headers=self.headers
        )
        # Delete might not return JSON, so we just check status
        if response.status_code == 200:
            return True
        else:
            self._handle_response(response)
            return False