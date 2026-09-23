
# Mystery Delivery System 📦🚚

A Python-based logistics simulation system for a fictional delivery company called **FastBox**. The system assigns packages to the nearest delivery agents, simulates package deliveries, calculates travel distances and efficiency, and generates a final JSON report.

## 📌 Features

* 📂 Read and parse JSON test-case files
* 📍 Assign packages to the nearest delivery agent
* 📐 Calculate distance using Euclidean distance
* 🚚 Simulate agent movement and package delivery
* 📊 Calculate total distance traveled by each agent
* 📦 Count packages delivered by each agent
* ⚡ Calculate delivery efficiency
* 🏆 Identify the most efficient agent
* 📄 Generate `report.json`
* 🗂️ Support different numbers of warehouses, agents, and packages
* 📁 Select the test JSON file using a file-selection window
* ✅ Validate that all packages are delivered

## 🛠️ Technologies Used

* **Python**
* **JSON**
* **Tkinter**
* **Math**
* **File Handling**

## ⚙️ How the System Works

### 1. Select Test Case

When the program starts, a file-selection window allows the user to select any JSON test-case file.

Example:

```text
Select Test Case JSON File
        ↓
   test_case_1.json
```

### 2. Read Input Data

The program reads:

* Warehouses and their locations
* Delivery agents and their locations
* Packages
* Package warehouse
* Package destination

### 3. Assign Packages

Each package is assigned to the nearest agent based on the Euclidean distance between the agent and the package's warehouse.

The Euclidean distance formula is:

```text
Distance = √((x₂ - x₁)² + (y₂ - y₁)²)
```

### 4. Simulate Delivery

For each package, the assigned agent travels:

```text
Current Agent Location
        ↓
Warehouse
        ↓
Package Destination
```

The distance traveled during both movements is added to the agent's total distance.

### 5. Calculate Efficiency

The efficiency value is calculated as:

```text
Efficiency = Total Distance / Packages Delivered
```

A lower average distance per delivery represents greater efficiency.

### 6. Generate Report

The program generates a `report.json` file containing each agent's:

* Number of packages delivered
* Total distance traveled
* Efficiency

It also identifies the best-performing agent.

## 📄 Output Format

The generated `report.json` has the following structure:

```json
{
    "A1": {
        "delivered": 2,
        "distance": 85.32,
        "efficiency": 42.66
    },
    "A2": {
        "delivered": 2,
        "distance": 120.12,
        "efficiency": 60.06
    },
    "A3": {
        "delivered": 1,
        "distance": 50.0,
        "efficiency": 50.0
    },
    "agent": "A1"
}
```

The actual values are calculated dynamically from the selected test-case file.

## 📁 Project Structure

```text
Mystery-Delivery-System/
│
├── main.py
├── data.json
├── test_case_1.json
├── test_case_2.json
├── test_case_3.json
├── test_case_4.json
├── report.json
└── README.md
```

## ▶️ How to Run

### Step 1: Clone the Repository

```bash
git clone <your-repository-url>
```

### Step 2: Open the Project

Open the project in **PyCharm** or any Python IDE.

### Step 3: Run the Program

Run:

```bash
python main.py
```

### Step 4: Select a Test Case

A file-selection window will appear.

Select any JSON test file, for example:

```text
test_case_1.json
```

The program will process the selected file automatically.

### Step 5: Check the Output

After processing, the program creates:

```text
report.json
```

The report is also displayed in the terminal.

## 🧪 Test Cases

The project can handle different test-case configurations, including:

* Different numbers of warehouses
* Different numbers of delivery agents
* Different numbers of packages
* Different warehouse and agent coordinates
* Different package destinations

The program does not depend on fixed warehouse, agent, or package IDs.

## ✅ Validation

The program checks that:

```text
Total packages delivered = Total packages in input
```

If the numbers do not match, the program reports a delivery validation error.

## 🚀 Future Enhancements

Possible future improvements include:

* Random delivery delays
* ASCII route visualization
* Agents joining during the day
* CSV export for the top-performing agent
* Package priority handling
* Route optimization
* Delivery time simulation

## 👩‍💻 Author

**Ankita Tode**

Python | Data Science | Software Development
