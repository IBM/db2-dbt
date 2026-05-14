# ibm-dbt-db2

The `ibm-dbt-db2` adapter allows dbt to work with IBM Db2 databases. This adapter uses the `ibm_db` Python driver to connect to Db2 databases.

## Features

- ✅ Full dbt support for IBM Db2
- ✅ Table and view materializations
- ✅ Incremental models (merge and delete+insert strategies)
- ✅ Seeds
- ✅ Snapshots
- ✅ Tests and documentation
- ✅ Grants management

## Requirements

- Python 3.10 - 3.12 (Python 3.13+ not yet tested; Python 3.9 not supported due to dbt-core 1.11+ requirements)
- dbt-core ~= 1.11.0
- ibm_db == 3.2.8
- IBM Db2 database (LUW, z/OS, or iSeries)

## Installation

### Install from source

```bash
git clone <repository-url>
cd db2-dbt
pip install -e .
```

### Install from PyPI (when available)

```bash
pip install ibm-dbt-db2
```

## Configuration

### profiles.yml

Configure your Db2 connection in `~/.dbt/profiles.yml`:

```yaml
my_db2_project:
  outputs:
    dev:
      type: db2
      host: your-db2-host
      port: 50000  # Default Db2 port
      database: your_database
      schema: your_schema
      username: your_username
      password: your_password
      threads: 4
  target: dev
```

For a complete example with all available options including SSL/TLS configuration, see [profiles.yml.example](dbt/include/db2/profiles.yml.example).

### Connection Parameters

#### Required Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `type` | Yes | - | Must be `db2` |
| `host` | Yes* | - | Db2 server hostname |
| `port` | No | 50000 | Db2 server port |
| `database` | Yes | - | Database name |
| `schema` | Yes | - | Schema name |
| `username` | Yes | - | Db2 username |
| `password` | Yes | - | Db2 password |
| `threads` | No | 1 | Number of threads for parallel execution |

*Not required if using `dsn`

#### Optional SSL/TLS Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `security` | No | - | Security protocol (use `SSL` to enable SSL/TLS) |
| `ssl_server_certificate` | No | - | Path to server CA certificate file |
| `ssl_client_keystore` | No | - | Path to client keystore database (.kdb file) |
| `ssl_client_keystash` | No | - | Path to client keystash file (.sth file) |
| `ssl_client_hostname_validation` | No | - | Enable hostname verification (true/false) |
| `retries` | No | 1 | Number of connection retry attempts |

#### SSL/TLS Configuration Example

```yaml
my_db2_project:
  outputs:
    prod:
      type: db2
      host: secure-db2.example.com
      port: 50001
      database: PRODDB
      schema: ANALYTICS
      username: prod_user
      password: prod_password
      threads: 8
      # SSL/TLS settings
      security: SSL
      ssl_server_certificate: /path/to/server-ca.crt
      ssl_client_hostname_validation: true
      retries: 3
  target: prod
```

### Using DSN Connection

Alternatively, you can use a DSN (Data Source Name):

```yaml
my_db2_project:
  outputs:
    dev:
      type: db2
      dsn: MY_Db2_DSN
      username: your_username
      password: your_password
      schema: your_schema
      threads: 4
  target: dev
```

## Db2-Specific Considerations

### Case Sensitivity

Db2 uppercases unquoted identifiers by default. The adapter handles this automatically, but be aware:

- Unquoted table/column names will be uppercased
- Use quotes in your SQL to preserve case: `"MyTable"` vs `MYTABLE`

### Data Types

The adapter maps dbt data types to Db2 types:

| dbt Type | Db2 Type |
|----------|----------|
| string | VARCHAR |
| text | VARCHAR(max_length) |
| integer | INTEGER |
| bigint | BIGINT |
| float | FLOAT |
| numeric | DECIMAL |
| boolean | BOOLEAN |
| timestamp | TIMESTAMP |
| date | DATE |
| time | TIME |

### Incremental Models

Supported incremental strategies:

1. **merge** (default) - Uses MERGE statement
2. **delete+insert** - Deletes matching records then inserts

Example:

```sql
{{
  config(
    materialized='incremental',
    unique_key='id',
    incremental_strategy='merge'
  )
}}

SELECT * FROM source_table
{% if is_incremental() %}
WHERE updated_at > (SELECT MAX(updated_at) FROM {{ this }})
{% endif %}
```

## Getting Started

### 1. Initialize a dbt Project

```bash
dbt init my_db2_project
```

### 2. Configure Connection

Edit `~/.dbt/profiles.yml` with your Db2 connection details.

### 3. Test Connection

```bash
cd my_db2_project
dbt debug
```

### 4. Create Models

Create SQL files in the `models/` directory:

```sql
-- models/my_model.sql
SELECT
    customer_id,
    customer_name,
    order_date
FROM {{ source('raw', 'orders') }}
WHERE order_date >= CURRENT_DATE - 30 DAYS
```

### 5. Run Models

```bash
dbt run
```

### 6. Test Models

```bash
dbt test
```

## Common Commands

```bash
# Run all models
dbt run

# Run specific model
dbt run --select my_model

# Run models and downstream dependencies
dbt run --select my_model+

# Test all models
dbt test

# Generate documentation
dbt docs generate

# Serve documentation
dbt docs serve

# Create snapshots
dbt snapshot

# Load seed data
dbt seed
```

## Supported dbt Features

