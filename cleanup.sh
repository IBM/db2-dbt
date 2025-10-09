rm -rf build dist *.egg-info
pip uninstall your-package-name -y
find . -name "__pycache__" -exec rm -rf {} +
find . -name "*.pyc" -delete
pip install -e .
