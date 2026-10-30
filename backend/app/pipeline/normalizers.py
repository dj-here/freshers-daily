import re
from typing import Optional, Tuple, List
from dataclasses import dataclass

@dataclass
class NormalizedLocation:
    is_valid_india: bool
    city: str
    state: Optional[str]
    is_remote: bool
    is_hybrid: bool
    rejection_reason: Optional[str] = None

# Known Indian Cities mapping to canonical representation
INDIAN_CITIES = {
    "bengaluru": ("Bengaluru", "Karnataka"),
    "bangalore": ("Bengaluru", "Karnataka"),
    "hyderabad": ("Hyderabad", "Telangana"),
    "secunderabad": ("Hyderabad", "Telangana"),
    "pune": ("Pune", "Maharashtra"),
    "gurgaon": ("Gurgaon", "Haryana"),
    "gurugram": ("Gurgaon", "Haryana"),
    "noida": ("Noida", "Uttar Pradesh"),
    "greater noida": ("Noida", "Uttar Pradesh"),
    "mumbai": ("Mumbai", "Maharashtra"),
    "navi mumbai": ("Mumbai", "Maharashtra"),
    "thane": ("Mumbai", "Maharashtra"),
    "chennai": ("Chennai", "Tamil Nadu"),
    "madras": ("Chennai", "Tamil Nadu"),
    "delhi": ("Delhi NCR", "Delhi"),
    "new delhi": ("Delhi NCR", "Delhi"),
    "ncr": ("Delhi NCR", "Delhi"),
    "kolkata": ("Kolkata", "West Bengal"),
    "calcutta": ("Kolkata", "West Bengal"),
    "ahmedabad": ("Ahmedabad", "Gujarat"),
    "coimbatore": ("Coimbatore", "Tamil Nadu"),
    "kochi": ("Kochi", "Kerala"),
    "cochin": ("Kochi", "Kerala"),
    "trivandrum": ("Trivandrum", "Kerala"),
    "thiruvananthapuram": ("Trivandrum", "Kerala"),
    "chandigarh": ("Chandigarh", "Punjab"),
    "mohali": ("Chandigarh", "Punjab"),
    "indore": ("Indore", "Madhya Pradesh"),
    "jaipur": ("Jaipur", "Rajasthan"),
    "bhubaneswar": ("Bhubaneswar", "Odisha"),
    "mysore": ("Mysuru", "Karnataka"),
    "mysuru": ("Mysuru", "Karnataka"),
    "nagpur": ("Nagpur", "Maharashtra"),
    "vadodara": ("Vadodara", "Gujarat"),
    "baroda": ("Vadodara", "Gujarat"),
    "surat": ("Surat", "Gujarat"),
    "vizag": ("Visakhapatnam", "Andhra Pradesh"),
    "visakhapatnam": ("Visakhapatnam", "Andhra Pradesh"),
    "lucknow": ("Lucknow", "Uttar Pradesh"),
    "mangalore": ("Mangaluru", "Karnataka"),
    "mangaluru": ("Mangaluru", "Karnataka"),
}

FOREIGN_LOCATIONS = [
    r"\b(usa|united states|us|uk|united kingdom|canada|germany|poland|singapore|australia|sydney|melbourne|london|berlin|tokyo|japan|netherlands|amsterdam|france|paris|ireland|dublin|israel|tel aviv|philippines|manila|brazil|mexico|spain|italy)\b"
]

