import json
import os
from collections import defaultdict

def load_alerts(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

def save_grouped_alerts(grouped_alerts, base_dir, date):
    for cam_id, desks in grouped_alerts.items():
        for desk, titles in desks.items():
            for title, alerts in titles.items():
                safe_title = title.replace(" ", "_")
                output_dir = os.path.join(base_dir, date, cam_id, str(desk))
                os.makedirs(output_dir, exist_ok=True)
                output_file = os.path.join(output_dir, f"{safe_title}.json")
                with open(output_file, "w") as f:
                    json.dump(alerts, f, indent=2)

def sort_and_group_alerts(alerts):
    grouped = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    for alert in alerts:
        date = alert["date"]
        cam_id = alert["cam_id"]
        for a in alert["alerts"]:
            desk = a["desk"]
            title = a["title"]
            grouped[cam_id][desk][title].append(alert)

    return grouped, date

if __name__ == "__main__":
    input_file = "06_03_2025_qiyas_multicam.alerts.json"   # 🔁 Your input file
    base_output_dir = "sorted_alerts"     # 🔁 Output directory

    alerts = load_alerts(input_file)
    grouped_alerts, date = sort_and_group_alerts(alerts)
    save_grouped_alerts(grouped_alerts, base_output_dir, date)

    print(f"Sorted and grouped alerts saved under '{base_output_dir}/{date}'")
