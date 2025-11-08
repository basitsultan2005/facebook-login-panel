# facebook_panel.py
# Simple local secret check: password is stored locally in .secret (not in code)

import os
import time
import json
import random
import getpass
from concurrent.futures import ThreadPoolExecutor
# selenium imports left in but if you only test password part it's ok
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class FacebookLoginPanel:
    def __init__(self):
        self.accounts_file = "accounts.txt"
        self.sessions_file = "sessions.json"
        self.results_file = "login_results.txt"
        self.successful_logins = 0
        self.failed_logins = 0

    # minimal browser setup (may need changes on Termux)
    def setup_browser_termux(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=360,740')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Linux; Android 10)')
        try:
            driver = webdriver.Chrome(options=chrome_options)
            return driver
        except Exception as e:
            print(f"❌ Browser setup failed: {e}")
            return None

    def load_accounts(self):
        accounts = []
        try:
            with open(self.accounts_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line=line.strip()
                    if ':' in line:
                        email,password = line.split(':',1)
                        accounts.append({'email':email.strip(),'password':password.strip(),'status':'pending'})
            print(f"✅ Loaded {len(accounts)} accounts")
            return accounts
        except FileNotFoundError:
            print(f"❌ {self.accounts_file} nahi mili. Pehle bana lo.")
            return []

    def login_facebook(self, account, thread_num=1):
        print(f"🧵 Thread {thread_num}: Logging in {account['email']}")
        driver = self.setup_browser_termux()
        if not driver:
            account['status']='failed'
            account['error']='Browser setup failed'
            return account
        try:
            driver.get("https://www.facebook.com/login")
            time.sleep(2)
            WebDriverWait(driver,10).until(EC.presence_of_element_located((By.ID,"email")))
            email_field = driver.find_element(By.ID,"email")
            email_field.clear()
            self.human_type(email_field, account['email'])
            password_field = driver.find_element(By.ID,"pass")
            password_field.clear()
            self.human_type(password_field, account['password'])
            login_button = driver.find_element(By.NAME,"login")
            login_button.click()
            time.sleep(4)
            if self.is_login_successful(driver):
                account['status']='success'
                account['cookies']=self.get_cookies(driver)
                account['login_time']=time.strftime("%Y-%m-%d %H:%M:%S")
                self.successful_logins += 1
                self.save_session(account)
            else:
                account['status']='failed'
                account['error']='Login failed'
                self.failed_logins += 1
        except Exception as e:
            account['status']='failed'
            account['error']=str(e)
            self.failed_logins += 1
        finally:
            try: driver.quit()
            except: pass
        return account

    def is_login_successful(self, driver):
        try:
            if "facebook.com/home" in driver.current_url: return True
            if driver.find_elements(By.XPATH, "//div[@role='feed']"): return True
            return False
        except: return False

    def get_cookies(self, driver):
        try: return driver.get_cookies()
        except: return []

    def human_type(self, element, text):
        for c in text:
            element.send_keys(c)
            time.sleep(random.uniform(0.05,0.18))

    def save_session(self, account):
        try:
            sessions = self.load_sessions()
            sessions[account['email']] = {
                'cookies': account.get('cookies',[]),
                'login_time': account.get('login_time',''),
                'status': account['status']
            }
            with open(self.sessions_file,'w',encoding='utf-8') as f:
                json.dump(sessions,f,indent=2)
        except Exception as e:
            print("❌ Error saving session:", e)

    def load_sessions(self):
        try:
            with open(self.sessions_file,'r',encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}

    def bulk_login(self, accounts, max_threads=3):
        print(f"🚀 Starting bulk login for {len(accounts)} accounts...")
        self.successful_logins=0; self.failed_logins=0
        results=[]
        with ThreadPoolExecutor(max_workers=max_threads) as ex:
            futures = {ex.submit(self.login_facebook, acc, i+1): acc for i,acc in enumerate(accounts)}
            for fut in futures:
                res = fut.result()
                results.append(res)
                completed = len([r for r in results if r['status']!='pending'])
                print(f"📊 {completed}/{len(accounts)} done")
        self.save_results(results)
        return results

    def save_results(self, results):
        with open(self.results_file,'w',encoding='utf-8') as f:
            f.write("FACEBOOK LOGIN RESULTS\n")
            f.write("="*40+"\n")
            f.write(f"Total: {len(results)}\n")
            f.write(f"Success: {self.successful_logins}\n")
            f.write(f"Failed: {self.failed_logins}\n\n")
            for a in results:
                icon = "✅" if a['status']=='success' else "❌"
                f.write(f"{icon} {a['email']} - {a['status']}\n")
                if a['status']=='failed': f.write(f"   Error: {a.get('error')}\n")

    def display_summary(self, results):
        succ=[r for r in results if r['status']=='success']
        fail=[r for r in results if r['status']=='failed']
        print("\n==== SUMMARY ====")
        print("Success:", len(succ))
        print("Failed:", len(fail))
        if succ:
            print("✅ Successful accounts:")
            for s in succ: print(" ", s['email'])
        if fail:
            print("❌ Failed accounts:")
            for f in fail: print(" ", f['email'], "-", f.get('error'))

    def create_accounts_template(self):
        if not os.path.exists(self.accounts_file):
            with open(self.accounts_file,'w',encoding='utf-8') as f:
                f.write("user1@gmail.com:password123\nuser2@yahoo.com:pass456\n")
            print("📁 accounts.txt template created")

def main():
    # --- PASSWORD CHECK (reads local .secret file) ---
    if not os.path.exists('.secret'):
        print("❌ .secret file nahi mili. Pehle apne computer/Termux par .secret file banao.")
        print("Example (Termux/PC): echo \"YourPasswordHere\" > .secret")
        return
    saved = open('.secret','r',encoding='utf-8').read().strip()
    entered = getpass.getpass("Enter tool password: ")
    if entered != saved:
        print("❌ Password ghalat. Script band kar raha hoon.")
        return
    print("✅ Password correct — starting script...\n")
    # --- end password check ---

    panel = FacebookLoginPanel()
    panel.create_accounts_template()
    accounts = panel.load_accounts()
    if not accounts:
        print("❌ No accounts found. Add accounts to accounts.txt first.")
        return
    try:
        threads = int(input("Enter number of parallel threads (1-5): ") or 3)
    except:
        threads = 3
    results = panel.bulk_login(accounts, threads)
    panel.display_summary(results)

if __name__ == "__main__":
    main()
        
