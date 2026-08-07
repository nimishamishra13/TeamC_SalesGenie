import re

TECH_STACK = {
    "React": [r"\breact\b", r"reactjs"],
    "Angular": [r"\bangular\b"],
    "Vue": [r"\bvue\b"],
    "Node.js": [r"node\.?js", r"\bnode\b"],
    "Python": [r"\bpython\b", r"django", r"flask", r"fastapi"],
    "Java": [r"\bjava\b", r"spring"],
    ".NET": [r"\.net", r"asp\.net"],
    "AWS": [r"\baws\b", r"amazon web services"],
    "Azure": [r"\bazure\b"],
    "GCP": [r"google cloud", r"\bgcp\b"],
    "Docker": [r"\bdocker\b"],
    "Kubernetes": [r"kubernetes", r"\bk8s\b"],
    "MongoDB": [r"mongodb"],
    "PostgreSQL": [r"postgres"],
    "MySQL": [r"mysql"],
    "Redis": [r"redis"],
}

def detect_tech_stack(text):
    if not text:
        return []

    text = text.lower()
    detected = []

    for tech, patterns in TECH_STACK.items():
        for pattern in patterns:
            if re.search(pattern, text):
                detected.append(tech)
                break

    return detected
