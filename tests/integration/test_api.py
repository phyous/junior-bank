import unittest
import requests
import os
import uuid
import time

class TestAPI(unittest.TestCase):
    API_BASE_URL = os.environ.get('API_BASE_URL', 'http://localhost:8000')
    FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
    
    # Store created user details to use across tests if needed, or generate unique for each
    # For simplicity, we'll generate unique users for signup/login tests to ensure independence
    # and handle potential state issues if tests are run in parallel or out of order.
    # A shared user could be created in a setUpClass method if preferred.

    def generate_unique_username(self):
        return f"testuser_{uuid.uuid4().hex[:8]}"

    def test_frontend_loads(self):
        """Test that the frontend loads successfully."""
        try:
            response = requests.get(self.FRONTEND_URL, timeout=10)
            self.assertEqual(response.status_code, 200)
            self.assertIn("<title>Bank Account App</title>", response.text)
        except requests.exceptions.ConnectionError as e:
            self.fail(f"Frontend connection failed: {e}. Ensure frontend server is running on {self.FRONTEND_URL}")
        except requests.exceptions.Timeout:
            self.fail(f"Request to frontend timed out: {self.FRONTEND_URL}")


    def test_signup_and_login(self):
        """Test user signup and then login with the created user."""
        username = self.generate_unique_username()
        password = "testpassword123"
        interest_rate = 0.05  # Example interest rate

        # Signup
        signup_payload = {
            "username": username,
            "password": password,
            "interest_rate": interest_rate 
        }
        try:
            response_signup = requests.post(f"{self.API_BASE_URL}/signup", json=signup_payload, timeout=10)
        except requests.exceptions.ConnectionError as e:
            self.fail(f"API connection failed for signup: {e}. Ensure backend server is running on {self.API_BASE_URL}")
        except requests.exceptions.Timeout:
            self.fail(f"API request timed out for signup: {self.API_BASE_URL}/signup")
        
        self.assertEqual(response_signup.status_code, 200, f"Signup failed: {response_signup.text}")
        signup_data = response_signup.json()
        self.assertEqual(signup_data["username"], username)
        self.assertTrue("id" in signup_data)
        user_id = signup_data["id"]

        # Give a slight delay for DB commit if necessary, though usually not for APIs
        # time.sleep(0.1) 

        # Login
        login_payload = {"username": username, "password": password}
        try:
            response_login = requests.post(f"{self.API_BASE_URL}/login", json=login_payload, timeout=10)
        except requests.exceptions.ConnectionError as e:
            self.fail(f"API connection failed for login: {e}.")
        except requests.exceptions.Timeout:
            self.fail(f"API request timed out for login: {self.API_BASE_URL}/login")
            
        self.assertEqual(response_login.status_code, 200, f"Login failed: {response_login.text}")
        login_data = response_login.json()
        self.assertEqual(login_data["username"], username)
        self.assertEqual(login_data["id"], user_id)
        
        # Store for authenticated test, or re-login there
        self.user_id_for_auth_test = user_id 
        self.username_for_auth_test = username
        self.password_for_auth_test = password


    def test_get_account_authenticated(self):
        """Test getting account details for an authenticated user."""
        # First, ensure a user is created and logged in to get a user_id
        # For test independence, we create a new user here.
        username = self.generate_unique_username()
        password = "testpassword_auth"
        interest_rate = 0.03

        signup_payload = {"username": username, "password": password, "interest_rate": interest_rate}
        try:
            response_signup = requests.post(f"{self.API_BASE_URL}/signup", json=signup_payload, timeout=10)
            self.assertEqual(response_signup.status_code, 200, f"Signup for auth test failed: {response_signup.text}")
            user_id = response_signup.json()["id"]

            # Login is not strictly necessary if the endpoint relies only on user_id from path
            # and doesn't use session/token based auth for this specific endpoint.
            # However, typical protected endpoints would require a session/token.
            # The current `/account/{user_id}` seems to not require a token, just a valid user_id.
            # If it required a token, we'd login here and pass the token in headers.

            response_account = requests.get(f"{self.API_BASE_URL}/account/{user_id}", timeout=10)
            self.assertEqual(response_account.status_code, 200, f"Getting account failed: {response_account.text}")
            account_data = response_account.json()
            self.assertEqual(account_data["user_id"], user_id)
            self.assertIn("balance", account_data)
            # Convert interest_rate for comparison, e.g. 0.03 stored might be 0.030000000000000002
            self.assertAlmostEqual(account_data["interest_rate"], interest_rate, places=5)

        except requests.exceptions.ConnectionError as e:
            self.fail(f"API connection failed for authenticated account get: {e}.")
        except requests.exceptions.Timeout:
            self.fail(f"API request timed out for authenticated account get.")


    def test_get_account_unauthenticated(self):
        """Test getting account details for a non-existent/unauthenticated user ID."""
        non_existent_user_id = 9999999  # Assuming this ID won't exist
        try:
            response = requests.get(f"{self.API_BASE_URL}/account/{non_existent_user_id}", timeout=10)
            # Expecting 404 Not Found if the user_id (and thus account) does not exist
            self.assertEqual(response.status_code, 404, f"Accessing non-existent account should be 404: {response.text}")
        except requests.exceptions.ConnectionError as e:
            self.fail(f"API connection failed for unauthenticated account get: {e}.")
        except requests.exceptions.Timeout:
             self.fail(f"API request timed out for unauthenticated account get.")

if __name__ == '__main__':
    unittest.main()
