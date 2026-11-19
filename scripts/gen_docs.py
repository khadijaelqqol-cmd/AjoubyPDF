# -*- coding: utf-8 -*-
"""توليد ملفي دليل الاستخدام Markdown من ajoubi/guide.py

الاستخدام:  python scripts/gen_docs.py
النتيجة:    docs/دليل_الاستخدام.md  و  docs/USER_GUIDE.md
"""
import os
import sys

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root)

from ajoubi import guide  # noqa: E402

docs = os.path.join(root, "docs")
os.makedirs(docs, exist_ok=True)

shots_ar = """
![الشاشة الرئيسية](screenshots/01_home_ar.png)

![فتح مستند والتنقل بين الصفحات](screenshots/02_document_ar.png)

![دليل الاستخدام داخل البرنامج](screenshots/03_guide_ar.png)
"""

shots_en = """
![Home screen](screenshots/04_home_en.png)

![Opening a document and navigating pages](screenshots/05_document_en.png)

![The built-in user guide](screenshots/06_guide_en.png)
"""

ar = guide.markdown("ar")
ar = ar.replace(
    "*كل ما تحتاجه خطوة بخطوة — ببساطة تامة*",
    "*كل ما تحتاجه خطوة بخطوة — ببساطة تامة*\n" + shots_ar +
    "\n> 💡 يمكنك فتح هذا الدليل من داخل البرنامج في أي وقت بالضغط على **F1** "
    "أو زر «دليل» في شريط الأدوات.", 1)
ar = ar.replace("*اجوبي PDF — دليل الاستخدام*",
                "*اجوبي PDF — دليل الاستخدام*\n\n"
                "[العودة إلى README](../README.md)", 1)

en = guide.markdown("en")
en = en.replace(
    "*Everything you need, step by step — nice and easy*",
    "*Everything you need, step by step — nice and easy*\n" + shots_en +
    "\n> 💡 You can open this guide inside the app at any time with **F1** "
    "or the “Guide” button in the toolbar.", 1)
en = en.replace("*Ajouby PDF — User Guide*",
                "*Ajouby PDF — User Guide*\n\n"
                "[Back to README](../README.md)", 1)

with open(os.path.join(docs, "دليل_الاستخدام.md"), "w", encoding="utf-8") as f:
    f.write(ar)
with open(os.path.join(docs, "USER_GUIDE.md"), "w", encoding="utf-8") as f:
    f.write(en)
print("written", len(ar), len(en), "->", docs)
