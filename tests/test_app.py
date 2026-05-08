import pytest
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = os.environ.get("BASE_URL", "http://localhost:3000")

# Unique test user so tests don't clash with existing data
TEST_EMAIL = "testuser_selenium@example.com"
TEST_PASS  = "TestPass123"
TEST_NAME  = "Selenium User"

def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(6)
    return driver

def signup_and_login(driver):
    """Helper: signs up (ignores duplicate error) then logs in."""
    driver.get(BASE_URL)
    driver.find_element(By.ID, "nameInput").clear()
    driver.find_element(By.ID, "nameInput").send_keys(TEST_NAME)
    driver.find_element(By.ID, "emailInput").clear()
    driver.find_element(By.ID, "emailInput").send_keys(TEST_EMAIL)
    driver.find_element(By.ID, "passwordInput").clear()
    driver.find_element(By.ID, "passwordInput").send_keys(TEST_PASS)
    driver.find_element(By.ID, "signupBtn").click()
    time.sleep(1)
    # If already exists, log in instead
    msg = driver.find_element(By.ID, "message").text
    if "already exists" in msg.lower():
        driver.find_element(By.ID, "emailInput").clear()
        driver.find_element(By.ID, "emailInput").send_keys(TEST_EMAIL)
        driver.find_element(By.ID, "passwordInput").clear()
        driver.find_element(By.ID, "passwordInput").send_keys(TEST_PASS)
        driver.find_element(By.ID, "loginBtn").click()
        time.sleep(1)

# ── Test 1: Page loads and title is correct ─────────────────────────
def test_01_page_title():
    driver = get_driver()
    driver.get(BASE_URL)
    assert driver.title == "Task Orbit"
    driver.quit()

# ── Test 2: Name input field is present ────────────────────────────
def test_02_name_input_present():
    driver = get_driver()
    driver.get(BASE_URL)
    field = driver.find_element(By.ID, "nameInput")
    assert field.is_displayed()
    driver.quit()

# ── Test 3: Email input field is present ───────────────────────────
def test_03_email_input_present():
    driver = get_driver()
    driver.get(BASE_URL)
    field = driver.find_element(By.ID, "emailInput")
    assert field.is_displayed()
    driver.quit()

# ── Test 4: Password input field is present ────────────────────────
def test_04_password_input_present():
    driver = get_driver()
    driver.get(BASE_URL)
    field = driver.find_element(By.ID, "passwordInput")
    assert field.is_displayed()
    driver.quit()

# ── Test 5: Sign Up button is present ──────────────────────────────
def test_05_signup_button_present():
    driver = get_driver()
    driver.get(BASE_URL)
    btn = driver.find_element(By.ID, "signupBtn")
    assert btn.is_displayed()
    driver.quit()

# ── Test 6: Login button is present ────────────────────────────────
def test_06_login_button_present():
    driver = get_driver()
    driver.get(BASE_URL)
    btn = driver.find_element(By.ID, "loginBtn")
    assert btn.is_displayed()
    driver.quit()

# ── Test 7: Signup with missing fields shows error ─────────────────
def test_07_signup_empty_fields_shows_error():
    driver = get_driver()
    driver.get(BASE_URL)
    driver.find_element(By.ID, "signupBtn").click()
    time.sleep(1)
    msg = driver.find_element(By.ID, "message").text
    assert len(msg) > 0  # some error message shown
    driver.quit()

# ── Test 8: Login with wrong credentials shows error ───────────────
def test_08_login_wrong_credentials():
    driver = get_driver()
    driver.get(BASE_URL)
    driver.find_element(By.ID, "emailInput").send_keys("wrong@wrong.com")
    driver.find_element(By.ID, "passwordInput").send_keys("wrongpass")
    driver.find_element(By.ID, "loginBtn").click()
    time.sleep(1)
    msg = driver.find_element(By.ID, "message").text
    assert len(msg) > 0
    driver.quit()

