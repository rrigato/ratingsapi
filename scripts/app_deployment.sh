detect-secrets scan | \
python3 -c "import sys, json; print(json.dumps(json.load(sys.stdin)['results'], indent=4))"