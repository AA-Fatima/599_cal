# Contributing to Calorie Chatbot

Thank you for your interest in contributing! This guide will help you get started.

## Development Setup

1. **Fork the repository** and clone your fork
2. **Follow QUICKSTART.md** to set up your development environment
3. **Create a feature branch** from `main`

```bash
git checkout -b feature/your-feature-name
```

## Code Style

### Python (Backend)
- Follow PEP 8 style guide
- Use type hints where appropriate
- Add docstrings for classes and functions
- Keep functions focused and small
- Use descriptive variable names

### TypeScript/Angular (Frontend)
- Follow Angular style guide
- Use TypeScript strict mode
- Add JSDoc comments for complex functions
- Use meaningful component and service names

## Adding New Features

### Adding a New Synonym
Edit `backend/scripts/populate_reference_data.py`:

```python
SYNONYMS_DATA = [
    # ... existing synonyms
    ("your_term", "canonical_form"),
]
```

Then run:
```bash
docker-compose exec backend python scripts/populate_reference_data.py
```

### Adding Unit Conversions
Edit `backend/scripts/populate_reference_data.py`:

```python
UNIT_CONVERSIONS_DATA = [
    # ... existing conversions
    ("ingredient_name", "unit", grams_value),
]
```

### Adding API Endpoints
1. Add route in `backend/main.py`
2. Add service logic in `backend/services/`
3. Update models if needed in `backend/models.py`
4. Update frontend service if needed

### Training Custom Models

#### Intent Classification
1. Create labeled data: `backend/data/intent_labeled.jsonl`
   ```json
   {"text": "how many calories", "label": "calorie_query"}
   {"text": "hello", "label": "greeting"}
   ```
2. Run training: `python scripts/train_intent.py`
3. Test the model

#### NER Model
1. Create labeled data: `backend/data/ner_labeled.jsonl`
   ```json
   {"tokens": ["how", "many", "calories", "in", "fajita"], 
    "labels": ["O", "O", "O", "O", "B-DISH"]}
   ```
2. Run training: `python scripts/train_ner_crf.py`
3. Test the model

## Testing

### Backend Tests
```bash
cd backend
pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Integration Tests
```bash
./dev.sh test
```

## Pull Request Process

1. **Update documentation** if needed
2. **Add tests** for new features
3. **Ensure all tests pass**
4. **Update CHANGELOG.md** (if exists)
5. **Create pull request** with clear description
6. **Link related issues**

### PR Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How was this tested?

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] All tests pass
```

## Common Tasks

### Adding a New Food Database Source
1. Create ingestion script in `backend/scripts/`
2. Add models if needed in `backend/models.py`
3. Update `ingest_all.py` to include new source
4. Document in README

### Improving NER Accuracy
1. Collect more labeled training data
2. Try different model architectures (CRF vs Transformer)
3. Experiment with features (word2vec, BERT embeddings)
4. Fine-tune hyperparameters

### Adding i18n Support
1. Frontend: Use Angular i18n
2. Backend: Add language parameter to API
3. Add translations for UI strings
4. Support RTL for Arabic

### Adding Nutrition Tracking
1. Add user model and authentication
2. Create history/tracking tables
3. Add endpoints for saving/retrieving history
4. Update frontend with tracking UI

## Database Migrations

When changing database schema:

1. Update models in `backend/models.py`
2. Create migration script (consider using Alembic)
3. Test migration on fresh database
4. Document migration in PR

## Debugging Tips

### Backend Issues
```bash
# View backend logs
docker-compose logs -f backend

# Shell into backend container
docker-compose exec backend bash

# Test database connection
docker-compose exec backend python -c "from db import engine; print(engine.connect())"
```

### Frontend Issues
```bash
# View frontend logs
docker-compose logs -f frontend

# Rebuild frontend
docker-compose build frontend
docker-compose up -d frontend
```

### Database Issues
```bash
# Access PostgreSQL shell
docker-compose exec postgres psql -U calories -d calories

# View tables
\dt

# Check data
SELECT COUNT(*) FROM usda_items;
```

## Code Review Guidelines

### For Reviewers
- Check code quality and style
- Verify tests are adequate
- Ensure documentation is updated
- Test functionality locally
- Provide constructive feedback

### For Contributors
- Respond to feedback promptly
- Make requested changes
- Keep PR scope focused
- Be patient and professional

## Release Process

1. Update version in relevant files
2. Update CHANGELOG.md
3. Create release branch
4. Tag release
5. Build and publish Docker images
6. Update documentation

## Questions?

- Open an issue for bugs or feature requests
- Use discussions for questions
- Check existing issues before creating new ones

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.