def normalize_location(raw_location: str) -> NormalizedLocation:
    if not raw_location or not raw_location.strip():
        return NormalizedLocation(
            is_valid_india=False,
            city="",
            state=None,
            is_remote=False,
            is_hybrid=False,
            rejection_reason="Empty location"
        )

    text = raw_location.lower().strip()

    # Foreign exclusion check
    for pattern in FOREIGN_LOCATIONS:
        if re.search(pattern, text) and not re.search(r"\bindia\b", text):
            return NormalizedLocation(
                is_valid_india=False,
                city="",
                state=None,
                is_remote=False,
                is_hybrid=False,
                rejection_reason=f"Foreign location detected: {raw_location}"
            )

    is_remote = bool(re.search(r"\b(remote|work from home|wfh)\b", text))
    is_hybrid = bool(re.search(r"\b(hybrid)\b", text))

    # Match Indian Cities
    for city_key, (canonical_city, state) in INDIAN_CITIES.items():
        if re.search(r"\b" + re.escape(city_key) + r"\b", text):
            return NormalizedLocation(
                is_valid_india=True,
                city=canonical_city,
                state=state,
                is_remote=is_remote,
                is_hybrid=is_hybrid
            )

    # General India match (e.g. "India", "Remote - India")
    if "india" in text or "in" in text.split(","):
        if is_remote:
            return NormalizedLocation(
                is_valid_india=True,
                city="Remote - India",
                state=None,
                is_remote=True,
                is_hybrid=False
            )
        return NormalizedLocation(
            is_valid_india=True,
            city="Pan India",
            state=None,
            is_remote=is_remote,
            is_hybrid=is_hybrid
        )

    return NormalizedLocation(
        is_valid_india=False,
        city="",
        state=None,
        is_remote=is_remote,
        is_hybrid=is_hybrid,
        rejection_reason=f"Non-India or unverified location: {raw_location}"
    )

# Role Categories Allow-list
ROLE_CATEGORIES = {
    "Frontend": [r"\bfrontend\b", r"\breact\b", r"\bui developer\b", r"\bui engineer\b", r"\bweb developer\b", r"\bangular\b", r"\bvue\b"],
    "Backend": [r"\bbackend\b", r"\bnode\.?js\b", r"\bpython\b", r"\bjava developer\b", r"\bgolang\b", r"\bapi\b", r"\bserver\b", r"\bruby\b"],
    "Fullstack": [r"\bfull[\s-]?stack\b"],
    "Mobile": [r"\bmobile\b", r"\bandroid\b", r"\bios\b", r"\bflutter\b", r"\breact native\b"],
    "QA/SDET": [r"\bqa\b", r"\bsdet\b", r"\btest automation\b", r"\btesting\b", r"\bquality assurance\b", r"\bsoftware test\b"],
    "DevOps/Cloud": [r"\bdevops\b", r"\bcloud\b", r"\bsre\b", r"\bsite reliability\b", r"\binfrastructure\b", r"\bplatform engineer\b"],
    "Data Engineer": [r"\bdata engineer\b", r"\bbig data\b", r"\betl\b", r"\bdata platform\b"],
    "ML/AI": [r"\bmachine learning\b", r"\bml engineer\b", r"\bai engineer\b", r"\bnlp\b", r"\bcomputer vision\b", r"\bdeep learning\b", r"\bdata scientist\b"],
    "Security": [r"\bsecurity\b", r"\bcyber\b", r"\bappsec\b", r"\binfosec\b"],
    "GET/ASE": [r"\bgraduate engineer trainee\b", r"\bget\b", r"\bassociate software engineer\b", r"\base\b", r"\bassociate engineer\b", r"\btechnology analyst\b", r"\btrainee\b"],
    "SDE": [r"\bsde\b", r"\bsoftware (development )?engineer\b", r"\bsoftware developer\b", r"\bprogrammer\b", r"\bengineer - software\b"]
}

def classify_role_category(title: str, description: str = "") -> Tuple[str, float]:
    """Classifies job title and text into a software category and confidence score."""
    text = f"{title} {description}".lower()

    # Non-software exclusion checks
    non_software_patterns = [
        r"\bsales\b", r"\bbusiness development\b", r"\bbpo\b", r"\btelecaller\b",
        r"\bcontent writer\b", r"\bgraphic designer\b", r"\bmarketing\b", r"\bhr\b",
        r"\brecruiter\b", r"\baccountant\b", r"\bcustomer support\b", r"\boperations executive\b"
    ]
    for nsp in non_software_patterns:
        if re.search(nsp, title.lower()):
            return "NON_SOFTWARE", 0.0

    for category, patterns in ROLE_CATEGORIES.items():
        for pattern in patterns:
            if re.search(pattern, title.lower()):
                return category, 0.95

    # Check description if title is ambiguous (e.g. "Campus Intern" or "Associate")
    if re.search(r"\b(intern|campus|graduate)\b", title.lower()):
        for category, patterns in ROLE_CATEGORIES.items():
            for pattern in patterns:
                if re.search(pattern, description.lower()):
                    return category, 0.85
        return "GET/ASE", 0.80

    return "UNKNOWN", 0.30
