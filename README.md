# scaling-engine

This repository contains the source code for the **Bitcoin Mining News Bot**, an automated system for fetching, processing, and posting news related to Bitcoin mining.

## Architecture

The bot follows a **Clean 4-File Design** philosophy:

### Core Files

- **`config.py`**: The single source of truth for all configurations
  - API keys and credentials
  - Filter lists (blacklisted sources, terms, etc.)
  - Prompt templates for AI content generation
  - Bot settings and parameters
  - Contains **no logic** - purely configuration data

- **`bot_lib.py`**: The core, stateless engine of the bot
  - All business logic implemented as functions
  - Fetching and filtering articles
  - Generating content with AI
  - Posting to social media platforms
  - Each function is pure and testable

- **`main.py`**: The single entry point for bot execution
  - Orchestrates the entire workflow
  - Calls functions from `bot_lib.py` in a linear sequence
  - Handles high-level error management
  - Simple, readable, and easy to understand

- **`tools.py`**: Command-line interface for bot management
  - Interactive tools for testing and debugging
  - Manual operations and administrative tasks
  - Development utilities

### Automation

- **`.github/workflows/main.yml`**: GitHub Actions workflow
  - Automates bot execution on a schedule
  - Ensures reliable, hands-free operation
  - Handles environment setup and credentials

## Development Philosophy

### 1. Simplicity

- **Functions over classes**: We use simple functions instead of complex object-oriented patterns
- **No inheritance**: Avoids unnecessary complexity and coupling
- **Clear data flow**: Each function has explicit inputs and outputs
- **Readable code**: Code should be easy to understand at first glance

### 2. Verification

- **Verify everything**: Every step is verified before proceeding to the next
- **File operations**: Always check that files exist and contain expected data
- **API responses**: Validate all external API calls
- **Data transformations**: Ensure data is in the expected format at each stage

### 3. Clear Error Handling

- **Specific exceptions**: Use custom exceptions for different failure scenarios
- **Graceful degradation**: Handle failures without halting the entire process
- **Informative messages**: Error messages should clearly explain what went wrong
- **Recovery strategies**: Where possible, implement automatic recovery from failures