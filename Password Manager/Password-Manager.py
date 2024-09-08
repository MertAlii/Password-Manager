import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from cryptography.fernet import Fernet
import os
import pyperclip
import random
import string
import re

class PasswordManager:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("Password Manager")
        self.window.geometry("400x550")

        if not os.path.exists("key.key"):
            self.write_key()
        self.key = self.load_key()
        self.fer = Fernet(self.key)

        self.load_settings()
        self.apply_theme()

        self.create_widgets()

    def create_widgets(self):
        self.frame = ctk.CTkFrame(self.window)
        self.frame.pack(pady=20, padx=20, fill="both", expand=True)

        self.label = ctk.CTkLabel(self.frame, text="Password Manager", font=("Roboto", 24, "bold"))
        self.label.pack(pady=12, padx=10)

        self.add_button = ctk.CTkButton(self.frame, text="Hesap Ekle", command=self.add_account_window)
        self.add_button.pack(pady=12, padx=10)

        self.view_button = ctk.CTkButton(self.frame, text="Hesapları Görüntüle", command=self.view_accounts_window)
        self.view_button.pack(pady=12, padx=10)

        self.change_password_button = ctk.CTkButton(self.frame, text="Şifre Değiştir", command=self.change_password_window)
        self.change_password_button.pack(pady=12, padx=10)

        self.generate_password_button = ctk.CTkButton(self.frame, text="Şifre Üret", command=self.generate_password_window)
        self.generate_password_button.pack(pady=12, padx=10)

        self.reset_key_button = ctk.CTkButton(self.frame, text="Key Sıfırla", command=self.reset_key)
        self.reset_key_button.pack(pady=12, padx=10)

        self.settings_button = ctk.CTkButton(self.frame, text="Ayarlar", command=self.settings_window)
        self.settings_button.pack(pady=12, padx=10)

        self.quit_button = ctk.CTkButton(self.frame, text="Çıkış", command=self.window.quit)
        self.quit_button.pack(pady=12, padx=10)

        self.credit_label = ctk.CTkLabel(self.window, text="@MertAlii", font=("Roboto", 14, "bold"))
        self.credit_label.pack(side="bottom", pady=10)

    def add_account_window(self):
        self.hide_main_window()
        self.add_window = ctk.CTkToplevel(self.window)
        self.add_window.title("Hesap Ekle")
        self.add_window.geometry("300x270")
        self.add_window.protocol("WM_DELETE_WINDOW", self.close_add_window)

        name_label = ctk.CTkLabel(self.add_window, text="Hesap Adı:")
        name_label.pack(pady=5)
        name_entry = ctk.CTkEntry(self.add_window)
        name_entry.pack(pady=5)

        pwd_label = ctk.CTkLabel(self.add_window, text="Şifre:")
        pwd_label.pack(pady=5)
        pwd_entry = ctk.CTkEntry(self.add_window, show="*")
        pwd_entry.pack(pady=5)

        save_button = ctk.CTkButton(self.add_window, text="Kaydet", command=lambda: self.add(name_entry.get(), pwd_entry.get()))
        save_button.pack(pady=10)

        back_button = ctk.CTkButton(self.add_window, text="Ana Menü", command=self.close_add_window)
        back_button.pack(pady=10)

    def view_accounts_window(self):
        self.hide_main_window()
        self.view_window = ctk.CTkToplevel(self.window)
        self.view_window.title("Hesaplar")
        self.view_window.geometry("700x500")
        self.view_window.protocol("WM_DELETE_WINDOW", self.close_view_window)

        self.scrollable_frame = ctk.CTkScrollableFrame(self.view_window)
        self.scrollable_frame.pack(pady=20, padx=20, fill="both", expand=True)

        self.update_account_list()

        back_button = ctk.CTkButton(self.view_window, text="Ana Menü", command=self.close_view_window)
        back_button.pack(pady=10)

    def update_account_list(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        accounts = self.view()
        for account in accounts:
            account_frame = ctk.CTkFrame(self.scrollable_frame)
            account_frame.pack(pady=5, padx=5, fill="x")

            account_label = ctk.CTkLabel(account_frame, text=account, anchor="w", width=300)
            account_label.pack(side="left", pady=5, padx=5)

            strength = self.check_password_strength(account.split("|")[1].split(":")[1].strip())
            strength_label = ctk.CTkLabel(account_frame, text=f"Güç: {strength}", width=100)
            strength_label.pack(side="left", pady=5, padx=5)

            button_frame = ctk.CTkFrame(account_frame)
            button_frame.pack(side="right", pady=5, padx=5)

            copy_username_button = ctk.CTkButton(button_frame, text="Hesap Adını Kopyala", 
                                                 command=lambda a=account: self.copy_username(a))
            copy_username_button.pack(pady=2)

            copy_password_button = ctk.CTkButton(button_frame, text="Şifreyi Kopyala", 
                                                 command=lambda a=account: self.copy_password(a))
            copy_password_button.pack(pady=2)

            delete_button = ctk.CTkButton(button_frame, text="Hesabı Sil", 
                                          command=lambda a=account: self.delete_account(a.split("|")[0].split(":")[1].strip()))
            delete_button.pack(pady=2)

    def change_password_window(self):
        self.hide_main_window()
        self.change_window = ctk.CTkToplevel(self.window)
        self.change_window.title("Şifre Değiştir")
        self.change_window.geometry("300x350")
        self.change_window.protocol("WM_DELETE_WINDOW", self.close_change_window)

        accounts = self.view()
        account_names = [account.split(":")[1].split("|")[0].strip() for account in accounts]

        account_label = ctk.CTkLabel(self.change_window, text="Hesap Seçin:")
        account_label.pack(pady=5)
        account_combobox = ctk.CTkComboBox(self.change_window, values=account_names)
        account_combobox.pack(pady=5)

        old_pwd_label = ctk.CTkLabel(self.change_window, text="Eski Şifre:")
        old_pwd_label.pack(pady=5)
        old_pwd_entry = ctk.CTkEntry(self.change_window, show="*")
        old_pwd_entry.pack(pady=5)

        new_pwd_label = ctk.CTkLabel(self.change_window, text="Yeni Şifre:")
        new_pwd_label.pack(pady=5)
        new_pwd_entry = ctk.CTkEntry(self.change_window, show="*")
        new_pwd_entry.pack(pady=5)

        change_button = ctk.CTkButton(self.change_window, text="Şifreyi Değiştir", 
                                      command=lambda: self.change_password(account_combobox.get(), old_pwd_entry.get(), new_pwd_entry.get()))
        change_button.pack(pady=10)

        back_button = ctk.CTkButton(self.change_window, text="Ana Menü", command=self.close_change_window)
        back_button.pack(pady=10)

    def generate_password_window(self):
        self.hide_main_window()
        self.generate_window = ctk.CTkToplevel(self.window)
        self.generate_window.title("Şifre Üret")
        self.generate_window.geometry("300x250")
        self.generate_window.protocol("WM_DELETE_WINDOW", self.close_generate_window)

        length_label = ctk.CTkLabel(self.generate_window, text="Şifre Uzunluğu:")
        length_label.pack(pady=5)
        length_entry = ctk.CTkEntry(self.generate_window)
        length_entry.pack(pady=5)

        generate_button = ctk.CTkButton(self.generate_window, text="Şifre Üret", 
                                        command=lambda: self.generate_password(length_entry.get()))
        generate_button.pack(pady=10)

        self.generated_password_label = ctk.CTkLabel(self.generate_window, text="")
        self.generated_password_label.pack(pady=5)

        # Kopyala butonu ekleniyor
        copy_button = ctk.CTkButton(self.generate_window, text="Kopyala", 
                                     command=self.copy_generated_password)
        copy_button.pack(pady=5)

        back_button = ctk.CTkButton(self.generate_window, text="Ana Menü", command=self.close_generate_window)
        back_button.pack(pady=10)

    def settings_window(self):
        self.hide_main_window()
        self.settings_window = ctk.CTkToplevel(self.window)
        self.settings_window.title("Ayarlar")
        self.settings_window.geometry("300x200")
        self.settings_window.protocol("WM_DELETE_WINDOW", self.close_settings_window)

        theme_label = ctk.CTkLabel(self.settings_window, text="Tema:")
        theme_label.pack(pady=5)
        theme_combobox = ctk.CTkComboBox(self.settings_window, values=["Açık", "Koyu", "Sistem"])
        theme_combobox.set(self.settings.get("theme", "Sistem"))
        theme_combobox.pack(pady=5)

        save_button = ctk.CTkButton(self.settings_window, text="Kaydet", 
                                    command=lambda: self.save_settings(theme_combobox.get()))
        save_button.pack(pady=10)

        back_button = ctk.CTkButton(self.settings_window, text="Ana Menü", command=self.close_settings_window)
        back_button.pack(pady=10)

    def write_key(self):
        key = Fernet.generate_key()
        with open("key.key", "wb") as key_file:
            key_file.write(key)

    def load_key(self):
        with open("key.key", "rb") as file:
            key = file.read()
        return key

    def view(self):
        accounts = []
        try:
            with open('passwords.txt', 'r') as f:
                for line in f.readlines():
                    data = line.rstrip()
                    user, passw = data.split("|")
                    try:
                        decrypted_pass = self.fer.decrypt(passw.encode()).decode()
                        accounts.append(f"Hesap adı: {user} | Şifre: {decrypted_pass}")
                    except Exception:
                        accounts.append(f"Hesap adı: {user} | Şifre: Şifreyi çözerken bir hata oluştu .")
        except FileNotFoundError:
            accounts.append("Henüz kaydedilmiş hesap bulunmamaktadır.")
        except Exception as e:
            accounts.append(f"Şifrelere erişiminiz bulunmamakta. Detay: {e}")
        return accounts

    def add(self, name, pwd):
        encrypted_pwd = self.fer.encrypt(pwd.encode()).decode()
        with open('passwords.txt', 'a') as f:
            f.write(f"{name}|{encrypted_pwd}\n")
        CTkMessagebox(title="Başarılı", message="Hesap başarıyla eklendi!")

    def change_password(self, username, old_password, new_password):
        accounts = []
        changed = False
        with open('passwords.txt', 'r') as f:
            for line in f.readlines():
                user, passw = line.strip().split("|")
                if user == username:
                    try:
                        decrypted_pass = self.fer.decrypt(passw.encode()).decode()
                        if decrypted_pass == old_password:
                            encrypted_new_pass = self.fer.encrypt(new_password.encode()).decode()
                            accounts.append(f"{user}|{encrypted_new_pass}\n")
                            changed = True
                        else:
                            accounts.append(line)
                    except Exception:
                        accounts.append(line)
                else:
                    accounts.append(line)
        
        if changed:
            with open('passwords.txt', 'w') as f:
                f.writelines(accounts)
            CTkMessagebox(title="Başarılı", message="Şifre başarıyla değiştirildi!")
        else:
            CTkMessagebox(title="Hata", message="Hesap adı veya eski şifre yanlış!")

    def delete_account(self, username):
        accounts = []
        deleted = False
        with open('passwords.txt', 'r') as f:
            for line in f.readlines():
                user, _ = line.strip().split("|")
                if user != username:
                    accounts.append(line)
                else:
                    deleted = True
        
        if deleted:
            with open('passwords.txt', 'w') as f:
                f.writelines(accounts)
            CTkMessagebox(title="Başarılı", message="Hesap başarıyla silindi!")
            self.update_account_list()  
        else:
            CTkMessagebox(title="Hata", message="Belirtilen hesap adına sahip hesap bulunamadı!")

    def copy_username(self, account):
        username = account.split("|")[0].split(":")[1].strip()
        pyperclip.copy(username)
        CTkMessagebox(title="Kopyalandı", message="Hesap adı panoya kopyalandı!")

    def copy_password(self, account):
        password = account.split("|")[1].split(":")[1].strip()
        pyperclip.copy(password)
        CTkMessagebox(title="Kopyalandı", message="Şifre panoya kopyalandı!")

    def generate_password(self, length):
        try:
            length = int(length)
            characters = string.ascii_letters + string.digits + string.punctuation
            password = ''.join(random.choice(characters) for _ in range(length))
            self.generated_password_label.configure(text=f"Üretilen Şifre: {password}")
            self.generated_password = password # Şifreyi kopyalama için saklıyoruz
        except ValueError:
            CTkMessagebox(title="Hata", message="Lütfen geçerli bir sayı girin!")

    def copy_generated_password(self):
        if hasattr(self, "generated_password"):
            pyperclip.copy(self.generated_password)
            CTkMessagebox(title="Kopyalandı", message="Şifre panoya kopyalandı!")
        else:
            CTkMessagebox(title="Hata", message="Önce bir şifre üretin!")

    def check_password_strength(self, password):
        score = 0
        if len(password) >= 8:
            score += 1
        if re.search(r"\d", password):
            score += 1
        if re.search(r"[A-Z]", password):
            score += 1
        if re.search(r"[a-z]", password):
            score += 1
        if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            score += 1
        return ["Çok Zayıf", "Zayıf", "Orta", "Güçlü", "Çok Güçlü"][score]

    def reset_key(self):
        confirm = CTkMessagebox(title="Onay", message="Key'i sıfırlamak istediğinizden emin misiniz?", icon="warning", option_1="Evet", option_2="Hayır")
        if confirm.get() == "Evet":
            old_key = self.key
            old_fer = self.fer

            self.write_key()
            self.key = self.load_key()
            self.fer = Fernet(self.key)

            accounts = []
            with open('passwords.txt', 'r') as f:
                for line in f.readlines():
                    user, passw = line.strip().split("|")
                    try:
                        decrypted_pass = old_fer.decrypt(passw.encode()).decode()
                        new_encrypted_pass = self.fer.encrypt(decrypted_pass.encode()).decode()
                        accounts.append(f"{user}|{new_encrypted_pass}\n")
                    except Exception:
                        accounts.append(line)

            with open('passwords.txt', 'w') as f:
                f.writelines(accounts)

            CTkMessagebox(title="Başarılı", message="Key başarıyla sıfırlandı!")
        else:
            CTkMessagebox(title="İptal", message="Key sıfırlama işlemi iptal edildi.")

    def hide_main_window(self):
        self.window.withdraw()

    def show_main_window(self):
        self.window.deiconify()

    def close_add_window(self):
        self.add_window.destroy()
        self.show_main_window()

    def close_view_window(self):
        self.view_window.destroy()
        self.show_main_window()

    def close_change_window(self):
        self.change_window.destroy()
        self.show_main_window()

    def close_generate_window(self):
        self.generate_window.destroy()
        self.show_main_window()

    def close_settings_window(self):
        self.settings_window.destroy()
        self.show_main_window()

    def load_settings(self):
        if os.path.exists("settings.txt"):
            with open("settings.txt", "r") as f:
                self.settings = eval(f.read())
        else:
            self.settings = {"theme": "Sistem"}

    def save_settings(self, theme):
        self.settings["theme"] = theme
        with open("settings.txt", "w") as f:
            f.write(str(self.settings))
        self.apply_theme()
        CTkMessagebox(title="Başarılı", message="Ayarlar kaydedildi!")

    def apply_theme(self):
        theme = self.settings.get("theme", "Sistem")
        if theme == "Açık":
            ctk.set_appearance_mode("light")
        elif theme == "Koyu":
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("system")

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = PasswordManager()
    app.run()