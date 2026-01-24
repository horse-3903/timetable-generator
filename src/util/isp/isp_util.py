import json
import logging
import os
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


async def get_cookies() -> List[Dict[str, Any]]:
    cookies = None
    cookie_data = None

    if os.path.exists("./secrets/cookies.json"):
        with open("./secrets/cookies.json", "r") as f:
            cookie_data = f.read()

        cookies = json.loads(cookie_data)

        for c in cookies:
            same_site = c.get("sameSite")
            if not same_site:
                c["sameSite"] = "Lax"
                continue

            same_site_norm = str(same_site).strip().lower()
            if same_site_norm in ("strict", "lax", "none"):
                c["sameSite"] = same_site_norm.capitalize()
                continue

            mapping = {
                "no_restriction": "None",
                "unspecified": "Lax",
                "unspecified_method": "Lax",
            }
            c["sameSite"] = mapping.get(same_site_norm, "Lax")
    else:
        logger.warning("cookies.json not found; ISP requests will fail.")
    
    return cookies
