#!/usr/bin/env python3
"""
Local test script for uptime monitoring functionality
"""

import json
from index import check_site_uptime

def test_local_checks():
    """Test uptime checks with local accessible resources"""
    
    test_sites = [
        {
            'name': 'Local TCP - SSH',
            'url': 'localhost',
            'type': 'tcp',
            'port': 22,
            'timeout': 5
        },
        {
            'name': 'Local TCP - Non-existent port',
            'url': 'localhost',
            'type': 'tcp', 
            'port': 9999,
            'timeout': 2
        },
        {
            'name': 'GitHub HTTPS (allowed)',
            'url': 'https://github.com',
            'type': 'https',
            'timeout': 10
        }
    ]
    
    print("Testing uptime monitoring components...")
    print("=" * 50)
    
    for site in test_sites:
        print(f"\nTesting: {site['name']}")
        result = check_site_uptime(site)
        
        print(f"  Status: {result['status']}")
        print(f"  Response Time: {result['response_time']}ms")
        if result['error']:
            print(f"  Error: {result['error']}")
        if 'http_code' in result:
            print(f"  HTTP Code: {result['http_code']}")
    
    print("\n" + "=" * 50)
    print("Test completed successfully!")

if __name__ == "__main__":
    test_local_checks()