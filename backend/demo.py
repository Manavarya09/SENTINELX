"""
Demo script for SentinelX
Populates database with realistic mock data for demonstration.
"""

import asyncio
import random
from datetime import datetime, timedelta
from app.database import init_db, get_db
from app.models.user import User
from app.models.request import RequestLog
from app.models.attack import Attack
from app.models.ip_reputation import IPReputation
from app.models.alert import Alert
from app.auth.jwt import JWTService

# Mock data generators
ATTACK_TYPES = ["sqli", "xss", "path_traversal", "brute_force", "rate_abuse"]
SEVERITIES = ["low", "medium", "high", "critical"]
COUNTRIES = [
    ("United States", "US", 40.7128, -74.0060),
    ("China", "CN", 39.9042, 116.4074),
    ("Russia", "RU", 55.7558, 37.6173),
    ("Germany", "DE", 52.5200, 13.4050),
    ("India", "IN", 28.7041, 77.1025),
    ("Brazil", "BR", -23.5505, -46.6333),
    ("Japan", "JP", 35.6762, 139.6503),
    ("United Kingdom", "GB", 51.5074, -0.1278),
]

MOCK_ATTACKS = {
    "sqli": {
        "payloads": [
            "1' OR '1'='1",
            "admin'--",
            "1; DROP TABLE users--",
            "UNION SELECT username, password FROM users",
        ],
        "explanations": [
            "Classic SQL injection with tautology",
            "Comment-based injection to bypass authentication",
            "DROP TABLE attack attempting data destruction",
            "UNION-based injection for data exfiltration"
        ]
    },
    "xss": {
        "payloads": [
            "<script>alert('XSS')</script>",
            "javascript:alert(document.cookie)",
            "<img src=x onerror=alert(1)>",
            "<iframe src='javascript:alert(1)'></iframe>",
        ],
        "explanations": [
            "Basic script tag injection",
            "JavaScript URL scheme exploitation",
            "Image onerror event handler injection",
            "Iframe with JavaScript URL"
        ]
    },
    "path_traversal": {
        "payloads": [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "/var/www/html/../../../etc/shadow",
        ],
        "explanations": [
            "Unix directory traversal to passwd file",
            "Windows SAM file access attempt",
            "URL-encoded directory traversal",
            "Web root traversal to shadow file"
        ]
    },
    "brute_force": {
        "payloads": [
            "admin/admin123",
            "root/password",
            "user/123456",
            "test/test123",
        ],
        "explanations": [
            "Common admin credential attempt",
            "Default root password guess",
            "Weak password pattern",
            "Dictionary-based password attempt"
        ]
    },
    "rate_abuse": {
        "payloads": [
            "/api/login (100 requests/min)",
            "/api/search (500 requests/min)",
            "/api/download (200 requests/min)",
            "/api/export (300 requests/min)",
        ],
        "explanations": [
            "Excessive login attempts per minute",
            "Search endpoint abuse",
            "Download rate limiting bypass attempt",
            "Data export flooding"
        ]
    }
}

async def create_demo_user():
    """Create a demo admin user."""
    async for db in get_db():
        try:
            # Check if user exists
            existing = await db.execute(
                select(User).where(User.username == "admin")
            )
            if existing.scalar_one_or_none():
                print("Demo user already exists")
                return

            # Create demo user
            hashed_password = JWTService.hash_password("admin123")
            demo_user = User(
                username="admin",
                email="admin@sentinelx.com",
                hashed_password=hashed_password,
                role="admin"
            )

            db.add(demo_user)
            await db.commit()
            print("Created demo user: admin/admin123")

        except Exception as e:
            await db.rollback()
            print(f"Error creating demo user: {e}")

