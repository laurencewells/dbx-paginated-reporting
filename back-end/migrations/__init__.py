"""
SQL migration strings for Lakebase PostgreSQL tables.

Storing migrations as Python strings avoids OS-level file reads
and simplifies deployment (no need to bundle .sql files separately).
"""

# -- app schema ----------------------------------------------------------------
# Created before any tables so we avoid needing CREATE privileges on 'public'.

CREATE_APP_SCHEMA = "CREATE SCHEMA IF NOT EXISTS {schema}"

# -- structures table ----------------------------------------------------------

CREATE_STRUCTURES_TABLE = """\
CREATE TABLE IF NOT EXISTS structures (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    fields JSONB NOT NULL DEFAULT '[]',
    tables JSONB NOT NULL DEFAULT '[]',
    relationships JSONB NOT NULL DEFAULT '[]',
    selected_columns JSONB NOT NULL DEFAULT '[]',
    sql_query TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
)"""

# -- templates table -----------------------------------------------------------

CREATE_TEMPLATES_TABLE = """\
CREATE TABLE IF NOT EXISTS templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    structure_id UUID NOT NULL REFERENCES structures(id) ON DELETE CASCADE,
    html_content TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
)"""

CREATE_TEMPLATES_INDEXES = """\
CREATE INDEX IF NOT EXISTS idx_templates_structure_id
    ON templates(structure_id)"""

# -- seed: structures ----------------------------------------------------------

SEED_STRUCTURES = """\
INSERT INTO structures (id, name, fields, tables, selected_columns, sql_query) VALUES
(
    'a0000000-0000-0000-0000-000000000001',
    'Customer Directory',
    '[
        {"name": "customerID", "type": "number"},
        {"name": "first_name", "type": "string"},
        {"name": "last_name", "type": "string"},
        {"name": "email_address", "type": "string"},
        {"name": "phone_number", "type": "string"},
        {"name": "address", "type": "string"},
        {"name": "city", "type": "string"},
        {"name": "state", "type": "string"},
        {"name": "country", "type": "string"},
        {"name": "continent", "type": "string"},
        {"name": "postal_zip_code", "type": "number"},
        {"name": "gender", "type": "string"}
    ]'::jsonb,
    '[{"full_name": "samples.bakehouse.sales_customers", "alias": "sales_customers"}]'::jsonb,
    '["customerID", "first_name", "last_name", "email_address", "phone_number", "address", "city", "state", "country", "continent", "postal_zip_code", "gender"]'::jsonb,
    'SELECT customerID, first_name, last_name, email_address, phone_number, address, city, state, country, continent, postal_zip_code, gender FROM samples.bakehouse.sales_customers'
),
(
    'a0000000-0000-0000-0000-000000000002',
    'Supplier Directory',
    '[
        {"name": "supplierID", "type": "number"},
        {"name": "name", "type": "string"},
        {"name": "ingredient", "type": "string"},
        {"name": "continent", "type": "string"},
        {"name": "city", "type": "string"},
        {"name": "district", "type": "string"},
        {"name": "size", "type": "string"},
        {"name": "longitude", "type": "number"},
        {"name": "latitude", "type": "number"},
        {"name": "approved", "type": "string"}
    ]'::jsonb,
    '[{"full_name": "samples.bakehouse.sales_suppliers", "alias": "sales_suppliers"}]'::jsonb,
    '["supplierID", "name", "ingredient", "continent", "city", "district", "size", "longitude", "latitude", "approved"]'::jsonb,
    'SELECT supplierID, name, ingredient, continent, city, district, size, longitude, latitude, approved FROM samples.bakehouse.sales_suppliers'
)
ON CONFLICT (id) DO NOTHING"""

# -- seed: templates -----------------------------------------------------------
# Template HTML is stored via separate per-template inserts to keep strings manageable.

