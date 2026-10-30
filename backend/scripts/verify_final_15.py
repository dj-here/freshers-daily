import httpx

urls = [
    # Cohort 2026
    ("Razorpay", "AI Builder", "https://job-boards.greenhouse.io/razorpaysoftwareprivatelimited/jobs/4744950005"),
    ("HackerRank", "DevOps Engineer II", "https://job-boards.greenhouse.io/hackerrank/jobs/7824249"),
    ("HackerRank", "SDET II", "https://job-boards.greenhouse.io/hackerrank/jobs/8155938"),
    ("CRED", "Cloud Security Engineer", "https://jobs.lever.co/cred/9a746e68-0858-4190-9144-54b19a2cbf2c"),
    ("CRED", "Threat Detection Engineer", "https://jobs.lever.co/cred/b3da0ae4-d0a8-45ce-a1e5-73be12b4bfe3"),
    # Cohort 2027
    ("Point72", "2027 SWE Campus - BHU", "https://boards.greenhouse.io/point72/jobs/8893940002?gh_jid=8893940002"),
    ("Point72", "2027 SWE Campus - Hyd", "https://boards.greenhouse.io/point72/jobs/8893936002?gh_jid=8893936002"),
    ("Point72", "2027 SWE Campus - Kanpur", "https://boards.greenhouse.io/point72/jobs/8893939002?gh_jid=8893939002"),
    ("Point72", "2027 SWE Campus - Madras", "https://boards.greenhouse.io/point72/jobs/8893935002?gh_jid=8893935002"),
    ("Enterpret", "SWE Intern (PPO Track)", "https://job-boards.greenhouse.io/enterpret/jobs/7847134003"),
    # Cohort 2028
    ("HackerRank", "SDE Intern", "https://job-boards.greenhouse.io/hackerrank/jobs/8229735"),
    ("HackerRank", "AI Researcher Intern", "https://job-boards.greenhouse.io/hackerrank/jobs/8281055"),
    ("Stripe", "Software Engineer Intern", "https://stripe.com/jobs/search?gh_jid=8031833"),
    ("GitLab", "Software Engineer, Delivery : Release", "https://job-boards.greenhouse.io/gitlab/jobs/8916232002"),
    ("Twilio", "Applications Engineer 2", "https://job-boards.greenhouse.io/twilio/jobs/7781659"),
]

client = httpx.Client(timeout=10.0, follow_redirects=True)

all_passed = True
for co, title, url in urls:
    res = client.get(url)
    status = res.status_code
    body = res.text.lower()
    is_live = status == 200 and 'page not found' not in body and 'job not found' not in body and 'job no longer' not in body
    print(f"{'[PASS 200]' if is_live else '[FAIL]'} {co} | {title} | Status: {status} | Final URL: {res.url}")
    if not is_live:
        all_passed = False

print(f"\nFinal Result: {'ALL 15 URLS VERIFIED 100% LIVE' if all_passed else 'SOME FAILED'}")
