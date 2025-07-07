# Property Monitor

![Python Version](https://img.shields.io/badge/Python-3.13%2B-blue.svg)
![Dependencies](https://img.shields.io/badge/Dependencies-aiohttp%2C%20beautifulsoup4%2C%20pandas-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## Table of Contents

- [Property Monitor](#property-monitor)
  - [About the Project](#about-the-project)
  - [Features](#features)
  - [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
  - [Usage](#usage)
  - [Project Structure](#project-structure)
  - [Contributing](#contributing)
  - [License](#license)

## About the Project

Property Monitor is a robust Python-based application designed for efficient and automated real estate listing surveillance. It specializes in extracting comprehensive data for 500 properties from a specified online real estate portal, cleaning and structuring this information, and storing it for further analysis. This tool demonstrates proficiency in web scraping, data processing, and handling asynchronous operations, making it ideal for anyone needing to track real estate market changes or build a property dataset.

## Features

- **Targeted Web Scraping:** Specifically extracts information for up to 500 properties from a designated online real estate portal.
- **Asynchronous Requests with `aiohttp`:** Utilizes `aiohttp` to perform efficient, non-blocking HTTP requests, significantly speeding up the data collection process.
- **Robust HTML Parsing with `Beautiful Soup 4`:** Employs Beautiful Soup 4 to accurately parse complex HTML structures and extract relevant property details such as price, location, number of rooms, size, and direct listing URLs.
- **Data Structuring and Cleaning with `Pandas`:** Leverages the `pandas` library to organize raw scraped data into DataFrames, allowing for easy cleaning, manipulation, and analysis.
- **Local Data Persistence:** Stores processed property data in a `SQLite` database (`property_listings.db`) and exports cleaned datasets to CSV files for convenient access and historical tracking.
- **Visual Data Representation:** Generates visual outputs, such as price distribution plots (`price_distribution.png`), to offer quick insights into the collected data.
- **Logging:** Implements logging (`log_scrape.log`) to track application activities, errors, and progress during the scraping process.

## Getting Started

Follow these steps to set up and run the Property Monitor on your local machine.

### Prerequisites

- **Python 3.13 or newer:** This project is developed and tested with Python 3.13. You can verify your Python version using:
  ```bash
  python3 --version
  ```
- **C/C++ Compiler:** As `pandas` (and other libraries) has C extensions (parts of the code written in C/C++ for performance), a C/C++ compiler is required on your system to install them correctly.

  - **On Fedora-based systems (e.g., Fedora KDE):**
    Ensure you have `g++` and `gcc-c++` installed. You can do this with:
    ```bash
    sudo dnf5 install g++ gcc-c++
    ```
  - **On Debian/Ubuntu-based systems:**
    Install essential build tools with:
    ```bash
    sudo apt-get update
    sudo apt-get install build-essential
    ```
  - **On macOS:**
    Ensure Xcode Command Line Tools are installed. You can install them (or check if already present) by running:
    ```bash
    xcode-select --install
    ```
  - **On Windows:**
    It is recommended to install [Microsoft Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/). You can download them from the Visual Studio website, selecting "Tools for Visual Studio" and choosing "Build Tools for Visual Studio." Alternatively, tools like [MinGW](https://osdn.net/projects/mingw/releases/) can be used, but MSVC Build Tools are often preferred for compatibility with Python packages on Windows.

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/Sangiorgi-Leandro/property-monitor.git
    cd property-monitor
    ```

2.  **Create and activate a virtual environment:**
    It's highly recommended to use a virtual environment to manage project dependencies in isolation.

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the required Python packages:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

To run the Property Monitor and begin scraping:

1.  **Execute the main script:**

    ```bash
    python main.py
    ```

    Upon successful execution, the script will:

    - Scrape data for 500 properties.
    - Store the structured data in `data/property_listings.db`.
    - Generate a cleaned CSV file (e.g., `output/rightmove_cleaned.csv`) and potentially timestamped CSVs in the `output/` directory.
    - Produce a price distribution graph (`output/price_distribution.png`).
    - Log all activities to `log_scrape.log`.

## Project Structure

A concise overview of the main files and directories in this project:

```
property-monitor/
├── data/                       # Contains the SQLite database (property_listings.db)
├── output/                     # Contains generated CSV files and plots
│   ├── rightmove_cleaned.csv
│   ├── rightmove_properties_2025-07-07_100000.csv (example)
│   └── price_distribution.png
├── src/                        # Core application source code
│   ├── init.py
│   ├── analyze.py              # Logic for data analysis and visualization
│   └── main.py                 # Main entry point for the application
├── venv/                       # Python virtual environment (ignored by Git)
├── tests/                      # Placeholder for future unit and integration tests
├── .gitignore                  # Specifies files/directories to be ignored by Git
├── requirements.txt            # Project dependencies list
├── LICENSE                     # Project license file (e.g., MIT License)
├── README.md                   # This README file
└── run_daily.sh                # Script for daily execution
```

## Contributing

This project is a personal portfolio piece to demonstrate specific skills. While direct contributions via pull requests are not the primary focus, I welcome any feedback, suggestions for improvement, or bug reports via the Issues section of this repository.

## License

Distributed under the MIT License. See the `LICENSE` file for more information.

---

## Author

Leandro Sangiorgi  
GitHub: [github.com/Sangiorgi-Leandro](https://github.com/Sangiorgi-Leandro)  
For inquiries, please open an issue or contact me via GitHub.
