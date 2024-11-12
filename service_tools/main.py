import os
import sys
import argparse
import subprocess
import time

from ayon_api.constants import (
    DEFAULT_VARIANT_ENV_KEY,
)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ADDON_DIR = os.path.dirname(CURRENT_DIR)


def run_all():
    all_idx = sys.argv.index("all")
    leecher_args = list(sys.argv)
    processor_args = list(sys.argv)
    transmitter_args = list(sys.argv)

    leecher_args[all_idx] = "leecher"
    processor_args[all_idx] = "processor"
    transmitter_args[all_idx] = "ayontof"

    leecher_args.insert(0, sys.executable)
    processor_args.insert(0, sys.executable)
    transmitter_args.insert(0, sys.executable)

    leecher = subprocess.Popen(leecher_args)
    processor = subprocess.Popen(processor_args)
    transmitter = subprocess.Popen(transmitter_args)
    processes = [leecher, processor, transmitter]
    try:
        while True:
            any_died = False
            for process in processes:
                if process.poll() is not None:
                    any_died = True
                    break

            if any_died:
                all_died = True
                for process in processes:
                    if process.poll() is None:
                        process.kill()
                        all_died = False

                if all_died:
                    break

            time.sleep(0.1)
    finally:
        for process in processes:
            if process.poll() is None:
                process.kill()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--service",
        help="Run processor service",
        choices=["processor", "leecher", "transmitter", "all"],
    )
    parser.add_argument(
        "--variant",
        default="production",
        help="Settings variant",
    )
    opts = parser.parse_args()
    if opts.variant:
        os.environ[DEFAULT_VARIANT_ENV_KEY] = opts.variant

    # Set download root for service tools inside service tools
    download_root = os.getenv("AYON_FTRACK_DOWNLOAD_ROOT")
    if not download_root:
        os.environ["AYON_FTRACK_DOWNLOAD_ROOT"] = os.path.join(
            CURRENT_DIR, "downloads"
        )

    service_name = opts.service
    if service_name == "all":
        return run_all()

    for path in (
        os.path.join(ADDON_DIR, "client", "ayon_ftrack"),
        os.path.join(ADDON_DIR, "services", service_name),
        os.path.join(ADDON_DIR),
    ):
        sys.path.insert(0, path)

    # Fix 'ftrack_common' import
    import common
    import common.event_handlers
    sys.modules["ftrack_common"] = common
    sys.modules["ftrack_common.event_handlers"] = common.event_handlers

    if service_name == "processor":
        from processor import main as service_main
    elif service_name == "leecher":
        from leecher import main as service_main
    elif service_name == "transmitter":
        from transmitter import main as service_main
    else:
        raise ValueError(f"Unknown service name {service_name}")

    service_main()


if __name__ == "__main__":
    main()
