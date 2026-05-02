# Interactive-Business-Intelligence-Dashboard-

A complete BI pipeline that integrates 6 data sources, builds a star schema, calculates 35+ business measures, and displays an interactive dashboard. Includes performance optimization achieving 40% faster queries.

## Features

- **6 Data Sources**: Orders, Customers, Products, Marketing, Inventory, Returns
- **Star Schema**: Fact and dimension tables for optimal querying
- **35+ Business Measures**: Revenue, profit, LTV, churn, retention, cohorts, ROI
- **Performance Optimized**: Indexing, caching, materialized views - 40% improvement
- **Interactive Dashboard**: Revenue trends, customer segmentation, product analysis
- **CI/CD Ready**: GitHub Actions, Docker, automated testing

## Quick Start (5 minutes)

### Prerequisites
- Python 3.8 or higher
- Git (optional)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/accenture-bi-dashboard
cd accenture-bi-dashboard

# Run setup (installs packages, generates 6 data sources)
python scripts/setup.py

# Run the complete pipeline and dashboard
python run.py
# Then choose option 4
