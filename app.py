import gradio as gr
import pandas as pd
import random
import re
import os

# --- Setup Gamified Mock Database ---
CSV_FILE = "donor_registry.csv"

def init_db():
    try:
        df = pd.read_csv(CSV_FILE)
    except FileNotFoundError:
        donors = [
            {"donor_id": 1, "name": "Ali Khan", "blood_type": "O+", "city": "Karachi", "area": "Clifton", "phone": "0300-1234567", "status": "Available", "Total Impact Score": 150, "Lifesaver Level Badge": "🥇 Hero"},
            {"donor_id": 2, "name": "Sara Ahmed", "blood_type": "A+", "city": "Karachi", "area": "DHA Phase 6", "phone": "0311-7654321", "status": "Unavailable", "Total Impact Score": 45, "Lifesaver Level Badge": "🥉 Bronze"},
            {"donor_id": 3, "name": "Omar Raza", "blood_type": "B-", "city": "Karachi", "area": "Gulshan-e-Iqbal", "phone": "0322-1112233", "status": "Available", "Total Impact Score": 300, "Lifesaver Level Badge": "💎 Legend"},
            {"donor_id": 4, "name": "Fatima Noor", "blood_type": "AB+", "city": "Karachi", "area": "Nazimabad", "phone": "0333-9998877", "status": "Available", "Total Impact Score": 120, "Lifesaver Level Badge": "🥈 Silver"},
            {"donor_id": 5, "name": "Bilal Tariq", "blood_type": "O-", "city": "Karachi", "area": "Malir", "phone": "0344-5556666", "status": "Unavailable", "Total Impact Score": 10, "Lifesaver Level Badge": "🌱 Novice"},
            {"donor_id": 6, "name": "Ayesha Zain", "blood_type": "B+", "city": "Karachi", "area": "Saddar", "phone": "0301-4445555", "status": "Available", "Total Impact Score": 220, "Lifesaver Level Badge": "🥇 Hero"}
        ]
        df = pd.DataFrame(donors)
        df.to_csv(CSV_FILE, index=False)
    return df

def load_data_7_cols():
    df = init_db()
    if 'Lifesaver Level Badge' in df.columns:
        df = df.rename(columns={'Lifesaver Level Badge': 'Badge'})
    elif 'Badge' not in df.columns:
        df['Badge'] = "🌟 Verified Responder"
        
    for col in ['name', 'blood_type', 'city', 'area', 'phone', 'status']:
        if col not in df.columns:
            df[col] = "Unknown"

    required_cols = ['name', 'blood_type', 'city', 'area', 'phone', 'status', 'Badge']
    df_clean = df[required_cols].rename(columns={
        'name': 'Name',
        'blood_type': 'Blood Type',
        'city': 'City',
        'area': 'Area',
        'phone': 'Phone Number',
        'status': 'Status'
    })
    return df_clean

initial_donors_df = load_data_7_cols()

