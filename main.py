import json
import math
import sys


def normalize_locations(data, key):
    """
    Accept both supported formats:
    1. {"W1": [x, y], "W2": [x, y]}
    2. [{"id": "W1", "location": [x, y]}, ...]
    """
    items = data.get(key, {})

    if isinstance(items, dict):
        return items

    result = {}
    for item in items:
        result[item["id"]] = item["location"]
    return result


def euclidean_distance(point1, point2):
    """Calculate Euclidean distance between two [x, y] points."""
    return math.hypot(
        point1[0] - point2[0],
        point1[1] - point2[1]
    )


def assign_packages(data):
    warehouses = normalize_locations(data, "warehouses")
    agents = normalize_locations(data, "agents")
    packages = data.get("packages", [])

    # Store each agent's current position and statistics.
    agent_state = {
        agent_id: {
            "position": list(location),
            "delivered": [],
            "distance": 0.0
        }
        for agent_id, location in agents.items()
    }

    assignments = {}

    # Assign every package to the nearest agent based on
    # the agent's position and the package's warehouse.
    for package in packages:
        package_id = package["id"]

        # Support both "warehouse" and "warehouse_id".
        warehouse_id = package.get("warehouse", package.get("warehouse_id"))

        if warehouse_id not in warehouses:
            raise ValueError(
                f"Package {package_id} refers to unknown warehouse "
                f"{warehouse_id!r}."
            )

        warehouse_location = warehouses[warehouse_id]

        nearest_agent = min(
            agents,
            key=lambda agent_id: (
                euclidean_distance(
                    agents[agent_id],
                    warehouse_location
                ),
                agent_id
            )
        )

        assignments[package_id] = nearest_agent

    # Simulate delivery.
    #
    # For each assigned package:
    # current position -> warehouse -> destination
    #
    # Packages are processed in the same order in which they appear
    # in the input JSON.
    for package in packages:
        package_id = package["id"]
        agent_id = assignments[package_id]
        warehouse_id = package.get("warehouse", package.get("warehouse_id"))

        state = agent_state[agent_id]
        warehouse_location = warehouses[warehouse_id]
        destination = package["destination"]

        # Travel from current position to warehouse.
        state["distance"] += euclidean_distance(
            state["position"],
            warehouse_location
        )
        state["position"] = list(warehouse_location)

        # Travel from warehouse to destination.
        state["distance"] += euclidean_distance(
            warehouse_location,
            destination
        )
        state["position"] = list(destination)

        state["delivered"].append(package_id)

    return agent_state, assignments


def generate_report(data):
    agent_state, assignments = assign_packages(data)

    report = {}

    for agent_id in agent_state:
        state = agent_state[agent_id]
        delivered_count = len(state["delivered"])
        distance = state["distance"]

        # Efficiency is total distance / packages delivered.
        # For an agent with no packages, use 0.0 so the report
        # remains valid and the agent cannot become best_agent.
        efficiency = (
            distance / delivered_count
            if delivered_count > 0
            else 0.0
        )

        report[agent_id] = {
            "delivered": delivered_count,
            "distance": round(distance, 2),
            "efficiency": round(efficiency, 2)
        }

    # Find the agent with the lowest average distance per delivery.
    active_agents = [
        agent_id
        for agent_id in report
        if report[agent_id]["delivered"] > 0
    ]

    best_agent = min(
        active_agents,
        key=lambda agent_id: (
            report[agent_id]["efficiency"],
            agent_id
        )
    ) if active_agents else None

    report["agent"] = best_agent

    # Safety check: every input package must be delivered exactly once.
    total_packages = len(data.get("packages", []))
    total_delivered = sum(
        report[agent_id]["delivered"]
        for agent_id in agent_state
    )

    if total_delivered != total_packages:
        raise RuntimeError(
            f"Delivery validation failed: "
            f"{total_delivered} delivered out of {total_packages} packages."
        )

    return report


def main():
    import tkinter as tk
    from tkinter import filedialog

    # Open a file-selection window.
    root = tk.Tk()
    root.withdraw()

    input_file = filedialog.askopenfilename(
        title="Select Test Case JSON File",
        filetypes=[
            ("JSON files", "*.json"),
            ("All files", "*.*")
        ]
    )

    # User cancelled the file selection.
    if not input_file:
        print("No test file selected.")
        return

    output_file = "report.json"

    try:
        # Read the selected JSON test file.
        with open(input_file, "r", encoding="utf-8") as file:
            data = json.load(file)

        # Generate the delivery report.
        report = generate_report(data)

        # Save the report.
        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(report, file, indent=4)

        print(f"\nInput file: {input_file}")
        print(f"Report saved to: {output_file}\n")

        print("Final Report:")
        print(json.dumps(report, indent=4))

    except FileNotFoundError:
        print(f"Error: File not found: {input_file}")

    except json.JSONDecodeError as error:
        print(f"Error: Invalid JSON file: {error}")

    except (KeyError, ValueError, RuntimeError) as error:
        print(f"Error: {error}")

if __name__ == "__main__":
    main()
