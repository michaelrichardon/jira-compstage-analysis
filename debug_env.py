import os
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("dotenv geladen")
except ImportError:
    print("dotenv nicht installiert")

print(f"CONFLUENCE_BASE_URL      = {os.environ.get('CONFLUENCE_BASE_URL','(nicht gesetzt)')}")
print(f"CONFLUENCE_PAT           = {'(gesetzt)' if os.environ.get('CONFLUENCE_PAT') else '(nicht gesetzt)'}")
print(f"CONFLUENCE_SPACE         = {os.environ.get('CONFLUENCE_SPACE','(nicht gesetzt)')}")
print(f"CONFLUENCE_PARENT_PAGE_ID= {os.environ.get('CONFLUENCE_PARENT_PAGE_ID','(nicht gesetzt)')}")
