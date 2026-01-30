import requests
import sys
from datetime import datetime
import json

class VRHBuildconAPITester:
    def __init__(self, base_url="https://vrh-buildcon.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        if headers is None:
            headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)

            print(f"   Status: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - {name}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, list):
                        print(f"   Response: List with {len(response_data)} items")
                    else:
                        print(f"   Response: {type(response_data).__name__}")
                except:
                    print(f"   Response: Non-JSON response")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Error: {response.text[:200]}")
                self.failed_tests.append({
                    'name': name,
                    'expected': expected_status,
                    'actual': response.status_code,
                    'endpoint': endpoint
                })

            return success, response.json() if success and response.content else {}

        except requests.exceptions.RequestException as e:
            print(f"❌ Failed - Network Error: {str(e)}")
            self.failed_tests.append({
                'name': name,
                'error': str(e),
                'endpoint': endpoint
            })
            return False, {}

    def test_root_endpoint(self):
        """Test API root endpoint"""
        return self.run_test("API Root", "GET", "", 200)

    def test_get_projects(self):
        """Test getting projects"""
        success, response = self.run_test("Get Projects", "GET", "projects", 200)
        if success and isinstance(response, list):
            print(f"   Found {len(response)} projects")
            if len(response) > 0:
                project = response[0]
                required_fields = ['id', 'title', 'category', 'description', 'image_url']
                for field in required_fields:
                    if field not in project:
                        print(f"   ⚠️  Missing field: {field}")
        return success

    def test_get_services(self):
        """Test getting services"""
        success, response = self.run_test("Get Services", "GET", "services", 200)
        if success and isinstance(response, list):
            print(f"   Found {len(response)} services")
            if len(response) > 0:
                service = response[0]
                required_fields = ['id', 'title', 'description', 'icon']
                for field in required_fields:
                    if field not in service:
                        print(f"   ⚠️  Missing field: {field}")
        return success

    def test_get_testimonials(self):
        """Test getting testimonials"""
        success, response = self.run_test("Get Testimonials", "GET", "testimonials", 200)
        if success and isinstance(response, list):
            print(f"   Found {len(response)} testimonials")
            if len(response) > 0:
                testimonial = response[0]
                required_fields = ['id', 'name', 'role', 'content', 'rating']
                for field in required_fields:
                    if field not in testimonial:
                        print(f"   ⚠️  Missing field: {field}")
        return success

    def test_create_contact(self):
        """Test creating a contact form submission"""
        test_data = {
            "name": f"Test User {datetime.now().strftime('%H%M%S')}",
            "email": "test@example.com",
            "phone": "+91 9876543210",
            "message": "This is a test message from automated testing."
        }
        
        success, response = self.run_test(
            "Create Contact", 
            "POST", 
            "contact", 
            200, 
            data=test_data
        )
        
        if success:
            required_fields = ['id', 'name', 'email', 'phone', 'message', 'created_at']
            for field in required_fields:
                if field not in response:
                    print(f"   ⚠️  Missing field in response: {field}")
        
        return success

    def test_create_quote(self):
        """Test creating a quote request"""
        test_data = {
            "name": f"Test Client {datetime.now().strftime('%H%M%S')}",
            "email": "client@example.com",
            "phone": "+91 9876543210",
            "service_type": "building",
            "project_details": "Test project for automated testing - 3BHK residential construction",
            "budget_range": "10l-25l",
            "timeline": "3-6months"
        }
        
        success, response = self.run_test(
            "Create Quote Request", 
            "POST", 
            "quote", 
            200, 
            data=test_data
        )
        
        if success:
            required_fields = ['id', 'name', 'email', 'phone', 'service_type', 'project_details', 'created_at']
            for field in required_fields:
                if field not in response:
                    print(f"   ⚠️  Missing field in response: {field}")
        
        return success

    def test_get_contacts(self):
        """Test getting contact submissions (admin endpoint)"""
        return self.run_test("Get Contacts", "GET", "contact", 200)

    def test_get_quotes(self):
        """Test getting quote requests (admin endpoint)"""
        return self.run_test("Get Quote Requests", "GET", "quote", 200)

def main():
    print("🚀 Starting VRH Buildcon API Tests")
    print("=" * 50)
    
    tester = VRHBuildconAPITester()
    
    # Test all endpoints
    tests = [
        tester.test_root_endpoint,
        tester.test_get_projects,
        tester.test_get_services,
        tester.test_get_testimonials,
        tester.test_create_contact,
        tester.test_create_quote,
        tester.test_get_contacts,
        tester.test_get_quotes,
    ]
    
    for test in tests:
        test()
    
    # Print summary
    print("\n" + "=" * 50)
    print(f"📊 Test Summary:")
    print(f"   Tests Run: {tester.tests_run}")
    print(f"   Tests Passed: {tester.tests_passed}")
    print(f"   Tests Failed: {len(tester.failed_tests)}")
    print(f"   Success Rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    if tester.failed_tests:
        print(f"\n❌ Failed Tests:")
        for test in tester.failed_tests:
            error_msg = test.get('error', f"Expected {test.get('expected')}, got {test.get('actual')}")
            print(f"   - {test['name']}: {error_msg}")
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())