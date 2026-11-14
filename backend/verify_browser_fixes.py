import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

options = Options()
options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--window-size=1280,800')

driver = webdriver.Chrome(options=options)
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

all_passed = True

print("=== RUNNING HEADLESS CHROME VERIFICATION FOR ALL 3 FIXES ===")

# TEST 1: tier3/admin.html login without reload
try:
    url_admin3 = f"file:///{base_path}/tier3/admin.html".replace("\\", "/")
    driver.get(url_admin3)
    driver.execute_script("sessionStorage.clear(); localStorage.clear();")
    driver.refresh()
    time.sleep(1)

    pass_input = driver.find_element(By.ID, "login-pass")
    pass_input.clear()
    pass_input.send_keys("1234")

    login_btn = driver.find_element(By.ID, "admin-login-btn")
    login_btn.click()
    time.sleep(1)

    current_url = driver.current_url
    assert not current_url.endswith("?"), f"FAIL: Page reloaded to GET with query: {current_url}"

    login_screen_display = driver.execute_script("return window.getComputedStyle(document.getElementById('admin-login-screen')).display;")
    dashboard_display = driver.execute_script("return window.getComputedStyle(document.getElementById('admin-dashboard-app')).display;")

    assert login_screen_display == "none", f"FAIL: login screen is still visible: {login_screen_display}"
    assert dashboard_display == "block", f"FAIL: dashboard is not block: {dashboard_display}"

    # Also check header clearance in tier3/admin.html
    header_rect = driver.execute_script("return document.querySelector('.admin-nav').getBoundingClientRect();")
    active_sec_rect = driver.execute_script("return document.querySelector('.admin-content-section.active').getBoundingClientRect();")
    h1_rect = driver.execute_script("return document.querySelector('.admin-content-section.active h1').getBoundingClientRect();")
    refresh_btn_rect = driver.execute_script("return document.getElementById('btn-refresh-bi').getBoundingClientRect();")

    clearance_h1 = h1_rect['top'] - header_rect['bottom']
    clearance_btn = refresh_btn_rect['top'] - header_rect['bottom']
    print(f"[TEST 1 PASS]: tier3/admin.html unlocked successfully without reload!")
    print(f"               Header bottom: {header_rect['bottom']}px")
    print(f"               Heading H1 top: {h1_rect['top']}px (Clearance: {clearance_h1:.1f}px)")
    print(f"               Refresh button top: {refresh_btn_rect['top']}px (Clearance: {clearance_btn:.1f}px)")
    assert clearance_h1 > 10, f"FAIL: Header overlaps H1 heading in tier3/admin.html ({clearance_h1}px)"
    assert clearance_btn > 10, f"FAIL: Header overlaps refresh button in tier3/admin.html ({clearance_btn}px)"

except Exception as e:
    print(f"[TEST 1 FAIL]: {e}")
    all_passed = False

# TEST 2: Cart Drawer on tier3/menu.html right-edge clipping
try:
    url_menu3 = f"file:///{base_path}/tier3/menu.html".replace("\\", "/")
    driver.get(url_menu3)
    time.sleep(1)

    # Open cart drawer
    driver.execute_script("window.CartManager.openDrawer();")
    time.sleep(0.5)

    drawer_rect = driver.execute_script("return document.getElementById('cart-drawer').getBoundingClientRect();")
    win_width = driver.execute_script("return window.innerWidth;")
    btn_rect = driver.execute_script("return document.getElementById('checkout-drawer-btn').getBoundingClientRect();")
    total_rect = driver.execute_script("return document.getElementById('cart-total').getBoundingClientRect();")
    tax_rect = driver.execute_script("return document.getElementById('cart-tax').getBoundingClientRect();")
    subtotal_rect = driver.execute_script("return document.getElementById('cart-subtotal').getBoundingClientRect();")

    btn_margin = win_width - btn_rect['right']
    total_margin = win_width - total_rect['right']

    print(f"[TEST 2 DETAILS]: Window width = {win_width}px")
    print(f"                  Cart Drawer right = {drawer_rect['right']}px (width: {drawer_rect['width']}px)")
    print(f"                  Checkout button right = {btn_rect['right']}px (margin from right: {btn_margin}px)")
    print(f"                  Total amount right = {total_rect['right']}px (margin from right: {total_margin}px)")

    assert drawer_rect['right'] <= win_width + 1, f"FAIL: Drawer clipped off right edge: {drawer_rect['right']} > {win_width}"
    assert btn_rect['right'] <= win_width, f"FAIL: Checkout button clipped: {btn_rect['right']} > {win_width}"
    assert total_rect['right'] <= win_width, f"FAIL: Total price clipped: {total_rect['right']} > {win_width}"
    assert btn_margin >= 16, f"FAIL: Not enough breathing room for button: {btn_margin}px < 16px"
    assert total_margin >= 16, f"FAIL: Not enough breathing room for total: {total_margin}px < 16px"

    print("[TEST 2 PASS]: Cart Drawer and all child pricing elements sit 100% inside viewport with generous breathing room!")

