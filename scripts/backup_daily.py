from pathlib import Path
from datetime import datetime
import shutil


# ==================================================
# Paths
# ==================================================

ROOT = Path(__file__).resolve().parent.parent

now = datetime.now()

date = now.strftime("%Y-%m-%d")
timestamp = now.strftime("%Y-%m-%d_%H%M%S")


SOURCE_OUTPUT = (
    ROOT
    / "output"
    / "daily"
    / date
)

SOURCE_DATA = (
    ROOT
    / "data"
    / "daily"
    / date
)


# ==================================================
# Backup destination
# ==================================================

BACKUP_ROOT = Path(
    r"D:\AP_Daily_Backup"
)

DESTINATION = (
    BACKUP_ROOT
    / timestamp
)


# ==================================================
# Copy helper
# ==================================================

def copy_folder(
    source: Path,
    destination: Path,
):

    if not source.exists():

        print(
            f"⚠️ 찾을 수 없습니다: "
            f"{source}"
        )

        return

    shutil.copytree(
        source,
        destination,
    )

    print()
    print(f"✅ {source}")
    print(f"   → {destination}")


# ==================================================
# Backup
# ==================================================

DESTINATION.mkdir(
    parents=True,
    exist_ok=False,
)


copy_folder(
    SOURCE_OUTPUT,
    DESTINATION / "output",
)


copy_folder(
    SOURCE_DATA,
    DESTINATION / "data",
)


# ==================================================
# Complete
# ==================================================

print()
print("====================================")
print("AP Daily Backup Complete")
print("====================================")
print()
print(f"DATE   : {date}")
print(f"BACKUP : {DESTINATION}")
print()