LANGUAGES = {
    "1": {
        "lang": "English",
        "branch": "Please select an option:\n1. Register for Blood Donation\n2. Unsubscribe / Remove Account",
        "weight": "Please provide your weight in kg (e.g., '65').",
        "weight_fail": "You entered {} kg. For your safety, donors must be at least 50 kg. You are safely deferred for now.",
        "recent_donation": "Great. Have you donated blood in the last 90 days? (Yes/No)",
        "recent_fail": "Since you have donated recently, you must wait 90 days before your next donation. You are safely deferred for now. Thank you!",
        "health": "Do you have any chronic medical conditions? (Yes/No)",
        "health_specify": "Please specify your health issue or medication.",
        "health_fail_minor": "This issue temporarily alters donor safety metrics. You are safely deferred for 14 days. We hope you feel better soon!",
        "health_fail_major": "This condition compromises transfusion safety or your vitals. You are safely deferred. Thank you for your honesty.",
        "high_risk": "Based on your input, you are permanently deferred for safety reasons. Thank you for understanding.",
        "onboarding": "You are eligible! Please reply with your details in this format: Name, Blood Type, City, Area, Phone Number (e.g., Shamsie, A+, Karachi, DHA Phase 6, 03001234567)",
        "onboarding_fail": "Please make sure to provide exactly 5 items separated by commas: Name, Blood Type, City, Area, Phone Number.",
        "success": "Congratulations! You meet all the criteria. You have been successfully added to the Donor Registry with a 'Verified Responder' badge!",
        "unsubscribe_prompt": "To safely verify your identity and protect your data, please reply with your registered details in this exact format: Name, Phone Number, City, Area",
        "unsubscribe_success": "Your account has been successfully removed from the registry. Thank you for your past contributions.",
        "unsubscribe_fail": "We could not find an account matching those details. Please try again or ensure your details are correct."
    },
    "2": {
        "lang": "Urdu",
        "branch": "براہ کرم ایک آپشن منتخب کریں:\n1. خون کے عطیہ کے لیے رجسٹر کریں\n2. ان سبسکرائب / اکاؤنٹ ہٹائیں",
        "weight": "براہ کرم اپنا وزن کلوگرام میں بتائیں (مثلاً '65')۔",
        "weight_fail": "آپ نے {} کلوگرام درج کیا۔ آپ کی حفاظت کے لیے، عطیہ دہندگان کا کم از کم وزن 50 کلو ہونا چاہیے۔ فی الحال آپ خون نہیں دے سکتے۔",
        "recent_donation": "کیا آپ نے پچھلے 90 دنوں میں خون کا عطیہ دیا ہے؟ (ہاں/نہیں)",
        "recent_fail": "چونکہ آپ نے حال ہی میں عطیہ دیا ہے، آپ کو اگلے عطیہ سے پہلے 90 دن انتظار کرنا ہوگا۔ آپ کا شکریہ!",
        "health": "کیا آپ کو کوئی دائمی طبی مسئلہ ہے؟ (ہاں/نہیں)",
        "health_specify": "براہ کرم اپنی بیماری یا دوا کی تفصیل بتائیں۔",
        "health_fail_minor": "یہ مسئلہ عارضی طور پر خون دینے کی شرائط کو متاثر کرتا ہے۔ آپ کو 14 دن کے لیے روکا گیا ہے۔ امید ہے آپ جلد صحت یاب ہوں گے!",
        "health_fail_major": "یہ حالت خون کی منتقلی کے دوران خطرے کا باعث بن سکتی ہے۔ اس لیے آپ مستقل طور پر خون عطیہ نہیں کر سکتے۔ سچ بتانے کا شکریہ۔",
        "high_risk": "آپ کی فراہم کردہ معلومات کی بنیاد پر حفاظتی وجوہات کی بنا پر آپ کو مستقل طور پر روکا گیا ہے۔ سمجھنے کے لیے شکریہ۔",
        "onboarding": "آپ اہل ہیں! براہ کرم اپنی تفصیلات اس شکل میں بھیجیں: نام, بلڈ گروپ, شہر, علاقہ, فون نمبر (مثلاً: Shamsie, A+, Karachi, DHA Phase 6, 03001234567)",
        "onboarding_fail": "براہ کرم یقینی بنائیں کہ آپ 5 چیزیں کوما (comma) کے ساتھ فراہم کر رہے ہیں: نام, بلڈ گروپ, شہر, علاقہ, فون نمبر۔",
        "success": "مبارک ہو! آپ تمام معیارات پر پورا اترتے ہیں۔ آپ کو کامیابی کے ساتھ ڈونر رجسٹری میں 'Verified Responder' کے بیج کے ساتھ شامل کر لیا گیا ہے!",
        "unsubscribe_prompt": "اپنی شناخت کی تصدیق اور ڈیٹا کے تحفظ کے لیے، براہ کرم اپنی رجسٹرڈ تفصیلات اس شکل میں بھیجیں: نام, فون نمبر, شہر, علاقہ",
        "unsubscribe_success": "آپ کا اکاؤنٹ رجسٹری سے کامیابی کے ساتھ ہٹا دیا گیا ہے۔ آپ کے پچھلے تعاون کا شکریہ۔",
        "unsubscribe_fail": "ہمیں ان تفصیلات سے ملتا جلتا کوئی اکاؤنٹ نہیں ملا۔ براہ کرم دوبارہ کوشش کریں۔"
    },
    "3": {
        "lang": "Roman Urdu",
        "branch": "Baraye meharbani ek option muntakhib karein:\n1. Blood Donation ke liye Register karein\n2. Unsubscribe / Account hatayein",
        "weight": "Baraye meharbani apna wazan kg mein batayein (jaise '65').",
        "weight_fail": "Aap ne {} kg darj kiya. Aap ki hifazat ke liye wazan kam az kam 50 kg hona chahiye. Filhal aap blood nahi de sakte.",
        "recent_donation": "Zabardast. Kya aap ne pichle 90 dinon mein khoon ka atiya diya hai? (Haan/Nahi)",
        "recent_fail": "Kyunke aap ne haal hi mein blood donate kiya hai, aglay donation tak 90 din intezar karein. Shukriya!",
        "health": "Kya aap ko koi daimi (chronic) medical conditions hain? (Haan/Nahi)",
        "health_specify": "Baraye meharbani apni beemari ya medicine specify karein.",
        "health_fail_minor": "Is maslay ki wajah se aap 14 din ke liye blood donate nahi kar sakte. Umeed hai aap jald theek ho jayenge!",
        "health_fail_major": "Ye condition blood transfusion ya aap ki health ke liye theek nahi. Aap permanent taur par defer kiye gaye hain. Sach batane ka shukriya.",
        "high_risk": "Aap ki input ke mutabiq aap ko safety reasons ki wajah se permanent taur par defer kiya gaya hai. Shukriya.",
        "onboarding": "Aap eligible hain! Baraye meharbani apni details is format mein bhejain: Name, Blood Type, City, Area, Phone Number (jaise: Shamsie, A+, Karachi, DHA Phase 6, 03001234567)",
        "onboarding_fail": "Baraye meharbani bilkul 5 items comma se alag kar ke bhejain: Name, Blood Type, City, Area, Phone Number.",
        "success": "Mubarak ho! Aap ne tamam criteria meet kar liye hain. Aap ko Donor Registry mein 'Verified Responder' badge ke sath add kar diya gaya hai!",
        "unsubscribe_prompt": "Apni shanakht verify karne aur data protect karne ke liye, baraye meharbani apni registered details is format mein bhejain: Name, Phone Number, City, Area",
        "unsubscribe_success": "Aap ka account registry se kamyabi ke sath hata diya gaya hai. Aap ke pichlay taawun ka shukriya.",
        "unsubscribe_fail": "Humein in details se milta julta koi account nahi mila. Baraye meharbani dobara koshish karein."
    }
}

