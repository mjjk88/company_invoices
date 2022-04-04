# Description
This is a demo script to download invoices from the revenue management platform Chargebee and commit them to SQLAlchemy database.

# Pre-requirments 
- `python >= 3.8` installed in the system
- token to Chargebee set as an environment variable: `CHARGEBEE_API_TOKEN`

# How to install
This package is managed by `setuptool`.
To install dependencies use:
 
```shell
cd company_invoices
python3 -m venv venv
source venv/bin/activate
python3 setup.py install
```

# How to run 
**TIP:**
Use `--help` to get the instruction how to run the script

Activate `venv` if not already active:
```shell
cd company_invoices
source venv/bin/activate
```

Run python command line script with all args (use proper Chargebee token), e.g.:
```shell
CHARGEBEE_API_TOKEN=PUT_YOUR_TOKEN_HERE python3 company_invoices/main.py --domain 'company-old-test' --db 'sqlite:///company_invoices.db'
```

# How it works
Script:
1) connects to Chargebee using their python library and provided token (via env variable)  
2) gets the invoices list in batches
3) maps the Chargebee DTOs ("attributes"/responses) to DB model and validates it
4) commits validated rows to DB tables (invoices table, invoices_items table) 
5) saves broken rows (e.g. with missing fields) to the data-error logs file that can be processed later e.g. for alerting


# Improvements to consider 
- Extend DB model validation, e.g. check if the value of the field is in proper Python type 
- Extend tests
- Persist more columns to the DB, e.g. `total` to be able to calculate discount in percentage (but was not the part of the task)