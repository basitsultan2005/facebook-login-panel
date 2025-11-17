#!/usr/bin/env python3
"""
Facebook Account Manager Tool
Roman Urdu Interface Version
"""

import requests
import time
import random
import json
import os
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class FacebookAccountManager:
    def __init__(self):
        self.driver = None
        self.current_account = {}
        
    def setup_browser(self):
        """Browser setup karta hai"""
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def roman_urdu_input(self, prompt):
        """Roman Urdu mein input leta hai"""
        print(f"\n{prompt}")
        return input("Aapka jawab: ")
    
    def login_to_facebook(self, email, password):
        """Facebook login karta hai"""
        try:
            self.driver.get("https://www.facebook.com/login")
            time.sleep(3)
            
            # Email field
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "email"))
            )
            email_field.clear()
            email_field.send_keys(email)
            
            # Password field
            password_field = self.driver.find_element(By.ID, "pass")
            password_field.clear()
            password_field.send_keys(password)
            
            # Login button
            login_button = self.driver.find_element(By.NAME, "login")
            login_button.click()
            
            time.sleep(5)
            
            # Check if login successful
            if "login_attempt" in self.driver.current_url or "checkpoint" in self.driver.current_url:
                return False
            return True
            
        except Exception as e:
            print(f"Login mein masla: {str(e)}")
            return False
    
    def change_email(self, new_email):
        """Email change karta hai"""
        try:
            # Settings page par jata hai
            self.driver.get("https://www.facebook.com/settings")
            time.sleep(3)
            
            # Contact info section
            contact_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'contact')]"))
            )
            contact_link.click()
            time.sleep(3)
            
            # Add new email
            add_email_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@aria-label, 'Add another email')]"))
            )
            add_email_btn.click()
            time.sleep(2)
            
            # New email enter karein
            email_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "contactpoint"))
            )
            email_input.clear()
            email_input.send_keys(new_email)
            
            # Save button
            save_btn = self.driver.find_element(By.NAME, "__submit__")
            save_btn.click()
            time.sleep(3)
            
            return True
            
        except Exception as e:
            print(f"Email change mein masla: {str(e)}")
            return False
    
    def change_password(self, new_password):
        """Password change karta hai"""
        try:
            # Security settings
            self.driver.get("https://www.facebook.com/security")
            time.sleep(3)
            
            # Password change section
            password_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'password')]"))
            )
            password_link.click()
            time.sleep(3)
            
            # Current password (yeh tool user se pochega)
            current_pass_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "password_old"))
            )
            
            # Naya password
            new_pass_input = self.driver.find_element(By.ID, "password_new")
            new_pass_input.clear()
            new_pass_input.send_keys(new_password)
            
            # Confirm password
            confirm_pass_input = self.driver.find_element(By.ID, "password_confirm")
            confirm_pass_input.clear()
            confirm_pass_input.send_keys(new_password)
            
            # Save button
            save_btn = self.driver.find_element(By.NAME, "save")
            save_btn.click()
            time.sleep(3)
            
            return True
            
        except Exception as e:
            print(f"Password change mein masla: {str(e)}")
            return False
    
    def process_account(self, original_email, original_password):
        """Single account process karta hai"""
        print(f"\n{'='*50}")
        print(f"Account process shuru: {original_email}")
        print(f"{'='*50}")
        
        # Browser setup
        self.setup_browser()
        
        # Login attempt
        login_success = self.login_to_facebook(original_email, original_password)
        
        if not login_success:
            print("Login nahi ho saka. Account check karein.")
            self.driver.quit()
            return False
        
        print("Login successful!")
        
        # Nayi email puchen
        new_email = self.roman_urdu_input("Nayi email bataein:")
        
        # Email change karein
        if self.change_email(new_email):
            print("Email successfully change ho gayi!")
        else:
            print("Email change mein masla aaya")
        
        # Naya password puchen
        new_password = self.roman_urdu_input("Naya password bataein:")
        
        # Password change karein
        if self.change_password(new_password):
            print("Password successfully change ho gaya!")
        else:
            print("Password change mein masla aaya")
        
        # OTP agar mangta hai toh handle karein
        otp_required = self.roman_urdu_input("Kya OTP manga hai? (haan/naahi):")
        if otp_required.lower() == 'haan':
            otp_code = self.roman_urdu_input("OTP code bataein:")
            # OTP enter karne ka code yahan add karein
        
        # Browser band karein
        self.driver.quit()
        
        # Updated account info save karein
        updated_account = {
            'original_email': original_email,
            'new_email': new_email,
            'new_password': new_password,
            'status': 'success'
        }
        
        return updated_account
    
    def load_accounts_from_file(self, filename):
        """File se accounts load karta hai"""
        accounts = []
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                for line in file:
                    if ':' in line:
                        parts = line.strip().split(':')
                        if len(parts) >= 2:
                            accounts.append({
                                'email': parts[0],
                                'password': parts[1]
                            })
        except Exception as e:
            print(f"File load karne mein masla: {str(e)}")
        
        return accounts
    
    def save_results(self, results, filename="updated_accounts.txt"):
        """Results save karta hai"""
        with open(filename, 'w', encoding='utf-8') as file:
            for result in results:
                file.write(f"{result['original_email']}:{result['new_password']}:{result['new_email']}\n")
    
    def main_menu(self):
        """Main menu display karta hai"""
        print("\n" + "="*60)
        print("FACEBOOK ACCOUNT MANAGER - ROMAN URDU INTERFACE")
        print("="*60)
        print("Yeh tool aapke liye Facebook accounts manage karega")
        print("Har account ki email aur password change karega")
        print("Aapko har account ke liye nayi email aur password batana hoga")
        print("="*60)
        
        # Accounts file ka path
        file_path = self.roman_urdu_input("Accounts file ka path bataein (text file):")
        
        # Accounts load karein
        accounts = self.load_accounts_from_file(file_path)
        
        if not accounts:
            print("Koi accounts nahi mile. File check karein.")
            return
        
        print(f"{len(accounts)} accounts load hue hain")
        
        results = []
        successful = 0
        
        for i, account in enumerate(accounts, 1):
            print(f"\nAccount {i}/{len(accounts)} process ho raha hai...")
            
            result = self.process_account(account['email'], account['password'])
            
            if result:
                results.append(result)
                successful += 1
                print(f"Account {i} successful!")
            else:
                print(f"Account {i} fail ho gaya!")
            
            # Thoda wait karein next account se pehle
            time.sleep(2)
        
        # Results save karein
        self.save_results(results)
        
        print(f"\n{'='*50}")
        print(f"Process complete!")
        print(f"Successful: {successful}/{len(accounts)}")
        print(f"Results saved: updated_accounts.txt")
        print(f"{'='*50}")

def main():
    """Main function"""
    try:
        manager = FacebookAccountManager()
        manager.main_menu()
        
    except Exception as e:
        print(f"Tool mein error aaya: {str(e)}")
        print("Chrome driver check karein aur phir try karein")

if __name__ == "__main__":
    main()
