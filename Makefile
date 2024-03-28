test:
	flake8 senziio --max-line-length=99 && \
	pytest -v --cov=senziio --cov-fail-under=50 --cov-report=html

.PHONY: test
.SILENT:
