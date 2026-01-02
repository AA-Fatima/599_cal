# Contributing to 599_cal

Thank you for your interest in contributing to the 599_cal project! This document provides guidelines and instructions for contributing.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/599_cal.git
   cd 599_cal
   ```
3. **Set up the development environment**:
   ```bash
   ./setup.sh
   ```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

Use descriptive branch names:
- `feature/add-meal-tracking`
- `fix/usda-lookup-error`
- `docs/update-api-documentation`

### 2. Make Your Changes

Follow the project structure:
- Backend changes: `backend/` or `backend_chatbot/`
- Frontend changes: `frontend/`
- Documentation: Update relevant README files

### 3. Test Your Changes

#### Backend Chatbot
```bash
cd backend_chatbot
python3 test_services.py
python3 main.py  # Manual testing
```

#### Original Backend
```bash
cd backend
# Run existing tests if available
uvicorn main:app --reload
```

### 4. Commit Your Changes

Write clear, descriptive commit messages:

```bash
git add .
git commit -m "Add USDA ingredient caching for faster lookups"
```

Good commit messages:
- Start with a verb (Add, Fix, Update, Remove)
- Be specific about what changed
- Keep under 72 characters for the title
- Add details in the body if needed

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:
- Clear title describing the change
- Description of what was changed and why
- Any related issues (e.g., "Fixes #123")
- Screenshots for UI changes

## Code Style Guidelines

### Python (Backend)

- Follow PEP 8 style guide
- Use type hints where possible
- Add docstrings to functions and classes
- Keep functions focused and small

Example:
```python
def calculate_nutrition(self, gpt_response: GPTResponse) -> ChatResponse:
    """
    Calculate nutrition based on GPT response
    
    Args:
        gpt_response: Parsed response from OpenAI GPT
        
    Returns:
        ChatResponse with ingredients and totals
    """
    # Implementation
```

### TypeScript/Angular (Frontend)

- Follow Angular style guide
- Use meaningful component and service names
- Add comments for complex logic
- Keep components focused

### Documentation

- Update README files when adding features
- Document new API endpoints
- Include examples where helpful
- Keep documentation up to date

## Adding New Features

### Adding a New API Endpoint

1. Define Pydantic schema in `models/schemas.py`
2. Add endpoint in `main.py`
3. Implement service logic in appropriate service file
4. Update API documentation in README
5. Add example to demo script

### Adding a New USDA Data Source

1. Update `usda_lookup.py` to handle new format
2. Update `config.py` with new path
3. Test with `test_services.py`
4. Document in README

### Adding Frontend Components

1. Create component in `frontend/src/app/components/`
2. Add service methods in `frontend/src/app/services/`
3. Update routing if needed
4. Document component usage

## Testing

### Manual Testing

1. Start the services:
   ```bash
   docker-compose up
   ```

2. Test endpoints:
   - Visit http://localhost:8001/docs for Swagger UI
   - Use curl or Postman
   - Run demo script: `python3 backend_chatbot/demo.py`

### Automated Testing

Run the test suite:
```bash
cd backend_chatbot
python3 test_services.py
```

## Common Tasks

### Adding a New Dish Type

1. Add dish data to `backend/data/dishes.xlsx`
2. Ensure ingredients exist in USDA dataset
3. Test via API or admin panel

### Expanding USDA Dataset

1. Obtain additional USDA data files
2. Update `usda_lookup.py` to load new files
3. Test ingredient lookup

### Improving GPT Prompts

1. Edit `backend_chatbot/services/openai_service.py`
2. Modify the `system_prompt` in `parse_food_query()`
3. Test with various queries
4. Document prompt design choices

## Reporting Issues

When reporting issues, include:

- **Description**: Clear description of the problem
- **Steps to Reproduce**: Numbered steps to reproduce
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Environment**: OS, Python version, Docker version
- **Logs**: Relevant error messages or logs

## Questions?

- Open an issue for questions
- Review existing documentation
- Check the README files in each directory

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the code, not the person
- Help others learn and grow

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

Thank you for contributing to 599_cal! 🎉