# --- Chatbot Screening Logic ---
def screening_chat(user_msg, history, state, df_state):
    if not history:
        history = []
    
    history.append({"role": "user", "content": user_msg})
    
    # Global Unsubscribe Check
    msg_lower = user_msg.lower()
    if msg_lower in ["unsubscribe", "delete my account"]:
        state["step"] = "unsubscribe_prompt"
        lang_code = state.get("lang_code", "1")
        history.append({"role": "assistant", "content": LANGUAGES[lang_code]["unsubscribe_prompt"]})
        return "", history, state, df_state

    # Global Keyword Intercept
    high_risk_keywords = ["hiv", "hepatitis", "jaundice", "cancer", "aids"]
    
    if any(k in msg_lower for k in high_risk_keywords) and state.get("step") not in ["unsubscribe_prompt", 0, "branch"]:
        state["failed"] = True
        lang_code = state.get("lang_code", "1")
        history.append({"role": "assistant", "content": LANGUAGES[lang_code]["high_risk"]})
        return "", history, state, df_state

    if state.get("failed"):
        lang_code = state.get("lang_code", "1")
        history.append({"role": "assistant", "content": LANGUAGES[lang_code].get("high_risk", "You are currently deferred. Thank you!")})
        return "", history, state, df_state
    
    if state.get("step") == 5:
        lang_code = state.get("lang_code", "1")
        history.append({"role": "assistant", "content": LANGUAGES[lang_code]["success"]})
        return "", history, state, df_state

    # Step 0: Language Selection
    if state.get("step") == 0:
        ans = user_msg.strip()
        if ans in ["1", "2", "3"]:
            state["lang_code"] = ans
            state["step"] = "branch"
            history.append({"role": "assistant", "content": LANGUAGES[ans]["branch"]})
        else:
            history.append({"role": "assistant", "content": "Invalid selection. Please type 1 for English, 2 for Urdu, or 3 for Roman Urdu."})
        return "", history, state, df_state

    lang_code = state["lang_code"]
    lang_dict = LANGUAGES[lang_code]

    # Branch Selection
    if state["step"] == "branch":
        ans = user_msg.strip()
        if ans == "1" or "register" in ans.lower():
            state["step"] = 1
            history.append({"role": "assistant", "content": lang_dict["weight"]})
        elif ans == "2" or "unsubscribe" in ans.lower() or "remove" in ans.lower():
            state["step"] = "unsubscribe_prompt"
            history.append({"role": "assistant", "content": lang_dict["unsubscribe_prompt"]})
        else:
            history.append({"role": "assistant", "content": lang_dict["branch"]})
        return "", history, state, df_state

    # Unsubscribe Flow
    if state["step"] == "unsubscribe_prompt":
        parts = [p.strip() for p in user_msg.split(',')]
        if len(parts) == 4:
            name, phone, city, area = parts
            
            try:
                df = pd.read_csv(CSV_FILE)
                phone_clean = phone.replace(" ", "").replace("-", "")
                
                def match_phone(p):
                    return str(p).replace(" ", "").replace("-", "") == phone_clean
                
                mask = df['phone'].apply(match_phone)
                
                if mask.any():
                    df = df[~mask]
                    df.to_csv(CSV_FILE, index=False)
                    
                    history.append({"role": "assistant", "content": lang_dict["unsubscribe_success"]})
                    # Update global df
                    new_df_state = load_data_7_cols()
                    state["step"] = 5 
                    return "", history, state, new_df_state
                else:
                    history.append({"role": "assistant", "content": lang_dict["unsubscribe_fail"]})
                    return "", history, state, df_state
            except Exception as e:
                 history.append({"role": "assistant", "content": "Error processing request."})
                 return "", history, state, df_state
        else:
            history.append({"role": "assistant", "content": "Please ensure you provide exactly 4 items separated by commas: Name, Phone Number, City, Area"})
            return "", history, state, df_state

    # Step 1: Weight
    if state["step"] == 1:
        nums = re.findall(r'\d+', user_msg)
        if not nums:
            history.append({"role": "assistant", "content": lang_dict["weight"]})
            return "", history, state, df_state
        weight = int(nums[0])
        if weight < 50:
            state["failed"] = True
            history.append({"role": "assistant", "content": lang_dict["weight_fail"].format(weight)})
            return "", history, state, df_state
        else:
            state["step"] = 2
            history.append({"role": "assistant", "content": lang_dict["recent_donation"]})
            return "", history, state, df_state

    # Step 2: Recent Donation
    elif state["step"] == 2:
        ans = user_msg.lower().strip()
        if "yes" in ans or "haan" in ans or ans == "y":
            state["failed"] = True
            history.append({"role": "assistant", "content": lang_dict["recent_fail"]})
            return "", history, state, df_state
        else:
            state["step"] = 3
            history.append({"role": "assistant", "content": lang_dict["health"]})
            return "", history, state, df_state

    # Step 3: Health Conditions
    elif state["step"] == 3:
        ans = user_msg.lower().strip()
        if "yes" in ans or "haan" in ans or ans == "y":
            state["step"] = "3b" # intermediate
            history.append({"role": "assistant", "content": lang_dict["health_specify"]})
            return "", history, state, df_state
        else:
            state["step"] = 4
            history.append({"role": "assistant", "content": lang_dict["onboarding"]})
            return "", history, state, df_state
            
    # Step 3b: Health Details conditional
    elif state["step"] == "3b":
        minor_issues = ["cough", "cold", "fever", "flu", "antibiotics"]
        ans = user_msg.lower()
        if any(m in ans for m in minor_issues):
            state["failed"] = True
            history.append({"role": "assistant", "content": lang_dict["health_fail_minor"]})
        else:
            state["failed"] = True
            history.append({"role": "assistant", "content": lang_dict["health_fail_major"]})
        return "", history, state, df_state

    # Step 4: Onboarding
    elif state["step"] == 4:
        parts = [p.strip() for p in user_msg.split(',')]
        if len(parts) != 5:
            history.append({"role": "assistant", "content": lang_dict["onboarding_fail"]})
            return "", history, state, df_state
            
        name, blood_type, city, area, phone = parts
        state["step"] = 5
        
        # Permanent Storage logic using open(..., 'a')
        with open(CSV_FILE, "a", encoding="utf-8") as f:
            df_temp = pd.read_csv(CSV_FILE)
            donor_id = df_temp['donor_id'].max() + 1 if ('donor_id' in df_temp.columns and not df_temp.empty) else 1
            f.write(f"{donor_id},{name},{blood_type},{city},{area},{phone},Available,0,🌟 Verified Responder\n")
            
        new_df_state = load_data_7_cols()
        history.append({"role": "assistant", "content": lang_dict["success"]})
        return "", history, state, new_df_state

    return "", history, state, df_state


