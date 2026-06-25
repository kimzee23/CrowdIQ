import os
import shutil
from pathlib import Path

def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)

# Define the root of the source
root = Path("src")

# 1. Define old-to-new mapping for directories
# Note: we will move files one by one to avoid overwriting issues and to accurately change filenames where needed.

moves = [
    # domain/exception
    (root / "shared/exceptions", root / "domain/exception"),
    
    # application/port/input (dtos)
    (root / "application/dto", root / "application/port/input"),
    
    # application/port/output (repositories interfaces)
    # We will move individual repository.py files to port/output as <module>_repository.py
    
    # domain/service
    (root / "application/services", root / "domain/service"),
    
    # infrastructure/config
    (root / "shared/configs", root / "infrastructure/config"),
    (root / "shared/security", root / "infrastructure/config/security"),
    (root / "shared/utils", root / "infrastructure/config/utils"),
    
    # infrastructure/input/rest/controller
    (root / "presentation/api/v1", root / "infrastructure/input/rest/controller"),
    
    # infrastructure/output/adapter
    (root / "infrastructure/redis", root / "infrastructure/output/adapter/redis"),
    (root / "infrastructure/opensearch", root / "infrastructure/output/adapter/opensearch"),
    (root / "infrastructure/keycloak", root / "infrastructure/output/adapter/keycloak"),
    (root / "infrastructure/celery", root / "infrastructure/output/adapter/celery"),
    (root / "infrastructure/openai", root / "infrastructure/output/adapter/openai"),
    
    # infrastructure/persistence
    (root / "infrastructure/postgres/repositories", root / "infrastructure/persistence/adapter"),
    (root / "infrastructure/postgres/models", root / "infrastructure/persistence/entity"),
]

# Execute directory moves
for src, dst in moves:
    if src.exists():
        ensure_dir(dst.parent)
        print(f"Moving {src} -> {dst}")
        shutil.move(str(src), str(dst))

# Handle specific files in domain subfolders (entity.py -> model/<module>.py, repository.py -> application/port/output/<module>_repository.py)
domain_dir = root / "domain"
model_dir = domain_dir / "model"
output_port_dir = root / "application/port/output"

ensure_dir(model_dir)
ensure_dir(output_port_dir)

if domain_dir.exists():
    for sub in domain_dir.iterdir():
        if sub.is_dir() and sub.name not in ["exception", "model", "service", "validator"]:
            # check for entity.py
            entity_file = sub / "entity.py"
            if entity_file.exists():
                dst_file = model_dir / f"{sub.name}.py"
                print(f"Moving {entity_file} -> {dst_file}")
                shutil.move(str(entity_file), str(dst_file))
            
            # check for repository.py
            repo_file = sub / "repository.py"
            if repo_file.exists():
                dst_file = output_port_dir / f"{sub.name}_repository.py"
                print(f"Moving {repo_file} -> {dst_file}")
                shutil.move(str(repo_file), str(dst_file))
            
            # remove __init__.py and delete directory if empty
            init_file = sub / "__init__.py"
            if init_file.exists():
                init_file.unlink()
                
            try:
                sub.rmdir()
            except OSError:
                pass # directory not empty (maybe pycache)
                shutil.rmtree(str(sub), ignore_errors=True)

# Move presentation/api/deps.py -> infrastructure/input/rest/controller/deps.py
deps_file = root / "presentation/api/deps.py"
deps_dst = root / "infrastructure/input/rest/controller/deps.py"
if deps_file.exists():
    print(f"Moving {deps_file} -> {deps_dst}")
    shutil.move(str(deps_file), str(deps_dst))

# Clean up presentation
presentation_dir = root / "presentation"
if presentation_dir.exists():
    shutil.rmtree(str(presentation_dir), ignore_errors=True)

# Move infrastructure/postgres/database.py -> infrastructure/persistence/repository/database.py
db_file = root / "infrastructure/postgres/database.py"
db_dst = root / "infrastructure/persistence/repository/database.py"
ensure_dir(db_dst.parent)
if db_file.exists():
    print(f"Moving {db_file} -> {db_dst}")
    shutil.move(str(db_file), str(db_dst))

