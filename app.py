
import streamlit as st
from pathlib import Path
from datetime import datetime, date
import json, re

# =========================================================
# KONFIGURASI
# =========================================================
st.set_page_config(
    page_title="Ayo Belajar Teks Anekdot",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_DIR = Path("data_app")
USERS_DIR = DATA_DIR / "users"
CONTENT_DIR = DATA_DIR / "content"
USERS_DIR.mkdir(parents=True, exist_ok=True)
CONTENT_DIR.mkdir(parents=True, exist_ok=True)

CUSTOM_QUIZ_FILE = CONTENT_DIR / "quiz_custom.json"
CUSTOM_MATERIAL_FILE = CONTENT_DIR / "material_custom.json"

# Ganti PIN ini sebelum disebarkan luas.
TEACHER_PIN = "1234"

# =========================================================
# STYLE
# =========================================================
st.markdown("""
<style>
.block-container {padding-top:1.4rem; padding-bottom:3rem; max-width:1180px;}
.hero {
  padding:1.5rem 1.6rem; border-radius:22px;
  background:linear-gradient(135deg,#f7d7e2,#e8f4ff);
  border:1px solid rgba(0,0,0,.08); margin-bottom:1rem;
}
.hero h1{margin:0;font-size:2.15rem}
.hero p{margin:.55rem 0 0;color:#4b5563;font-size:1.02rem}
.card {
  padding:1rem 1.1rem; border-radius:18px; border:1px solid #e5e7eb;
  background:white; min-height:110px; margin-bottom:.75rem;
  box-shadow:0 4px 16px rgba(0,0,0,.035);
}
.soft {padding:.95rem 1rem;border-radius:14px;background:#faf7ff;border:1px solid #eee7fb;margin:.55rem 0}
.tip {padding:.85rem 1rem;border-left:5px solid #ff6b9a;background:#fff7fa;border-radius:10px;margin:.7rem 0}
.good {padding:.8rem 1rem;border-radius:12px;background:#eefbf3;border:1px solid #caefd7}
.mid  {padding:.8rem 1rem;border-radius:12px;background:#fff9e8;border:1px solid #f5e5a9}
.bad  {padding:.8rem 1rem;border-radius:12px;background:#fff1f1;border:1px solid #f5caca}
.small {font-size:.9rem;color:#6b7280}
div[data-testid="stMetric"]{border:1px solid #e5e7eb;border-radius:16px;padding:.8rem;background:white}
</style>
""", unsafe_allow_html=True)

# =========================================================
# MATERI BAWAAN
# =========================================================
TUJUAN = """
### 🎯 Tujuan Pembelajaran Teks Anekdot
Di akhir Fase E, peserta didik mampu menulis gagasan, pikiran, pandangan, arahan, atau pesan tertulis untuk berbagai tujuan secara logis, kritis, dan kreatif dalam bentuk teks informasional dan/atau fiksi.

### 🏆 Capaian Pembelajaran
Pada akhir Fase E, peserta didik mampu menulis berbagai teks untuk menyampaikan pendapat dan mempresentasikan serta menanggapi informasi nonfiksi dan fiksi secara kritis dan etis.
"""

PENGANTAR = """
Pada bagian ini, peserta didik mempelajari konsep dasar teks anekdot secara bertahap, meliputi pengertian dan karakteristik teks anekdot, struktur teks, kaidah kebahasaan, serta penerapan konsep melalui contoh dan analisis teks.

Materi dirancang agar peserta didik tidak hanya mengenali unsur kelucuan, tetapi juga mampu memahami kritik, sindiran, pesan, dan makna tersirat yang terdapat dalam teks anekdot.

Setelah mempelajari bagian ini, peserta didik diharapkan mampu:
1. menjelaskan pengertian dan fungsi teks anekdot;
2. mengidentifikasi struktur abstrak, orientasi, krisis/komplikasi, reaksi, dan koda;
3. menemukan kaidah kebahasaan yang digunakan;
4. menganalisis kritik atau sindiran dalam teks; dan
5. memberikan penjelasan dengan bahasa sendiri berdasarkan pemahaman terhadap materi.
"""

PENGERTIAN = """
Menurut Agustina (2019:29), teks anekdot merupakan cerita atau karangan singkat yang memberikan kesan lucu kepada pembaca. Topiknya dapat berasal dari pengalaman hidup seseorang dan dapat berupa sindiran atau kritikan dalam bidang hukum, politik, atau pendidikan.

Teks anekdot adalah teks naratif singkat yang mengandung humor serta maksud tertentu di balik kelucuannya. Kelucuan dapat muncul melalui tindakan tokoh, percakapan, situasi tidak terduga, atau peristiwa yang bertentangan dengan kebiasaan atau logika umum.

Kosasih (2014:2) menjelaskan bahwa anekdot berbentuk cerita yang mengandung humor dan kritikan. Anekdot tidak semata-mata menyediakan hal yang lucu, tetapi juga dapat mengandung pesan yang diharapkan memberi pelajaran kepada khalayak.
"""

STRUKTUR = {
"Abstrak":"Bagian awal yang memberi gambaran tentang isi teks atau hal unik yang akan muncul. Sifatnya opsional.",
"Orientasi":"Bagian yang menunjukkan awal kejadian, latar belakang, tokoh, situasi, atau kondisi yang mengarah pada munculnya krisis.",
"Krisis/Komplikasi":"Bagian inti ketika muncul masalah, kejanggalan, ketidakpuasan, atau kejadian tidak biasa.",
"Reaksi":"Tanggapan atau respons terhadap krisis.",
"Koda":"Bagian akhir yang berisi simpulan, komentar, atau penjelasan atas cerita. Sifatnya opsional."
}

KAIDAH = [
("Kalimat langsung","Petikan langsung dari dialog tokoh."),
("Nama tokoh utama/orang ketiga tunggal","Tokoh dapat disebut langsung atau disamarkan."),
("Keterangan waktu","Misalnya kemarin, sore ini, suatu hari, ketika itu."),
("Kata kiasan/konotasi","Kata atau ungkapan yang tidak selalu bermakna harfiah."),
("Kalimat sindiran","Sindiran dapat diungkapkan melalui pengandaian, perbandingan, atau lawan kata."),
("Konjungsi penjelas","Misalnya kata 'bahwa'."),
("Kata kerja material","Menunjukkan aktivitas yang dapat diamati."),
("Kata kerja mental","Menunjukkan sesuatu yang dipikirkan atau dirasakan."),
("Konjungsi sebab akibat","Misalnya maka, sehingga, oleh karena itu."),
("Kalimat imperatif","Berisi perintah, larangan, atau peringatan."),
("Kalimat seru","Biasanya ditandai tanda seru."),
("Konjungsi temporal","Misalnya akhirnya, kemudian, lalu, selanjutnya."),
("Kalimat retoris","Pertanyaan yang tidak membutuhkan jawaban.")
]

CONTOH = """**Politikus Sering Berbohong**

Sebuah bus penuh dengan para politikus keluar dari marka jalan dan menabrak sebuah pohon besar di ladang seorang petani tua.

Petani tua segera memberikan bantuan, tetapi menganggap para penumpang sudah tidak dapat tertolong dan kemudian menguburkan mereka.

Beberapa hari kemudian polisi datang dan bertanya, “Apakah benar mereka semua meninggal, Pak?”

Petani tua menjawab bahwa beberapa masih bergerak dan mengatakan belum meninggal, tetapi ia tidak mempercayai mereka karena menganggap politikus sering berbohong.
"""

REFERENSI = [
"Sucikaharti, A. (2021). e-Modul Anekdot Bahasa Indonesia.",
"Utama, T. H. F. (2021). Alur Tujuan Pembelajaran Mata Pelajaran Bahasa Indonesia (Fase E).",
"Permatasari, I. A. (2020). Modul Pembelajaran SMA Bahasa Indonesia.",
"Ediawati, R. (2020). E-modul Bahasa dan Sastra Indonesia Kelas X: Makna Tersirat dalam Teks Anekdot.",
"Rifai, B. (2020). E-modul Bahasa dan Sastra Indonesia Kelas X: Struktur dan Teks Kebahasaan Anekdot."
]

BASE_QUIZ = [
{"q":"Cerita lucu (humor) berbeda dengan teks anekdot karena ...","ops":["Humor hanya mengandung kelucuan saja","Humor tidak bisa dikonsumsi oleh semua orang","Humor tidak mengandung manfaat sama sekali","Humor tidak memuat sindiran atau kritik halus","Humor hanya cocok untuk orang dewasa"],"ans":3,"exp":"Anekdot umumnya tidak hanya lucu, tetapi juga memuat kritik/sindiran.","active":True},
{"q":"Berikut ini yang bukan ciri-ciri teks anekdot adalah ...","ops":["Menggelitik","Berbentuk cerita","Memiliki pesan moral","Struktur terdiri dari abstraksi, reaksi dan koda","Memiliki unsur lucu"],"ans":2,"exp":"Mengacu pada kunci latihan yang digunakan dalam blueprint.","active":True},
{"q":"Pernyataan bertujuan menghibur, membangkitkan tawa, dan menggambarkan karakter secara singkat merupakan ...","ops":["Tujuan anekdot","Manfaat anekdot","Visi anekdot","Struktur anekdot","Kebahasaan anekdot"],"ans":0,"exp":"Pernyataan tersebut mengarah pada tujuan anekdot.","active":True},
{"q":"Abstraksi merupakan bagian awal yang biasanya menunjukkan ...","ops":["Hal yang unik","Latar belakang peristiwa","Masalah tokoh","Penyelesaian masalah","Fenomena alam"],"ans":0,"exp":"Abstrak memberi gambaran awal tentang hal unik yang akan muncul.","active":True},
{"q":"“Akhirnya dia menyesal dan berjanji menjadi orang yang lebih baik.” termasuk struktur ...","ops":["Orientasi","Krisis","Reaksi","Abstraksi","Koda"],"ans":4,"exp":"Bagian tersebut bersifat penutup/simpulan.","active":True},
{"q":"Kalimat yang bukan menunjukkan peristiwa masa lalu adalah ...","ops":["Pada suatu hari aku berbelanja di pasar","Pada bulan Mei, dia telah lulus sekolah","Seharusnya, besok menjadi hari bahagia","Ketika itu aku lupa menawarkan diskon","Kemarin, hujan sangat deras"],"ans":2,"exp":"Kata 'besok' menunjukkan waktu yang akan datang.","active":True},
{"q":"“Aku turut berduka cita ...” memenuhi maksim ...","ops":["Kearifan","Simpati","Kedermawanan","Kerendahan hati","Pujian"],"ans":1,"exp":"Ungkapan duka menunjukkan simpati.","active":True},
{"q":"Kalimat yang menunjukkan konjungsi waktu adalah ...","ops":["Dosen muda lulusan UPI menjadi dosen terbaik","Mahasiswa sedang mengerjakan tugas","Dosen menjelaskan kepada mahasiswa","Saat tiba presentasi, Deny gugup","Kelas kembali online"],"ans":3,"exp":"Kata 'saat' menunjukkan hubungan waktu.","active":True},
{"q":"Berikut langkah menganalisis teks anekdot, kecuali ...","ops":["Menemukan kata kias","Menganalisis struktur dan kebahasaan","Memahami teks dengan baik","Mencermati teks dengan sungguh-sungguh","Membaca anekdot dengan saksama"],"ans":1,"exp":"Mengacu pada kunci latihan blueprint.","active":True},
{"q":"Penulisan kalimat langsung yang tepat adalah ...","ops":["Akhirnya, hakim berkata, “Pak, tolong berhenti.","“Pak tolong angkat telefonnya.”: Hakim.","Guru: “Silahkan kumpulkan tugasnya!”","Akhirnya siswa selesai mengerjakan tugas.","“Sel, tolong ambilkan penghapus,” kata guru."],"ans":2,"exp":"Mengacu pada kunci latihan blueprint.","active":True}
]

ESSAYS = [
{"q":"Jelaskan pengertian teks anekdot dengan menggunakan bahasamu sendiri!","concepts":[["cerita","teks","kisah"],["singkat","pendek"],["lucu","humor","menghibur"],["kritik","sindiran"]],"required":3,"hint":"Anekdot adalah cerita singkat, lucu/menghibur, dan mengandung kritik atau sindiran."},
{"q":"Sebutkan dan jelaskan ciri-ciri teks anekdot!","concepts":[["cerita","naratif"],["lucu","humor","menghibur"],["kritik","sindiran"],["pesan","makna"],["tokoh","kejadian","peristiwa"]],"required":3,"hint":"Minimal tiga ciri yang benar dan sebaiknya diberi penjelasan."},
{"q":"Jelaskan fungsi atau tujuan dari teks anekdot!","concepts":[["menghibur","hiburan","lucu"],["kritik","mengkritik"],["sindiran","menyindir"],["pesan","pandangan","pelajaran"]],"required":3,"hint":"Mencakup fungsi menghibur serta menyampaikan kritik/sindiran dan pesan."},
{"q":"Jelaskan apa yang dimaksud dengan makna tersirat dalam teks anekdot! Berikan contohnya secara singkat.","concepts":[["tidak langsung","tersirat","tersembunyi"],["konteks","isi cerita","dipahami"],["kritik","sindiran","pesan"],["contoh","misalnya"]],"required":3,"hint":"Makna tersirat tidak disampaikan secara langsung, dipahami dari konteks, lalu diberi contoh."}
]

# =========================================================
# UTILITAS
# =========================================================
def slugify(text):
    text=(text or "").lower().strip()
    text=re.sub(r"[^a-z0-9_-]+","_",text)
    return text.strip("_") or "user"

def read_json(path, default):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except:
        pass
    return default

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def user_dir():
    u=st.session_state.get("user")
    if not u: return None
    p=USERS_DIR/slugify(u["nama"])
    p.mkdir(parents=True, exist_ok=True)
    return p


def save_profile():
    """Simpan identitas dan peran pengguna agar Guru tidak terbaca sebagai Siswa."""
    p = user_dir()
    if not p:
        return
    write_json(
        p / "profile.json",
        {
            "nama": st.session_state.user["nama"],
            "peran": st.session_state.user["peran"],
        },
    )

def add_activity(kind, detail=""):
    p=user_dir()
    if not p: return
    path=p/"activity.json"
    data=read_json(path,[])
    data.append({"waktu":datetime.now().isoformat(timespec="seconds"),"jenis":kind,"detail":detail})
    write_json(path,data[-500:])

def load_custom_quiz():
    data=read_json(CUSTOM_QUIZ_FILE,[])
    return data if isinstance(data,list) else []

def save_custom_quiz(data):
    write_json(CUSTOM_QUIZ_FILE,data)

def get_quiz_bank():
    """
    Latihan selalu terdiri atas 10 soal agar rubrik 10 x 10 = 100 konsisten.
    Soal tambahan guru yang aktif diprioritaskan, lalu dilengkapi soal bawaan.
    """
    custom_active = [q for q in load_custom_quiz() if q.get("active", True)]
    base_active = [q for q in BASE_QUIZ if q.get("active", True)]
    return (custom_active + base_active)[:10]

def load_custom_materials():
    data=read_json(CUSTOM_MATERIAL_FILE,[])
    return data if isinstance(data,list) else []

def save_custom_materials(data):
    write_json(CUSTOM_MATERIAL_FILE,data)

def save_chat(q,a):
    p=user_dir()
    if not p:return
    path=p/"chat.json"
    data=read_json(path,[])
    data.append({"waktu":datetime.now().isoformat(timespec="seconds"),"q":q,"a":a})
    write_json(path,data[-100:])

def save_quiz(score,correct,total,answers=None):
    p=user_dir()
    if not p:return
    path=p/"quiz.json"
    data=read_json(path,[])
    data.append({"waktu":datetime.now().isoformat(timespec="seconds"),"score":score,"correct":correct,"total":total,"answers":answers or []})
    write_json(path,data[-100:])
    add_activity("Latihan",f"Skor {score}")

def normalize(t):
    return re.sub(r"\s+"," ",re.sub(r"[^a-zA-ZÀ-ÿ0-9\s]"," ",(t or "").lower())).strip()

def contains_any(text, variants):
    t=normalize(text)
    return any(normalize(v) in t for v in variants)

REFLECTIONS = {
    "Tujuan & Capaian": {"q":"Setelah membaca tujuan dan capaian pembelajaran, kemampuan apa yang harus kamu kuasai setelah mempelajari teks anekdot?","concepts":[["menulis","menyampaikan","gagasan","pendapat"],["logis","kritis","kreatif"],["teks","anekdot","informasi"],["menanggapi","mempresentasikan","pesan"]],"hint":"Coba sebutkan kemampuan utama yang berkaitan dengan menulis, menyampaikan gagasan, dan berpikir kritis."},
    "Pengantar": {"q":"Menurutmu, mengapa memahami kritik, sindiran, dan makna tersirat penting dalam teks anekdot?","concepts":[["kritik","sindiran"],["pesan","makna tersirat","tersirat"],["memahami","menafsirkan","menangkap"],["cerita","anekdot"]],"hint":"Hubungkan jawabanmu dengan fungsi anekdot yang tidak hanya lucu, tetapi juga menyampaikan pesan."},
    "Pengertian": {"q":"Menurut pemahamanmu, apa yang membedakan teks anekdot dengan cerita lucu biasa?","concepts":[["lucu","humor","menghibur"],["kritik","sindiran"],["pesan","makna"],["cerita","anekdot"]],"hint":"Pikirkan unsur yang ada pada anekdot selain kelucuan."},
    "Struktur": {"q":"Bagaimana cara membedakan bagian orientasi dan krisis dalam teks anekdot?","concepts":[["orientasi","awal","latar","tokoh","situasi"],["krisis","masalah","kejanggalan","konflik"],["sebelum masalah","awal kejadian"],["muncul masalah","inti masalah"]],"hint":"Orientasi berkaitan dengan keadaan awal, sedangkan krisis mulai menunjukkan masalah atau kejanggalan."},
    "Kaidah Kebahasaan": {"q":"Sebutkan dua kaidah kebahasaan teks anekdot dan jelaskan fungsinya secara singkat.","concepts":[["kalimat langsung","konjungsi","kata kerja","kalimat sindiran","retoris","temporal","imperatif"],["fungsi","menunjukkan","menghubungkan","menegaskan","menyindir"],["dua","2"],["contoh","misalnya"]],"hint":"Kamu bisa memilih dua dari: kalimat langsung, konjungsi temporal, kata kerja material/mental, kalimat sindiran, kalimat retoris, dan lainnya."},
    "Contoh Teks": {"q":"Kritik atau sindiran apa yang terdapat dalam teks contoh, dan bagian mana yang menunjukkan hal tersebut?","concepts":[["kritik","sindiran"],["politikus","berbohong","tidak jujur"],["petani","tidak percaya","mengubur"],["bagian","kutipan","cerita"]],"hint":"Perhatikan alasan petani tidak mempercayai para politikus."},
    "Materi Tambahan": {"q":"Tuliskan satu hal baru yang kamu pahami dari materi tambahan dan jelaskan dengan bahasamu sendiri.","concepts":[["paham","memahami","mengetahui","belajar"],["materi","konsep","isi"],["menjelaskan","bahasa sendiri"],["contoh","alasan"]],"hint":"Sebutkan inti materi tambahan yang baru kamu pahami, lalu jelaskan secara singkat."},
    "Referensi": {"q":"Mengapa sumber atau referensi penting dalam mempelajari materi teks anekdot?","concepts":[["sumber","referensi","rujukan"],["percaya","valid","akurat"],["materi","informasi"],["belajar","memahami"]],"hint":"Pikirkan fungsi referensi sebagai dasar agar materi lebih dapat dipercaya dan ditelusuri."}
}

def evaluate_reflection(answer, spec):
    a=normalize(answer)
    if len(a.split())<5:
        return {"category":"🔴 Perlu belajar lagi","score":25,"reason":"Jawaban masih terlalu singkat untuk menunjukkan pemahaman yang cukup.","advice":spec["hint"]}
    hits=sum(1 for group in spec["concepts"] if contains_any(a,group))
    total=len(spec["concepts"])
    ratio=hits/total if total else 0
    if ratio>=0.70:
        return {"category":"✅ Sudah paham","score":100,"reason":f"Jawabanmu sudah menangkap inti materi. {hits} dari {total} unsur utama terdeteksi.","advice":"Bagus. Kamu sudah bisa menjelaskan dengan bahasamu sendiri."}
    elif ratio>=0.40:
        return {"category":"🟡 Cukup paham","score":70,"reason":f"Jawabanmu sudah mengarah benar, tetapi masih ada unsur penting yang belum dijelaskan. {hits} dari {total} unsur utama terdeteksi.","advice":spec["hint"]}
    return {"category":"🔴 Perlu belajar lagi","score":40,"reason":f"Jawabanmu belum cukup menunjukkan inti materi. Baru {hits} dari {total} unsur utama terdeteksi.","advice":spec["hint"]}

def save_reflection(topic, answer, result):
    p=user_dir()
    if not p: return
    path=p/'reflections.json'
    data=read_json(path,[])
    data.append({"waktu":datetime.now().isoformat(timespec="seconds"),"topik":topic,"jawaban":answer,"kategori":result["category"],"score":result["score"],"reason":result["reason"],"advice":result["advice"]})
    write_json(path,data[-200:])
    add_activity('Refleksi',f"{topic} - {result['category']}")

def render_reflection(topic,key_suffix):
    spec=REFLECTIONS[topic]
    st.markdown('---')
    st.markdown('### 🧠 Uji Pemahaman Materi')
    st.caption('Jawab dengan bahasamu sendiri. Bagian ini tidak menambah nilai akhir, tetapi membantu kamu dan guru melihat tingkat pemahamanmu.')
    ans=st.text_area(spec['q'],key=f'reflection_{key_suffix}',height=110,placeholder='Tulis jawabanmu di sini...')
    if st.button('Cek Pemahaman',key=f'reflection_btn_{key_suffix}',type='primary'):
        if not ans.strip():
            st.warning('Isi jawaban refleksi terlebih dahulu.')
        else:
            result=evaluate_reflection(ans,spec)
            save_reflection(topic,ans.strip(),result)
            if 'Sudah paham' in result['category']: st.success(result['category'])
            elif 'Cukup paham' in result['category']: st.warning(result['category'])
            else: st.error(result['category'])
            st.write(result['reason'])
            st.caption('Saran: '+result['advice'])

def evaluate_essay(answer,spec):
    a=normalize(answer)
    if len(a.split())<4:
        return {"category":"🔴 Belum sesuai","score":5,"reason":"Jawaban masih terlalu singkat untuk menunjukkan pemahaman konsep.","advice":spec["hint"]}
    hits=sum(1 for group in spec["concepts"] if contains_any(a,group))
    total=len(spec["concepts"])
    ratio=hits/total if total else 0
    elaboration=min(len(a.split())/45,1)*0.15
    weighted=min(1,ratio*0.85+elaboration)
    score=round(weighted*25)
    if hits>=spec["required"] and weighted>=.72:
        cat="✅ Sudah sesuai"
        score=max(21,min(25,score))
        reason=f"Inti jawaban sudah sesuai. {hits} dari {total} unsur konsep utama terdeteksi."
        advice="Pertahankan cara menjelaskan dengan bahasa sendiri."
    elif hits>=max(1,spec["required"]-1):
        cat="🟡 Sebagian sesuai"
        score=max(13,min(20,score))
        reason=f"Jawaban sudah mengarah benar, tetapi baru mencakup sekitar {hits} dari {total} unsur utama."
        advice=spec["hint"]
    else:
        cat="🔴 Belum sesuai"
        score=max(0,min(12,score))
        reason=f"Jawaban belum cukup menunjukkan inti konsep. Baru sekitar {hits} dari {total} unsur utama terdeteksi."
        advice=spec["hint"]
    return {"category":cat,"score":score,"reason":reason,"advice":advice}

# =========================================================
# AI TUTOR / KNOWLEDGE BASE
# =========================================================
BASE_KB = {
"pengertian":PENGERTIAN,
"tujuan":TUJUAN,
"struktur":"\n".join([f"{k}: {v}" for k,v in STRUKTUR.items()]),
"kaidah":"\n".join([f"{k}: {v}" for k,v in KAIDAH]),
"contoh":CONTOH,
"referensi":"\n".join(REFERENSI)
}
STOP={"apa","yang","dan","di","ke","dari","itu","ini","dengan","untuk","tentang","jelaskan","tolong","dong","ya","aku","saya","kamu","bisa","gimana","bagaimana","kenapa","mengapa","lagi","contoh"}

def keywords(q):
    return [w for w in normalize(q).split() if len(w)>2 and w not in STOP]

def current_kb():
    kb=dict(BASE_KB)
    for i,item in enumerate(load_custom_materials(),1):
        if item.get("active",True) and item.get("isi","").strip():
            kb[f"materi tambahan: {item.get('judul',f'Materi {i}')}"]=item["isi"]
    return kb

def retrieve(q):
    kws=keywords(q)
    scored=[]
    for title,body in current_kb().items():
        t=normalize(title+" "+body)
        score=sum(t.count(k) for k in kws)
        if any(k in normalize(title) for k in kws):
            score+=5
        scored.append((score,title,body))
    scored.sort(reverse=True)
    return scored[0] if scored else (0,"","")

def tutor_answer(q,history):
    qn=normalize(q)
    previous=history[-1]["q"] if history else ""
    search_q=q if len(keywords(q))>=2 else ((previous+" "+q) if previous else q)

    if "beda" in qn and "orientasi" in qn and ("krisis" in qn or "komplikasi" in qn):
        return "Orientasi memperkenalkan situasi awal sebelum masalah utama muncul. Krisis/komplikasi adalah bagian ketika masalah atau kejanggalan mulai terjadi. Cara gampang: **orientasi = sebelum masalah, krisis = masalah mulai muncul**."
    if "kemudian" in qn and ("termasuk" in qn or "apa" in qn):
        return "Kata **kemudian** termasuk **konjungsi temporal** karena menunjukkan urutan waktu/peristiwa."
    if any(x in qn for x in ["jawaban latihan","kunci latihan","jawaban evaluasi","kunci jawaban"]):
        return "Aku bantu dengan petunjuk dulu ya supaya kamu tetap belajar. Sebutkan nomor soal atau konsep yang membuatmu bingung."

    score,title,body=retrieve(search_q)
    if score<=0:
        return "Aku belum menemukan bagian materi yang paling cocok. Coba tanyakan lebih spesifik tentang pengertian, struktur, kaidah kebahasaan, contoh, kritik/sindiran, atau makna tersirat."
    paras=[p.strip() for p in body.split("\n") if p.strip()]
    picked=[]
    kws=keywords(search_q)
    for p in paras:
        if any(k in normalize(p) for k in kws):
            picked.append(p)
        if len(" ".join(picked))>1100:
            break
    if not picked:
        picked=paras[:3]
    return f"**{title.title()}**\n\n"+"\n\n".join(picked[:5])

# =========================================================
# SESSION & NAVIGATION
# =========================================================
for k,v in {"user":None,"menu":"🏠 Beranda","pending_menu":None,"teacher_verified":False}.items():
    if k not in st.session_state:
        st.session_state[k]=v

MENU=["🏠 Beranda","🧭 Tutorial Penggunaan AI","📚 Materi","🤖 Tanya AI","🎯 Latihan","✍️ Evaluasi","⭐ Favorit","🗒️ Catatan","📅 Absensi","📈 Progress","🔎 Pencarian","👩‍🏫 Dashboard Guru"]

if st.session_state.pending_menu:
    st.session_state.menu=st.session_state.pending_menu
    st.session_state.pending_menu=None

def goto(name):
    st.session_state.pending_menu=name
    st.rerun()

with st.sidebar:
    st.markdown("## 📚 Ayo Belajar")
    if not st.session_state.user:
        nama=st.text_input("Nama")
        peran=st.selectbox("Peran",["Siswa","Guru"])
        pin=""
        if peran=="Guru":
            pin=st.text_input("PIN Guru",type="password")
        if st.button("Masuk",type="primary",use_container_width=True):
            if not nama.strip():
                st.warning("Masukkan nama terlebih dahulu.")
            elif peran=="Guru" and pin!=TEACHER_PIN:
                st.error("PIN Guru salah.")
            else:
                st.session_state.user={"nama":nama.strip(),"peran":peran}
                st.session_state.teacher_verified=(peran=="Guru")
                save_profile()
                add_activity("Login",peran)
                st.rerun()
    else:
        st.success(f"Halo, **{st.session_state.user['nama']}** 👋")
        st.caption(st.session_state.user["peran"])
        if st.button("Keluar",use_container_width=True):
            st.session_state.user=None
            st.session_state.teacher_verified=False
            st.session_state.menu="🏠 Beranda"
            st.rerun()

    st.divider()
    current=st.session_state.menu if st.session_state.menu in MENU else MENU[0]
    idx=MENU.index(current)
    choice=st.radio("Navigasi",MENU,index=idx,key="nav_radio")
    if choice!=st.session_state.menu:
        st.session_state.menu=choice
        st.rerun()

def need_login():
    if not st.session_state.user:
        st.info("Silakan login dari sidebar untuk menggunakan fitur ini.")
        return False
    return True

st.markdown("""
<div class="hero">
<h1>📚 Ayo Belajar Teks Anekdot</h1>
<p>Belajar santai, tanya sesukamu, latihan, lalu cek seberapa jauh kamu sudah paham ✨</p>
</div>
""",unsafe_allow_html=True)

menu=st.session_state.menu

# =========================================================
# BERANDA
# =========================================================
if menu=="🏠 Beranda":
    st.markdown("## Hai, bestie! 👋")
    st.write("Belajar teks anekdot sekarang lebih santai dan interaktif. Kamu bisa baca materi, tanya AI Tutor, coba latihan, kerjakan evaluasi, dan cek perkembangan belajarmu.")
    st.markdown('<div class="tip"><b>✨ Nggak harus langsung paham.</b><br>Kamu bisa tanya, coba, salah, perbaiki, lalu makin ngerti.</div>',unsafe_allow_html=True)
    c1,c2,c3,c4,c5=st.columns(5)
    if c1.button("📖 Mulai Belajar",use_container_width=True): goto("📚 Materi")
    if c2.button("🤖 Tanya AI",use_container_width=True): goto("🤖 Tanya AI")
    if c3.button("🎯 Coba Latihan",use_container_width=True): goto("🎯 Latihan")
    if c4.button("✍️ Evaluasi",use_container_width=True): goto("✍️ Evaluasi")
    if c5.button("📈 Progress",use_container_width=True): goto("📈 Progress")

elif menu=="🧭 Tutorial Penggunaan AI":
    st.markdown("## 🧭 Tutorial Penggunaan AI")
    steps=[
        ("1️⃣ Login","Masukkan nama dan pilih peran. Khusus Guru harus memasukkan PIN."),
        ("2️⃣ Baca Materi","Pelajari Tujuan, Pengantar, Pengertian, Struktur, Kaidah, Contoh, Materi Tambahan, dan Referensi."),
        ("3️⃣ Tanya AI","Ketik pertanyaan dengan bahasa sendiri. AI memahami pertanyaan lanjutan."),
        ("4️⃣ Kerjakan Latihan","Latihan berisi pilihan ganda dan menampilkan skor serta pembahasan."),
        ("5️⃣ Kerjakan Evaluasi","Jawab esai dengan bahasa sendiri. Penilaian berdasarkan inti makna dan ketepatan konsep."),
        ("6️⃣ Lihat Feedback & Progress","Gunakan menu Progress untuk melihat perkembangan belajarmu.")
    ]
    for title,body in steps:
        st.markdown(f'<div class="card"><b>{title}</b><br><span class="small">{body}</span></div>',unsafe_allow_html=True)

# =========================================================
# MATERI
# =========================================================
elif menu=="📚 Materi":
    if need_login():
        st.markdown("## 📚 Materi Teks Anekdot")
        tabs=st.tabs(["🎯 Tujuan & Capaian","📝 Pengantar","💡 Pengertian","🧩 Struktur","🗣️ Kaidah","📖 Contoh","➕ Materi Tambahan","📚 Referensi"])
        with tabs[0]:
            st.markdown(TUJUAN)
            render_reflection("Tujuan & Capaian","tujuan")
        with tabs[1]:
            st.markdown(PENGANTAR)
            render_reflection("Pengantar","pengantar")
        with tabs[2]:
            st.markdown("### 💡 Pengertian Teks Anekdot")
            st.markdown('<div class="tip"><b>Inti cepat:</b> Anekdot = cerita singkat + humor + kritik/sindiran/pesan.</div>',unsafe_allow_html=True)
            st.write(PENGERTIAN)
            render_reflection("Pengertian","pengertian")
        with tabs[3]:
            st.markdown("### 🧩 Struktur Teks Anekdot")
            cols=st.columns(5)
            for i,(k,v) in enumerate(STRUKTUR.items()):
                with cols[i]:
                    st.markdown(f'<div class="card"><b>{i+1}. {k}</b><br><span class="small">{v}</span></div>',unsafe_allow_html=True)
            render_reflection("Struktur","struktur")
        with tabs[4]:
            st.markdown("### 🗣️ Kaidah Kebahasaan")
            for i,(k,v) in enumerate(KAIDAH,1):
                with st.expander(f"{i}. {k}"):
                    st.write(v)
            render_reflection("Kaidah Kebahasaan","kaidah")
        with tabs[5]:
            st.markdown("### 📖 Contoh Teks Anekdot")
            st.markdown(CONTOH)
            render_reflection("Contoh Teks","contoh")
        with tabs[6]:
            st.markdown("### ➕ Materi Tambahan dari Guru")
            mats=[x for x in load_custom_materials() if x.get("active",True)]
            if not mats:
                st.info("Belum ada materi tambahan dari guru.")
            else:
                for i,item in enumerate(mats,1):
                    with st.expander(f"{i}. {item.get('judul','Materi Tambahan')}"):
                        st.caption(f"Kategori: {item.get('kategori','-')}")
                        st.markdown(item.get("isi",""))
                render_reflection("Materi Tambahan","materi_tambahan")
        with tabs[7]:
            st.markdown("### 📚 Referensi")
            for r in REFERENSI:
                st.write("•",r)
            render_reflection("Referensi","referensi")

# =========================================================
# TANYA AI
# =========================================================
elif menu=="🤖 Tanya AI":
    if need_login():
        st.markdown("## 🤖 Tanya AI Tutor")
        p=user_dir()
        hist=read_json(p/"chat.json",[]) if p else []
        for item in hist[-12:]:
            with st.chat_message("user"):
                st.write(item["q"])
            with st.chat_message("assistant"):
                st.markdown(item["a"])
        q=st.chat_input("Contoh: Apa bedanya orientasi dan krisis?")
        if q:
            ans=tutor_answer(q,hist)
            save_chat(q,ans)
            add_activity("Tanya AI",q[:90])
            st.rerun()

# =========================================================
# LATIHAN
# =========================================================
elif menu=="🎯 Latihan":
    if need_login():
        quiz_bank = get_quiz_bank()

        st.markdown("## 🎯 Latihan Pilihan Ganda")
        st.caption("Mode kuis interaktif: jawab satu soal, cek feedback, lalu lanjut ke soal berikutnya.")

        st.markdown("### 📊 Rubrik Penilaian Latihan")
        st.markdown("""
        <div class="soft">
        <b>Aturan penilaian:</b><br>
        • Jumlah soal: <b>10 soal</b><br>
        • Jawaban benar: <b>10 poin</b><br>
        • Jawaban salah: <b>0 poin</b><br>
        • Nilai maksimal: <b>100</b><br>
        • Rumus: <b>Jumlah jawaban benar × 10</b><br><br>
        Contoh: 8 jawaban benar = 8 × 10 = <b>80</b>.<br>
        Jika 10 jawaban benar = 10 × 10 = <b>100</b>.
        </div>
        """, unsafe_allow_html=True)

        # State kuis per sesi
        defaults_quiz = {
            "live_quiz_index": 0,
            "live_quiz_correct": 0,
            "live_quiz_answers": [],
            "live_quiz_checked": False,
            "live_quiz_current_choice": None,
            "live_quiz_finished": False,
            "live_quiz_saved": False,
        }
        for k, v in defaults_quiz.items():
            if k not in st.session_state:
                st.session_state[k] = v

        def reset_live_quiz():
            st.session_state.live_quiz_index = 0
            st.session_state.live_quiz_correct = 0
            st.session_state.live_quiz_answers = []
            st.session_state.live_quiz_checked = False
            st.session_state.live_quiz_current_choice = None
            st.session_state.live_quiz_finished = False
            st.session_state.live_quiz_saved = False
            # Bersihkan pilihan radio lama
            for i in range(10):
                key = f"live_quiz_choice_{i}"
                if key in st.session_state:
                    del st.session_state[key]

        if len(quiz_bank) < 10:
            st.warning(
                f"Saat ini hanya ada {len(quiz_bank)} soal aktif. "
                "Aktifkan/tambahkan soal hingga berjumlah 10 agar rubrik 10 × 10 = 100 dapat digunakan."
            )

        if not st.session_state.live_quiz_finished and quiz_bank:
            idx = st.session_state.live_quiz_index

            # Jika bank berubah saat sesi berlangsung
            if idx >= len(quiz_bank):
                st.session_state.live_quiz_finished = True
                st.rerun()

            q = quiz_bank[idx]

            # Progress visual
            progress_value = idx / len(quiz_bank)
            st.progress(progress_value)
            st.caption(f"Soal {idx + 1} dari {len(quiz_bank)}")

            st.markdown(f"### {idx + 1}. {q['q']}")

            choice = st.radio(
                "Pilih jawabanmu:",
                range(len(q["ops"])),
                format_func=lambda x, ops=q["ops"]: f"{chr(65+x)}. {ops[x]}",
                key=f"live_quiz_choice_{idx}",
                index=None,
                disabled=st.session_state.live_quiz_checked,
            )

            # Cek jawaban
            if not st.session_state.live_quiz_checked:
                if st.button("✅ Cek Jawaban", type="primary", use_container_width=True):
                    if choice is None:
                        st.warning("Pilih salah satu jawaban terlebih dahulu.")
                    else:
                        is_correct = choice == q["ans"]
                        st.session_state.live_quiz_current_choice = choice
                        st.session_state.live_quiz_checked = True
                        if is_correct:
                            st.session_state.live_quiz_correct += 1

                        st.session_state.live_quiz_answers.append({
                            "nomor": idx + 1,
                            "pilihan": choice,
                            "benar": is_correct,
                            "kunci": q["ans"],
                            "pertanyaan": q["q"],
                        })
                        st.rerun()

            # Feedback langsung setelah jawaban dikunci
            if st.session_state.live_quiz_checked:
                chosen = st.session_state.live_quiz_current_choice
                is_correct = chosen == q["ans"]

                if is_correct:
                    st.markdown(
                        f'<div class="good"><b>✅ Benar! +10 poin</b><br>'
                        f'Jawabanmu <b>{chr(65+chosen)}. {q["ops"][chosen]}</b> sudah tepat.</div>',
                        unsafe_allow_html=True
                    )
                    st.success("Kamu sudah memahami konsep pada soal ini. Pertahankan! 🎉")
                else:
                    st.markdown(
                        f'<div class="bad"><b>❌ Belum tepat. +0 poin</b><br>'
                        f'Jawabanmu: <b>{chr(65+chosen)}. {q["ops"][chosen]}</b><br>'
                        f'Jawaban yang tepat: <b>{chr(65+q["ans"])}. {q["ops"][q["ans"]]}</b></div>',
                        unsafe_allow_html=True
                    )
                    st.info("Jangan berhenti di jawaban salah—lihat pembahasannya supaya konsepnya makin jelas.")

                st.markdown("#### 💡 Pembahasan")
                st.write(q.get("exp", "Perhatikan kembali konsep yang berkaitan dengan soal ini."))

                if idx < len(quiz_bank) - 1:
                    if st.button("Soal Berikutnya →", type="primary", use_container_width=True):
                        st.session_state.live_quiz_index += 1
                        st.session_state.live_quiz_checked = False
                        st.session_state.live_quiz_current_choice = None
                        st.rerun()
                else:
                    if st.button("🏁 Lihat Hasil Akhir", type="primary", use_container_width=True):
                        st.session_state.live_quiz_finished = True
                        st.rerun()

        # Hasil akhir
        if st.session_state.live_quiz_finished:
            correct = st.session_state.live_quiz_correct
            total = len(quiz_bank)
            score = correct * 10 if total == 10 else round(correct / total * 100) if total else 0
            wrong = max(total - correct, 0)

            if not st.session_state.live_quiz_saved and total:
                simple_answers = [x["pilihan"] for x in st.session_state.live_quiz_answers]
                save_quiz(score, correct, total, simple_answers)
                st.session_state.live_quiz_saved = True

            st.progress(1.0)
            st.markdown("## 🏆 Hasil Latihan")

            c1, c2, c3 = st.columns(3)
            c1.metric("Nilai Akhir", score)
            c2.metric("Jawaban Benar", correct)
            c3.metric("Jawaban Salah", wrong)

            if score >= 90:
                st.success("🌟 Mantap! Pemahamanmu sangat baik.")
            elif score >= 75:
                st.success("👍 Bagus! Tinggal perkuat beberapa bagian.")
            elif score >= 60:
                st.warning("📚 Cukup baik, tetapi masih ada materi yang perlu kamu pelajari kembali.")
            else:
                st.error("💪 Yuk, baca kembali materi lalu coba lagi. Salah itu bagian dari proses belajar.")

            st.markdown("### 📋 Rekap Jawaban")
            for item in st.session_state.live_quiz_answers:
                q_index = item["nomor"] - 1
                if q_index >= len(quiz_bank):
                    continue
                q = quiz_bank[q_index]
                icon = "✅" if item["benar"] else "❌"
                with st.expander(f"{icon} Soal {item['nomor']}"):
                    st.write(q["q"])
                    st.write(
                        "Jawabanmu:",
                        f"{chr(65+item['pilihan'])}. {q['ops'][item['pilihan']]}"
                    )
                    if not item["benar"]:
                        st.write(
                            "Jawaban yang tepat:",
                            f"{chr(65+q['ans'])}. {q['ops'][q['ans']]}"
                        )
                    st.caption(q.get("exp", ""))

            if st.button("🔄 Coba Latihan Lagi", use_container_width=True):
                reset_live_quiz()
                st.rerun()

# =========================================================
# EVALUASI
# =========================================================
elif menu=="✍️ Evaluasi":
    if need_login():
        st.markdown("## ✍️ Evaluasi Esai")
        st.caption("Jawaban tidak harus sama persis dengan materi. Sistem menilai inti makna dan ketepatan konsep.")
        st.markdown("### 📊 Rubrik Penilaian Evaluasi")
        st.markdown("""
        <div class="soft">
        <b>Aturan penilaian:</b><br>
        • Jumlah soal: <b>4 soal</b><br>
        • Skor maksimal tiap soal: <b>25 poin</b><br>
        • Nilai maksimal: <b>100</b><br>
        • Rumus: <b>25 × 4 = 100</b><br><br>
        <b>Kategori tiap jawaban:</b><br>
        • ✅ Sudah sesuai: <b>21–25 poin</b><br>
        • 🟡 Sebagian sesuai: <b>13–20 poin</b><br>
        • 🔴 Belum sesuai: <b>0–12 poin</b><br><br>
        Penilaian mempertimbangkan ketepatan konsep, relevansi jawaban, kelengkapan inti, dan kemampuan menjelaskan dengan bahasa sendiri.
        </div>
        """, unsafe_allow_html=True)
        with st.form("essay_form"):
            answers=[]
            for i,s in enumerate(ESSAYS,1):
                st.markdown(f"**{i}. {s['q']}**")
                answers.append(st.text_area("Jawabanmu",key=f"essay_{i}",height=120))
            submit=st.form_submit_button("Kirim Evaluasi",type="primary")
        if submit:
            if any(not a.strip() for a in answers):
                st.warning("Semua soal perlu dijawab.")
            else:
                results=[evaluate_essay(a,s) for a,s in zip(answers,ESSAYS)]
                p=user_dir()
                data=read_json(p/"essay.json",[])
                total=sum(r["score"] for r in results)
                data.append({"waktu":datetime.now().isoformat(timespec="seconds"),"score":total,"results":results,"answers":answers})
                write_json(p/"essay.json",data[-100:])
                add_activity("Evaluasi",f"Skor {total}")
                st.metric("Nilai Evaluasi",total)
                for i,r in enumerate(results,1):
                    cls="good" if "Sudah" in r["category"] else ("mid" if "Sebagian" in r["category"] else "bad")
                    st.markdown(f'<div class="{cls}"><b>Soal {i} — {r["category"]} ({r["score"]}/25)</b><br>{r["reason"]}<br><br><b>Saran:</b> {r["advice"]}</div>',unsafe_allow_html=True)

# =========================================================
# FAVORIT / CATATAN / ABSENSI / PROGRESS / PENCARIAN
# =========================================================
elif menu=="⭐ Favorit":
    if need_login():
        p=user_dir()
        fav=read_json(p/"favorites.json",[])
        opts=["Tujuan & Capaian","Pengantar","Pengertian","Struktur","Kaidah Kebahasaan","Contoh Teks","Materi Tambahan","Referensi"]
        selected=st.multiselect("Pilih materi favorit",opts,default=[x for x in fav if x in opts])
        if st.button("Simpan Favorit"):
            write_json(p/"favorites.json",selected)
            st.success("Favorit tersimpan.")

elif menu=="🗒️ Catatan":
    if need_login():
        p=user_dir()
        notes=read_json(p/"notes.json",[])
        text=st.text_area("Catatan baru")
        if st.button("Simpan Catatan"):
            if text.strip():
                notes.append({"waktu":datetime.now().isoformat(timespec="seconds"),"isi":text.strip()})
                write_json(p/"notes.json",notes[-100:])
                add_activity("Catatan",text[:80])
                st.rerun()
        for n in reversed(notes[-20:]):
            st.markdown(f'<div class="soft"><span class="small">{n["waktu"]}</span><br>{n["isi"]}</div>',unsafe_allow_html=True)

elif menu=="📅 Absensi":
    if need_login():
        p=user_dir()
        rows=read_json(p/"attendance.json",[])
        today=date.today().isoformat()
        if any(r.get("tanggal")==today for r in rows):
            st.success("Kamu sudah absen hari ini ✅")
        else:
            if st.button("Absen Hari Ini",type="primary"):
                rows.append({"tanggal":today,"waktu":datetime.now().strftime("%H:%M:%S")})
                write_json(p/"attendance.json",rows)
                add_activity("Absensi",today)
                st.rerun()
        if rows:
            st.dataframe(rows,use_container_width=True)
        else:
            st.info("Belum ada riwayat absensi.")

elif menu=="📈 Progress":
    if need_login():
        p=user_dir()
        quiz=read_json(p/"quiz.json",[])
        essay=read_json(p/"essay.json",[])
        chat=read_json(p/"chat.json",[])
        act=read_json(p/"activity.json",[])
        reflections=read_json(p/"reflections.json",[])
        c1,c2,c3,c4,c5=st.columns(5)
        c1.metric("Pertanyaan AI",len(chat))
        c2.metric("Latihan terakhir",quiz[-1]["score"] if quiz else "-")
        c3.metric("Evaluasi terakhir",essay[-1]["score"] if essay else "-")
        c4.metric("Refleksi selesai",len(reflections))
        c5.metric("Aktivitas",len(act))
        if reflections:
            st.markdown("### 🧠 Riwayat Uji Pemahaman")
            reflection_rows=[{"Waktu":r.get("waktu",""),"Materi":r.get("topik",""),"Kategori":r.get("kategori",""),"Skor indikator":r.get("score","")} for r in reflections[-20:]]
            st.dataframe(reflection_rows,use_container_width=True)
        if act:
            st.markdown("### 🗂️ Aktivitas Terakhir")
            st.dataframe(act[-20:],use_container_width=True)
        else:
            st.info("Belum ada aktivitas.")

elif menu=="🔎 Pencarian":
    if need_login():
        q=st.text_input("Cari kata/topik",placeholder="Contoh: krisis, sindiran, temporal")
        if q:
            score,title,body=retrieve(q)
            if score>0:
                st.markdown(f"### Hasil teratas: {title.title()}")
                st.write(body[:4000])
            else:
                st.info("Belum ada hasil yang cocok.")

# =========================================================
# DASHBOARD GURU
# =========================================================
elif menu=="👩‍🏫 Dashboard Guru":
    if not need_login():
        pass
    elif st.session_state.user["peran"]!="Guru" or not st.session_state.teacher_verified:
        st.warning("Dashboard Guru hanya dapat diakses oleh akun Guru.")
    else:
        st.markdown("## 👩‍🏫 Dashboard Guru")
        st.caption("Pusat monitoring siswa sekaligus pengelolaan kuis dan materi.")

        students=[]
        for folder in USERS_DIR.iterdir():
            if not folder.is_dir():
                continue

            profile = read_json(folder/"profile.json", {})

            # Hanya masukkan akun yang memang berperan sebagai Siswa.
            # Folder lama tanpa profile.json juga tidak dimasukkan agar akun Guru lama tidak terseret.
            if profile.get("peran") != "Siswa":
                continue

            students.append({
                "folder":folder,
                "nama":profile.get("nama") or folder.name.replace("_"," ").title(),
                "chat":read_json(folder/"chat.json",[]),
                "quiz":read_json(folder/"quiz.json",[]),
                "essay":read_json(folder/"essay.json",[]),
                "attendance":read_json(folder/"attendance.json",[]),
                "activity":read_json(folder/"activity.json",[]),
                "reflections":read_json(folder/"reflections.json",[])
            })

        tab1,tab2,tab3,tab4,tab5,tab6,tab_ref,tab7,tab8=st.tabs([
            "📊 Ringkasan",
            "📅 Absensi",
            "📈 Progress",
            "🎯 Latihan/Kuis",
            "✍️ Evaluasi Esai",
            "🤖 Aktivitas AI",
            "🧠 Uji Pemahaman",
            "🛠️ Kelola Kuis",
            "📚 Kelola Materi"
        ])

        with tab1:
            all_quiz=[q.get("score") for s in students for q in s["quiz"] if isinstance(q.get("score"),(int,float))]
            all_essay=[e.get("score") for s in students for e in s["essay"] if isinstance(e.get("score"),(int,float))]
            c1,c2,c3,c4=st.columns(4)
            c1.metric("Siswa tercatat",len(students))
            c2.metric("Rata-rata latihan",round(sum(all_quiz)/len(all_quiz),1) if all_quiz else "-")
            c3.metric("Rata-rata evaluasi",round(sum(all_essay)/len(all_essay),1) if all_essay else "-")
            c4.metric("Soal aktif",len(get_quiz_bank()))

            rows=[]
            for s in students:
                rows.append({
                    "Siswa":s["nama"],
                    "Pertanyaan AI":len(s["chat"]),
                    "Latihan terakhir":s["quiz"][-1]["score"] if s["quiz"] else None,
                    "Latihan tertinggi":max([x.get("score",0) for x in s["quiz"]],default=None),
                    "Evaluasi terakhir":s["essay"][-1]["score"] if s["essay"] else None,
                    "Uji pemahaman":len(s["reflections"]),
                    "Absensi":len(s["attendance"]),
                    "Aktivitas terakhir":s["activity"][-1]["waktu"] if s["activity"] else None
                })
            if rows:
                st.dataframe(rows,use_container_width=True)
            else:
                st.info("Belum ada data siswa.")

        with tab2:
            st.markdown("### 📅 Rekap Absensi")
            rows=[]
            for s in students:
                for a in s["attendance"]:
                    rows.append({"Siswa":s["nama"],"Tanggal":a.get("tanggal",""),"Waktu":a.get("waktu","")})
            if rows:
                st.dataframe(rows,use_container_width=True)
            else:
                st.info("Belum ada data absensi.")

        with tab3:
            st.markdown("### 📈 Progress Siswa")
            rows=[]
            for s in students:
                rows.append({
                    "Siswa":s["nama"],
                    "Jumlah aktivitas":len(s["activity"]),
                    "Pertanyaan AI":len(s["chat"]),
                    "Percobaan latihan":len(s["quiz"]),
                    "Nilai latihan terakhir":s["quiz"][-1]["score"] if s["quiz"] else None,
                    "Evaluasi terakhir":s["essay"][-1]["score"] if s["essay"] else None
                })
            if rows:
                st.dataframe(rows,use_container_width=True)
            else:
                st.info("Belum ada progress siswa.")

        with tab4:
            st.markdown("### 🎯 Hasil Latihan/Kuis")
            if not students:
                st.info("Belum ada data siswa.")
            else:
                pick=st.selectbox("Pilih siswa",[s["nama"] for s in students],key="quiz_student")
                s=next(x for x in students if x["nama"]==pick)
                if s["quiz"]:
                    scores=[x.get("score",0) for x in s["quiz"]]
                    c1,c2,c3=st.columns(3)
                    c1.metric("Percobaan",len(scores))
                    c2.metric("Nilai tertinggi",max(scores))
                    c3.metric("Nilai terakhir",scores[-1])
                    st.dataframe(s["quiz"],use_container_width=True)
                else:
                    st.info("Siswa ini belum mengerjakan latihan.")

        with tab5:
            st.markdown("### ✍️ Hasil Evaluasi Esai")
            if not students:
                st.info("Belum ada data siswa.")
            else:
                pick=st.selectbox("Pilih siswa",[s["nama"] for s in students],key="essay_student")
                s=next(x for x in students if x["nama"]==pick)
                if not s["essay"]:
                    st.info("Siswa ini belum mengerjakan evaluasi.")
                else:
                    latest=s["essay"][-1]
                    st.metric("Nilai terakhir",latest.get("score","-"))
                    for i,(ans,res) in enumerate(zip(latest.get("answers",[]),latest.get("results",[])),1):
                        with st.expander(f"Soal {i} — {res.get('category','')} ({res.get('score',0)}/25)"):
                            st.write("**Jawaban siswa:**")
                            st.write(ans)
                            st.write("**Umpan balik:**")
                            st.write(res.get("reason",""))
                            st.caption(res.get("advice",""))

        with tab6:
            st.markdown("### 🤖 Aktivitas AI Tutor")
            if not students:
                st.info("Belum ada data siswa.")
            else:
                pick=st.selectbox("Pilih siswa",[s["nama"] for s in students],key="ai_student")
                s=next(x for x in students if x["nama"]==pick)
                if not s["chat"]:
                    st.info("Siswa ini belum menggunakan AI Tutor.")
                else:
                    for item in reversed(s["chat"][-30:]):
                        st.markdown(f"**Siswa:** {item.get('q','')}")
                        st.markdown(f"**AI Tutor:** {item.get('a','')}")
                        st.caption(item.get("waktu",""))
                        st.divider()

        with tab_ref:
            st.markdown("### 🧠 Uji Pemahaman Materi")
            if not students:
                st.info("Belum ada data siswa.")
            else:
                pick=st.selectbox("Pilih siswa",[s["nama"] for s in students],key="reflection_student")
                s=next(x for x in students if x["nama"]==pick)
                if not s["reflections"]:
                    st.info("Siswa ini belum mengerjakan refleksi materi.")
                else:
                    rows=[{"Waktu":r.get("waktu",""),"Materi":r.get("topik",""),"Kategori":r.get("kategori",""),"Indikator":r.get("score",""),"Jawaban":r.get("jawaban","")} for r in s["reflections"]]
                    st.dataframe(rows,use_container_width=True)
                    latest=s["reflections"][-1]
                    st.markdown("#### Feedback Terakhir")
                    st.write("**Materi:**",latest.get("topik",""))
                    st.write("**Jawaban siswa:**",latest.get("jawaban",""))
                    st.write("**Kategori:**",latest.get("kategori",""))
                    st.write("**Umpan balik:**",latest.get("reason",""))
                    st.caption(latest.get("advice",""))

        with tab7:
            st.markdown("### 🛠️ Kelola Kuis")
            st.caption("Latihan siswa selalu menampilkan 10 soal aktif. Soal tambahan guru diprioritaskan, lalu dilengkapi soal bawaan.")

            with st.expander("➕ Tambah soal baru",expanded=True):
                with st.form("add_quiz_form"):
                    qtext=st.text_area("Pertanyaan")
                    opts=[st.text_input(f"Pilihan {chr(65+i)}",key=f"qo{i}") for i in range(5)]
                    key_letter=st.selectbox("Kunci jawaban",["A","B","C","D","E"])
                    exp=st.text_area("Pembahasan")
                    add=st.form_submit_button("Tambahkan Soal",type="primary")
                if add:
                    if not qtext.strip() or any(not x.strip() for x in opts):
                        st.warning("Pertanyaan dan pilihan A–E wajib diisi.")
                    else:
                        custom=load_custom_quiz()
                        custom.append({
                            "q":qtext.strip(),
                            "ops":[x.strip() for x in opts],
                            "ans":["A","B","C","D","E"].index(key_letter),
                            "exp":exp.strip() or "Pembahasan ditambahkan oleh guru.",
                            "active":True,
                            "created_at":datetime.now().isoformat(timespec="seconds")
                        })
                        save_custom_quiz(custom)
                        st.success("Soal ditambahkan.")
                        st.rerun()

            custom=load_custom_quiz()
            st.markdown(f"#### Soal tambahan guru ({len(custom)})")
            if not custom:
                st.info("Belum ada soal tambahan.")
            else:
                for idx,q in enumerate(custom):
                    with st.expander(f"{idx+1}. {q.get('q','Soal')}"):
                        active=st.checkbox("Aktif",value=q.get("active",True),key=f"qactive_{idx}")
                        if active!=q.get("active",True):
                            custom[idx]["active"]=active
                            save_custom_quiz(custom)
                            st.rerun()
                        for j,opt in enumerate(q.get("ops",[])):
                            st.write(f"{chr(65+j)}. {opt}")
                        ans_idx=q.get("ans",0)
                        if q.get("ops"):
                            st.success(f"Kunci: {chr(65+ans_idx)}. {q['ops'][ans_idx]}")
                        st.caption(q.get("exp",""))
                        if st.button("Hapus Soal",key=f"delq_{idx}"):
                            custom.pop(idx)
                            save_custom_quiz(custom)
                            st.rerun()

        with tab8:
            st.markdown("### 📚 Kelola Materi")
            st.caption("Materi tambahan guru otomatis muncul pada Materi siswa dan dibaca AI Tutor/Pencarian.")

            with st.expander("➕ Tambah materi baru",expanded=True):
                with st.form("add_material_form"):
                    judul=st.text_input("Judul materi")
                    kategori=st.selectbox("Kategori",["Pengertian","Struktur","Kaidah Kebahasaan","Contoh Teks","Pengayaan","Referensi","Lainnya"])
                    isi=st.text_area("Isi materi",height=260)
                    addm=st.form_submit_button("Tambahkan Materi",type="primary")
                if addm:
                    if not judul.strip() or not isi.strip():
                        st.warning("Judul dan isi materi wajib diisi.")
                    else:
                        mats=load_custom_materials()
                        mats.append({
                            "judul":judul.strip(),
                            "kategori":kategori,
                            "isi":isi.strip(),
                            "active":True,
                            "created_at":datetime.now().isoformat(timespec="seconds")
                        })
                        save_custom_materials(mats)
                        st.success("Materi ditambahkan.")
                        st.rerun()

            mats=load_custom_materials()
            st.markdown(f"#### Materi tambahan ({len(mats)})")
            if not mats:
                st.info("Belum ada materi tambahan.")
            else:
                for idx,item in enumerate(mats):
                    with st.expander(f"{idx+1}. {item.get('judul','Materi Tambahan')}"):
                        active=st.checkbox("Aktif",value=item.get("active",True),key=f"mactive_{idx}")
                        if active!=item.get("active",True):
                            mats[idx]["active"]=active
                            save_custom_materials(mats)
                            st.rerun()
                        st.caption(f"Kategori: {item.get('kategori','-')}")
                        st.markdown(item.get("isi",""))
                        if st.button("Hapus Materi",key=f"delm_{idx}"):
                            mats.pop(idx)
                            save_custom_materials(mats)
                            st.rerun()

st.divider()
st.caption("Prototype pembelajaran • Ayo Belajar Teks Anekdot")