# --- Admin Panel Logic ---
def admin_remove_donor(phone_to_remove, current_df):
    try:
        df = pd.read_csv(CSV_FILE)
        phone_clean = str(phone_to_remove).replace(" ", "").replace("-", "").lower()
        
        def match_phone(p):
            return str(p).replace(" ", "").replace("-", "").lower() == phone_clean
            
        mask = df['phone'].apply(match_phone)
        
        if mask.any():
            df = df[~mask]
            df.to_csv(CSV_FILE, index=False)
            df_clean = load_data_7_cols()
            return f"✅ Donor removed successfully.", "", df_clean
        else:
            return f"❌ No donor found with phone {phone_to_remove}.", phone_to_remove, current_df
    except Exception as e:
        return f"Error: {str(e)}", phone_to_remove, current_df


# --- Predictive Analytics ---
def run_predictive_analytics():
    events = [
        ("Eid-ul-Fitr Approaching", "High travel volume and accidents expected. Expected 30% spike in trauma cases. 🔴 RUN BLOOD DRIVE IMMEDIATELY!"),
        ("Monsoon Heatwave Alert", "Heat stroke and Dengue cases rising. Platelets and O- demand up. 🟠 Plan awareness campaign."),
        ("Normal Season", "No major anomalies detected. Blood banks are stable. 🟢 Monitor stock routinely.")
    ]
    event_name, forecast = random.choice(events)
    return f"### Forecast Detected: {event_name}\n\n**Action Alert:** {forecast}"

