import requests
import json

base_url = "http://localhost:8000/api/v1"

# 1. Login to get token (using an admin account or existing user)
# I don't know the password, so I will bypass auth if possible, but POST /incidents/report doesn't require get_current_user in the route directly?
# Wait! Let's check incidents/routes/incident.py

