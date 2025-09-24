import os
import csv
import shutil
from datetime import datetime

class PomeloStatusUpdater:
    def __init__(self, csv_path, class_folders, backups_path):
        self.csv_path = csv_path
        self.class_folders = class_folders
        self.backups_path = backups_path
        self.class_counters = {cls: 0 for cls in class_folders.keys()}
        self.not_found_images = []
        self.rows = []
        self.header = []
        self.csv_lookup = {}

    def make_backup(self):
        file_name = os.path.split(self.csv_path)[1]
        csv_name, extension = os.path.splitext(file_name)
        now = datetime.now()
        year = now.year
        month = str(now.month).zfill(2)
        day = str(now.day).zfill(2)
        hour = str(now.hour).zfill(2)
        minute = str(now.minute).zfill(2)
        second = str(now.second).zfill(2)
        csv_name = f"{csv_name}_backup_{year}{month}{day}{hour}{minute}{second}"
        new_path = os.path.join(self.backups_path, f"{csv_name}{extension}")
        os.makedirs(self.backups_path, exist_ok=True)
        shutil.copy2(self.csv_path, new_path)
        print(f"Backup created at: {new_path}")
        return new_path

    def load_csv(self):
        with open(self.csv_path, newline="", encoding="utf-8") as f:
            reader = list(csv.reader(f))
            self.header = reader[0]
            self.rows = reader[1:]  # skip header

        # Make dict for fast lookup (image_name -> row index)
        self.csv_lookup = {row[0]: i for i, row in enumerate(self.rows)}

        # Ensure header has at least 3 columns
        while len(self.header) < 3:
            self.header.append(f"col{len(self.header)+1}")

    def process_class_folders(self):
        for class_name, folder in self.class_folders.items():
            if not os.path.isdir(folder):
                print(f"Warning: folder '{folder}' not found. Skipping...")
                continue

            for file in os.listdir(folder):
                if not os.path.isfile(os.path.join(folder, file)):
                    continue

                image_name, _ = os.path.splitext(file)

                if image_name in self.csv_lookup:
                    row_index = self.csv_lookup[image_name]
                    row = self.rows[row_index]
                    while len(row) < 3:
                        row.append("")
                    if row[2] != class_name:
                        row[2] = class_name
                        self.class_counters[class_name] += 1
                else:
                    self.not_found_images.append(image_name)

    def save_csv(self):
        with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(self.header)
            writer.writerows(self.rows)

    def print_results(self):
        print("\n=== Rewrite Summary ===")
        for cls, count in self.class_counters.items():
            print(f"{cls}: {count} successful rewrites")

        if self.not_found_images:
            print("\n=== Images not found in CSV ===")
            for img in self.not_found_images:
                print(img)
        else:
            print("\nNo missing images.")

    def run(self):
        self.make_backup()
        self.load_csv()
        self.process_class_folders()
        self.save_csv()
        self.print_results()


def main():
    csv_path = r"dataset\tracker\tracker.csv"
    class_folders = {
        "Extracted": r"dataset\pomelo_images\extracted",
        "Incorrect": r"dataset\pomelo_images\incorrect",
        "Partial": r"dataset\pomelo_images\partial",
        "Unusable": r"dataset\pomelo_images\unusable",
        "Processed": r"dataset\pomelo_images\processed",
    }
    backups_path = r"dataset\tracker\backups"

    updater = PomeloStatusUpdater(csv_path, class_folders, backups_path)
    updater.run()


if __name__ == "__main__":
    main()
