#!/bin/bash
# Development helper script

set -e

case "$1" in
  start)
    echo "Starting all services..."
    docker-compose up -d
    echo "✓ Services started"
    echo "  Backend: http://localhost:8000"
    echo "  Frontend: http://localhost:4200"
    echo "  API Docs: http://localhost:8000/docs"
    ;;
    
  stop)
    echo "Stopping all services..."
    docker-compose down
    echo "✓ Services stopped"
    ;;
    
  restart)
    echo "Restarting all services..."
    docker-compose restart
    echo "✓ Services restarted"
    ;;
    
  logs)
    docker-compose logs -f "${2:-backend}"
    ;;
    
  init)
    echo "Initializing database and ingesting data..."
    docker-compose up -d postgres redis
    sleep 5
    docker-compose run --rm backend python scripts/ingest_all.py
    echo "✓ Initialization complete"
    ;;
    
  reset)
    echo "⚠️  WARNING: This will delete all data!"
    read -p "Are you sure? (yes/no): " confirm
    if [ "$confirm" = "yes" ]; then
      docker-compose down -v
      echo "✓ All data deleted"
      echo "Run './dev.sh init' to reinitialize"
    else
      echo "Cancelled"
    fi
    ;;
    
  test)
    echo "Running backend verification..."
    docker-compose run --rm backend python verify_setup.py
    ;;
    
  shell)
    docker-compose exec backend bash
    ;;
    
  db)
    docker-compose exec postgres psql -U calories -d calories
    ;;
    
  *)
    echo "Usage: $0 {start|stop|restart|logs|init|reset|test|shell|db}"
    echo ""
    echo "Commands:"
    echo "  start    - Start all services"
    echo "  stop     - Stop all services"
    echo "  restart  - Restart all services"
    echo "  logs     - View logs (optional: logs backend|frontend|postgres)"
    echo "  init     - Initialize database and ingest data"
    echo "  reset    - Delete all data and volumes (WARNING: destructive)"
    echo "  test     - Run verification tests"
    echo "  shell    - Open bash shell in backend container"
    echo "  db       - Open PostgreSQL shell"
    exit 1
    ;;
esac
