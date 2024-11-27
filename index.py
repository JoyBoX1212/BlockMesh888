import time
import random
from playwright.sync_api import sync_playwright

# Fungsi logging
def log_message(message, level="INFO"):
    levels = {"INFO": "\033[34m", "SUCCESS": "\033[32m", "ERROR": "\033[31m"}
    prefix = levels.get(level, "\033[34m")
    print(f"{prefix}[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}\033[0m")

# Fungsi retry_action
def retry_action(action, retries=3, delay=5):
    for attempt in range(retries):
        try:
            if action():
                return True
        except Exception as e:
            log_message(f"Percobaan {attempt + 1} gagal: {e}", "ERROR")
        time.sleep(delay)
    log_message("Semua percobaan gagal.", "ERROR")
    return False

# Fungsi untuk mendapatkan email acak
def generate_email(user_email):
    random_number = random.randint(1000, 9999)
    return f"{user_email}{random_number}@mailto.plus", f"{user_email}{random_number}"

# Fungsi untuk menunggu pemuatan halaman dinamis
def wait_until_page_loaded(page, timeout=60000):
    try:
        page.wait_for_load_state("networkidle", timeout=timeout)
        log_message("Halaman selesai dimuat.", "SUCCESS")
        return True
    except Exception as e:
        log_message(f"Timeout menunggu halaman selesai dimuat: {e}", "ERROR")
        return False

# Fungsi untuk mengonfirmasi email
def confirm_email(context, email_username):
    def confirm():
        page = context.new_page()
        page.goto('https://tempmail.plus/')
        log_message("Membuka halaman TempMail...")

        try:
            # Ganti email
            page.fill('#pre_button', email_username)
            page.keyboard.press("Enter")
            wait_until_page_loaded(page)
            log_message(f"Email berhasil diganti ke: {email_username}")
        except Exception as e:
            log_message(f"Gagal mengatur email: {e}", "ERROR")
            return False

        try:
            # Tunggu email konfirmasi
            email_selector = "text=Confirmation Email from BlockMesh Network"
            page.wait_for_selector(email_selector, timeout=60000)
            page.click(email_selector)
            log_message("Email konfirmasi diterima.")
        except Exception as e:
            log_message(f"Gagal menemukan email konfirmasi: {e}", "ERROR")
            return False

        try:
            # Klik link konfirmasi
            confirmation_link = page.locator("a:has-text('Click Here')")
            confirmation_link.wait_for(timeout=10000)
            confirmation_link.click()
            log_message("Tautan konfirmasi berhasil diklik.", "SUCCESS")
        except Exception as e:
            log_message(f"Gagal mengklik tautan konfirmasi: {e}", "ERROR")
            return False
        finally:
            page.close()

        return True

    return retry_action(confirm)

# Fungsi untuk menjalankan proses referral
def restart_process(context, referral_url, user_email, default_password, referrals):
    successful_referrals = 0
    failed_referrals = 0

    for i in range(referrals):
        log_message(f"Mulai Referral {i + 1}/{referrals}...")

        def process_referral():
            page = context.new_page()
            try:
                # Buka halaman Proxyium
                page.goto("https://proxyium.com/?__cpo=1")
                log_message("Membuka Proxyium...")

                # Masukkan URL referral
                page.fill("#unique-form-control", referral_url)
                page.click("#unique-btn-blue")
                if not wait_until_page_loaded(page):
                    page.close()
                    return False
                log_message("Berhasil membuka halaman BlockMesh.")

                # Daftar akun
                email, email_username = generate_email(user_email)
                page.fill("#email", email)
                page.fill("#password", default_password)
                page.fill("#password_confirm", default_password)
                page.click("button[type='submit']")
                if not wait_until_page_loaded(page):
                    page.close()
                    return False
                log_message(f"Berhasil Mendaftar - {email}", "SUCCESS")

                with open("generated_email.txt", "a") as file:
                    file.write(f"{email}\n")

                # Konfirmasi email
                if confirm_email(context, email_username):
                    log_message(f"Proses Referral {i + 1} BERHASIL!", "SUCCESS")
                    page.close()
                    return True
                else:
                    page.close()
                    return False

            except Exception as e:
                log_message(f"Error pada proses referral: {e}", "ERROR")
                return False
            finally:
                page.close()

        if retry_action(process_referral):
            successful_referrals += 1
        else:
            failed_referrals += 1

        # Tambahkan jeda acak sebelum iterasi berikutnya
        time.sleep(random.uniform(5, 10))

    # Ringkasan hasil referral
    log_message(f"BERHASIL!! {successful_referrals} REFERRAL SUDAH DIBUAT", "SUCCESS")
    log_message(f"GAGAL!! {failed_referrals} REFERRAL TIDAK DIBUAT", "ERROR")

# Fungsi utama
def main():
    # Input dari user
    referral_url = input("Masukkan URL Referral: ")
    user_email = input("Masukkan nama email (contoh: akunbm): ")
    default_password = input("Masukkan password default: ")
    referrals = int(input("Berapa Referral yang ingin Anda buat? : "))

    if referrals <= 0:
        log_message("Jumlah referral harus lebih dari 0!", "ERROR")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()

        try:
            restart_process(context, referral_url, user_email, default_password, referrals)
        finally:
            browser.close()
            log_message("Browser ditutup.")

if __name__ == "__main__":
    main()
