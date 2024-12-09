import os

import pyblish.api

try:
    from ayon_core.pipeline.publish import FARM_JOB_ENV_DATA_KEY
except ImportError:
    # NOTE Can be removed when ayon-core >= 1.0.10 is required in package.py
    FARM_JOB_ENV_DATA_KEY = "farmJobEnv"


class CollectFtrackJobEnvVars(pyblish.api.ContextPlugin):
    """Collect set of environment variables to submit with deadline jobs"""
    order = pyblish.api.CollectorOrder - 0.45
    label = "Collect ftrack farm environment variables"
    targets = ["local"]

    def process(self, context):
        env = context.data.setdefault(FARM_JOB_ENV_DATA_KEY, {})
        for key in [
            "FTRACK_SERVER",
            "FTRACK_API_USER",
            "FTRACK_API_KEY",
        ]:
            value = os.getenv(key)
            if value:
                self.log.debug(f"Setting job env: {key}: {value}")
                env[key] = value
