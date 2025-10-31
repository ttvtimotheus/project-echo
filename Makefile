.PHONY: help deploy-all deploy-analyzer deploy-summarizer deploy-reporter deploy-crawler setup-pubsub test clean

PROJECT_ID := echo-476821
REGION := europe-west4

help:
	@echo "Project ECHO - Make Commands"
	@echo ""
	@echo "Deploy Commands:"
	@echo "  make deploy-all         Deploy all services and setup Pub/Sub"
	@echo "  make deploy-analyzer    Deploy analyzer service (GPU)"
	@echo "  make deploy-summarizer  Deploy summarizer service"
	@echo "  make deploy-reporter    Deploy reporter service"
	@echo "  make deploy-crawler     Deploy crawler job"
	@echo "  make setup-pubsub       Setup Pub/Sub topics and subscriptions"
	@echo ""
	@echo "Test Commands:"
	@echo "  make test              Test all service endpoints"
	@echo "  make run-crawler       Execute crawler job"
	@echo "  make view-report       View latest report"
	@echo "  make logs              Tail all service logs"
	@echo ""
	@echo "Utility Commands:"
	@echo "  make clean             Clean local build artifacts"

deploy-all:
	@chmod +x infra/scripts/*.sh
	@cd infra/scripts && ./deploy-all.sh

deploy-analyzer:
	@chmod +x infra/scripts/deploy-analyzer.sh
	@cd infra/scripts && ./deploy-analyzer.sh

deploy-summarizer:
	@chmod +x infra/scripts/deploy-summarizer.sh
	@cd infra/scripts && ./deploy-summarizer.sh

deploy-reporter:
	@chmod +x infra/scripts/deploy-reporter.sh
	@cd infra/scripts && ./deploy-reporter.sh

deploy-crawler:
	@chmod +x infra/scripts/deploy-crawler-job.sh
	@cd infra/scripts && ./deploy-crawler-job.sh

setup-pubsub:
	@chmod +x infra/scripts/setup-pubsub.sh
	@cd infra/scripts && ./setup-pubsub.sh

test:
	@echo "Testing all services..."
	@echo ""
	@echo "Analyzer:"
	@curl -s $$(gcloud run services describe analyzer --region=$(REGION) --project=$(PROJECT_ID) --format='value(status.url)')/ | jq
	@echo ""
	@echo "Summarizer:"
	@curl -s $$(gcloud run services describe summarizer --region=$(REGION) --project=$(PROJECT_ID) --format='value(status.url)')/ | jq
	@echo ""
	@echo "Reporter:"
	@curl -s $$(gcloud run services describe reporter --region=$(REGION) --project=$(PROJECT_ID) --format='value(status.url)')/ | jq

run-crawler:
	@echo "Executing crawler job..."
	@gcloud run jobs execute crawler --region=$(REGION) --project=$(PROJECT_ID)

view-report:
	@echo "Fetching latest report..."
	@curl -s $$(gcloud run services describe reporter --region=$(REGION) --project=$(PROJECT_ID) --format='value(status.url)')/latest | jq -r '.html'

logs:
	@echo "Tailing logs for all services..."
	@gcloud beta logging tail 'resource.type=cloud_run_revision AND (resource.labels.service_name=analyzer OR resource.labels.service_name=summarizer OR resource.labels.service_name=reporter)' --project=$(PROJECT_ID)

clean:
	@echo "Cleaning build artifacts..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "Clean complete"