# --- Traffic-Aware Dispatch Algorithm ---
def dispatch_donors(blood_type, current_donors_df):
    matches = current_donors_df[(current_donors_df["Blood Type"] == blood_type) & (current_donors_df["Status"] == "Available")].copy()
    if matches.empty:
        matches = current_donors_df[current_donors_df["Status"] == "Available"].copy()
    
    results = []
    for _, row in matches.iterrows():
        base_distance = random.randint(10, 45)
        traffic_factor = round(random.uniform(1.0, 3.5), 2)
        true_arrival = int(base_distance * traffic_factor)
        results.append({
            "Name": row["Name"],
            "City": row.get("City", "Karachi"),
            "Area": row.get("Area", "Unknown"),
            "Phone Number": row["Phone Number"],
            "Base Dist (mins)": base_distance,
            "Traffic Factor": f"{traffic_factor}x",
            "True Arrival Time (mins)": true_arrival,
            "Badge": row["Badge"]
        })
    
    results_df = pd.DataFrame(results)
    if not results_df.empty:
        results_df = results_df.sort_values(by="True Arrival Time (mins)", ascending=True)
    return results_df

# --- Simulator Logic ---
def simulate_input(input_text, is_voice, current_donors_df):
    if is_voice:
        transcription = "🎙️ [Transcribed Urdu]: Mujhe O negative khoon ki ashad zarurat hai Jinnah Hospital mein. (I urgently need O- blood at Jinnah Hospital.)"
        parsed_type = "O-"
    else:
        transcription = input_text
        parsed_type = "A+" if "A+" in input_text.upper() else "O+"
        
    status_msg = f"🟢 Actioned! AI routed request for {parsed_type} blood type."
    return transcription, status_msg, dispatch_donors(parsed_type, current_donors_df)

def toggle_emergency_status(is_fulfilled):
    if is_fulfilled:
        return "✅ Crisis Resolved (WhatsApp Broadcast Sent)"
    else:
        return "🚨 Emergency Active. Waiting for donor response..."

