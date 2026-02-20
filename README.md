# Real-Time EcoHouse PV Monitoring Dashboard (Demo)

A prototype real-time photovoltaic (PV) monitoring dashboard designed
for EcoHouse environments.\
This project visualizes simulated live solar energy data, including
temperature and power metrics, through an interactive Streamlit
interface.

------------------------------------------------------------------------

## Project Overview

This repository contains a lightweight real-time monitoring system that
simulates photovoltaic sensor data and renders it through an interactive
web dashboard.

The system demonstrates:

-   Real-time temperature monitoring
-   Real-time power monitoring
-   Rolling average power calculation
-   Live trend visualization
-   Insight/status detection panel
-   Recent data feed (newest first)

⚠️ Note: At this stage, the system operates on synthetic data generated
locally. It is structured to allow seamless integration with real PV
hardware in future extensions.

------------------------------------------------------------------------

## Repository Structure

    Real-Time-EcoHouse-PV/
    │
    ├── dashboard.py              # Main Streamlit dashboard application
    ├── datagen.py                # Synthetic real-time data generator
    ├── requirements.txt          # Python dependencies
    │
    ├── data/
    │   └── sample_data.csv       # Example CSV file with sample sensor data
    │
    ├── documentation.pdf         # Development report / project documentation
    │
    └── README.md                 # This file

------------------------------------------------------------------------

## System Architecture

### `datagen.py`

Continuously generates simulated photovoltaic readings (temperature and
power) and appends them to a CSV file. This mimics a live PV data
stream.

### `dashboard.py`

Built with Streamlit, it reads the live-updating CSV and renders: - KPI
cards - Time-series charts - Insight alerts - Recent data table

------------------------------------------------------------------------

## How to Run the Project

### 1️⃣ Clone the Repository

``` bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
cd YOUR-REPO-NAME
```

------------------------------------------------------------------------

### 2️⃣ Create a Virtual Environment (Recommended)

``` bash
python -m venv venv
```

Activate:

**Mac/Linux**

``` bash
source venv/bin/activate
```

**Windows (PowerShell)**

``` bash
venv\Scripts\Activate.ps1
```

------------------------------------------------------------------------

### 3️⃣ Install Dependencies

``` bash
pip install -r requirements.txt
```

------------------------------------------------------------------------

### 4️⃣ Start the Synthetic Data Generator

``` bash
python datagen.py
```

------------------------------------------------------------------------

### 5️⃣ Launch the Dashboard

``` bash
streamlit run dashboard.py
```

The dashboard will automatically open in your browser.

------------------------------------------------------------------------

## Example Data

The `data/` folder contains:

    sample_data.csv

This file shows example PV readings and can be used for testing or
initial previewing.

------------------------------------------------------------------------

## Documentation

A short development report describing the system architecture, design
rationale, and implementation details is included as:

    documentation.pdf

------------------------------------------------------------------------

## 🛠 Technologies Used

-   Python
-   Streamlit
-   Pandas
-   CSV-based data streaming

------------------------------------------------------------------------


This project is intended for educational and research demonstration
purposes.
