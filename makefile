.PHONY: help build run test lint clean

help:
	@echo "GuardianSensor Development Commands:"
	@echo "  make build     - Build Docker image"
	@echo "  make run       - Run development environment"
	@echo "  make test      - Run tests in Docker"
	@echo "  make lint      - Run code quality checks"
	@echo "  make clean     - Clean up containers and volumes"
	@echo "  make deploy    - Deploy to production (example)"

build:
	docker build -t guardiansensor:latest .

run:
	docker-compose up --build

run-detached:
	docker-compose up -d --build

stop:
	docker-compose down

test:
	docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit

lint:
	docker run --rm -v $(PWD):/app guardiansensor:latest \
		sh -c "black --check . && flake8 . && mypy api/ processing/ risk/"

clean:
	docker-compose down -v
	docker system prune -f

logs:
	docker-compose logs -f

# Production deployment example (would need actual cloud credentials)
deploy:
	@echo "Building production image..."
	docker build -t guardiansensor:prod .
	@echo "Tagging and pushing to registry..."
	# docker tag guardiansensor:prod your-registry/guardiansensor:latest
	# docker push your-registry/guardiansensor:latest
	@echo "Update would be triggered here (k8s, ECS, etc.)"