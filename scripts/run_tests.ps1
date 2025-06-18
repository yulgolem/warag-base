# Run unit tests
Write-Host "Running unit tests..." -ForegroundColor Green
pytest tests/agents/test_graph_coordinator.py -v

# Run integration tests if requested
$run_integration = Read-Host "Run integration tests? (y/n)"
if ($run_integration -eq "y") {
    Write-Host "Running integration tests..." -ForegroundColor Green
    pytest tests/integration/test_graph_coordinator_integration.py -v
}

# Generate coverage report
Write-Host "Generating coverage report..." -ForegroundColor Green
pytest --cov=src --cov-report=html 