# Clean up postgres
postgres_dir = root / "infrastructure/postgres"
if postgres_dir.exists():
    shutil.rmtree(str(postgres_dir), ignore_errors=True)
    
# Clean up shared
shared_dir = root / "shared"
if shared_dir.exists():
    shutil.rmtree(str(shared_dir), ignore_errors=True)

# Clean up application (except port and service if service is there, wait service moved to domain)
app_dir = root / "application"
for sub in app_dir.iterdir():
    if sub.name not in ["port"] and sub.is_dir():
        shutil.rmtree(str(sub), ignore_errors=True)

# Create missing directories
ensure_dir(root / "domain/validator")
ensure_dir(root / "infrastructure/input/data")
ensure_dir(root / "infrastructure/input/mapper")
ensure_dir(root / "infrastructure/messages")
ensure_dir(root / "infrastructure/output/mapper")
(root / "infrastructure/messages/constants.py").touch()

# IMPORT REPLACEMENTS
import_map = {
    # exact paths
    "src.shared.exceptions": "src.domain.exception",
    "src.shared.configs": "src.infrastructure.config",
    "src.shared.security": "src.infrastructure.config.security",
    "src.shared.utils": "src.infrastructure.config.utils",
    
    "src.presentation.api.v1": "src.infrastructure.input.rest.controller",
    "src.presentation.api.deps": "src.infrastructure.input.rest.controller.deps",
    
    "src.application.dto": "src.application.port.input",
    "src.application.services": "src.domain.service",
    
    "src.infrastructure.postgres.repositories": "src.infrastructure.persistence.adapter",
    "src.infrastructure.postgres.models": "src.infrastructure.persistence.entity",
    "src.infrastructure.postgres.database": "src.infrastructure.persistence.repository.database",
    
    "src.infrastructure.redis": "src.infrastructure.output.adapter.redis",
    "src.infrastructure.opensearch": "src.infrastructure.output.adapter.opensearch",
    "src.infrastructure.keycloak": "src.infrastructure.output.adapter.keycloak",
    "src.infrastructure.celery": "src.infrastructure.output.adapter.celery",
    "src.infrastructure.openai": "src.infrastructure.output.adapter.openai",
    
    # specific entities and repositories
    "src.domain.user.entity": "src.domain.model.user",
    "src.domain.prediction.entity": "src.domain.model.prediction",
    "src.domain.category.entity": "src.domain.model.category",
    "src.domain.comment.entity": "src.domain.model.comment",
    "src.domain.notification.entity": "src.domain.model.notification",
    "src.domain.reputation.entity": "src.domain.model.reputation",
    "src.domain.vote.entity": "src.domain.model.vote",
    "src.domain.ai.entity": "src.domain.model.ai",
    "src.domain.base.entity": "src.domain.model.base",
    
    "src.domain.user.repository": "src.application.port.output.user_repository",
    "src.domain.prediction.repository": "src.application.port.output.prediction_repository",
    "src.domain.comment.repository": "src.application.port.output.comment_repository",
    "src.domain.notification.repository": "src.application.port.output.notification_repository",
    "src.domain.reputation.repository": "src.application.port.output.reputation_repository",
    "src.domain.vote.repository": "src.application.port.output.vote_repository",
    "src.domain.category.repository": "src.application.port.output.category_repository",
}

# Update main.py separately
main_file = Path("main.py")
if main_file.exists():
    content = main_file.read_text("utf-8")
    for old, new in import_map.items():
        content = content.replace(old, new)
    main_file.write_text(content, "utf-8")

# Update tests and src
for directory in ["src", "tests"]:
    for filepath in Path(directory).rglob("*.py"):
        if filepath.is_file():
            content = filepath.read_text("utf-8")
            original_content = content
            for old, new in import_map.items():
                content = content.replace(old, new)
            if content != original_content:
                filepath.write_text(content, "utf-8")
                print(f"Updated imports in {filepath}")

print("Migration completed!")
