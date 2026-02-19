CREATE OR REPLACE VIEW  reporting_data_dev.paginated_dev.gold_supplier_summary AS 
WITH supplier_customer_stats AS (
  SELECT 
    s.supplierID,
    s.name AS supplier_name,
    s.city AS supplier_city,
    s.continent AS supplier_continent,
    c.customerID,
    CONCAT(c.first_name, ' ', c.last_name) AS customer_name,
    COUNT(t.transactionID) AS customer_transactions,
    SUM(t.totalPrice) AS customer_sales_amount
  FROM samples.bakehouse.sales_transactions t
  JOIN samples.bakehouse.sales_franchises f ON t.franchiseID = f.franchiseID
  JOIN samples.bakehouse.sales_suppliers s ON f.supplierID = s.supplierID
  JOIN samples.bakehouse.sales_customers c ON t.customerID = c.customerID
  GROUP BY s.supplierID, s.name, s.city, s.continent, c.customerID, c.first_name, c.last_name
),
supplier_product_stats AS (
  SELECT 
    s.supplierID,
    t.product,
    COUNT(t.transactionID) AS product_transactions,
    SUM(t.totalPrice) AS product_sales_amount
  FROM samples.bakehouse.sales_transactions t
  JOIN samples.bakehouse.sales_franchises f ON t.franchiseID = f.franchiseID
  JOIN samples.bakehouse.sales_suppliers s ON f.supplierID = s.supplierID
  GROUP BY s.supplierID, t.product
),
supplier_summary AS (
  SELECT 
    supplierID,
    supplier_name,
    supplier_city,
    supplier_continent,
    SUM(customer_transactions) AS total_transactions,
    SUM(customer_sales_amount) AS total_sales_amount,
    SLICE(
      ARRAY_SORT(
        COLLECT_LIST(
          STRUCT(
            customer_name,
            customer_transactions AS transactions,
            customer_sales_amount AS amount
          )
        ),
        (left, right) -> CASE 
          WHEN left.transactions > right.transactions THEN -1 
          WHEN left.transactions < right.transactions THEN 1 
          ELSE 0 
        END
      ),
      1,
      5
    ) AS top_5_customers
  FROM supplier_customer_stats
  GROUP BY supplierID, supplier_name, supplier_city, supplier_continent
),
supplier_top_products AS (
  SELECT 
    supplierID,
    SLICE(
      ARRAY_SORT(
        COLLECT_LIST(
          STRUCT(
            product,
            product_transactions AS transactions,
            product_sales_amount AS amount
          )
        ),
        (left, right) -> CASE 
          WHEN left.transactions > right.transactions THEN -1 
          WHEN left.transactions < right.transactions THEN 1 
          ELSE 0 
        END
      ),
      1,
      3
    ) AS top_3_products
  FROM supplier_product_stats
  GROUP BY supplierID
)
SELECT 
  ss.supplierID,
  ss.supplier_name,
  ss.supplier_city,
  ss.supplier_continent,
  ss.total_transactions,
  ss.total_sales_amount,
  ss.top_5_customers,
  stp.top_3_products
FROM supplier_summary ss
LEFT JOIN supplier_top_products stp ON ss.supplierID = stp.supplierID
ORDER BY ss.total_transactions DESC;