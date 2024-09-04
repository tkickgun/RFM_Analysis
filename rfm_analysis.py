import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Load sales data with appropriate parsing and data types
sales_data = pd.read_csv('sales_data.csv', parse_dates=['OrderDate'], dtype={'_CustomerID': 'str'})

# Display the data types of the columns
sales_data.dtypes

# Create a copy of the original DataFrame for further processing
df = sales_data.copy()
df.head()

# Calculate revenue per order based on pricing, discounts, and order quantity
df['Revenue'] = ((df['Unit Price'] - (df['Unit Price'] * df['Discount Applied'])) - df['Unit Cost']) * df['Order Quantity']

# Select relevant columns for RFM analysis
columns = ['OrderNumber', '_CustomerID', 'OrderDate', 'Revenue']
rfm_data = df[columns]

# Determine the most recent order date and set 'today' as two days after this date - since the data is pretty old one
max_order_date = max(df['OrderDate'])
today = max_order_date + timedelta(days=2)

# Aggregate RFM metrics: Recency (days since last purchase), Frequency (total orders), Monetary (total revenue)
rfm = rfm_data.groupby('_CustomerID').agg({'OrderDate': lambda x: (today - x.max()).days,
                                           'OrderNumber': 'count',
                                           'Revenue': 'sum'})

# Rename the columns for better clarity
rfm.columns = ['Recency', 'Frequency', 'Monetary']

# Rank customers based on Recency, Frequency, and Monetary value into quintiles (5 groups)
r = pd.qcut(rfm['Recency'], q=5, labels=range(5, 0, -1))
f = pd.qcut(rfm['Frequency'], q=5, labels=range(1, 6))
m = pd.qcut(rfm['Monetary'], q=5, labels=range(1, 6))

# Assign R, F, M scores to each customer based on their quintile rankings
rfm_df = rfm.assign(R=r.values, F=f.values, M=m.values)

# Create a combined RFM group and calculate the overall RFM score
rfm_df['rfm_group'] = rfm_df[['R', 'F', 'M']].apply(lambda x: '-'.join(x.astype(str)), axis=1)
rfm_df['rfm_score'] = rfm_df[['R', 'F', 'M']].sum(axis=1)

# Sort customers by their RFM score in descending order
rfm_df.sort_values('rfm_score', ascending=False).reset_index()
