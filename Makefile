PYTHON=python3
VENV=.venv
PIP=$(VENV)/bin/pip
PY=$(VENV)/bin/python
REQUIREMENTS=requirements.txt
BUILD_DIR=build

all: english french

$(VENV)/bin/activate: $(REQUIREMENTS)
	@echo "🔧 Creating virtual environment..."
	@$(PYTHON) -m venv $(VENV)
	@$(PIP) install --upgrade pip
	@$(PIP) install -r $(REQUIREMENTS)

english: $(VENV)/bin/activate
	@$(PY) generate.py english

french: $(VENV)/bin/activate
	@$(PY) generate.py french

clean:
	rm -rf $(BUILD_DIR) *.aux *.log *.out *.bbl *.blg

full_clean: clean
	@rm -rf $(VENV)

rebuild: clean all
