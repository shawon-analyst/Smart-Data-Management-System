# 📊 Smart Data Management System (SaaS Edition)

একটি multi-user Streamlit-ভিত্তিক ডাটা ম্যানেজমেন্ট ও ভিজুয়ালাইজেশন প্ল্যাটফর্ম —
যেখানে user নিজে সাইনআপ/লগইন করে CSV/Excel আপলোড করে KPI ও চার্ট দেখতে পারে,
এবং Admin আলাদা প্যানেল থেকে সব user-এর তথ্য ও activity দেখতে পারে।

---

## 🚀 চালু করার নিয়ম (Run Locally)

```bash
pip install -r requirements.txt
streamlit run app.py
```

প্রথমবার চালানোর সময় `data/sdms.db` নামে SQLite ফাইল automatically তৈরি হয়ে যাবে।
এই ফাইলেই সব ব্যবহারকারী, session, এবং আপলোড করা ফাইল সংরক্ষিত থাকে।

---

## 🔑 Admin Login

```
Username: admin
Password: Admin@123
```

⚠️ **Production-এ deploy করার আগে অবশ্যই `auth.py` ফাইলের `ADMIN_PASSWORD` পরিবর্তন করুন।**

---

## 👤 সাধারণ ব্যবহারকারী (User)

- "নতুন একাউন্ট" ট্যাব থেকে নিজে সাইনআপ করতে পারবে
- লগইন করার পর CSV/Excel আপলোড করতে পারবে
- প্রতিটি আপলোড স্বয়ংক্রিয়ভাবে database-এ সংরক্ষিত হয় (ফাইল history)
- আগের যেকোনো আপলোড করা ফাইল sidebar থেকে select করে আবার দেখা যাবে
- "আমাকে লগইন রাখো" চেক করলে browser বন্ধ করে আবার খুললেও লগইন থাকবে (cookie-based, ১৪ দিন পর্যন্ত)

---

## 🛡️ Admin Dashboard

Admin লগইন করলে আলাদা ভিউ দেখাবে:
- **Platform Overview** — মোট user, মোট ফাইল, আজকের signup/upload সংখ্যা
- **সব ব্যবহারকারী** — কে কখন সাইনআপ করেছে, last login, কতগুলো ফাইল আপলোড করেছে
- **সব ফাইল** — কোন user কোন ফাইল কখন আপলোড করেছে
- **Activity Log** — login/logout/signup/upload-এর টাইমলাইন

---

## 📁 প্রজেক্ট স্ট্রাকচার

```
sdms/
├── app.py            # মূল Streamlit অ্যাপ (UI + routing)
├── auth.py           # লগইন/লগআউট/সেশন লজিক
├── db.py             # SQLite ডাটাবেস লেয়ার (users, files, sessions, logs)
├── requirements.txt
├── data/
│   └── sdms.db       # SQLite ডাটাবেস (প্রথম রানে অটো-তৈরি হয়)
└── README.md
```

---



## 🔧 পরবর্তীতে যা যোগ করা যেতে পারে

- Email verification / password reset
- Per-user storage quota
- Role-based permissions (multiple admin levels)
- Export admin reports as PDF/Excel
- Rate limiting on login attempts
