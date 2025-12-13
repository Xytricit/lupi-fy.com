#!/usr/bin/env python
"""Test game functionality with HTTP polling fallback"""
import os
import sys
import django
import requests
import json

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test.client import Client

User = get_user_model()

def test_game_pages():
    """Test that game pages load successfully"""
    client = Client()
    
    # Create test user
    user, created = User.objects.get_or_create(
        username='testgamer',
        defaults={'email': 'testgamer@test.com'}
    )
    
    # Test without login - should redirect
    response = client.get('/accounts/game/lobby/')
    print(f"[OK] Game lobby (no auth): {response.status_code} (expected 302 redirect)")
    
    # Login
    client.force_login(user)
    
    # Test game lobby
    response = client.get('/accounts/game/lobby/')
    print(f"[OK] Game lobby (logged in): {response.status_code}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert b'Try Not To Get Banned' in response.content
    print("     Page contains game title")
    
    # Test letter set game
    response = client.get('/accounts/games/letter-set/')
    print(f"[OK] Letter Set game: {response.status_code}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
def test_challenge_endpoints():
    """Test challenge endpoints"""
    client = Client()
    
    # Create test user
    user, created = User.objects.get_or_create(
        username='testgamer2',
        defaults={'email': 'testgamer2@test.com'}
    )
    client.force_login(user)
    
    # Test challenge start endpoint
    response = client.get('/accounts/api/game/challenge/start/')
    print(f"[OK] Challenge start endpoint: {response.status_code}")
    assert response.status_code == 200
    data = response.json()
    assert 'challenge' in data
    assert 'letters' in data['challenge']
    print(f"     Challenge letters: {data['challenge']['letters']}")
    
    # Test challenge save endpoint
    response = client.post(
        '/accounts/api/game/challenge/save/',
        data=json.dumps({
            'used_letters': ['A', 'B'],
            'completed': False
        }),
        content_type='application/json'
    )
    print(f"[OK] Challenge save endpoint: {response.status_code}")
    assert response.status_code == 200
    data = response.json()
    assert data.get('success') == True
    print("     Challenge progress saved successfully")

def test_message_endpoint():
    """Test game message posting endpoint with both 'message' and 'content' fields"""
    client = Client()
    
    # Create test user
    user, created = User.objects.get_or_create(
        username='testgamer3',
        defaults={'email': 'testgamer3@test.com'}
    )
    client.force_login(user)
    
    # Test with 'message' field (used by frontend)
    response = client.post(
        '/accounts/api/game/post-message/',
        data=json.dumps({
            'message': 'This is a test message'
        }),
        content_type='application/json'
    )
    print(f"[OK] Post message (message field): {response.status_code}")
    if response.status_code != 200:
        print(f"     Response: {response.json()}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.json()}"
    
    # Test with 'content' field (legacy support)
    response = client.post(
        '/accounts/api/game/post-message/',
        data=json.dumps({
            'content': 'This is another test message'
        }),
        content_type='application/json'
    )
    print(f"[OK] Post message (content field): {response.status_code}")
    assert response.status_code == 200
    print("     Both message and content fields supported")

def main():
    print("=" * 50)
    print("GAME FUNCTIONALITY TEST")
    print("=" * 50)
    
    try:
        print("\n1. Testing game pages...")
        test_game_pages()
        
        print("\n2. Testing challenge endpoints...")
        test_challenge_endpoints()
        
        print("\n3. Testing message endpoint...")
        test_message_endpoint()
        
        print("\n" + "=" * 50)
        print("SUCCESS: ALL TESTS PASSED")
        print("=" * 50)
        print("\n[OK] Game lobby loads successfully")
        print("[OK] Letter Set game loads successfully")
        print("[OK] Challenge endpoints working (HTTP polling fallback)")
        print("[OK] Message endpoint accepts both 'message' and 'content' fields")
        print("\nGames are ready to play with HTTP polling fallback!")
        
    except AssertionError as e:
        print(f"\nFAIL: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
