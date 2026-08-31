import re

TECH_STACK = {

    # -----------------------------
    # Frontend
    # -----------------------------

    "React": [
        r"\breact\b",
        r"reactjs"
    ],

    "Angular": [
        r"\bangular\b"
    ],

    "Vue": [
        r"\bvue\b",
        r"vue\.js"
    ],

    # -----------------------------
    # Backend
    # -----------------------------

    "Node.js": [
        r"node\.?js",
        r"\bnode\b"
    ],

    "Python": [
        r"\bpython\b",
        r"django",
        r"flask",
        r"fastapi"
    ],

    "Java": [
        r"\bjava\b",
        r"spring"
    ],

    ".NET": [
        r"\.net",
        r"asp\.net"
    ],

    # -----------------------------
    # Cloud
    # -----------------------------

    "AWS": [
        r"\baws\b",
        r"amazon web services"
    ],

    "Azure": [
        r"\bazure\b"
    ],

    "GCP": [
        r"google cloud",
        r"\bgcp\b"
    ],

    # -----------------------------
    # DevOps / Infrastructure
    # -----------------------------

    "Docker": [
        r"\bdocker\b"
    ],

    "Kubernetes": [
        r"kubernetes",
        r"\bk8s\b"
    ],

    # -----------------------------
    # Databases
    # -----------------------------

    "MongoDB": [
        r"mongodb"
    ],

    "PostgreSQL": [
        r"postgres",
        r"postgresql"
    ],

    "MySQL": [
        r"mysql"
    ],

    "Redis": [
        r"\bredis\b"
    ],

    # -----------------------------
    # AI / ML
    # -----------------------------

    "Artificial Intelligence": [
        r"\bai\b",
        r"artificial intelligence",
        r"ai libraries"
    ],

    "Machine Learning": [
        r"\bmachine learning\b",
        r"\bml\b"
    ],

    "Deep Learning": [
        r"\bdeep learning\b"
    ],

    "PyTorch": [
        r"\bpytorch\b"
    ],

    "TensorFlow": [
        r"\btensorflow\b"
    ],

    "CUDA": [
        r"\bcuda\b"
    ],

    "Generative AI": [
        r"generative ai",
        r"genai"
    ],

    # -----------------------------
    # Data / Analytics
    # -----------------------------

    "Apache Spark": [
        r"apache spark",
        r"\bspark\b"
    ],

    "Hadoop": [
        r"\bhadoop\b"
    ],

    "Databricks": [
        r"\bdatabricks\b"
    ],
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
def get_tech_stack_match(analysis: dict) -> int:

    tech_stack = analysis.get("tech_stack", [])

    if not tech_stack:
        return 0

    weights = {

        # AI / ML
        "Artificial Intelligence": 20,
        "Machine Learning": 20,
        "Deep Learning": 20,
        "Generative AI": 20,
        "PyTorch": 18,
        "TensorFlow": 18,
        "CUDA": 18,

        # Cloud
        "AWS": 15,
        "Azure": 15,
        "GCP": 15,

        # Infrastructure
        "Kubernetes": 15,
        "Docker": 12,

        # Backend
        "Python": 10,
        "Java": 10,
        "Node.js": 8,

        # Frontend
        "React": 7,
        "Angular": 7,
        "Vue": 7,

        # Database
        "PostgreSQL": 7,
        "MongoDB": 7,
        "MySQL": 5,
        "Redis": 5,

        # Data
        "Apache Spark": 10,
        "Hadoop": 8,
        "Databricks": 10,
    }

    score = sum(
        weights.get(tech, 5)
        for tech in tech_stack
    )

    return min(score, 100)
