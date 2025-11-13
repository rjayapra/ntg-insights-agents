# ntg-insights-agents

Repository to setup required agents for insights project.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## Overview

This repository contains the configuration and setup for agents used in the NTG Insights project. These agents are designed to collect, process, and analyze data for generating insights.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- **Git**: Version control system
  - Install: [https://git-scm.com/downloads](https://git-scm.com/downloads)
- **Python**: Version 3.8 or higher (if using Python-based agents)
  - Install: [https://www.python.org/downloads/](https://www.python.org/downloads/)
- **Node.js**: Version 14 or higher (if using Node.js-based agents)
  - Install: [https://nodejs.org/](https://nodejs.org/)
- **Docker**: (Optional, for containerized deployment)
  - Install: [https://docs.docker.com/get-docker/](https://docs.docker.com/get-docker/)

## Installation

### Clone the Repository

```bash
git clone https://github.com/rjayapra/ntg-insights-agents.git
cd ntg-insights-agents
```

### Install Dependencies

#### For Python-based agents:

```bash
pip install -r requirements.txt
```

#### For Node.js-based agents:

```bash
npm install
```

#### Using Docker:

```bash
docker build -t ntg-insights-agents .
```

## Configuration

1. **Environment Variables**: Create a `.env` file in the root directory with the following variables:

```env
# Example environment variables
AGENT_NAME=your-agent-name
API_KEY=your-api-key
DATABASE_URL=your-database-url
LOG_LEVEL=info
```

2. **Configuration File**: Update the `config.json` or `config.yaml` file with your specific settings:

```json
{
  "agents": {
    "enabled": true,
    "interval": 3600,
    "timeout": 300
  }
}
```

## Usage

### Running the Agents

#### Using Python:

```bash
python main.py
```

#### Using Node.js:

```bash
npm start
```

#### Using Docker:

```bash
docker run -d --name ntg-insights-agents \
  --env-file .env \
  ntg-insights-agents
```

### Running Specific Agents

To run a specific agent:

```bash
# Python
python agents/agent_name.py

# Node.js
npm run agent:name
```

### Testing

Run tests to ensure everything is working correctly:

```bash
# Python
pytest tests/

# Node.js
npm test
```

## Project Structure

```
ntg-insights-agents/
├── agents/              # Agent implementations
├── config/              # Configuration files
├── tests/               # Test files
├── docs/                # Additional documentation
├── scripts/             # Utility scripts
├── .env.example         # Example environment variables
├── README.md            # This file
└── requirements.txt     # Python dependencies (if applicable)
```

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow the existing code style
- Write tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting PR

## Troubleshooting

### Common Issues

**Issue**: Agent fails to start
- **Solution**: Check that all environment variables are set correctly in `.env`

**Issue**: Connection errors
- **Solution**: Verify network connectivity and API endpoint URLs

**Issue**: Permission errors
- **Solution**: Ensure proper file permissions and user access rights

### Getting Help

- Check the [Issues](https://github.com/rjayapra/ntg-insights-agents/issues) page for known problems
- Create a new issue if you encounter a bug
- Contact the maintainers for support

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For questions or support, please contact:
- Project Maintainer: [rjayapra](https://github.com/rjayapra)
- Issues: [GitHub Issues](https://github.com/rjayapra/ntg-insights-agents/issues)
