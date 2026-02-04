import json
import os
import sys


def main():
    print("Running License Checker...")
    report_path = os.path.join(os.getcwd(), "logs", "licenses", "license_report.json")
    if not os.path.exists(report_path):
        print(
            "Error: license_report.json not found. Please run the license-checker first.",
            file=sys.stderr,
        )
        sys.exit(1)

    with open(report_path, "r") as f:
        license_report = json.load(f)

    gpl_licenses = ["GPL", "AGPL", "LGPL"]
    gpl_dependencies = {}

    for dependency, details in license_report.items():
        licenses = details.get("licenses", [])
        if isinstance(licenses, list):
            for license in licenses:
                if any(gpl in license for gpl in gpl_licenses):
                    gpl_dependencies[dependency] = licenses
        else:
            if any(gpl in licenses for gpl in gpl_licenses):
                gpl_dependencies[dependency] = licenses

    if gpl_dependencies:
        print("Found GPL licensed dependencies:")
        print(json.dumps(gpl_dependencies, indent=2))
    else:
        print("No GPL licensed dependencies found.")


if __name__ == "__main__":
    main()