| Feature | Supported |
|---------|-----------|
| Table materialization | ✅ Yes |
| View materialization | ✅ Yes |
| Incremental materialization | ✅ Yes |
| Ephemeral materialization | ✅ Yes |
| Seeds | ✅ Yes |
| Snapshots | ✅ Yes |
| Tests | ✅ Yes |
| Documentation | ✅ Yes |
| Sources | ✅ Yes |
| Custom schemas | ✅ Yes |
| Grants | ✅ Yes |
| Constraints | ⚠️ Partial (NOT NULL enforced, others not enforced) |

## Troubleshooting

### Connection Issues

1. **Verify Db2 is accessible**:
   ```bash
   db2 connect to your_database user your_username
   ```

2. **Check firewall/network**: Ensure port 50000 (or your custom port) is open

3. **Verify credentials**: Ensure username/password are correct

### Python Version Issues

This adapter requires Python 3.10 or higher due to dbt-core 1.11+ dependencies requiring `dbt-common~=1.37` and `dbt-adapters~=1.15`, which both require Python 3.10+.

**Supported versions:** Python 3.10, 3.11, 3.12
**Not supported:** Python 3.9 (use older dbt-core versions), Python 3.13+ (not yet tested)

### Driver Issues

If `ibm_db` installation fails:

```bash
# On macOS
brew install gcc

# On Linux
sudo apt-get install python3-dev gcc

# Then reinstall
pip install ibm_db==3.2.8
```

## Known Limitations

1. **Python Version**:
   - Requires Python 3.10+ (dbt-core 1.11+ dependency requirement)
   - Python 3.13+ not yet tested
2. **Constraints**: CHECK, UNIQUE, PRIMARY KEY, and FOREIGN KEY constraints are defined but not enforced by Db2 in dbt context
3. **LISTAGG limit_num**: Db2's LISTAGG function does not support limiting the number of aggregated values

## Development

### Building from Source

To build the wheel file for development:

```bash
# Install build dependencies
pip install build

# Build the wheel
python -m build

# The wheel file will be in dist/
```

### Running Tests

The project uses pytest for testing with support for multiple Python versions and platforms:

```bash
# Install test dependencies
pip install -e ".[dev]"

# Run unit tests
pytest tests/unit -v

# Run functional tests (requires DB2 connection)
pytest tests/functional -v

# Run all tests
pytest tests/ -v
```

### Code Quality

The project uses flake8 for linting:

```bash
# Run linting
flake8 dbt/ tests/

# Auto-fix some issues with pre-commit
pre-commit run --all-files
```

### Continuous Integration

The project uses GitHub Actions for CI/CD:

#### Unit Tests Workflow
- **Triggers**: Push to main, pull requests
- **Testing Matrix**:
  - OS: Ubuntu, macOS
  - Python: 3.10, 3.11, 3.12
- **Jobs**: Lint (flake8) and test across all combinations
- **Note**: Windows is excluded due to ibm_db DLL dependency issues in CI environments

#### Release Workflow
- **Triggers**: Manual workflow dispatch or GitHub release
- **Process**:
  1. **Build**: Creates wheel and validates with `twine check`
  2. **Test Install**: Verifies installation on Ubuntu and macOS with Python 3.10 and 3.12
  3. **Publish**: Deploys to Test PyPI or PyPI based on selection

### Release Process

#### Testing a Release (Test PyPI)
1. Go to **Actions** tab in GitHub
2. Select **"Build and Publish Release"** workflow
3. Click **"Run workflow"**
4. Choose **`test-pypi`** from the dropdown
5. Package will be published to https://test.pypi.org/p/ibm-dbt-db2

To install from Test PyPI:
```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ ibm-dbt-db2
```

#### Production Release (PyPI)
1. Ensure all tests pass and code is ready
2. Test the release on Test PyPI first (see above)
3. Go to **Actions** tab in GitHub
4. Select **"Build and Publish Release"** workflow
5. Click **"Run workflow"**
6. Choose **`pypi`** from the dropdown
7. Package will be published to https://pypi.org/p/ibm-dbt-db2

#### Automatic Release on GitHub Release
When you create a GitHub release (tag), the workflow will automatically trigger but requires manual dispatch to publish.

**Prerequisites**: Configure GitHub environments:
- **test-pypi** environment with Test PyPI trusted publisher
- **pypi** environment with PyPI trusted publisher

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests (unit and/or functional)
5. Ensure all tests pass and code passes linting
6. Submit a pull request

All pull requests will automatically run:
- Linting checks (flake8)
- Unit tests across multiple Python versions and platforms
- Code quality validation

## License

[Add your license here]

## Support

For issues and questions:
- GitHub Issues: https://github.com/IBM/db2-dbt/issues
- dbt Community: https://community.getdbt.com/

## Version History

### 1.0.0 (Current)
- Migrated to modern `pyproject.toml` packaging (PEP 517/518/621)
- Updated to dbt-core ~1.11.0
- Updated ibm_db to 3.2.8
- **Breaking:** Dropped Python 3.9 support (requires Python 3.10+)
- Tested on Python 3.10, 3.11, 3.12
- Fixed 27 Flake8 linting errors
- Improved unit test coverage (37 passing, 8 skipped)
- Updated to strict code quality standards
- Modernized CI/CD workflows
- Security updates (PyYAML 6.0.3+, flake8 7.3)

## Related Projects

- [dbt-core](https://github.com/dbt-labs/dbt-core)
- [ibm_db Python driver](https://github.com/ibmdb/python-ibmdb)
