import json
import time
import socket
import ssl
import urllib.request
import urllib.error
from datetime import datetime
import base64
import os


def handler(event, context):
    """
    Alibaba Cloud Function Compute handler for uptime monitoring
    """
    try:
        # Load site configuration
        sites = load_site_config()
        
        # Perform uptime checks
        results = []
        timestamp = datetime.now().isoformat()
        
        for site in sites:
            result = check_site_uptime(site)
            result['timestamp'] = timestamp
            results.append(result)
        
        # Create result summary
        summary = {
            'check_time': timestamp,
            'total_sites': len(sites),
            'results': results
        }
        
        # Push results to GitHub (optional for testing)
        github_success = False
        try:
            push_to_github(summary, timestamp)
            github_success = True
            summary['github_push'] = 'success'
        except Exception as github_error:
            summary['github_push'] = f'failed: {str(github_error)}'
            print(f"GitHub push failed (continuing anyway): {github_error}")
        
        return {
            'statusCode': 200,
            'body': json.dumps(summary, ensure_ascii=False, indent=2)
        }
        
    except Exception as e:
        error_response = {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }, ensure_ascii=False)
        }
        return error_response


def load_site_config():
    """
    Load site configuration from site.json
    """
    try:
        with open('site.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config.get('sites', [])
    except FileNotFoundError:
        # Return default configuration if file doesn't exist
        return [
            {
                'name': 'Google',
                'url': 'https://www.google.com',
                'type': 'https',
                'timeout': 10
            }
        ]


def check_site_uptime(site):
    """
    Check uptime for a single site
    """
    result = {
        'name': site.get('name', 'Unknown'),
        'url': site.get('url', ''),
        'type': site.get('type', 'https'),
        'status': 'unknown',
        'response_time': 0,
        'error': None
    }
    
    start_time = time.time()
    
    try:
        if result['type'].lower() in ['http', 'https']:
            result = check_http_site(site, result, start_time)
        elif result['type'].lower() == 'tcp':
            result = check_tcp_site(site, result, start_time)
        else:
            result['status'] = 'error'
            result['error'] = f"Unsupported check type: {result['type']}"
            
    except Exception as e:
        result['status'] = 'error'
        result['error'] = str(e)
        result['response_time'] = int((time.time() - start_time) * 1000)
    
    return result


def check_http_site(site, result, start_time):
    """
    Check HTTP/HTTPS site availability
    """
    url = site.get('url', '')
    timeout = site.get('timeout', 10)
    
    try:
        request = urllib.request.Request(url)
        request.add_header('User-Agent', 'FC-Uptime-Bot/1.0')
        
        with urllib.request.urlopen(request, timeout=timeout) as response:
            result['response_time'] = int((time.time() - start_time) * 1000)
            result['status'] = 'up'
            result['http_code'] = response.getcode()
            
    except urllib.error.HTTPError as e:
        result['response_time'] = int((time.time() - start_time) * 1000)
        result['status'] = 'down'
        result['http_code'] = e.code
        result['error'] = f"HTTP {e.code}: {e.reason}"
        
    except urllib.error.URLError as e:
        result['response_time'] = int((time.time() - start_time) * 1000)
        result['status'] = 'down'
        result['error'] = str(e.reason)
        
    except socket.timeout:
        result['response_time'] = timeout * 1000
        result['status'] = 'timeout'
        result['error'] = f"Request timeout after {timeout}s"
    
    return result


def check_tcp_site(site, result, start_time):
    """
    Check TCP port availability
    """
    url = site.get('url', '')
    timeout = site.get('timeout', 10)
    port = site.get('port', 80)
    
    # Parse host from URL or use URL directly as host
    if url.startswith(('http://', 'https://')):
        host = url.split('/')[2].split(':')[0]
    else:
        host = url.split(':')[0]
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        
        connection_result = sock.connect_ex((host, port))
        result['response_time'] = int((time.time() - start_time) * 1000)
        
        if connection_result == 0:
            result['status'] = 'up'
        else:
            result['status'] = 'down'
            result['error'] = f"Connection failed to {host}:{port}"
            
        sock.close()
        
    except socket.gaierror as e:
        result['response_time'] = int((time.time() - start_time) * 1000)
        result['status'] = 'down'
        result['error'] = f"DNS resolution failed: {str(e)}"
        
    except Exception as e:
        result['response_time'] = int((time.time() - start_time) * 1000)
        result['status'] = 'error'
        result['error'] = str(e)
    
    return result


def push_to_github(data, timestamp):
    """
    Push results to GitHub repository using Personal Access Token
    """
    # GitHub configuration (hardcoded for testing as requested)
    GITHUB_TOKEN = "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"
    REPO_OWNER = "sunforwork"
    REPO_NAME = "uptime_page"
    
    # Create filename with timestamp
    filename = f"uptime-{timestamp.replace(':', '-').replace('.', '-')}.json"
    
    # Prepare file content
    content = json.dumps(data, ensure_ascii=False, indent=2)
    content_b64 = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    
    # GitHub API endpoint
    api_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{filename}"
    
    # Prepare request data
    request_data = {
        "message": f"Add uptime check results for {timestamp}",
        "content": content_b64,
        "branch": "main"
    }
    
    # Create request
    req_data = json.dumps(request_data).encode('utf-8')
    request = urllib.request.Request(api_url, data=req_data, method='PUT')
    request.add_header('Authorization', f'token {GITHUB_TOKEN}')
    request.add_header('Content-Type', 'application/json')
    request.add_header('User-Agent', 'FC-Uptime-Bot/1.0')
    
    try:
        with urllib.request.urlopen(request) as response:
            if response.getcode() in [200, 201]:
                print(f"Successfully pushed results to GitHub: {filename}")
            else:
                print(f"GitHub API response: {response.getcode()}")
                
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"Failed to push to GitHub: {e.code} - {error_body}")
        raise Exception(f"GitHub push failed: {e.code}")
        
    except Exception as e:
        print(f"Error pushing to GitHub: {str(e)}")
        raise


# For local testing
if __name__ == "__main__":
    # Simulate FC event and context for local testing
    test_event = {}
    test_context = {}
    
    result = handler(test_event, test_context)
    print(json.dumps(result, ensure_ascii=False, indent=2))