_CUSTOMER_PER_PAGE_HTML = r"""<div class="report-preview">
  <div class="report-page">
    <div class="report-page-header">
      <h1>Customer Profiles</h1>
      <p class="lead">Individual Customer Report</p>
    </div>
    <div class="text-center my-4">
      <i class="bi bi-people-fill" style="font-size: 4rem; color: #3498db;"></i>
      <p class="text-muted mt-3">samples.bakehouse.sales_customers</p>
    </div>
    <div class="page-number">Cover Page</div>
  </div>
  {{#rows}}
  <div class="report-page">
    <div class="report-page-header">
      <div class="d-flex justify-content-between align-items-center">
        <div>
          <h2>{{first_name}} {{last_name}}</h2>
          <p class="text-muted mb-0">Customer #{{customerID}}</p>
        </div>
        <span class="badge bg-primary fs-6">{{gender}}</span>
      </div>
    </div>
    <div class="row mb-4">
      <div class="col-md-4">
        <div class="text-center p-4 bg-light rounded">
          <i class="bi bi-person-circle" style="font-size: 5rem; color: #6c757d;"></i>
          <h4 class="mt-3">{{first_name}} {{last_name}}</h4>
          <p class="text-muted">Record {{_index}} of {{_total}}</p>
        </div>
      </div>
      <div class="col-md-8">
        <div class="card h-100">
          <div class="card-header"><strong>Contact Information</strong></div>
          <div class="card-body">
            <table class="table table-borderless mb-0">
              <tr><td class="text-muted" style="width:140px;">Email:</td><td><strong>{{email_address}}</strong></td></tr>
              <tr><td class="text-muted">Phone:</td><td><strong>{{phone_number}}</strong></td></tr>
              <tr><td class="text-muted">Address:</td><td><strong>{{address}}</strong></td></tr>
            </table>
          </div>
        </div>
      </div>
    </div>
    <div class="row mb-4">
      <div class="col-md-6">
        <div class="card">
          <div class="card-header"><strong>Location</strong></div>
          <div class="card-body">
            <table class="table table-borderless mb-0">
              <tr><td class="text-muted" style="width:120px;">City:</td><td><strong>{{city}}</strong></td></tr>
              <tr><td class="text-muted">State:</td><td><strong>{{state}}</strong></td></tr>
              <tr><td class="text-muted">Country:</td><td><strong>{{country}}</strong></td></tr>
              <tr><td class="text-muted">Continent:</td><td><strong>{{continent}}</strong></td></tr>
              <tr><td class="text-muted">Postal Code:</td><td><strong>{{postal_zip_code}}</strong></td></tr>
            </table>
          </div>
        </div>
      </div>
      <div class="col-md-6">
        <div class="report-tile tile-primary mb-3">
          <div class="report-tile-title">Customer ID</div>
          <div class="report-tile-value">{{customerID}}</div>
        </div>
        <div class="report-tile tile-success">
          <div class="report-tile-title">Region</div>
          <div class="report-tile-value">{{continent}}</div>
        </div>
      </div>
    </div>
    <div class="page-number">Customer {{_index}} of {{_total}}</div>
  </div>
  {{/rows}}
</div>"""