async def generate_mock_requests(count: int = 1000):
    """Generate mock HTTP requests with some attacks."""
    async for db in get_db():
        try:
            print(f"Generating {count} mock requests...")

            for i in range(count):
                # Generate random IP
                ip = f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"

                # Decide if this is an attack (20% chance)
                is_attack = random.random() < 0.2

                # Generate request data
                methods = ["GET", "POST", "PUT", "DELETE"]
                method = random.choice(methods)

                paths = [
                    "/api/login",
                    "/api/search",
                    "/api/users",
                    "/api/products",
                    "/admin/dashboard",
                    "/api/orders",
                    "/files/download",
                    "/api/comments"
                ]
                path = random.choice(paths)

                # Add query parameters sometimes
                if random.random() < 0.3:
                    path += f"?id={random.randint(1,100)}&page={random.randint(1,10)}"

                # Create request log
                request_log = RequestLog(
                    ip_address=ip,
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    method=method,
                    path=path,
                    query_string=path.split('?')[1] if '?' in path else "",
                    headers='{"user-agent": "Mozilla/5.0", "accept": "application/json"}',
                    body="" if method == "GET" else '{"username": "test", "password": "test"}',
                    is_attack=is_attack,
                    response_status=random.choice([200, 201, 400, 401, 403, 404, 500]),
                    response_time=random.uniform(0.1, 2.0)
                )

                db.add(request_log)
                await db.flush()  # Get ID

                # If it's an attack, create attack record
                if is_attack:
                    attack_type = random.choice(ATTACK_TYPES)
                    confidence = random.uniform(0.3, 0.95)
                    severity = random.choice(SEVERITIES)

                    # Get mock data for this attack type
                    attack_data = MOCK_ATTACKS.get(attack_type, MOCK_ATTACKS["sqli"])
                    payload = random.choice(attack_data["payloads"])
                    explanation = random.choice(attack_data["explanations"])

                    # Calculate risk score
                    risk_score = min(confidence * 100 * random.uniform(0.8, 1.5), 100)

                    attack = Attack(
                        request_id=request_log.id,
                        attack_type=attack_type,
                        severity=severity,
                        confidence=confidence,
                        explanation=explanation,
                        payload=payload,
                        matched_patterns='["test_pattern"]',
                        risk_factors='{"frequency": 1, "complexity": 0.5}',
                        base_score=confidence * 100,
                        final_risk_score=risk_score
                    )

                    db.add(attack)

                    # Update request log
                    request_log.attack_type = attack_type
                    request_log.confidence_score = confidence
                    request_log.risk_score = risk_score

                # Update IP reputation
                await update_ip_reputation(db, ip, is_attack)

                if (i + 1) % 100 == 0:
                    print(f"Generated {i + 1}/{count} requests...")
                    await db.commit()  # Commit in batches

            await db.commit()
            print(f"Successfully generated {count} mock requests")

        except Exception as e:
            await db.rollback()
            print(f"Error generating mock requests: {e}")

async def update_ip_reputation(db, ip_address: str, had_attack: bool):
    """Update or create IP reputation record."""
    try:
        # Check if IP exists
        existing = await db.execute(
            select(IPReputation).where(IPReputation.ip_address == ip_address)
        )
        ip_rep = existing.scalar_one_or_none()

        if not ip_rep:
            # Create new record
            country_data = random.choice(COUNTRIES)
            ip_rep = IPReputation(
                ip_address=ip_address,
                country=country_data[1],
                latitude=country_data[2],
                longitude=country_data[3],
                total_requests=1,
                attack_count=1 if had_attack else 0,
                reputation_score=random.uniform(0, 30) if not had_attack else random.uniform(40, 80)
            )
            db.add(ip_rep)
        else:
            # Update existing
            ip_rep.total_requests += 1
            if had_attack:
                ip_rep.attack_count += 1
                ip_rep.reputation_score = min(ip_rep.reputation_score + 5, 100)

    except Exception as e:
        print(f"Error updating IP reputation for {ip_address}: {e}")

async def generate_mock_alerts(count: int = 20):
    """Generate mock security alerts."""
    async for db in get_db():
        try:
            print(f"Generating {count} mock alerts...")

            alert_templates = [
                {
                    "title": "High-Risk SQL Injection Detected",
                    "message": "Multiple SQL injection attempts from IP {ip} targeting {path}",
                    "severity": "high"
                },
                {
                    "title": "XSS Attack Pattern Identified",
                    "message": "Cross-site scripting payload detected in request to {path}",
                    "severity": "medium"
                },
                {
                    "title": "Brute Force Login Attempts",
                    "message": "Excessive failed login attempts from IP {ip}",
                    "severity": "high"
                },
                {
                    "title": "Path Traversal Attempt",
                    "message": "Directory traversal attack blocked from {ip}",
                    "severity": "critical"
                },
                {
                    "title": "Rate Limit Exceeded",
                    "message": "IP {ip} exceeded rate limit on {path}",
                    "severity": "low"
                }
            ]

            for i in range(count):
                template = random.choice(alert_templates)
                ip = f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"
                path = random.choice(["/api/login", "/api/search", "/admin", "/files"])

                alert = Alert(
                    title=template["title"],
                    message=template["message"].format(ip=ip, path=path),
                    alert_type="attack_detected",
                    severity=template["severity"]
                )

                db.add(alert)

            await db.commit()
            print(f"Successfully generated {count} mock alerts")

        except Exception as e:
            await db.rollback()
            print(f"Error generating mock alerts: {e}")

async def main():
    """Main demo setup function."""
    print("Setting up SentinelX demo data...")

    # Initialize database
    await init_db()

    # Create demo user
    await create_demo_user()

    # Generate mock data
    await generate_mock_requests(500)  # Generate 500 requests
    await generate_mock_alerts(15)     # Generate 15 alerts

    print("Demo setup complete!")
    print("\nDemo Statistics:")
    print("- Created admin user: admin/admin123")
    print("- Generated 500 mock HTTP requests")
    print("- Included ~100 attack attempts")
    print("- Created 15 security alerts")
    print("- Populated IP reputation data")
    print("\n🌐 Access the application:")
    print("- Frontend: http://localhost:3000")
    print("- Backend API: http://localhost:8000")
    print("- API Docs: http://localhost:8000/docs")

if __name__ == "__main__":
    asyncio.run(main())