# Custom CSS
custom_css = """
body, .gradio-container {
    background-color: #121214 !important;
}
.header-banner {
    background-color: #1e1e24;
    color: white;
    padding: 20px;
    border-radius: 8px;
    text-align: center;
    margin-bottom: 20px;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    border-bottom: 3px solid #D32F2F;
}
.header-banner h1 {
    margin: 0;
    font-size: 2.5em;
    color: #ffffff;
}
.header-banner p {
    margin: 5px 0 0 0;
    color: #cccccc;
    font-size: 1.1em;
}
.primary {
    background-color: #D32F2F !important;
    border-color: #b71c1c !important;
    color: white !important;
    border-radius: 8px !important;
}
.primary:hover {
    background-color: #b71c1c !important;
}
button {
    border-radius: 8px !important;
}
table, .table-wrap, tbody tr, td, th, .gr-dataframe {
    background-color: #ffffff !important;
    color: #121214 !important;
    border-radius: 8px !important;
}
.metric-card {
    background-color: #1e1e24;
    border-left: 5px solid #007bff;
    padding: 15px;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    text-align: center;
    color: #e0e0e0;
}
.metric-card.red { border-left-color: #D32F2F; }
.metric-card.green { border-left-color: #28a745; }
.metric-card.yellow { border-left-color: #ffc107; }
.metric-value { font-size: 1.8em; font-weight: bold; margin-bottom: 5px; color: #ffffff; }
.metric-title { font-size: 0.9em; color: #aaaaaa; text-transform: uppercase; letter-spacing: 1px; }

/* === 1. HEADINGS FIX (Solid White) === */
.prose h1, .prose h2, .prose h3, .prose h4, 
.gr-form .gr-block-title, .gr-block-header span,
div[class*="fieldset"] > span, 
.gr-markdown h1, .gr-markdown h2, .gr-markdown h3 {
    color: #FFFFFF !important;
    font-weight: 600 !important;
}

/* === 2. TABS FIX (White by default, Red on hover/selection) === */
.tabs div button, button[id*="tab-"], .tab-nav button {
    color: #FFFFFF !important;
    opacity: 0.8 !important;
    font-weight: 600 !important;
}
.tabs div button:hover, button[id*="tab-"]:hover, .tab-nav button:hover {
    color: #D32F2F !important;
    opacity: 1 !important;
}
.tabs div button.selected, button[id*="tab-"].selected, .tab-nav button.selected {
    color: #D32F2F !important;
    opacity: 1 !important;
    border-bottom: 2px solid #D32F2F !important;
}

/* === 3. INSTRUCTION TEXT FIX (Solid White) === */
.prose p, .gr-markdown p, .gr-markdown span, p {
    color: #FFFFFF !important;
}

/* === 4. CHATBOT BUBBLE CONTRAST FIX === */
.gr-chatbot, .chatbot {
    background-color: #121214 !important;
    border: 1px solid #333333 !important;
}

.message-wrap .message, 
.gr-chatbot .message, 
div[class*="message"] {
    background-color: #F3F4F6 !important; 
    color: #111827 !important;            
}

.message-wrap .message p, 
.gr-chatbot .message p,
.message p span {
    color: #111827 !important;
    font-weight: 500 !important;
}

/* === DATAFRAME COLUMN MENU CONTRAST FIX === */
.tbody-menu, .table-menu, .grid-wrap th .cell-menu, .grid-wrap th .cell-menu ul,
.grid-wrap th .cell-menu li, .cell-menu button, div[class*="menu"] button, div[class*="menu"] li {
    color: #111827 !important;
    background-color: #FFFFFF !important;
}
.cell-menu button:hover, div[class*="menu"] button:hover, div[class*="menu"] li:hover {
    color: #D32F2F !important;
    background-color: #F3F4F6 !important;
}
"""

# HTML for Header
header_html = """
<div class="header-banner">
    <h1>🩸 Hayaat AI Engine | Emergency Civic Dispatch</h1>
    <p>Predictive & Traffic-Aware Life-Saving Network</p>
</div>
"""

# HTML for Live Status Metrics
metrics_html = """
<div style="display: flex; gap: 20px; margin-bottom: 20px;">
    <div class="metric-card red" style="flex: 1;">
        <div class="metric-value">1</div>
        <div class="metric-title">Total Active Requests</div>
    </div>
    <div class="metric-card green" style="flex: 1;">
        <div class="metric-value">4</div>
        <div class="metric-title">Available Donors Ready</div>
    </div>
    <div class="metric-card yellow" style="flex: 1;">
        <div class="metric-value">14.5 min</div>
        <div class="metric-title">Avg. Dispatch Time</div>
    </div>
</div>
"""

