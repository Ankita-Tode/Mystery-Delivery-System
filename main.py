import json
import math
import random
import csv
import sys
import tkinter as tk
from tkinter import filedialog


# ============================================================
# MYSTERY DELIVERY SYSTEM - FASTBOX
# ============================================================

def normalize_locations(data, key):
    """
    Supports both formats:

    Dictionary:
        "warehouses": {
            "W1": [0, 0]
        }

    List:
        "warehouses": [
            {"id": "W1", "location": [0, 0]}
        ]
    """
    items = data.get(key, {})

    if isinstance(items, dict):
        return items

    result = {}
    for item in items:
        result[item["id"]] = item["location"]

    return result


def euclidean_distance(point1, point2, show=False, label=""):
    """
    Calculate Euclidean distance.

    Formula:
    distance = sqrt((x2-x1)^2 + (y2-y1)^2)
    """

    dx = point1[0] - point2[0]
    dy = point1[1] - point2[1]

    distance = math.hypot(dx, dy)

    if show:
        print(label)
        print(
            f"  Distance = √(({point1[0]} - {point2[0]})² + "
            f"({point1[1]} - {point2[1]})²)"
        )
        print(f"           = √({dx}² + {dy}²)")
        print(f"           = √({dx ** 2 + dy ** 2})")
        print(f"           = {distance:.4f}")
        print()

    return distance


# ============================================================
# BONUS 1: RANDOM DELIVERY DELAYS
# ============================================================

def random_delivery_delay():
    """
    Generate a random delivery delay between 5 and 30 minutes.
    The delay is informational and does not change distance.
    """
    return random.randint(5, 30)


# ============================================================
# BONUS 2: ASCII ROUTE VISUALIZATION
# ============================================================

def ascii_route(agent_id, route):
    """
    Display a simple text representation of an agent's route.
    """

    if not route:
        return

    print(f"\nASCII ROUTE - {agent_id}")
    print("-" * 50)

    print("START", end="")

    for location in route:
        print(f" -> {location}", end="")

    print(" -> END")


# ============================================================
# BONUS 3: NEW AGENT JOINING MID-DAY
# ============================================================

def get_midday_agents(data):
    """
    Supports an optional 'new_agents' section.

    Example:

    "new_agents": [
        {
            "id": "A5",
            "location": [50, 50],
            "after_package": 5
        }
    ]

    The new agent becomes available after the specified
    number of packages have already been processed.
    """

    new_agents = data.get("new_agents", [])

    if isinstance(new_agents, dict):
        new_agents = [
            {
                "id": agent_id,
                "location": location,
                "after_package": 0
            }
            for agent_id, location in new_agents.items()
        ]

    return new_agents


# ============================================================
# BONUS 4: EXPORT TOP PERFORMER TO CSV
# ============================================================

def export_top_performer(report, filename="top_performer.csv"):
    """Export the top-performing agent to CSV."""

    best_agent = report.get("agent")

    if not best_agent:
        return

    best_data = report[best_agent]

    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([
            "agent",
            "packages_delivered",
            "total_distance",
            "efficiency"
        ])

        writer.writerow([
            best_agent,
            best_data["delivered"],
            best_data["distance"],
            best_data["efficiency"]
        ])


# ============================================================
# MAIN SIMULATION
# ============================================================

