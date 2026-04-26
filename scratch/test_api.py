import requests
import json

base_url = "http://localhost:8000/api/v1"

# We need a token. We can get it by logging in.
# I'll just check if the endpoint works without token first? No, it needs current_user.
# I'll modify the backend to print the json in the terminal briefly, or I can just login if I know a password.