_SUPPLIER_PER_PAGE_HTML = r"""<div class="report-preview">
  <div class="report-page">
    <div class="report-page-header">
      <h1>Supplier Profiles</h1>
      <p class="lead">Individual Supplier Report</p>
    </div>
    <div class="text-center my-4">
      <i class="bi bi-shop" style="font-size: 4rem; color: #27ae60;"></i>
      <p class="text-muted mt-3">samples.bakehouse.sales_suppliers</p>
    </div>
    <div class="page-number">Cover Page</div>
  </div>
  {{#rows}}
  <div class="report-page">
    <div class="report-page-header">
      <div class="d-flex justify-content-between align-items-center">
        <div>
          <h2>{{name}}</h2>
          <p class="text-muted mb-0">Supplier #{{supplierID}}</p>
        </div>
        {{#approved}}<span class="badge bg-success fs-6">{{approved}}</span>{{/approved}}
      </div>
    </div>
    <div class="row mb-4">
      <div class="col-md-4">
        <div class="text-center p-4 bg-light rounded">
          <i class="bi bi-building" style="font-size: 5rem; color: #6c757d;"></i>
          <h4 class="mt-3">{{name}}</h4>
          <p class="text-muted">Record {{_index}} of {{_total}}</p>
        </div>
      </div>
      <div class="col-md-8">
        <div class="card h-100">
          <div class="card-header"><strong>Supplier Details</strong></div>
          <div class="card-body">
            <table class="table table-borderless mb-0">
              <tr><td class="text-muted" style="width:140px;">Supplier ID:</td><td><strong>{{supplierID}}</strong></td></tr>
              <tr><td class="text-muted">Ingredient:</td><td><strong>{{ingredient}}</strong></td></tr>
              <tr><td class="text-muted">Size:</td><td><strong>{{size}}</strong></td></tr>
              <tr><td class="text-muted">Approved:</td><td><strong>{{approved}}</strong></td></tr>
            </table>
          </div>
        </div>
      </div>
    </div>
    <div class="row mb-4">
      <div class="col-md-6">
        <div class="card">
          <div class="card-header"><strong>Location</strong></div>
          <div class="card-body">
            <table class="table table-borderless mb-0">
              <tr><td class="text-muted" style="width:120px;">City:</td><td><strong>{{city}}</strong></td></tr>
              <tr><td class="text-muted">District:</td><td><strong>{{district}}</strong></td></tr>
              <tr><td class="text-muted">Continent:</td><td><strong>{{continent}}</strong></td></tr>
            </table>
          </div>
        </div>
      </div>
      <div class="col-md-6">
        <div class="card">
          <div class="card-header"><strong>Coordinates</strong></div>
          <div class="card-body">
            <div class="report-tile tile-primary mb-3">
              <div class="report-tile-title">Longitude</div>
              <div class="report-tile-value">{{longitude}}</div>
            </div>
            <div class="report-tile tile-success">
              <div class="report-tile-title">Latitude</div>
              <div class="report-tile-value">{{latitude}}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="page-number">Supplier {{_index}} of {{_total}}</div>
  </div>
  {{/rows}}
</div>"""

# Built at import time so the factory can reference a single constant
SEED_TEMPLATES = (
    "INSERT INTO templates (id, name, structure_id, html_content) VALUES\n"
    "('b0000000-0000-0000-0000-000000000001', 'Customer Profiles (Per-Page)', 'a0000000-0000-0000-0000-000000000001', $tmpl$" + _CUSTOMER_PER_PAGE_HTML + "$tmpl$),\n"
    "('b0000000-0000-0000-0000-000000000002', 'Supplier Profiles (Per-Page)', 'a0000000-0000-0000-0000-000000000002', $tmpl$" + _SUPPLIER_PER_PAGE_HTML + "$tmpl$)\n"
    "ON CONFLICT (id) DO NOTHING"
)

# -- conversation_messages table ------------------------------------------------

CREATE_CONVERSATION_MESSAGES_TABLE = """\
CREATE TABLE IF NOT EXISTS conversation_messages (
    id UUID PRIMARY KEY,
    space_id VARCHAR(255) NOT NULL,
    conversation_id VARCHAR(255) NOT NULL,
    message_id VARCHAR(255) NOT NULL,
    user_message TEXT NOT NULL,
    genie_response TEXT,
    query_result JSONB,
    query_data JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
)"""

CREATE_CONVERSATION_MESSAGES_INDEXES = """\
CREATE INDEX IF NOT EXISTS idx_conversation_messages_conversation_id
    ON conversation_messages(conversation_id);

CREATE INDEX IF NOT EXISTS idx_conversation_messages_created_at
    ON conversation_messages(created_at);

CREATE INDEX IF NOT EXISTS idx_conversation_messages_space_id
    ON conversation_messages(space_id)"""
