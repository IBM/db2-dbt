  rm -rf dbt-env/
  python -m venv dbt-env
  pip install -r requirements.txt 
  pip install .
  cd dbtdb2sampleproject/
  dbt debug
