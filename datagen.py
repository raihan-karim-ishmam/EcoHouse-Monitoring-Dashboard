import argparse
import os
import time
from datetime import datetime, timezone

import numpy as np
import pandas as pd


def ensure_parent_dir(path: str) -> None:
    parent = os.path.dirname(path)
    if parent and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)


def init_csv_if_missing(csv_path: str) -> None:
    if os.path.exists(csv_path):
        return

    ensure_parent_dir(csv_path)
    df = pd.DataFrame(columns=["timestamp", "temperature_c", "power_w"])
    df.to_csv(csv_path, index=False)


def generate_next_row(
    t: float,
    base_temp: float,
    base_power: float,
    temp_noise: float,
    power_noise: float,
) -> dict:
    """
    Generates a plausible ecohouse-like signal:
    - temperature: slow wave + noise
    - power: wave + occasional spikes + noise
    """
    # Slow daily-ish wave (compressed for demo)
    temp = base_temp + 2.5 * np.sin(t / 35.0) + np.random.normal(0, temp_noise)

    # Power has more variation
    power = base_power + 180 * np.sin(t / 12.0) + np.random.normal(0, power_noise)

    # Random spikes (e.g., kettle / AC switching)
    if np.random.rand() < 0.08:
        power += np.random.uniform(250, 700)

    # Random dips (e.g., PV drop / load off)
    if np.random.rand() < 0.05:
        power -= np.random.uniform(150, 400)

    # Clamp to reasonable ranges
    temp = float(np.clip(temp, 10, 55))
    power = float(np.clip(power, 0, 6000))

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "temperature_c": round(temp, 2),
        "power_w": round(power, 1),
    }


def append_row(csv_path: str, row: dict) -> None:
    # Append without reading the entire file
    pd.DataFrame([row]).to_csv(csv_path, mode="a", header=False, index=False)


def main():
    parser = argparse.ArgumentParser(description="Dummy live data generator for Ecohouse monitoring.")
    parser.add_argument("--csv", default="data/live_data.csv", help="Path to CSV file.")
    parser.add_argument("--interval", type=float, default=2.0, help="Seconds between updates.")
    parser.add_argument("--base-temp", type=float, default=28.0, help="Base temperature (C).")
    parser.add_argument("--base-power", type=float, default=900.0, help="Base power (W).")
    parser.add_argument("--temp-noise", type=float, default=0.25, help="Temperature noise std.")
    parser.add_argument("--power-noise", type=float, default=40.0, help="Power noise std.")
    parser.add_argument("--max-rows", type=int, default=0, help="Stop after N rows (0 = run forever).")
    args = parser.parse_args()

    init_csv_if_missing(args.csv)

    print(f"Writing live data to: {args.csv}")
    print(f"Update interval: {args.interval} seconds")
    print("Press Ctrl+C to stop.\n")

    t = 0.0
    rows_written = 0

    try:
        while True:
            row = generate_next_row(
                t=t,
                base_temp=args.base_temp,
                base_power=args.base_power,
                temp_noise=args.temp_noise,
                power_noise=args.power_noise,
            )
            append_row(args.csv, row)

            rows_written += 1
            if rows_written % 10 == 0:
                print(f"Wrote {rows_written} rows. Latest: {row}")

            if args.max_rows > 0 and rows_written >= args.max_rows:
                print("Reached max rows, stopping.")
                break

            t += 1.0
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()