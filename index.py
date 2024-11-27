import time
import random
from playwright.sync_api import sync_playwright

# Fungsi retry_action
def retry_action(action, retries=3, delay=5):
    """
    Mengulangi tindakan tertentu hingga berhasil atau mencapai batas percobaan.
    """
    for attempt in range(retries):
        try:
            if action():
                return True
        except Exception as e:
            print(f"\033[31mPercobaan {attempt + 1} gagal: {e}\033[0m")
        time.sleep(delay)
    print("\033[31mSemua percobaan gagal.\033[0m")
    return False

# Fungsi untuk mendapatkan email acak dengan prefix dari user
def generate_email(prefix):
    random_number = random.randint(1000, 9999)
    return f"{prefix}{random_number}@mailto.plus", f"{prefix}{random_number}"

# Fungsi untuk menunggu pemuatan halaman dinamis
def wait_until_page_loaded(page, timeout=60000):
    try:
        page.wait_for_load_state("networkidle", timeout=timeout)
        print("\033[32mHalaman selesai dimuat.\033[0m")
        return True
    except Exception as e:
        print(f"\033[31mTimeout menunggu halaman selesai dimuat: {e}\033[0m")
        return False

# Fungsi untuk mengonfirmasi email
def confirm_email(context, email_username):
    def confirm():
        page = context.new_page()
        page.goto('https://tempmail.plus/')
        print("\033[34mMembuka halaman TempMail...\033[0m")

        # Ganti email
        try:
            page.fill('#pre_button', email_username)
            page.keyboard.press("Enter")
            wait_until_page_loaded(page)
            print(f"\033[34mEmail berhasil diganti ke: {email_username}\033[0m")
        except Exception as e:
            print(f"\033[31mGagal mengatur email: {e}\033[0m")
            return False

        # Tunggu email konfirmasi
        try:
            email_selector = "text=Confirmation Email from BlockMesh Network"
            page.wait_for_selector(email_selector, timeout=60000)
            page.click(email_selector)
            print("\033[34mEmail konfirmasi diterima.\033[0m")
        except Exception as e:
            print(f"\033[31mGagal menemukan email konfirmasi: {e}\033[0m")
            return False

        # Klik link konfirmasi
        try:
            confirmation_link = page.locator("a:has-text('Click Here')")
            confirmation_link.wait_for(timeout=10000)
            confirmation_link.click()
            print("\033[32mTautan konfirmasi berhasil diklik.\033[0m")
        except Exception as e:
            print(f"\033[31mGagal mengklik tautan konfirmasi: {e}\033[0m")
            return False
        finally:
            page.close()

        return True

    return retry_action(confirm)

# Fungsi untuk menjalankan proses referral
def restart_process(driver, referrals, referral_link, email_prefix):
    failed_referrals = 0
    successful_referrals = 0

    for i in range(referrals):
        print(f"\033[34mMulai Referral {i + 1}/{referrals}...\033[0m")

        def process_referral():
            page = driver.new_page()
            page.goto("https://proxyium.com/?__cpo=1")
            print("\033[34mMembuka Proxyium...\033[0m")

            # Masukkan URL referral
            try:
                page.fill("#unique-form-control", referral_link)
                page.click("#unique-btn-blue")
                if not wait_until_page_loaded(page):
                    page.close()
                    return False
                print("\033[34mBerhasil membuka halaman referral.\033[0m")
            except Exception as e:
                print(f"\033[31mGagal mengakses halaman referral: {e}\033[0m")
                page.close()
                return False

            # Daftar akun
            try:
                email, email_username = generate_email(email_prefix)
                page.fill("#email", email)
                page.fill("#password", "Akun12345$")
                page.fill("#password_confirm", "Akun12345$")
                page.click("button[type='submit']")
                if not wait_until_page_loaded(page):
                    page.close()
                    return False
                print(f"\033[32mBerhasil Mendaftar - {email}\033[0m")
                with open("generated_email.txt", "a") as file:
                    file.write(f"{email}\n")
            except Exception as e:
                print(f"\033[31mGagal mendaftar akun: {e}\033[0m")
                page.close()
                return False

            # Konfirmasi email
            if confirm_email(driver, email_username):
                print(f"\033[32mProses Referral {i + 1} BERHASIL!\033[0m")
                page.close()
                return True
            else:
                page.close()
                return False

        if retry_action(process_referral):
            successful_referrals += 1
        else:
            failed_referrals += 1

        # Tambahkan jeda acak sebelum iterasi berikutnya
        time.sleep(random.uniform(5, 10))

    # Ringkasan hasil referral
    print(f"\033[32mBERHASIL!! {successful_referrals} REFERRAL SUDAH DIBUAT\033[0m")
    print(f"\033[31mGAGAL!! {failed_referrals} REFERRAL TIDAK DIBUAT\033[0m")
    driver.close()

# Fungsi utama
def main():
    referral_link = input("Masukkan link referral Anda: ").strip()
    if not referral_link.startswith("http"):
        print("\033[31mLink referral tidak valid! Harap masukkan URL lengkap.\033[0m")
        return

    email_prefix = input("Masukkan nama untuk email akun (tanpa spasi, contoh: akungarapan): ").strip()
    if not email_prefix.isalnum():
        print("\033[31mNama email tidak valid! Harap gunakan hanya huruf dan angka.\033[0m")
        return

    referrals = int(input("Berapa referral yang ingin Anda buat? : "))
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        
        restart_process(context, referrals, referral_link, email_prefix)

if __name__ == "__main__":
    main()
