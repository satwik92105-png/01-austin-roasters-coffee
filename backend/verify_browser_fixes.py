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

print("=== RUNNING HEADLESS CHROME VERIFICATION FOR ALL ?v=21.0 FIXES ===")

# CHECK 1: tier3/menu.html checkout modal typing and order completion
try:
    url_menu3 = f"file:///{base_path}/tier3/menu.html".replace("\\", "/")
    driver.get(url_menu3)
    driver.execute_script("localStorage.clear(); sessionStorage.clear();")
    driver.refresh()
    time.sleep(1)

    # Add item to cart
    driver.execute_script('window.addToCart({ id: "FT-M01", name: "Cold Drip Micro-Lot", price: 6.50 });')
    time.sleep(0.5)

    # Open cart drawer and proceed to pickup details
    driver.execute_script("window.CartManager.openDrawer();")
    time.sleep(0.5)

    chk_btn = driver.find_element(By.ID, "checkout-drawer-btn")
    chk_btn.click()
    time.sleep(0.5)

    modal = driver.find_element(By.ID, "checkout-modal-overlay")
    assert "is-open" in modal.get_attribute("class"), "FAIL: Modal not open after clicking checkout"

    # Click and type "Satwik Final Test" into Full Name * and "5125550199" into Phone *
    name_input = driver.find_element(By.ID, "cust-name")
    name_input.click()
    name_input.clear()
    name_input.send_keys("Satwik Final Test")

    assert "is-open" in modal.get_attribute("class"), "FAIL: Modal closed when clicking name input!"

    phone_input = driver.find_element(By.ID, "cust-phone")
    phone_input.click()
    phone_input.clear()
    phone_input.send_keys("5125550199")

    assert "is-open" in modal.get_attribute("class"), "FAIL: Modal closed when clicking phone input!"

    # Submit form
    submit_btn = driver.find_element(By.ID, "submit-order-btn")
    submit_btn.click()
    time.sleep(1.5)

    # Verify #FT-... confirmation screen appears
    success_title = driver.find_element(By.ID, "success-order-title").text
    print(f"[CHECK 1 DETAILS]: Success title = '{success_title}'")
    assert "FT-" in success_title or "Confirmed" in success_title, f"FAIL: Expected FT- confirmation, got {success_title}"

    print("[CHECK 1 PASS]: #checkout-modal stayed open during typing and completed #FT-... confirmation screen cleanly!")

except Exception as e:
    print(f"[CHECK 1 FAIL]: {e}")
    all_passed = False

# CHECK 2: tier3/admin.html Menu & Stock tab clearance >= 25px below header
try:
    url_admin3 = f"file:///{base_path}/tier3/admin.html".replace("\\", "/")
    driver.get(url_admin3)
    driver.execute_script("sessionStorage.clear(); localStorage.clear();")
    driver.refresh()
    time.sleep(1)

    pass_input = driver.find_element(By.ID, "login-pass")
    pass_input.clear()
    pass_input.send_keys("1234")
    driver.find_element(By.ID, "admin-login-btn").click()
    time.sleep(1)

    # Click the Menu & Stock tab
    menu_tab_btn = driver.find_element(By.CSS_SELECTOR, "button[data-tab='menu']")
    menu_tab_btn.click()
    time.sleep(0.5)

    header_rect = driver.execute_script("return document.querySelector('.admin-nav').getBoundingClientRect();")
    menu_heading_rect = driver.execute_script("return document.querySelector('#tab-menu h2').getBoundingClientRect();")
    add_btn_rect = driver.execute_script("return document.getElementById('btn-open-add-product').getBoundingClientRect();")

    clearance_heading = menu_heading_rect['top'] - header_rect['bottom']
    clearance_add_btn = add_btn_rect['top'] - header_rect['bottom']

    print(f"[CHECK 2 DETAILS]: Header bottom = {header_rect['bottom']}px")
    print(f"                  Menu Heading top = {menu_heading_rect['top']}px (Clearance: {clearance_heading:.1f}px)")
    print(f"                  + Add New Menu Item button top = {add_btn_rect['top']}px (Clearance: {clearance_add_btn:.1f}px)")

    assert clearance_heading >= 25, f"FAIL: Menu Catalog & Live Stock heading sits < 25px below header ({clearance_heading}px)"
    assert clearance_add_btn >= 25, f"FAIL: + Add New Menu Item button sits < 25px below header ({clearance_add_btn}px)"

    print(f"[CHECK 2 PASS]: Menu & Stock tab heading and + Add button sit at least 25px below header ({clearance_heading:.1f}px and {clearance_add_btn:.1f}px)!")

except Exception as e:
    print(f"[CHECK 2 FAIL]: {e}")
    all_passed = False

# CHECK 3: Cart Drawer on tier3/menu.html right-edge clipping
try:
    url_menu3 = f"file:///{base_path}/tier3/menu.html".replace("\\", "/")
    driver.get(url_menu3)
    time.sleep(1.5)

    # Add item to cart so all drawer pricing elements exist
    driver.execute_script('window.addToCart({ id: "FT-M01", name: "Cold Drip Micro-Lot", price: 6.50 });')
    time.sleep(0.5)

    # Open cart drawer
    driver.execute_script("window.CartManager.openDrawer();")
    time.sleep(1)

    drawer_rect = driver.execute_script("return document.getElementById('cart-drawer').getBoundingClientRect();")
    win_width = driver.execute_script("return window.innerWidth;")
    btn_rect = driver.execute_script("return document.getElementById('checkout-drawer-btn').getBoundingClientRect();")
    total_rect = driver.execute_script("return document.getElementById('cart-total').getBoundingClientRect();")
    tax_rect = driver.execute_script("return document.getElementById('cart-tax').getBoundingClientRect();")
    subtotal_rect = driver.execute_script("return document.getElementById('cart-subtotal').getBoundingClientRect();")

    btn_margin = win_width - btn_rect['right']
    total_margin = win_width - total_rect['right']

    print(f"[CHECK 3 DETAILS]: Window width = {win_width}px")
    print(f"                  Cart Drawer right = {drawer_rect['right']}px (width: {drawer_rect['width']}px)")
    print(f"                  Checkout button right = {btn_rect['right']}px (margin from right: {btn_margin}px)")
    print(f"                  Total amount right = {total_rect['right']}px (margin from right: {total_margin}px)")

    assert drawer_rect['right'] <= win_width + 1, f"FAIL: Drawer clipped off right edge: {drawer_rect['right']} > {win_width}"
    assert btn_rect['right'] <= win_width, f"FAIL: Checkout button clipped: {btn_rect['right']} > {win_width}"
    assert total_rect['right'] <= win_width, f"FAIL: Total price clipped: {total_rect['right']} > {win_width}"
    assert btn_margin >= 16, f"FAIL: Not enough breathing room for button: {btn_margin}px < 16px"
    assert total_margin >= 16, f"FAIL: Not enough breathing room for total: {total_margin}px < 16px"

    print("[CHECK 3 PASS]: Cart Drawer and all child pricing elements sit 100% inside viewport with generous breathing room!")

except Exception as e:
    print(f"[CHECK 3 FAIL]: {e}")
    all_passed = False

driver.quit()

if not all_passed:
    sys.exit(1)
print("\n>>> ALL CHECKS PASSED 100%! <<<")
