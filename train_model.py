import pandas as pd
import random
import os

print("Building base 10,000 row chunk...")

# Base lists
sender_domains_legit = ['vit.ac.in', 'linkedin.com', 'google.com', 'microsoft.com', 'github.com', 'amazon.com']
sender_domains_spam = ['deals.com', 'promo-hub.net', 'marketing.com', 'sales.co', 'offers-today.com', 'cheap-watches.net']
sender_domains_phish = ['fakebank.com', 'verify-acc.com', 'update-secure.net', 'alert-system.org', 'secure-login-gateway.net']

subjects_legit = ["Team Meeting Update", "Project Deadline", "Welcome to the new semester", "Your LinkedIn connections", "Weekly Sync", "Lunch today?", "Invoice attached for Q3", "Interview Schedule", "Git push notification"]
body_legit = [
    "Hi team, let's meet at 10 AM tomorrow to discuss the new features. Please bring the report.",
    "Dear Student, the academic calendar for this semester is attached.",
    "You have new profile views. Sincerely, the LinkedIn team.",
    "Please find attached the invoice for the last quarter software services.",
    "Are we still on for lunch at noon? Let me know.",
    "The pull request has been merged successfully."
]

subjects_spam = ["50% OFF everything!", "Save big on watches", "Your weekly newsletter is here", "Exclusive offer inside", "Last chance to claim discount", "Clearance sale starts today"]
body_spam = [
    "Huge discount happening right now! Buy now and save big! Click to view in browser. unsubscribe",
    "Read our latest news and updates regarding the upcoming products. opt out here.",
    "Get 50% off all watches if you buy today! Promo code inside. free shipping.",
    "Exclusive newsletter for our subscribers. Discover exactly what you missed."
]

subjects_phish = ["Urgent: Account Suspended", "Security Alert: Unauthorized Login", "Verify Your Identity", "Immediate Action Required", "Password expiring soon", "Update billing immediately"]
body_phish = [
    "Your bank account has detected an unauthorized login. Click here to verify your identity immediately.",
    "Immediate action required. Verify your billing or your account will be suspended within 24 hours.",
    "Your Microsoft 365 password expires in 2 hours. Update immediately.",
    "Warning: we detected suspicious activity. Please login to secure your funds now."
]

data = []

# Generate Legitimate (0) -> 5,000
for _ in range(5000):
    url = random.choice(["", f"http://{random.choice(sender_domains_legit)}/page", "http://docs.google.com/doc"])
    links = random.randint(0, 1)
    data.append({
        "subject": random.choice(subjects_legit),
        "body": random.choice(body_legit) + " " + random.choice(["Regards,", "Sincerely,", "Thanks!"]) + " " + random.choice(["Team", "Admin", "User"]),
        "url": url,
        "sender": f"{random.choice(['admin', 'hr', 'support', 'noreply', 'john'])}@{random.choice(sender_domains_legit)}",
        "link_count": links,
        "label": 0
    })

# Generate Spam (1) -> 3,000
for _ in range(3000):
    url = f"http://{random.choice(sender_domains_spam)}/promo"
    links = random.randint(2, 6)
    data.append({
        "subject": random.choice(subjects_spam) + " " + random.choice(["⚡", "🔥", ""]),
        "body": random.choice(body_spam) + " " + random.choice(["subscribe", "discount", "offer"]),
        "url": url,
        "sender": f"newsletter@{random.choice(sender_domains_spam)}",
        "link_count": links,
        "label": 1
    })

# Generate Phishing (2) -> 2,000
for _ in range(2000):
    ip_url = f"http://{random.randint(10, 255)}.{random.randint(10, 255)}.{random.randint(1,10)}.1/login"
    nested_url = f"http://secure-update-login-verify-account.{random.choice(sender_domains_phish)}/auth"
    url = random.choice([ip_url, nested_url])
    links = random.randint(1, 3)
    data.append({
        "subject": random.choice(subjects_phish),
        "body": random.choice(body_phish) + " update account password.",
        "url": url,
        "sender": f"security@{random.choice(sender_domains_phish)}",
        "link_count": links,
        "label": 2
    })

random.shuffle(data)
df = pd.DataFrame(data)

target_size_gb = 0.05 # 50 Megabytes
print(f"Executing high-speed Disk I/O IO loop targeting > {target_size_gb}GB Dataset Size...")

filename = "dataset.csv"
# Write header natively for the first chunk
df.to_csv(filename, index=False, mode='w', header=True)

iterations = 0
while True:
    iterations += 1
    # Rapid-append chunk to file natively
    df.to_csv(filename, index=False, mode='a', header=False)
    
    # Check size in MB iteratively
    current_size_mb = os.path.getsize(filename) / (1024 * 1024)
    if iterations % 50 == 0:
        print(f"Appended iteration {iterations}... Reached Disk Size: {current_size_mb:.2f} MB")
        
    if current_size_mb >= (target_size_gb * 1024):
        break

final_size = os.path.getsize(filename) / (1024 * 1024 * 1024)
print(f"Data generation completely finalized. Generated file size: {final_size:.2f} GB natively spanning {10000 * (iterations + 1)} logical rows!")