def generate_report(data):

    warehouses = normalize_locations(data, "warehouses")
    agents = normalize_locations(data, "agents")
    packages = data.get("packages", [])

    # Current position and statistics for every agent.
    agent_state = {
        agent_id: {
            "position": list(location),
            "delivered": [],
            "distance": 0.0,
            "route": [],
            "delays": []
        }
        for agent_id, location in agents.items()
    }

    assignments = {}

    new_agents = get_midday_agents(data)
    new_agent_index = 0

    # --------------------------------------------------------
    # Package assignment
    # --------------------------------------------------------

    for package_number, package in enumerate(packages):

        # Check whether a new agent should join.
        while (
            new_agent_index < len(new_agents)
            and package_number >= new_agents[new_agent_index].get(
                "after_package", 0
            )
        ):
            new_agent = new_agents[new_agent_index]

            new_id = new_agent["id"]

            if new_id not in agent_state:
                agent_state[new_id] = {
                    "position": list(new_agent["location"]),
                    "delivered": [],
                    "distance": 0.0,
                    "route": [],
                    "delays": []
                }

                agents[new_id] = list(new_agent["location"])

                print(
                    f"\n*** NEW AGENT JOINED MID-DAY: "
                    f"{new_id} at {new_agent['location']} ***\n"
                )

            new_agent_index += 1

        package_id = package["id"]

        warehouse_id = package.get(
            "warehouse",
            package.get("warehouse_id")
        )

        if warehouse_id not in warehouses:
            raise ValueError(
                f"Package {package_id} refers to unknown warehouse "
                f"{warehouse_id!r}."
            )

        warehouse_location = warehouses[warehouse_id]

        print(f"\nPackage {package_id} -> Warehouse {warehouse_id}")
        print("=" * 60)

        distances = {}

        # Calculate distance from every available agent
        # to the package warehouse.
        for agent_id in agents:

            distance = euclidean_distance(
                agent_state[agent_id]["position"],
                warehouse_location,
                show=True,
                label=(
                    f"{agent_id} "
                    f"{tuple(agent_state[agent_id]['position'])} "
                    f"-> {warehouse_id} "
                    f"{tuple(warehouse_location)}"
                )
            )

            distances[agent_id] = distance

        # Nearest agent gets the package.
        nearest_agent = min(
            distances,
            key=lambda agent_id: (
                distances[agent_id],
                agent_id
            )
        )

        assignments[package_id] = nearest_agent

        print(f"Nearest Agent = {nearest_agent}")

    # --------------------------------------------------------
    # Delivery simulation
    # --------------------------------------------------------

    print("\n")
    print("=" * 60)
    print("DELIVERY SIMULATION")
    print("=" * 60)

    for package in packages:

        package_id = package["id"]
        agent_id = assignments[package_id]

        warehouse_id = package.get(
            "warehouse",
            package.get("warehouse_id")
        )

        warehouse_location = warehouses[warehouse_id]
        destination = package["destination"]

        state = agent_state[agent_id]

        print(
            f"\nDelivery: {package_id} by {agent_id}"
        )
        print("-" * 60)

        # Agent -> warehouse
        to_warehouse = euclidean_distance(
            state["position"],
            warehouse_location,
            show=True,
            label=(
                f"{agent_id} current position "
                f"{tuple(state['position'])} -> "
                f"{warehouse_id} "
                f"{tuple(warehouse_location)}"
            )
        )

        state["distance"] += to_warehouse

        state["route"].append(
            f"Warehouse {warehouse_id}"
        )

        state["position"] = list(warehouse_location)

        # Warehouse -> destination
        to_destination = euclidean_distance(
            warehouse_location,
            destination,
            show=True,
            label=(
                f"{warehouse_id} "
                f"{tuple(warehouse_location)} -> "
                f"Destination {tuple(destination)}"
            )
        )

        state["distance"] += to_destination

        state["route"].append(
            f"Destination {tuple(destination)}"
        )

        state["position"] = list(destination)

        # Package delivered.
        state["delivered"].append(package_id)

        # BONUS: random delivery delay.
        delay = random_delivery_delay()
        state["delays"].append(delay)

        print(
            f"Package {package_id} delivery distance: "
            f"{to_warehouse + to_destination:.4f}"
        )

        print(
            f"Random delivery delay: {delay} minutes"
        )

    # --------------------------------------------------------
    # Create required report
    # --------------------------------------------------------

    report = {}

    for agent_id in agent_state:

        state = agent_state[agent_id]

        delivered_count = len(state["delivered"])
        distance = state["distance"]

        if delivered_count > 0:
            efficiency = distance / delivered_count
        else:
            efficiency = 0.0

        report[agent_id] = {
            "delivered": delivered_count,
            "distance": round(distance, 2),
            "efficiency": round(efficiency, 2)
        }

    # Agents with deliveries are considered for best agent.
    active_agents = [
        agent_id
        for agent_id in report
        if report[agent_id]["delivered"] > 0
    ]

    if active_agents:
        best_agent = min(
            active_agents,
            key=lambda agent_id: (
                report[agent_id]["efficiency"],
                agent_id
            )
        )
    else:
        best_agent = None

    report["agent"] = best_agent

    # Validation: every package must be delivered exactly once.
    total_packages = len(packages)

    total_delivered = sum(
        report[agent_id]["delivered"]
        for agent_id in agent_state
    )

    if total_delivered != total_packages:
        raise RuntimeError(
            f"Delivery validation failed: "
            f"{total_delivered} delivered out of "
            f"{total_packages} packages."
        )

    # --------------------------------------------------------
    # BONUS: ASCII routes
    # --------------------------------------------------------

    print("\n")
    print("=" * 60)
    print("ASCII ROUTE VISUALIZATION")
    print("=" * 60)

    for agent_id, state in agent_state.items():
        if state["route"]:
            ascii_route(
                agent_id,
                state["route"]
            )

    # --------------------------------------------------------
    # BONUS: display delay summary
    # --------------------------------------------------------

    print("\n")
    print("=" * 60)
    print("DELIVERY DELAY SUMMARY")
    print("=" * 60)

    for agent_id, state in agent_state.items():

        if state["delays"]:
            total_delay = sum(state["delays"])

            print(
                f"{agent_id}: "
                f"{total_delay} minutes total delay"
            )

    # --------------------------------------------------------
    # BONUS: export top performer
    # --------------------------------------------------------

    export_top_performer(
        report,
        "top_performer.csv"
    )

    print(
        "\nTop performer exported to: top_performer.csv"
    )

    return report


# ============================================================
# FILE UPLOAD / SELECTION
# ============================================================

def main():

    # ONE input option:
    # Select any JSON test case using the file picker.

    root = tk.Tk()
    root.withdraw()

    input_file = filedialog.askopenfilename(
        title="Select Test Case JSON File",
        filetypes=[
            ("JSON files", "*.json"),
            ("All files", "*.*")
        ]
    )

    if not input_file:
        print("No test file selected.")
        return

    output_file = "report.json"

    try:

        # Read selected JSON file.
        with open(
            input_file,
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(file)

        # Generate report.
        report = generate_report(data)

        # Save required report.json.
        with open(
            output_file,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                report,
                file,
                indent=4
            )

        print("\n")
        print("=" * 60)
        print("FINAL REPORT")
        print("=" * 60)

        print(
            json.dumps(
                report,
                indent=4
            )
        )

        print(
            f"\nInput file: {input_file}"
        )

        print(
            f"Report saved to: {output_file}"
        )

        print(
            "Top performer saved to: top_performer.csv"
        )

    except FileNotFoundError:
        print(
            f"Error: File not found: {input_file}"
        )

    except json.JSONDecodeError as error:
        print(
            f"Error: Invalid JSON file: {error}"
        )

    except (
        KeyError,
        ValueError,
        RuntimeError
    ) as error:
        print(
            f"Error: {error}"
        )


if __name__ == "__main__":
    main()
