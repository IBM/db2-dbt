# dbt-db2

The `dbt-db2` adapter allows dbt to work with IBM DB2 databases. This adapter uses the `ibm_db` Python driver to connect to DB2 databases.

## Features

- ✅ Full dbt support for IBM DB2
- ✅ Table and view materializations
- ✅ Incremental models (merge and delete+insert strategies)
- ✅ Seeds
- ✅ Snapshots
- ✅ Tests and documentation
- ✅ Grants management

## Requirements

- Python 3.9 - 3.13 (Python 3.14 not yet supported due to dependency issues)
- dbt-core ~= 1.11.0
- ibm_db == 3.2.8
- IBM DB2 database (LUW, z/OS, or iSeries)

## Installation

### Install from source

```bash
git clone <repository-url>
cd db2-dbt
pip install -e .
```

### Install from PyPI (when available)

```bash
pip install dbt-db2
```

## Configuration

### profiles.yml

Configure your DB2 connection in `~/.dbt/profiles.yml`:

```yaml
my_db2_project:
  outputs:
    dev:
      type: db2
      host: your-db2-host
      port: 50000  # Default DB2 port
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
| `host` | Yes* | - | DB2 server hostname |
| `port` | No | 50000 | DB2 server port |
| `database` | Yes | - | Database name |
| `schema` | Yes | - | Schema name |
| `username` | Yes | - | DB2 username |
| `password` | Yes | - | DB2 password |
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
      dsn: MY_DB2_DSN
      username: your_username
      password: your_password
      schema: your_schema
      threads: 4
  target: dev
```

## DB2-Specific Considerations

### Case Sensitivity

DB2 uppercases unquoted identifiers by default. The adapter handles this automatically, but be aware:

- Unquoted table/column names will be uppercased
- Use quotes in your SQL to preserve case: `"MyTable"` vs `MYTABLE`

### Data Types

The adapter maps dbt data types to DB2 types:

| dbt Type | DB2 Type |
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

Edit `~/.dbt/profiles.yml` with your DB2 connection details.

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

1. **Verify DB2 is accessible**:
   ```bash
   db2 connect to your_database user your_username
   ```

2. **Check firewall/network**: Ensure port 50000 (or your custom port) is open

3. **Verify credentials**: Ensure username/password are correct

### Python Version Issues

If you encounter mashumaro serialization errors, ensure you're using Python 3.9-3.13 (not 3.14).

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

1. **Python 3.14**: Not yet supported due to mashumaro library compatibility
2. **Constraints**: CHECK, UNIQUE, PRIMARY KEY, and FOREIGN KEY constraints are defined but not enforced by DB2 in dbt context
3. **Distribution keys**: Not applicable to DB2 (Netezza-specific feature)

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

[Add your license here]

## Support

For issues and questions:
- GitHub Issues: [repository-url]/issues
- dbt Community: https://community.getdbt.com/

## Version History

### 1.0.5
- Updated ibm_db to 3.2.8
- Updated dbt-core to ~1.8.0
- Improved DB2 compatibility
- Fixed connection handling

## Related Projects

- [dbt-core](https://github.com/dbt-labs/dbt-core)
- [ibm_db Python driver](https://github.com/ibmdb/python-ibmdb)
