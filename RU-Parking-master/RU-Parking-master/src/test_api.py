"""
API Testing Script
Test Flask API endpoints without React frontend
Works with DeepSeek-powered backend
"""

import requests
import json
import time

API_BASE_URL = "http://localhost:5000"

def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def print_response(response):
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response:")
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)

def test_health():
    """Test health endpoint"""
    print_header("Testing Health Endpoint")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        print_response(response)
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Is Flask server running?")
        return False

def test_api_info():
    """Test root endpoint"""
    print_header("Testing API Info Endpoint")
    try:
        response = requests.get(f"{API_BASE_URL}/")
        print_response(response)
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API")
        return False

def test_chat_conversation():
    """Test full chat conversation"""
    print_header("Testing Chat Conversation (DeepSeek)")
    
    messages = [
        "Hi, I need help finding parking",
        "I'm a student",
        "College Avenue",
        "Just for a few hours"
    ]
    
    session_id = None
    
    for i, message in enumerate(messages, 1):
        print(f"\n--- Message {i} ---")
        print(f"👤 User: {message}")
        
        payload = {
            "message": message
        }
        
        if session_id:
            payload["session_id"] = session_id
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/chat",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                session_id = data.get("session_id")
                print(f"🤖 Bot: {data.get('response')}")
                print(f"📋 Session ID: {session_id[:8]}...")
            else:
                print(f"❌ Error: {response.status_code}")
                print(response.text)
                return False
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False
        
        time.sleep(1)  # Delay between messages
    
    return True

def test_reset():
    """Test reset endpoint"""
    print_header("Testing Reset Endpoint")
    
    # First, create a conversation
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/chat",
            json={"message": "Hello"}
        )
        
        if response.status_code != 200:
            print("❌ Failed to create conversation")
            return False
        
        session_id = response.json().get("session_id")
        print(f"✅ Created session: {session_id[:8]}...")
        
        # Now reset it
        response = requests.post(
            f"{API_BASE_URL}/api/reset",
            json={"session_id": session_id}
        )
        
        print_response(response)
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_get_lots():
    """Test get parking lots endpoint"""
    print_header("Testing Get Parking Lots")
    
    try:
        # Get all lots
        print("\n--- All Lots ---")
        response = requests.get(f"{API_BASE_URL}/api/lots")
        print_response(response)
        
        # Filter by campus
        print("\n--- College Avenue Lots ---")
        response = requests.get(
            f"{API_BASE_URL}/api/lots",
            params={"campus": "College Avenue"}
        )
        print_response(response)
        
        # Filter by permit type
        print("\n--- Student Parking ---")
        response = requests.get(
            f"{API_BASE_URL}/api/lots",
            params={"permit_type": "student"}
        )
        print_response(response)
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_stats():
    """Test stats endpoint"""
    print_header("Testing Stats Endpoint")
    try:
        response = requests.get(f"{API_BASE_URL}/api/stats")
        print_response(response)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def run_all_tests():
    """Run all API tests"""
    print("\n" + "🚀" * 30)
    print("RU-PATH API Test Suite (DeepSeek Backend)")
    print("🚀" * 30)
    
    print("\n⚠️  Prerequisites:")
    print("1. Flask server must be running: python app.py")
    print("2. DEEPSEEK_API_KEY must be in .env file")
    print("\nPress Enter to continue or Ctrl+C to cancel...")
    
    try:
        input()
    except KeyboardInterrupt:
        print("\n\n👋 Tests cancelled")
        return
    
    tests = [
        ("Health Check", test_health),
        ("API Info", test_api_info),
        ("Chat Conversation", test_chat_conversation),
        ("Reset Conversation", test_reset),
        ("Get Parking Lots", test_get_lots),
        ("Statistics", test_stats),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except requests.exceptions.ConnectionError:
            print(f"\n❌ Cannot connect to API at {API_BASE_URL}")
            print("Is Flask server running? (python app.py)")
            return
        except Exception as e:
            print(f"\n❌ Error in {test_name}: {str(e)}")
            results.append((test_name, False))
        
        time.sleep(0.5)
    
    # Print summary
    print_header("Test Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n📊 Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your DeepSeek-powered API is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\n👋 Tests cancelled by user.")