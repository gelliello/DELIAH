# Contributing to DELIAH

Thank you for your interest in contributing to DELIAH! This document provides guidelines and information for contributors.

## Getting Started

1. Fork the repository
2. Clone your fork
3. Create a feature branch
4. Make your changes
5. Submit a pull request

## Development Setup

### Backend
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn backend.api.main:app --reload
```

### Desktop
```bash
cd apps/windows
npm install
npm run dev
```

## Code Style

- Python: Follow PEP 8
- TypeScript: Use ESLint and Prettier
- Flutter: Follow Dart style guide

## Pull Requests

- Keep PRs focused on a single change
- Include tests when possible
- Update documentation as needed
- Reference any related issues

## Reporting Issues

- Use GitHub Issues
- Include steps to reproduce
- Include system information
- Be specific about expected vs actual behavior

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
