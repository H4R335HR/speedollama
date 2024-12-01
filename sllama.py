import argparse
import requests
import concurrent.futures
import json
from typing import List, Union
from datetime import datetime

class OllamaSpeedTest:
    def __init__(self, threads: int = 1, timeout: int = 30):
        self.threads = threads
        self.timeout = timeout
        self.test_prompt = "Why is the sky blue?"
        self.preferred_model = "llama3.2"
        # Print header once
        print("\nResults:")
        print("-" * 100)
        print(f"{'Timestamp':<20} {'IP Address':<20} {'Model':<15} {'Status':<10} {'Tokens/sec':<12} {'Total Duration (ns)':<20}")
        print("-" * 100)

    def check_available_models(self, ip: str) -> dict:
        """Check available models on the IP"""
        try:
            url = f"http://{ip}:11434/api/tags"
            # Use 1/3 of the total timeout for model checking
            response = requests.get(url, timeout=self.timeout/3)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m['name'].split(':')[0] for m in models]
                if self.preferred_model in model_names:
                    return {'status': 'success', 'model': self.preferred_model}
                elif models:
                    return {'status': 'success', 'model': models[0]['name'].split(':')[0]}
                return {'status': 'error', 'message': 'No models available'}
            return {'status': 'error', 'message': f'HTTP {response.status_code}'}
        except requests.exceptions.RequestException as e:
            return {'status': 'error', 'message': f'Model check timeout ({self.timeout/3}s): {str(e)}'}

    def print_result(self, result: dict):
        """Print a single result"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        ip = result['ip']
        model = result.get('model', 'N/A')
        status = result['status']
        tokens_per_sec = result.get('tokens_per_second', 'N/A')
        total_duration = result.get('total_duration', 'N/A')
        
        print(f"{timestamp:<20} {ip:<20} {model:<15} {status:<10} {tokens_per_sec:<12} {total_duration:<20}")

    def test_single_ip(self, ip: str) -> dict:
        """Test a single IP address for Ollama API speed"""
        # First check available models
        model_check = self.check_available_models(ip)
        if model_check['status'] == 'error':
            result = {
                'ip': ip,
                'status': 'error',
                'message': model_check['message'],
                'model': 'N/A'
            }
            self.print_result(result)
            return result

        model_to_use = model_check['model']

        try:
            url = f"http://{ip}:11434/api/generate"
            payload = {
                "model": model_to_use,
                "prompt": self.test_prompt
            }
            
            response = requests.post(url, json=payload, timeout=self.timeout)
            
            # Process the streaming response
            last_response = None
            for line in response.iter_lines():
                if line:
                    last_response = json.loads(line)
            
            if last_response and last_response.get('done'):
                eval_count = last_response.get('eval_count', 0)
                eval_duration = last_response.get('eval_duration', 1)
                tokens_per_second = (eval_count / eval_duration) * 1e9
                
                result = {
                    'ip': ip,
                    'status': 'success',
                    'model': model_to_use,
                    'tokens_per_second': round(tokens_per_second, 2),
                    'eval_count': eval_count,
                    'total_duration': last_response.get('total_duration'),
                }
                self.print_result(result)
                return result
            
            result = {
                'ip': ip,
                'status': 'error',
                'model': model_to_use,
                'message': 'Invalid response format'
            }
            self.print_result(result)
            return result
            
        except requests.exceptions.RequestException as e:
            result = {
                'ip': ip,
                'status': 'error',
                'model': model_to_use,
                'message': f'Generation timeout ({self.timeout}s): {str(e)}'
            }
            self.print_result(result)
            return result

    def test_multiple_ips(self, ips: List[str]) -> List[dict]:
        """Test multiple IPs using thread pool"""
        all_results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.threads) as executor:
            future_to_ip = {executor.submit(self.test_single_ip, ip): ip for ip in ips}
            for future in concurrent.futures.as_completed(future_to_ip):
                result = future.result()
                all_results.append(result)
        return all_results

def read_ips_from_file(filepath: str) -> List[str]:
    """Read IPs from a file"""
    with open(filepath, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def main():
    parser = argparse.ArgumentParser(description='Test Ollama API speed across different IPs')
    parser.add_argument('--ip', help='Single IP address to test')
    parser.add_argument('--file', help='File containing list of IPs')
    parser.add_argument('--threads', type=int, default=1, help='Number of parallel threads')
    parser.add_argument('--timeout', type=int, default=30, 
                      help='Timeout in seconds for each request (default: 30)')
    
    args = parser.parse_args()
    
    if not args.ip and not args.file:
        parser.error("Either --ip or --file must be provided")
    
    # Get list of IPs to test
    ips_to_test = []
    if args.file:
        ips_to_test.extend(read_ips_from_file(args.file))
    if args.ip:
        ips_to_test.append(args.ip)
    
    # Remove duplicates while preserving order
    ips_to_test = list(dict.fromkeys(ips_to_test))
    
    print(f"\nStarting tests with timeout of {args.timeout} seconds per request...")
    
    # Initialize and run tests
    speed_tester = OllamaSpeedTest(threads=args.threads, timeout=args.timeout)
    results = speed_tester.test_multiple_ips(ips_to_test)

if __name__ == "__main__":
    main()