with gr.Blocks() as demo:
    gr.HTML(header_html)
    
    # Global state for dataframe so both tabs share it
    global_df_state = gr.State(initial_donors_df)
    
    with gr.Tabs():
        # Tab 1: Active Crisis & Dispatch
        with gr.TabItem("Active Crisis & Dispatch"):
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### 🎛️ Control Panel")
                    with gr.Group():
                        gr.Markdown("**Submit Emergency Request**\n<small>Type a mock request or simulate an Urdu voice note below.</small>")
                        input_text = gr.Textbox(label="Text Input (English/Urdu)", placeholder="e.g. Need A+ blood at Aga Khan Hospital urgently")
                        simulate_voice_btn = gr.Button("🎙️ Simulate Voice Note (Urdu)", variant="secondary")
                        parse_btn = gr.Button("Analyze Request & Dispatch Donors", variant="primary")
                        
                    with gr.Group():
                        gr.Markdown("**Emergency Controls**\n<small>Check when the emergency is over to auto-notify donors.</small>")
                        fulfilled_checkbox = gr.Checkbox(label="Emergency Fulfilled (Spam-Proof Expiry Toggle)")
                        broadcast_status = gr.Textbox(label="Auto-Response Status", value="🚨 Emergency Active. Waiting for donor response...", interactive=False)

                with gr.Column(scale=1):
                    gr.Markdown("### 📡 System Output Status")
                    with gr.Group():
                        transcription_box = gr.Textbox(label="Parsed Transcription", interactive=False, lines=2)
                        status_box = gr.Textbox(label="AI Status Indicator", interactive=False)
            
            gr.HTML("<hr style='margin: 30px 0;'>")
            
            gr.HTML(metrics_html)
            
            gr.Markdown("### 🚦 Traffic-Aware Dispatch Results")
            dispatch_table = gr.Dataframe(interactive=False)
            
            simulate_voice_btn.click(
                fn=lambda df: simulate_input("", True, df),
                inputs=[global_df_state],
                outputs=[transcription_box, status_box, dispatch_table]
            )
            parse_btn.click(
                fn=lambda x, df: simulate_input(x, False, df),
                inputs=[input_text, global_df_state],
                outputs=[transcription_box, status_box, dispatch_table]
            )
            fulfilled_checkbox.change(
                fn=toggle_emergency_status,
                inputs=[fulfilled_checkbox],
                outputs=[broadcast_status]
            )

        # Tab 2: Donor Registry & Screening
        with gr.TabItem("Donor Registry (Gamified)"):
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### Hayaat Medical Screening Bot (Urdu/English Support)")
                    gr.Markdown("Answer the questions to see if you are eligible to register as a donor.")
                    
                    initial_msg = [{"role": "assistant", "content": "Welcome! Please select your language:\n1. English\n2. Urdu (اردو)\n3. Roman Urdu"}]
                    chatbot = gr.Chatbot(value=initial_msg)
                    chat_input = gr.Textbox(label="Your Answer", placeholder="Type your answer here...")
                    
                    chat_state = gr.State({"step": 0, "failed": False, "lang_code": "1"})
                    
                with gr.Column(scale=2):
                    gr.Markdown("### Registered Blood Donors")
                    registry_table = gr.Dataframe(value=initial_donors_df, interactive=False)
                    
                    gr.Markdown("#### Admin Panel: Manual Deletion")
                    with gr.Row():
                        admin_phone_input = gr.Textbox(label="Phone Number to Remove", placeholder="e.g. 03001234567")
                        admin_remove_btn = gr.Button("Remove Selected Donor", variant="stop")
                    admin_status = gr.Textbox(label="Admin Action Status", interactive=False)
                    
            chat_input.submit(
                fn=screening_chat,
                inputs=[chat_input, chatbot, chat_state, global_df_state],
                outputs=[chat_input, chatbot, chat_state, global_df_state]
            ).then(
                fn=lambda df: df,
                inputs=[global_df_state],
                outputs=[registry_table]
            )

            admin_remove_btn.click(
                fn=admin_remove_donor,
                inputs=[admin_phone_input, global_df_state],
                outputs=[admin_status, admin_phone_input, global_df_state]
            ).then(
                fn=lambda df: df,
                inputs=[global_df_state],
                outputs=[registry_table]
            )

        # Tab 3: Predictive Analytics
        with gr.TabItem("Predictive Analytics"):
            gr.Markdown("### Seasonal Forecasting & Demand Prediction")
            analyze_btn = gr.Button("Run Seasonal Forecast", variant="primary")
            forecast_output = gr.Markdown(value="Click the button to analyze current seasonal and traffic trends nationwide (Pakistan).", label="Forecast Alert")
            
            analyze_btn.click(
                fn=run_predictive_analytics,
                outputs=[forecast_output]
            )

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860, theme=gr.themes.Soft(), css=custom_css)