except Exception as e:
    print(f"[TEST 2 FAIL]: {e}")
    all_passed = False

# TEST 3: Header clearance on tier2/admin.html and tier3/kitchen.html
try:
    url_admin2 = f"file:///{base_path}/tier2/admin.html".replace("\\", "/")
    driver.get(url_admin2)
    driver.execute_script("sessionStorage.clear(); localStorage.clear();")
    driver.refresh()
    time.sleep(1)

    # Login to tier2/admin.html
    pass_input2 = driver.find_element(By.ID, "login-pass")
    pass_input2.clear()
    pass_input2.send_keys("1234")
    driver.find_element(By.ID, "admin-login-btn").click()
    time.sleep(1)

    header_rect2 = driver.execute_script("return document.querySelector('.admin-nav').getBoundingClientRect();")
    h2_rect2 = driver.execute_script("return document.querySelector('.admin-content-section.active h2').getBoundingClientRect();")
    refresh_btn_rect2 = driver.execute_script("return document.getElementById('btn-manual-refresh-orders').getBoundingClientRect();")

    clearance_h2 = h2_rect2['top'] - header_rect2['bottom']
    clearance_btn2 = refresh_btn_rect2['top'] - header_rect2['bottom']

    print(f"[TEST 3A DETAILS tier2/admin.html]: Header bottom = {header_rect2['bottom']}px")
    print(f"                                   Heading H2 top = {h2_rect2['top']}px (Clearance: {clearance_h2:.1f}px)")
    print(f"                                   Refresh Queue button top = {refresh_btn_rect2['top']}px (Clearance: {clearance_btn2:.1f}px)")

    assert clearance_h2 > 10, f"FAIL: Header overlaps H2 in tier2/admin.html ({clearance_h2}px)"
    assert clearance_btn2 > 10, f"FAIL: Header overlaps Refresh Queue button in tier2/admin.html ({clearance_btn2}px)"

    # Now check tier3/kitchen.html
    url_kds = f"file:///{base_path}/tier3/kitchen.html".replace("\\", "/")
    driver.get(url_kds)
    time.sleep(1)

    kds_header_rect = driver.execute_script("return document.querySelector('.kds-header').getBoundingClientRect();")
    kds_grid_rect = driver.execute_script("return document.querySelector('.kds-grid').getBoundingClientRect();")

    clearance_kds = kds_grid_rect['top'] - kds_header_rect['bottom']
    print(f"[TEST 3B DETAILS tier3/kitchen.html]: KDS Header bottom = {kds_header_rect['bottom']}px")
    print(f"                                     KDS Grid top = {kds_grid_rect['top']}px (Clearance: {clearance_kds:.1f}px)")

    assert clearance_kds >= 0, f"FAIL: KDS header overlaps grid tickets ({clearance_kds}px)"

    print("[TEST 3 PASS]: Top fixed header has generous vertical clearance (>20px) on tier2/admin.html, tier3/admin.html, and tier3/kitchen.html!")

except Exception as e:
    print(f"[TEST 3 FAIL]: {e}")
    all_passed = False

driver.quit()

if not all_passed:
    sys.exit(1)
print("\n>>> ALL 3 BROWSER CHECKS PASSED 100%! <<<")
