import sys
import os
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from pathlib import Path

# Add project root to path so we can import src
sys.path.append(str(Path(__file__).resolve().parent.parent))
from src import config

# Set page config
st.set_page_config(
    page_title="Imer Hukuk LLM Benchmark Dashboard",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=Outfit:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    h1, h2, h3 {
        font-family: 'Outfit', sans-serif;
        font-weight: 800;
    }
    
    .main-title {
        background: linear-gradient(135deg, #FF4B4B 0%, #852D91 50%, #312A6C 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        margin-bottom: 0.2rem;
    }
    
    .subtitle {
        color: #8C8C8C;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background-color: #1E1E2E;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #2D2D44;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #FF4B4B;
        margin-top: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #A0A0B0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Custom button */
    .stButton>button {
        background: linear-gradient(135deg, #FF4B4B 0%, #852D91 100%);
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(255, 75, 75, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# Helper functions to load scored files
def get_scored_runs() -> list:
    files = list(config.SCORED_RESULTS_DIR.glob("*.json"))
    runs = []
    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as file:
                runs.append((f.name, json.load(file)))
        except Exception as e:
            st.error(f"Error loading {f.name}: {e}")
    return runs

def get_final_score(record: dict) -> float:
    """Compute final score using 70% Human + 30% LLM-Judge formula if overridden."""
    if record.get("human_override", False) and record.get("human_total_score") is not None:
        return 0.7 * record["human_total_score"] + 0.3 * record["total_score"]
    return record["total_score"]

def save_scored_run(filename: str, run_data: dict):
    file_path = config.SCORED_RESULTS_DIR / filename
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(run_data, f, ensure_ascii=False, indent=2)

# Main structure
st.markdown("<h1 class='main-title' id='title-main'>TRLawBench-Practice</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle' id='title-sub'>İmer Hukuk LLM Benchmark - Avukatlık Pratiği Ölçümü</p>", unsafe_allow_html=True)

# Sidebar filters
st.sidebar.markdown("<h3 id='sb-hdr'>Ayarlar & Filtreler</h3>", unsafe_allow_html=True)
runs = get_scored_runs()

if not runs:
    st.info("Henüz değerlendirilmiş bir test çalışması (scored results) bulunamadı. Lütfen önce test çalıştırın ve değerlendirin.")
else:
    # Sidebar selection
    run_options = {f"{r[1]['model_name']} ({r[1]['mode']}) - {r[1]['run_id']}": (r[0], r[1]) for r in runs}
    selected_run_name = st.sidebar.selectbox("Test Çalışması Seçiniz", list(run_options.keys()), id="sb-run-select")
    selected_filename, selected_run_data = run_options[selected_run_name]
    
    # Calculate updated averages based on human override settings
    processed_results = []
    for r in selected_run_data["results"]:
        rec = r.copy()
        rec["final_score"] = get_final_score(r)
        processed_results.append(rec)
        
    df_results = pd.DataFrame(processed_results)
    
    # Summary Metrics
    st.markdown("<h2 id='summary-hdr'>Özet Metrikler</h2>", unsafe_allow_html=True)
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    
    avg_final = df_results["final_score"].mean() if not df_results.empty else 0
    hallucination_rate = df_results["hallucination_detected"].mean() if "hallucination_detected" in df_results.columns else 0
    trap_rate = df_results["trap_triggered"].mean() if "trap_triggered" in df_results.columns else 0
    avg_latency = df_results["duration"].mean() if "duration" in df_results.columns else 0
    
    with m_col1:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Genel Başarı Skoru</div>
            <div class='metric-value'>{avg_final:.1f} / 100</div>
        </div>
        """, unsafe_allow_html=True)
    with m_col2:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Halüsinasyon Oranı</div>
            <div class='metric-value'>{hallucination_rate:.1%}</div>
        </div>
        """, unsafe_allow_html=True)
    with m_col3:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Tuzaklara Düşme Oranı</div>
            <div class='metric-value'>{trap_rate:.1%}</div>
        </div>
        """, unsafe_allow_html=True)
    with m_col4:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Ortalama Yanıt Süresi</div>
            <div class='metric-value'>{avg_latency:.2f} sn</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("---")
    
    # Visualizations
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown("<h3 id='area-hdr'>Hukuk Alanı Bazlı Performans</h3>", unsafe_allow_html=True)
        if not df_results.empty:
            df_area = df_results.groupby("area")["final_score"].mean().reset_index()
            # Map areas to friendly names
            area_mapping = {
                "icra_hukuku": "İcra",
                "kira_hukuku": "Kira",
                "is_hukuku": "İş Hukuku",
                "ceza_hukuku": "Ceza",
                "tazminat_hukuku": "Tazminat",
                "idare_vergi_hukuku": "İdare/Vergi",
                "avukatlik_pratigi": "Avukatlık/UYAP",
                "aile_miras_hukuku": "Aile/Miras"
            }
            df_area["area_friendly"] = df_area["area"].map(area_mapping).fillna(df_area["area"])
            fig_area = px.bar(
                df_area, 
                x="area_friendly", 
                y="final_score",
                labels={"area_friendly": "Hukuk Alanı", "final_score": "Ortalama Skor"},
                color="final_score",
                color_continuous_scale="Purples",
                range_y=[0, 100]
            )
            fig_area.update_layout(template="plotly_dark", height=350)
            st.plotly_chart(fig_area, use_container_width=True)
            
    with chart_col2:
        st.markdown("<h3 id='type-hdr'>Görev Tipi Bazlı Performans</h3>", unsafe_allow_html=True)
        if not df_results.empty:
            df_type = df_results.groupby("task_type")["final_score"].mean().reset_index()
            type_mapping = {
                "mcq": "Çoktan Seçmeli",
                "sure_hesabi": "Süre Hesabı",
                "somut_olay_analizi": "Somut Olay",
                "belge_uretimi": "Belge Üretimi",
                "hata_yakalama": "Hata Yakalama"
            }
            df_type["type_friendly"] = df_type["task_type"].map(type_mapping).fillna(df_type["task_type"])
            fig_type = px.bar(
                df_type,
                x="type_friendly",
                y="final_score",
                labels={"type_friendly": "Görev Tipi", "final_score": "Ortalama Skor"},
                color="final_score",
                color_continuous_scale="Reds",
                range_y=[0, 100]
            )
            fig_type.update_layout(template="plotly_dark", height=350)
            st.plotly_chart(fig_type, use_container_width=True)
            
    st.markdown("---")
    
    # Leaderboard of all loaded runs
    st.markdown("<h3 id='leader-hdr'>Genel Karşılaştırma Tablosu (Leaderboard)</h3>", unsafe_allow_html=True)
    leaderboard_data = []
    for fn, rdata in runs:
        # compute average final scores factoring in human overrides
        scores = []
        hallucinations = 0
        traps = 0
        durations = []
        for result in rdata["results"]:
            scores.append(get_final_score(result))
            if result.get("hallucination_detected", False):
                hallucinations += 1
            if result.get("trap_triggered", False):
                traps += 1
            durations.append(result.get("duration", 0))
            
        cnt = len(rdata["results"])
        leaderboard_data.append({
            "Model Name": rdata["model_name"],
            "Evaluation Mode": rdata["mode"],
            "Average Score": round(sum(scores)/cnt, 1) if cnt else 0,
            "Hallucination Rate": f"{hallucinations/cnt:.1%}" if cnt else "0.0%",
            "Trap Triggered Rate": f"{traps/cnt:.1%}" if cnt else "0.0%",
            "Avg Response Time (s)": round(sum(durations)/cnt, 2) if cnt else 0,
            "Run ID": rdata["run_id"],
            "_filename": fn
        })
    df_leaderboard = pd.DataFrame(leaderboard_data).sort_values("Average Score", ascending=False)
    st.dataframe(df_leaderboard.drop(columns=["_filename"]), hide_index=True, use_container_width=True)
    
    st.markdown("---")
    
    # Detailed Inspector and Human Override
    st.markdown("<h2 id='inspect-hdr'>Detaylı Müfettiş & İnsan Puanı Müdahalesi</h2>", unsafe_allow_html=True)
    
    # Select question
    questions_list = {f"{q['question_id']} - {q['task_type']} ({q['area']})": q for q in processed_results}
    selected_q_name = st.selectbox("İncelemek İstediğiniz Görevi Seçiniz", list(questions_list.keys()), id="inspect-select")
    selected_q = questions_list[selected_q_name]
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown(f"#### Görev: `{selected_q['question_id']}`")
        st.info(f"**Soru:**\n{selected_q['question']}")
        st.success(f"**Beklenen Hukuki Çözüm (Gold Answer):**\n{selected_q['expected_answer']}")
        if selected_q.get("legal_basis"):
            st.markdown(f"**Yasal Dayanaklar:** {', '.join(selected_q['legal_basis'])}")
        if selected_q.get("trap_details"):
            st.warning(f"**Tuzak Detayı:** {selected_q['trap_details']}")
            
    with col_right:
        st.markdown(f"#### Aday Model Yanıtı")
        st.text_area("Modelin Yanıtı", selected_q["model_answer"], height=250, disabled=True, id="candidate-ans-ta")
        
        st.markdown("#### LLM-Judge Puanlama Ayrıntısı")
        st.markdown(f"**Toplam LLM-Judge Puanı:** `{selected_q['total_score']} / 100`")
        
        # Display rubric breakdown
        if selected_q.get("scores"):
            for crit, val in selected_q["scores"].items():
                st.write(f"- **{crit}**: {val} puan. *(Gerekçe: {selected_q.get('justifications', {}).get(crit, 'Belirtilmemiş')})*")
        st.write(f"**Genel Feedback:** {selected_q.get('feedback', '')}")
        st.write(f"**Halüsinasyon Tespit Edildi:** {'Evet ❌' if selected_q.get('hallucination_detected') else 'Hayır  (Güvenli) ✅'}")
        st.write(f"**Yasal Tuzağa Düştü:** {'Evet ❌' if selected_q.get('trap_triggered') else 'Hayır (Uyanık) ✅'}")
        
        st.markdown("---")
        st.markdown("#### ⚖️ İnsan Değerlendirici Formu")
        st.markdown("> **Not:** Değerlendirmeyi kaydettiğinizde final puanı **%70 İnsan Puanı + %30 LLM-Judge Puanı** formülü ile hesaplanacaktır.")
        
        is_override = st.checkbox("Bu görev için İnsan Puanını Etkinleştir (Override)", value=selected_q.get("human_override", False), id="human-override-cb")
        
        # Allow inputting custom total score
        human_score = st.number_input("İnsan Puanı (0 - 100)", min_value=0, max_value=100, 
                                     value=int(selected_q.get("human_total_score")) if selected_q.get("human_total_score") is not None else int(selected_q["total_score"]),
                                     id="human-score-input")
        human_feedback = st.text_area("İnsan Değerlendirici Yorumu", value=selected_q.get("human_feedback", ""), id="human-feedback-ta")
        
        if st.button("Puanı ve Geri Bildirimi Kaydet", id="save-override-btn"):
            # Update the specific record in run data
            for idx, r in enumerate(selected_run_data["results"]):
                if r["question_id"] == selected_q["question_id"]:
                    selected_run_data["results"][idx]["human_override"] = is_override
                    selected_run_data["results"][idx]["human_total_score"] = human_score if is_override else None
                    selected_run_data["results"][idx]["human_feedback"] = human_feedback
                    break
            
            # Recalculate average scored fields
            scores = []
            for r in selected_run_data["results"]:
                scores.append(get_final_score(r))
            selected_run_data["summary"]["average_score"] = sum(scores) / len(scores) if scores else 0
            
            # Save back to file
            save_scored_run(selected_filename, selected_run_data)
            st.success("İnsan değerlendirme sonuçları başarıyla kaydedildi! Sayfa yenileniyor...")
            st.rerun()
