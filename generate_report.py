import os
import json
import cv2
import pandas as pd


if __name__ == "__main__":

    # Set the base directory where sorted alerts are stored
    base_dir = "sorted_alerts"  # Change if needed
    date = "2025-04-13"  # Change to your desired date
    image_prefix = "images"  # Set the correct path where images are stored

    # Full path to the date's directory
    date_dir = os.path.join(base_dir, date)

    # Check if the date directory exists
    if not os.path.exists(date_dir):
        print(f"Error: Directory for {date} not found.")
        exit()

    # Dictionary to store images sorted by camera
    image_data = {}
    class_counts = {}

    # Read all camera directories
    for cam_id in sorted(os.listdir(date_dir)):  # Sorting cameras
        cam_dir = os.path.join(date_dir, cam_id)

        if os.path.isdir(cam_dir):
            image_data[cam_id] = []
            class_counts[cam_id] = {}

            # Read desk directories
            for desk in sorted(os.listdir(cam_dir)):  # Sorting desks
                desk_dir = os.path.join(cam_dir, desk)

                if os.path.isdir(desk_dir):
                    # Read all JSON files (each corresponds to a class title)
                    for json_file in sorted(os.listdir(desk_dir)):  # Sorting titles
                        if json_file.endswith(".json"):
                            class_name = json_file.replace("_", " ").replace(".json", "")
                            json_path = os.path.join(desk_dir, json_file)

                            # Load JSON data
                            with open(json_path, "r") as f:
                                alerts = json.load(f)

                            class_counts[cam_id][class_name] = class_counts[cam_id].get(class_name, 0) + len(alerts)

                            # Collect image paths and metadata
                            for alert in sorted(alerts, key=lambda x: x["alert_ID"]):  # Sorting alerts by timestamp
                                file_name = alert["file_name"] + ".jpg"  # Assuming image format is .jpg
                                img_path = os.path.join(image_prefix, file_name)
                                timestamp = alert["alert_ID"]

                                # Store in the correct camera group
                                image_data[cam_id].append((img_path, timestamp, class_name, desk, cam_id))

    # Print total counts per class for each camera
    print("\n### Alert Counts Per Camera ###")
    for cam, counts in class_counts.items():
        print(f"\n{cam}:")
        for title, count in counts.items():
            print(f"  {title}: {count}")

    # Flatten the sorted image list for sequential viewing
    image_list = []
    for cam_id in sorted(image_data.keys()):
        image_list.extend(image_data[cam_id])  # Append images sorted per camera

    # If no images found, exit
    if not image_list:
        print("\nNo images found to display.")
        exit()

    # DataFrame to store classifications
    results = pd.DataFrame(columns=["cam_id", "class_name", "desk", "timestamp", "TP", "FP", "Flag"])

    # Image Navigation
    index = 0
    while True:
        img_path, timestamp, class_name, desk, cam_id = image_list[index]

        # Load image
        img = cv2.imread(img_path)
        if img is None:
            print(f"Warning: Image not found {img_path}")
            index = (index + 1) % len(image_list)  # Skip missing images
            continue

        # Show image with timestamp and class title
        title = f"{class_name} | {timestamp} | {desk} | {cam_id}"

        filter = results[(results['timestamp']==timestamp) & (results['cam_id']==cam_id) & (results['desk']==desk)]
        if not filter.empty:
            myfilter = filter.iloc[0]
            if myfilter['TP']==1:
                cv2.putText(img, "TP", (70, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA) 
            elif myfilter['FP']==1:
                cv2.putText(img, "FP", (70, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA) 

        
        cv2.putText(img, "A: Prev, D: Next, T: TP, F: FP, Esc: Exit", (25,25), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2 , cv2.LINE_AA)
        # Frame resized.
        img_resized = cv2.resize(img, (800,500))
        cv2.imshow(title, img_resized)

        # Key controls
        flag = cv2.waitKey(0) & 0xFF  # Wait for key press
        key = flag

        # if flag in [ord('t'), ord('T')]:  # True Positive
        #     new_entry = pd.DataFrame([{ "cam_id": cam_id, "class_name": class_name, "desk": desk, "timestamp": timestamp, "TP": 1, "FP": 0 }])
        #     results = pd.concat([results, new_entry], ignore_index=True)
        #     print( f"-Entered {title} as {flag}. ")
        # elif flag in [ord('f'), ord('F')]:  # False Positive
        #     new_entry = pd.DataFrame([{ "cam_id": cam_id, "class_name": class_name, "desk": desk, "timestamp": timestamp, "TP": 0, "FP": 1 }])
        #     results = pd.concat([results, new_entry], ignore_index=True)
        #     print( f"-Entered {title} as {flag}. ")
        # elif flag in [ord('y'), ord('Y')]:  # True Positive + *
        #     new_entry = pd.DataFrame([{ "cam_id": cam_id, "class_name": class_name, "desk": desk, "timestamp": timestamp, "TP": 1, "FP": 0, "Flag": "*"}])
        #     results = pd.concat([results, new_entry], ignore_index=True)
        #     print( f"-Entered {title} as {flag}. ")
        # elif flag in [ord('g'), ord('G')]:  # False Positive + *
        #     new_entry = pd.DataFrame([{ "cam_id": cam_id, "class_name": class_name, "desk": desk, "timestamp": timestamp, "TP": 0, "FP": 1 ,"Flag": "*"}])
        #     results = pd.concat([results, new_entry], ignore_index=True)
        #     print( f"-Entered {title} as {flag}. ")

        if flag in [ord('t'), ord('T')]:  # True Positive
            results.loc[(results['timestamp'] == timestamp) & (results['cam_id'] == cam_id) & (results['desk'] == desk), ['TP', 'FP', 'Flag']] = [1, 0, None]
            if results[(results['timestamp'] == timestamp) & (results['cam_id'] == cam_id) & (results['desk'] == desk)].empty:
                new_entry = pd.DataFrame([{ "cam_id": cam_id, "class_name": class_name, "desk": desk, "timestamp": timestamp, "TP": 1, "FP": 0 }])
                results = pd.concat([results, new_entry], ignore_index=True)
            print(f"-Entered {title} as {flag}. ")
        elif flag in [ord('f'), ord('F')]:  # False Positive
            results.loc[(results['timestamp'] == timestamp) & (results['cam_id'] == cam_id) & (results['desk'] == desk), ['TP', 'FP', 'Flag']] = [0, 1, None]
            if results[(results['timestamp'] == timestamp) & (results['cam_id'] == cam_id) & (results['desk'] == desk)].empty:
                new_entry = pd.DataFrame([{ "cam_id": cam_id, "class_name": class_name, "desk": desk, "timestamp": timestamp, "TP": 0, "FP": 1 }])
                results = pd.concat([results, new_entry], ignore_index=True)
            print(f"-Entered {title} as {flag}. ")
        elif flag in [ord('y'), ord('Y')]:  # True Positive + *
            results.loc[(results['timestamp'] == timestamp) & (results['cam_id'] == cam_id) & (results['desk'] == desk), ['TP', 'FP', 'Flag']] = [1, 0, '*']
            if results[(results['timestamp'] == timestamp) & (results['cam_id'] == cam_id) & (results['desk'] == desk)].empty:
                new_entry = pd.DataFrame([{ "cam_id": cam_id, "class_name": class_name, "desk": desk, "timestamp": timestamp, "TP": 1, "FP": 0, "Flag": "*" }])
                results = pd.concat([results, new_entry], ignore_index=True)
            print(f"-Entered {title} as {flag}. ")
        elif flag in [ord('g'), ord('G')]:  # False Positive + *
            results.loc[(results['timestamp'] == timestamp) & (results['cam_id'] == cam_id) & (results['desk'] == desk), ['TP', 'FP', 'Flag']] = [0, 1, '*']
            if results[(results['timestamp'] == timestamp) & (results['cam_id'] == cam_id) & (results['desk'] == desk)].empty:
                new_entry = pd.DataFrame([{ "cam_id": cam_id, "class_name": class_name, "desk": desk, "timestamp": timestamp, "TP": 0, "FP": 1, "Flag": "*" }])
                results = pd.concat([results, new_entry], ignore_index=True)
            print(f"-Entered {title} as {flag}. ")

        elif key == 27:  # ESC key to exit
            cv2.destroyAllWindows()
            break
        elif key in [ord('a'), ord('A')]:  # Left arrow key (previous)
            index = (index - 1) % len(image_list)
            cv2.destroyAllWindows()
        elif key in [ord('d'), ord('D')]:  # Right arrow key (next)
            index = (index + 1) % len(image_list)
            cv2.destroyAllWindows()

    # Save results to CSV
    results.to_csv(f"reports/{date}_class_results.csv", index=False)
    print(f"Classification results saved to {date}_class_results.csv")

    cv2.destroyAllWindows()