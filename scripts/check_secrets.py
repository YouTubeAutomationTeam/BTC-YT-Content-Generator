import os

print("🔍 Listing available OAuth token environment variables:")
for name in os.environ:
    if name.endswith("_OAUTH_TOKEN_PICKLE_B64"):
        print(name)
