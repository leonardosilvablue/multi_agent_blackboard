from autogen_core.tools import FunctionTool
import random
from typing import List, Dict

# Mock data for Python developers
MOCK_PROFILES = [
    {
        "name": "Ana Silva",
        "title": "Senior Python Developer",
        "experience": "8 years",
        "skills": ["Python", "Django", "FastAPI", "AWS", "Docker"],
        "current_company": "Tech Solutions Inc.",
        "location": "São Paulo, Brazil",
        "education": "Computer Science - USP",
    },
    {
        "name": "Pedro Santos",
        "title": "Python Backend Engineer",
        "experience": "5 years",
        "skills": ["Python", "Flask", "PostgreSQL", "Redis", "Kubernetes"],
        "current_company": "Digital Innovations",
        "location": "Rio de Janeiro, Brazil",
        "education": "Software Engineering - PUC-Rio",
    },
    {
        "name": "Mariana Costa",
        "title": "Full Stack Python Developer",
        "experience": "6 years",
        "skills": ["Python", "React", "MongoDB", "Node.js", "GraphQL"],
        "current_company": "Startup XYZ",
        "location": "Florianópolis, Brazil",
        "education": "Computer Engineering - UFSC",
    },
    {
        "name": "Lucas Oliveira",
        "title": "Python Data Engineer",
        "experience": "4 years",
        "skills": ["Python", "Pandas", "Spark", "Airflow", "GCP"],
        "current_company": "Data Corp",
        "location": "Belo Horizonte, Brazil",
        "education": "Data Science - UFMG",
    },
    {
        "name": "Julia Mendes",
        "title": "Python Tech Lead",
        "experience": "7 years",
        "skills": ["Python", "FastAPI", "Microservices", "Azure", "CI/CD"],
        "current_company": "Cloud Systems",
        "location": "Curitiba, Brazil",
        "education": "Systems Engineering - UTFPR",
    },
]


async def search_profiles(
    role: str = "Python Developer", experience_years: int = 0
) -> List[Dict]:
    """
    Search for professional profiles on LinkedIn (mock).

    Args:
        role: The job role to search for
        experience_years: Minimum years of experience required

    Returns:
        List of matching professional profiles
    """
    # In a real implementation, this would actually search LinkedIn
    filtered_profiles = [
        profile
        for profile in MOCK_PROFILES
        if int(profile["experience"].split()[0]) >= experience_years
    ]
    return filtered_profiles


async def get_profile_details(profile_name: str) -> Dict:
    """
    Get detailed information about a specific profile (mock).

    Args:
        profile_name: Name of the professional to look up

    Returns:
        Detailed profile information
    """
    # In a real implementation, this would fetch actual LinkedIn profile details
    for profile in MOCK_PROFILES:
        if profile["name"] == profile_name:
            return profile
    return {"error": "Profile not found"}


async def check_profile_availability(profile_name: str) -> Dict:
    """
    Check if a profile is open to work opportunities (mock).

    Args:
        profile_name: Name of the professional to check

    Returns:
        Availability status and additional information
    """
    # In a real implementation, this would check actual LinkedIn profile status
    statuses = ["Open to work", "Not looking", "Open to opportunities"]
    return {
        "name": profile_name,
        "status": random.choice(statuses),
        "response_rate": f"{random.randint(70, 99)}%",
        "last_active": "Recently active",
    }


# Create the tool instances
search_profiles_tool = FunctionTool(
    name="search_profiles",
    description="Search for professional profiles on LinkedIn",
    func=search_profiles,
)

get_profile_details_tool = FunctionTool(
    name="get_profile_details",
    description="Get detailed information about a specific profile on LinkedIn",
    func=get_profile_details,
)

check_profile_availability_tool = FunctionTool(
    name="check_profile_availability",
    description="Check if a LinkedIn profile is open to work opportunities",
    func=check_profile_availability,
)
