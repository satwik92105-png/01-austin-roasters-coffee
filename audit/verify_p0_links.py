from bs4 import BeautifulSoup

paths = ['tier2/reserve.html', 'tier3/reserve.html']
target_ids = ['btn-add-calendar', 'btn-email-self', 'btn-add-calendar3', 'btn-email-self3']

all_valid = True
for path in paths:
    with open(path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    for tid in target_ids:
        el = soup.find(id=tid)
        if el:
            href = el.get('href', '')
            is_valid = bool(href and not href.startswith('#') and (href.startswith('https://') or href.startswith('mailto:')))
            print(f"[{'PASS' if is_valid else 'FAIL'}] {path} #{tid} -> {href}")
            if not is_valid:
                all_valid = False

if all_valid:
    print("ALL 4 RESERVATION LINKS SUCCESSFULLY VERIFIED!")
else:
    print("VALIDATION FAILED!")
    exit(1)
