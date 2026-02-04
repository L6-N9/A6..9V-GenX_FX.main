import csv
import os
from pathlib import Path


def verify_signal_format():
    signal_file = Path("signal_output/MT4_Signals.csv")

    if not signal_file.exists():
        print(f"❌ Signal file not found: {signal_file}")
        return False

    print(f"🔍 Verifying signal format for: {signal_file}")

    try:
        with open(signal_file, mode="r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)

            print(f"Header: {header}")

            # Expected header for new EA version
            # timestamp,symbol,action,entry_price,stop_loss,take_profit,confidence,reasoning,source
            expected_fields = 9
            if len(header) < 7:
                print(
                    f"❌ Error: Header has only {len(header)} fields, expected at least 7."
                )
                return False

            print(
                f"✅ Header has {len(header)} fields (expected at least 7 for the improved EA)."
            )

            row_count = 0
            for row in reader:
                row_count += 1
                if len(row) < 7:
                    print(f"❌ Row {row_count} has only {len(row)} fields.")
                    return False

                # Verify types
                try:
                    symbol = row[1]
                    action = row[2]
                    entry = float(row[3])
                    sl = float(row[4])
                    tp = float(row[5])
                    confidence = float(row[6])

                    if action not in ["BUY", "SELL", "HOLD"]:
                        print(
                            f"⚠️ Warning: Row {row_count} has unusual action: {action}"
                        )

                except ValueError as e:
                    print(f"❌ Row {row_count} has invalid numeric data: {e}")
                    return False

            print(f"✅ Successfully verified {row_count} signals.")
            return True

    except Exception as e:
        print(f"❌ An error occurred: {e}")
        return False


if __name__ == "__main__":
    if verify_signal_format():
        print("🚀 Signal format verification PASSED")
        exit(0)
    else:
        print("❌ Signal format verification FAILED")
        exit(1)