# ── Test 9: Successful signup logs user in ─────────────────────────
def test_09_signup_success():
    driver = get_driver()
    signup_and_login(driver)
    user_label = driver.find_element(By.ID, "userLabel").text
    assert "Not logged in" not in user_label
    driver.quit()

# ── Test 10: Task form becomes visible after login ─────────────────
def test_10_task_form_visible_after_login():
    driver = get_driver()
    signup_and_login(driver)
    task_form = driver.find_element(By.ID, "taskForm")
    assert task_form.is_displayed()
    driver.quit()

# ── Test 11: Task input field accepts text ─────────────────────────
def test_11_task_input_accepts_text():
    driver = get_driver()
    signup_and_login(driver)
    inp = driver.find_element(By.ID, "taskInput")
    inp.send_keys("My Selenium Task")
    assert inp.get_attribute("value") == "My Selenium Task"
    driver.quit()

# ── Test 12: Adding a task shows it in the list ────────────────────
def test_12_add_task_appears_in_list():
    driver = get_driver()
    signup_and_login(driver)
    driver.find_element(By.ID, "taskInput").send_keys("Buy groceries")
    driver.find_element(By.CSS_SELECTOR, "#taskForm button[type='submit']").click()
    time.sleep(1.5)
    task_list = driver.find_element(By.ID, "taskList").text
    assert "Buy groceries" in task_list
    driver.quit()

# ── Test 13: Task count label updates after adding ─────────────────
def test_13_count_label_updates():
    driver = get_driver()
    signup_and_login(driver)
    driver.find_element(By.ID, "taskInput").send_keys("Count test task")
    driver.find_element(By.CSS_SELECTOR, "#taskForm button[type='submit']").click()
    time.sleep(1.5)
    count_text = driver.find_element(By.ID, "countLabel").text
    assert "to-do" in count_text
    driver.quit()

# ── Test 14: Filter chip buttons are present ───────────────────────
def test_14_filter_chips_present():
    driver = get_driver()
    driver.get(BASE_URL)
    chips = driver.find_elements(By.CSS_SELECTOR, "[data-filter]")
    assert len(chips) == 3  # All, To-Do, Done
    driver.quit()

# ── Test 15: All filter chip is active by default ──────────────────
def test_15_all_filter_active_by_default():
    driver = get_driver()
    driver.get(BASE_URL)
    all_chip = driver.find_element(By.CSS_SELECTOR, "[data-filter='all']")
    assert "active" in all_chip.get_attribute("class")
    driver.quit()

# ── Test 16: Logout button hidden before login ─────────────────────
def test_16_logout_hidden_before_login():
    driver = get_driver()
    driver.get(BASE_URL)
    logout_btn = driver.find_element(By.ID, "logoutBtn")
    assert not logout_btn.is_displayed()
    driver.quit()

# ── Test 17: Logout button visible after login ─────────────────────
def test_17_logout_visible_after_login():
    driver = get_driver()
    signup_and_login(driver)
    logout_btn = driver.find_element(By.ID, "logoutBtn")
    assert logout_btn.is_displayed()
    driver.quit()

# ── Test 18: Logout resets user label ──────────────────────────────
def test_18_logout_resets_user():
    driver = get_driver()
    signup_and_login(driver)
    driver.find_element(By.ID, "logoutBtn").click()
    time.sleep(1)
    user_label = driver.find_element(By.ID, "userLabel").text
    assert "Not logged in" in user_label
    driver.quit()

# ── Test 19: Task form hidden after logout ─────────────────────────
def test_19_task_form_hidden_after_logout():
    driver = get_driver()
    signup_and_login(driver)
    driver.find_element(By.ID, "logoutBtn").click()
    time.sleep(1)
    task_form = driver.find_element(By.ID, "taskForm")
    assert not task_form.is_displayed()
    driver.quit()

# ── Test 20: Task list shows message when not logged in ────────────
def test_20_task_list_shows_login_prompt():
    driver = get_driver()
    driver.get(BASE_URL)
    task_list_text = driver.find_element(By.ID, "taskList").text
    assert "Log in" in task_list_text
    driver.quit()