import os

# ruleid: no-hardcoded-password
password = "fictional-training-value"

# ok: no-hardcoded-password
password = os.environ.get("TRAINING_PASSWORD")
