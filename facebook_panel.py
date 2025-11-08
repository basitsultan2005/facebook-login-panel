import os
import sys
import time
import json
import re
import random
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class FacebookLoginPanel:
    def __init__(self):
        self.accounts_file = "accounts.txt"
        self.sessions_file = "sessions.json"
        self.results_file = "login_results.txt"
        self.successful_logins = 0
        self.failed_logins = 0

    def setup_browser_termux(self):
        """Setup Chrome browser for Termux"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=360,740')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36')

        try:
            driver = webdriver.Chrome(options=chrome_options)
            return driver
        except Exception as e:
            print(f"❌ Browser setup failed: {e}")
            return None

    def load_accounts(self):
        """Load accounts from file"""
        accounts = []
        try:
            with open(self.accounts_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if ':' in line:
                        email, password = line.split(':', 1)
                        accounts.append({
                            'email': email.strip(),
                            'password': password.strip(),
                            'status': 'pending'
                        })
            print(f"✅ Loaded {len(accounts)} accounts from {self.accounts_file}")
            return accounts
        except FileNotFoundError:
            print(f"❌ Accounts file '{self.accounts_file}' not found!")
            return []

    def login_facebook(self, account, thread_num=1):
        """Login to Facebook with single account"""
        print(f"🧵 Thread {thread_num}: Logging in {account['email']}")

        driver = self.setup_browser_termux()
        if not driver:
            account['status'] = 'failed'
            account['error'] = 'Browser setup failed'
            return account

        try:
            driver.get("https://www.facebook.com/login")
            time.sleep(3)

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "email"))
            )

            email_field = driver.find_element(By.ID, "email")
            email_field.clear()
            self.human_type(email_field, account['email'])
            time.sleep(1)

            password_field = driver.find_element(By.ID, "pass")
            password_field.clear()
            self.human_type(password_field, account['password'])
            time.sleep(1)

            login_button = driver.find_element(By.NAME, "login")
            login_button.click()
            time.sleep(5)

            if self.is_login_successful(driver):
                account['status'] = 'success'
                account['cookies'] = self.get_cookies(driver)
                account['login_time'] = time.strftime("%Y-%m-%d %H:%M:%S")
                self.successful_logins += 1
                print(f"✅ Thread {thread_num}: Login successful for {account['email']}")
                self.save_session(account)
            else:
                account['status'] = 'failed'
                account['error'] = 'Login failed - check credentials'
                self.failed_logins += 1
                print(f"❌ Thread {thread_num}: Login failed for {account['email']}")

        except Exception as e:
            account['status'] = 'failed'
            account['error'] = str(e)
            self.failed_logins += 1
            print(f"❌ Thread {thread_num}: Error for {account['email']}: {e}")

        finally:
            driver.quit()

        return account

    def is_login_successful(self, driver):
        try:
            if "facebook.com/home" in driver.current_url:
                return True
            if "Welcome" in driver.page_source:
                return True
            if driver.find_elements(By.XPATH, "//div[@role='feed']"):
                return True
            if driver.find_elements(By.XPATH, "//a[contains(@href, '/me/')]"):
                return True
            return False
        except:
            return False

    def get_cookies(self, driver):
        try:
            return driver.get_cookies()
        except:
            return []

    def human_type(self, element, text):
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.2))

    def save_session(self, account):
        try:
            sessions = self.load_sessions()
            sessions[account['email']] = {
                'cookies': account.get('cookies', []),
                'login_time': account.get('login_time', ''),
                'status': account['status']
            }
            with open(self.sessions_file, 'w', encoding='utf-8') as f:
                json.dump(sessions, f, indent=2)
        except Exception as e:
            print(f"❌ Error saving session: {e}")

    def load_sessions(self):
        try:
            with open(self.sessions_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}

    def bulk_login(self, accounts, max_threads=3):
        print(f"🚀 Starting bulk login for {len(accounts)} accounts...")
        print(f"🧵 Using {max_threads} parallel threads")

        self.successful_logins = 0
        self.failed_logins = 0
        results = []

        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            future_to_account = {
                executor.submit(self.login_facebook, account, i+1): account
                for i, account in enumerate(accounts)
            }

            for future in future_to_account:
                result = future.result()
                results.append(result)
                total = len(accounts)
                completed = len([r for r in results if r['status'] != 'pending'])
                print(f"📊 Progress: {completed}/{total} accounts processed")

        self.save_results(results)
        return results

    def save_results(self, results):
        with open(self.results_file, 'w', encoding='utf-8') as f:
            f.write("FACEBOOK LOGIN RESULTS\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total accounts: {len(results)}\n")
            f.write(f"Successful: {self.successful_logins}\n")
            f.write(f"Failed: {self.failed_logins}\n\n")

            for account in results:
                status_icon = "✅" if account['status'] == 'success' else "❌"
                f.write(f"{status_icon} {account['email']} - {account['status']}\n")
                if account['status'] == 'failed':
                    f.write(f"   Error: {account.get('error', 'Unknown error')}\n")

    def display_summary(self, results):
        successful = [acc for acc in results if acc['status'] == 'success']
        failed = [acc for acc in results if acc['status'] == 'failed']

        print("\n" + "=" * 50)
        print("📊 LOGIN SUMMARY")
        print("=" * 50)
        print(f"✅ Successful: {len(successful)}")
        print(f"❌ Failed: {len(failed)}")
        print(f"📝 Total: {len(results)}")

        if successful:
            print("\n✅ SUCCESSFUL ACCOUNTS:")
            for acc in successful:
                print(f"   📧 {acc['email']}")

        if failed:
            print("\n❌ FAILED ACCOUNTS:")
            for acc in failed:
                print(f"   📧 {acc['email']} - {acc.get('error', 'Unknown error')}")

    def create_accounts_template(self):
        if not os.path.exists(self.accounts_file):
            with open(self.accounts_file, 'w', encoding='utf-8') as f:
                f.write("# Add your Facebook accounts in format: email:password\n")
                f.write("# Example:\n")
                f.write("user1@gmail.com:password123\n")
                f.write("user2@yahoo.com:pass456\n")
            print(f"📁 Created accounts template: {self.accounts_file}")

def main():
    print("🔐 FACEBOOK AUTO LOGIN PANEL")
    print("=" * 50)

    panel = FacebookLoginPanel()
    panel.create_accounts_template()

    accounts = panel.load_accounts()
    if not accounts:
        print("❌ No accounts found! Please add accounts to accounts.txt")
        return

    try:
        threads = int(input("🧵 Enter number of parallel threads (1-5): ") or 3)
        threads = max(1, min(5, threads))
    except:
        threads = 3

    print(f"\n🚀 Starting login process with {threads} threads...")

    start_time = time.time()
    results = panel.bulk_login(accounts, threads)
    end_time = time.time()

    panel.display_summary(results)
    print(f"\n⏰ Total time: {end_time - start_time:.2f} seconds")
    print(f"📁 Results saved to: {panel.results_file}")
    print(f"💾 Sessions saved to: {panel.sessions_file}")

if __name__ == "__main__":
    main()
      
