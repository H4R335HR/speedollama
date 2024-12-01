# SpeedOllama

SpeedOllama is a Python-based command-line tool for testing and benchmarking Ollama API endpoints across multiple servers. It measures the response times and processing speeds of Ollama language models, with a preference for llama3.2.

## Features

- Test single or multiple Ollama endpoints simultaneously
- Multi-threaded testing capability
- Automatic model detection with preference for llama3.2
- Real-time results output
- Configurable timeout settings
- Token per second (TPS) speed calculation
- Support for reading IPs from a file

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/speedollama.git
cd speedollama
```

2. Install required dependencies:
```bash
pip install requests
```

## Usage

### Basic Usage

Test a single IP:
```bash
python sllama.py --ip 192.168.1.100
```

Test multiple IPs from a file:
```bash
python sllama.py --file ips.txt
```

### Advanced Options

- Use multiple threads:
```bash
python sllama.py --file ips.txt --threads 4
```

- Set custom timeout:
```bash
python sllama.py --ip 192.168.1.100 --timeout 60
```

### Command Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| --ip | Single IP address to test | None |
| --file | File containing list of IPs (one per line) | None |
| --threads | Number of parallel threads | 1 |
| --timeout | Timeout in seconds for each request | 30 |

### Input File Format

The IP file should contain one IP address per line:
```
192.168.1.100
192.168.1.101
192.168.1.102
```

## Output Format

The tool provides real-time results in a tabulated format:
```
Results:
----------------------------------------------------------------------------------------------------
Timestamp            IP Address           Model          Status     Tokens/sec  Total Duration (ns)
----------------------------------------------------------------------------------------------------
14:25:30            192.168.1.100       llama3.2       success    45.67       10706818083
14:25:32            192.168.1.102       qwen2.5        success    38.92       11234567890
14:25:33            192.168.1.101       N/A            error      N/A         N/A
```

## Error Handling

SpeedOllama handles various error conditions:
- Connection timeouts
- Invalid responses
- Missing models
- Network errors

## Requirements

- Python 3.6+
- requests library
- Ollama endpoints with API access

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

[H4R335HR]

## Acknowledgments

- Ollama team for their excellent API
- All contributors and testers
