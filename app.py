import streamlit as st
import pandas as pd
import io
import os
import re
import time
import random

# --- 1. [테마 및 라이브러리 설정] ---
if not os.path.exists(".streamlit"):
    os.makedirs(".streamlit")

try:
    with open(".streamlit/config.toml", "w", encoding="utf-8") as f:
        f.write("""[theme]
primaryColor = "#5DADEC"
backgroundColor = "#F0F2F6" 
secondaryBackgroundColor = "#FFFFFF"
textColor = "#262730"
font = "sans serif"
""")
except:
    pass

try:
    import xlsxwriter
except ImportError:
    st.error("⚠️ 라이브러리 설치 필요: 터미널에 'pip install xlsxwriter' 입력")
    st.stop()

# 사이드바 없이 넓은 화면 사용
st.set_page_config(page_title="반편성 프로그램 v32.0", layout="wide", initial_sidebar_state="collapsed") 

# CSS: 디자인 디테일 설정
st.markdown("""
<style>
    .stApp { background-color: #F4F6F9; }
    
    /* 한국어 단어 단위 줄바꿈 적용 */
    * { word-break: keep-all !important; }

    .block-container { 
        padding-top: 2rem; 
        padding-bottom: 5rem; 
        padding-left: 1rem; 
        padding-right: 1rem; 
        max-width: 100%;
    }

    /* 버튼 색상 강제 고정 (파란색) */
    button[kind="primary"] {
        background-color: #5DADEC !important;
        border-color: #5DADEC !important;
        color: white !important;
    }
    div.stButton > button {
        background-color: #5DADEC !important;
        color: white !important;
        border: none !important;
        font-weight: 700 !important;
    }
    div.stDownloadButton > button {
        background-color: #5DADEC !important;
        color: white !important;
        border: none !important;
        font-weight: 700 !important;
        white-space: pre-wrap !important;
        height: auto !important;
        padding-top: 12px !important;
        padding-bottom: 12px !important;
        line-height: 1.4 !important;
    }

    /* 드롭다운 및 입력창 테두리 강화 */
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div {
        border: 1px solid #B0BEC5 !important;
        border-radius: 4px !important;
        background-color: white !important;
    }

    /* 점수판 헤더 */
    .class-header {
        width: 100%; margin-bottom: 6px; background-color: white;
        border-top: 4px solid #5DADEC; border-radius: 6px; padding: 6px 2px;
        text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .class-title { font-size: 16px; font-weight: 800; color: #333; margin: 0; line-height: 1.2; white-space: nowrap; }
    .real-count-tag { font-size: 13px; color: #555; font-weight: 600; margin-left: 2px;}
    .score-text { font-size: 20px; font-weight: 900; color: #E65100; line-height: 1.0; margin: 3px 0; }
    .count-text { font-size: 11px; color: #333; font-weight: 700; margin: 2px 0 0 0; line-height: 1.2; white-space: nowrap; }
    .count-sub { font-size: 10px; color: #757575; font-weight: 600; display: block; margin-top: 1px; white-space: nowrap; }
    
    /* 뱃지 */
    .badge-container { display: flex; justify-content: center; flex-wrap: wrap; gap: 2px; margin-top: 3px; }
    .stat-badge { background-color: #F3E5F5; color: #7B1FA2; border: 1px solid #E1BEE7; border-radius: 4px; padding: 1px 3px; font-size: 9px; font-weight: bold; }
    .transfer-badge { background-color: #E3F2FD; color: #1565C0; border: 1px solid #90CAF9; border-radius: 4px; padding: 1px 3px; font-size: 9px; font-weight: bold; }
    
    /* 학생 카드 */
    .student-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 2px; }
    .student-card {
        width: 100%; border-radius: 4px; padding: 3px 1px;
        text-align: center; box-shadow: 0 1px 1px rgba(0,0,0,0.05);
        border: 1px solid rgba(0,0,0,0.05); line-height: 1.1; overflow: hidden;
    }
    .empty-card { width: 100%; height: 100%; min-height: 25px; background: transparent; border: none; }
    .bg-male { background-color: #E1F5FE; border-left: 3px solid #29B6F6; }
    .bg-female { background-color: #FCE4EC; border-left: 3px solid #EC407A; }
    .card-conflict { border: 2px solid #FF3D00 !important; background-color: #FFF3E0 !important; }
    
    .std-name { 
        font-size: 13px; font-weight: 800; color: #263238; margin: 0; 
        display: flex; justify-content: center; align-items: center; gap: 1px;
        padding-bottom: 1px; white-space: nowrap;
    }
    .prev-class { font-size: 10px; color: #90A4AE; font-weight: 600; margin-left: 1px; } 
    .std-note { font-size: 10px; color: #D81B60; font-weight: 700; display: block; margin-top: 2px; line-height: 1.2; }
    
    /* 뱃지 스타일 */
    .badge-in-card { display: inline-block; padding: 0px 3px; border-radius: 3px; font-size: 9px; font-weight: bold; margin-right: 2px; margin-bottom: 1px; vertical-align: middle; }
    .badge-transfer { background-color: #E3F2FD; color: #1565C0; border: 1px solid #90CAF9; } 
    .badge-separation { background-color: #FFF9C4; color: #F57F17; border: 1px solid #FBC02D; } 
    .badge-twin { background-color: #F1F8E9 !important; color: #33691E !important; border: 1px solid #DCEDC8 !important; }
    .badge-difficulty { background-color: #F5F5F5; color: #616161; border: 1px solid #E0E0E0; }

    .header-title-text { font-size: 24px; font-weight: 700; color: #333; margin-bottom: 0px; line-height: 1.5; white-space: nowrap; }
    .swap-label { font-size: 14px; font-weight: 700; color: #555; margin-bottom: 5px; }
    div[data-testid="stExpander"] { border: 1px solid #ddd; border-radius: 8px; background-color: white; }
</style>
""", unsafe_allow_html=True)

# 팝업 함수
@st.dialog("👋 환영합니다! 자동 반편성 기능 안내")
def show_help_popup():
    st.markdown("""
    **1. ⚡ 분리희망학생 자동 반편성**
    > 서로 피하고 싶은 학생은 **1순위로** 다른 반에 배정합니다.
    
    **2. 👯‍♀️ 쌍생아 분반/합반 자동 반편성**
    > 합반 희망은 무조건 같은 반으로, 분반 희망은 무조건 다른 반으로 배정합니다.
    
    **3. 📛 동명이인 자동 반편성**
    > 이름이 같은 학생이 한 반에 배정되지 않도록 자동으로 흩어놓습니다.
    
    **4. ⚖️ 성별 및 인원 균형**
    > 남학생과 여학생의 비율, 그리고 학급별 총 인원수를 최대한 균등하게 맞춥니다.
    
    **5. 📊 곤란도 점수별 자동 반편성**
    > 특정 반에 생활지도나 학습부진 학생이 몰리지 않도록 **점수 총합**을 고르게 분산합니다.
    
    **6. 🏫 출신 학급 안배**
    > 이전 학년의 같은 반 친구들이 한 곳에 너무 많이 몰리지 않도록 적절히 섞어줍니다.
    
    **7. 📉 특수/통합 학급 정원 감축**
    > 해당 학급은 타 학급 대비 학생 수를 적게 배정하며, **특수/통합 학생끼리는 한 반에 배정되지 않도록 분산**합니다.
    """)

st.title("🏫 반편성 프로그램 (v32.0)")

# 최초 1회 팝업 실행
if 'first_visit' not in st.session_state:
    show_help_popup()
    st.session_state['first_visit'] = False

# --- 2. 상단 컨트롤 패널 ---
col_set, col_down, col_blank = st.columns([2, 2.5, 5.5])

with col_set:
    target_classes = st.number_input("학급 수 설정", 1, 15, 4)
    class_names = ["가", "나", "다", "라", "마", "바", "사", "아", "자", "차", "카", "타", "파", "하"]
    target_class_names = class_names[:target_classes]

with col_down:
    template_cols = [
        "현재반", "번호", "이름", "성별", 
        "곤란도(1)", "곤란도점수(1)", "곤란도(2)", "곤란도점수(2)", 
        "비고(쌍생아/전출)", "쌍생아_이름", "쌍생아_반", "쌍생아반편성", 
        "분리희망학생_이름", "분리희망학생_반", "분리희망학생_번호"
    ]
    
    def get_template_excel():
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            pd.DataFrame(columns=template_cols).to_excel(writer, index=False, sheet_name='명단작성')
            ws = writer.sheets['명단작성']
            wb = writer.book
            header_format = wb.add_format({'bold': True, 'text_wrap': True, 'valign': 'vcenter', 'align': 'center', 'fg_color': '#DCE6F1', 'border': 1})
            for i, col in enumerate(template_cols):
                ws.write(0, i, col, header_format)
                # [수정] 텍스트가 잘리지 않도록 열 너비 확장
                ws.set_column(i, i, len(col) + 12)
                
            val_int = {'validate': 'integer', 'criteria': '>', 'value': 0, 'error_title': '입력 오류', 'error_message': '숫자만 입력할 수 있습니다. (예: 1, 2, 3)'}
            
            # 유효성 검사 적용
            col_rules = {}
            for c in [0, 1, 5, 7, 10, 13, 14]: col_rules[c] = val_int.copy() # 숫자 칼럼들
            
            val_list_reason = {
                'validate': 'list', 
                'source': ["학습부진", "교우관계", "생활지도", "학부모민원", "특수학급", "완전통합", "학교폭력", "다문화"],
                'error_type': 'information',
                'error_message': '목록에 없는 값이지만 입력은 가능합니다.'
            }
            col_rules[4] = val_list_reason # 곤란도(1)
            col_rules[6] = val_list_reason # 곤란도(2)
            
            val_list_note = {'validate': 'list', 'source': ["쌍생아", "전출예정"], 'error_message': '목록에 있는 값만 선택해주세요.'}
            col_rules[8] = val_list_note
            val_list_twin = {'validate': 'list', 'source': ["분반희망", "합반희망"], 'error_message': '목록에 있는 값만 선택해주세요.'}
            col_rules[11] = val_list_twin
            
            # [수정] 곤란도점수(2)에도 안내 메시지 추가
            msgs = {
                0: "현재 학급을\n숫자로 입력하세요.", 
                1: "학생 번호를\n숫자로 입력하세요.", 
                3: "남/여 중\n하나를 입력하세요.",
                5: "점수를\n숫자로 입력하세요.", # 곤란도점수(1)
                7: "점수를\n숫자로 입력하세요."  # 곤란도점수(2)
            }
            
            for c, msg in msgs.items():
                if c not in col_rules: col_rules[c] = {'validate': 'any'}
                col_rules[c]['input_title'] = '입력 안내'; col_rules[c]['input_message'] = msg
            
            for c, rule in col_rules.items():
                col_char = chr(65 + c) 
                ws.data_validation(f"{col_char}2:{col_char}1000", rule)
            
            ws.freeze_panes(1, 0)
        return output.getvalue()
    
    st.write("")
    st.write("")
    # 버튼 배치: 도움말 | 양식다운로드
    c_help, c_down = st.columns([0.8, 1.2])
    with c_help:
        if st.button("❓ 기능설명", use_container_width=True):
            show_help_popup()
    with c_down:
        st.download_button("📥 기초명단 양식", get_template_excel(), '반편성_양식.xlsx', type="primary", use_container_width=True)

# --- 3. 데이터 처리 함수 ---
def clean_text(text): return re.sub(r'[^가-힣a-zA-Z0-9, ]', '', str(text)) if pd.notna(text) else "" 
def clean_number(val): return str(int(float(val))) if pd.notna(val) and str(val).strip() != "" else ""
def get_given_name(full_name): return full_name[1:] if len(full_name) >= 2 else full_name

def build_conflict_map(df):
    lookup = {}
    conflict_pairs = set(); separation_pairs = set(); together_pairs = set()
    for _, r in df.iterrows():
        lookup[r['Internal_ID']] = r; lookup[f"{r['이름']}"] = r['Internal_ID']
        lookup[f"{r['이름']}_{r['현재반']}_{r['번호']}"] = r['Internal_ID']
        lookup[f"{r['이름']}_{r['현재반']}"] = r['Internal_ID']

    # 분리희망
    for _, r in df.iterrows():
        my_id = r['Internal_ID']; t_name = r['분리희망학생_이름']
        if t_name:
            t_key = f"{t_name}_{r['분리희망학생_반']}_{r['분리희망학생_번호']}"
            target_id = lookup.get(t_key)
            if not isinstance(target_id, str): target_id = lookup.get(t_name)
            if isinstance(target_id, str) and target_id != my_id:
                pair = frozenset([my_id, target_id])
                conflict_pairs.add(pair); separation_pairs.add(pair)
    
    # 동명이인
    given_name_map = {} 
    for _, r in df.iterrows():
        g_name = get_given_name(r['이름'])
        if g_name:
            if g_name not in given_name_map: given_name_map[g_name] = []
            given_name_map[g_name].append(r['Internal_ID'])
    for g_name, ids in given_name_map.items():
        if len(ids) > 1:
            for i in range(len(ids)):
                for j in range(i + 1, len(ids)):
                    conflict_pairs.add(frozenset([ids[i], ids[j]]))

    # 쌍생아
    for _, r in df.iterrows():
        if pd.notna(r['쌍생아_이름']) and str(r['쌍생아_이름']).strip() != "":
            my_id = r['Internal_ID']
            t_key = f"{r['쌍생아_이름']}_{r['쌍생아_반']}"
            target_id = lookup.get(t_key)
            if isinstance(target_id, str) and target_id != my_id:
                pair = frozenset([my_id, target_id])
                if r['쌍생아반편성'] == "분반희망": conflict_pairs.add(pair)
                elif r['쌍생아반편성'] == "합반희망": together_pairs.add(pair)

    return conflict_pairs, separation_pairs, together_pairs, lookup

# 관계 자동 동기화
def sync_relationships(df):
    for idx, row in df.iterrows():
        if pd.notna(row['쌍생아_이름']) and str(row['쌍생아_이름']).strip() != "":
            target_name = row['쌍생아_이름']
            target_class = str(int(float(row['쌍생아_반']))) if pd.notna(row['쌍생아_반']) else ""
            targets = df[ (df['이름'] == target_name) & (df['현재반'].astype(str).replace(r'\.0$', '', regex=True) == target_class) ]
            if not targets.empty:
                t_idx = targets.index[0]
                if pd.isna(df.at[t_idx, '쌍생아_이름']) or str(df.at[t_idx, '쌍생아_이름']).strip() == "":
                    df.at[t_idx, '쌍생아_이름'] = row['이름']
                    df.at[t_idx, '쌍생아_반'] = row['현재반']
                    df.at[t_idx, '쌍생아반편성'] = row['쌍생아반편성']
                    if "쌍생아" not in str(df.at[t_idx, '비고']):
                        df.at[t_idx, '비고'] = (str(df.at[t_idx, '비고']) + " 쌍생아").strip()

    for idx, row in df.iterrows():
        if pd.notna(row['분리희망학생_이름']) and str(row['분리희망학생_이름']).strip() != "":
            target_name = row['분리희망학생_이름']
            target_class = str(int(float(row['분리희망학생_반']))) if pd.notna(row['분리희망학생_반']) else ""
            targets = df[ (df['이름'] == target_name) & (df['현재반'].astype(str).replace(r'\.0$', '', regex=True) == target_class) ]
            if not targets.empty:
                t_idx = targets.index[0]
                if pd.isna(df.at[t_idx, '분리희망학생_이름']) or str(df.at[t_idx, '분리희망학생_이름']).strip() == "":
                    df.at[t_idx, '분리희망학생_이름'] = row['이름']
                    df.at[t_idx, '분리희망학생_반'] = row['현재반']
                    df.at[t_idx, '분리희망학생_번호'] = row['번호']
    return df

# --- 4. 파일 업로드 ---
st.markdown("---")
uploaded_files = st.file_uploader("엑셀 파일 선택 (여러 개 가능)", type=['xlsx', 'xls', 'csv'], accept_multiple_files=True)

if uploaded_files:
    curr_files = sorted([f.name for f in uploaded_files])
    if 'uploaded_file_names' not in st.session_state or st.session_state['uploaded_file_names'] != curr_files:
        all_dfs = []
        for file in uploaded_files:
            try:
                df = pd.read_csv(file) if file.name.endswith('.csv') else pd.read_excel(file)
                df.columns = df.columns.str.replace(' ', '').str.strip()
                all_dfs.append(df)
            except Exception as e: st.error(f"오류: {e}")

        if all_dfs:
            df = pd.concat(all_dfs, ignore_index=True)
            rename_map = {'비고(쌍생아/전출)': '비고', '비고(쌍생아/전출/동명이인)': '비고', '비고(쌍생아/전출예정)': '비고'}
            df.rename(columns=rename_map, inplace=True)
            df['이름'] = df['이름'].apply(clean_text)
            
            num_cols = ['현재반', '번호', '분리희망학생_반', '분리희망학생_번호', '쌍생아_반']
            if '쌍생아_번호' in df.columns: num_cols.append('쌍생아_번호')
            for c in num_cols: df[c] = df[c].apply(clean_number) if c in df.columns else ""
            for c in ['분리희망학생_이름', '쌍생아_이름', '쌍생아반편성']: df[c] = df[c].apply(clean_text) if c in df.columns else ""
            
            # 2열 곤란도 및 점수 처리
            s1 = pd.to_numeric(df['곤란도점수(1)'], errors='coerce').fillna(0)
            s2 = pd.to_numeric(df['곤란도점수(2)'], errors='coerce').fillna(0)
            df['곤란도점수'] = s1 + s2
            
            r1 = df['곤란도(1)'].fillna('').astype(str).str.strip()
            r2 = df['곤란도(2)'].fillna('').astype(str).str.strip()
            df['곤란도'] = r1
            df.loc[(r1 != "") & (r2 != ""), '곤란도'] = r1 + "," + r2
            df.loc[(r1 == "") & (r2 != ""), '곤란도'] = r2
            
            df['비고'] = df['비고'].fillna("") if '비고' in df.columns else ""
            df['is_transfer'] = df['비고'].str.contains('전출', na=False)
            df['Internal_ID'] = [f"ID_{i}" for i in range(len(df))]
            
            # 관계 자동 동기화
            df = sync_relationships(df)
            
            st.session_state['student_data'] = df
            st.session_state['uploaded_file_names'] = curr_files
            st.success(f"✅ {len(df)}명 로드 완료")

# --- 5. [v15.0] 3단계 우선순위 배정 ---
def run_assignment(df, class_names):
    df = df.copy()
    conflict_pairs, _, together_pairs, _ = build_conflict_map(df)
    classes = {c: {'students': [], 'score_sum': 0, 'm': 0, 'f': 0, 'conflict_ids': set(), 'reasons': {}, 'virtual_cnt': 0, 'has_special': False} for c in class_names}
    
    conflict_counts = {id: 0 for id in df['Internal_ID']}
    for pair in conflict_pairs:
        for p in pair: conflict_counts[p] += 1
    df['conflict_degree'] = df['Internal_ID'].map(conflict_counts)
    
    id_to_prev = df.set_index('Internal_ID')['현재반'].apply(lambda x: str(int(float(x))) if pd.notna(x) and str(x).strip() else "").to_dict()

    transfer_mask = df['is_transfer'] == True
    high_score_mask = (df['곤란도점수'] > 0) & (~transfer_mask)
    regular_mask = (df['곤란도점수'] == 0) & (~transfer_mask)
    
    group_1 = df[high_score_mask].sort_values(by=['conflict_degree', '곤란도점수', '이름'], ascending=[False, False, True])
    for _, row in group_1.iterrows(): assign_with_priority(row, classes, conflict_pairs, together_pairs, "SCORE_BALANCE", df, id_to_prev)
    
    group_2 = df[regular_mask].sort_values(by=['conflict_degree', '성별', '이름'], ascending=[False, True, True])
    for _, row in group_2.iterrows(): assign_with_priority(row, classes, conflict_pairs, together_pairs, "REAL_COUNT_BALANCE", df, id_to_prev)
    
    group_3 = df[transfer_mask].sort_values(by=['conflict_degree'], ascending=[False])
    for _, row in group_3.iterrows(): assign_with_priority(row, classes, conflict_pairs, together_pairs, "CUSHION_BALANCE", df, id_to_prev)
        
    for c_name, c_info in classes.items():
        for s_id in c_info['students']: df.loc[df['Internal_ID'] == s_id, '배정반'] = c_name
    return df

def assign_with_priority(row, classes, conflict_pairs, together_pairs, priority_mode, df, id_to_prev):
    s_id = row['Internal_ID']; s_score = row['곤란도점수']; s_gender = row['성별']; s_reason = row['곤란도']
    s_prev = id_to_prev.get(s_id, "")
    
    is_special = "특수" in s_reason or "통합" in s_reason

    forced_class = None
    for pair in together_pairs:
        if s_id in pair:
            others = [x for x in pair if x != s_id]
            for c_name, c_info in classes.items():
                if others[0] in c_info['students']: forced_class = c_name; break
        if forced_class: break
    
    if forced_class:
        best_class = forced_class
    else:
        my_enemies = set()
        for pair in conflict_pairs:
            if s_id in pair: my_enemies.update(pair)
                
        class_costs = []
        transfer_ids = set(df[df['is_transfer']].Internal_ID.values)

        for c_name, c_info in classes.items():
            cost = 0
            if not my_enemies.isdisjoint(c_info['conflict_ids']): cost += float('inf')
            
            if is_special and c_info['has_special']:
                cost += 1000000

            if priority_mode == "SCORE_BALANCE":
                cost += (c_info['score_sum'] * 1000)
                # s_reason이 이제 콤마로 연결된 문자열이므로, reasons 카운트에 포함되는지 확인
                for r_key in c_info['reasons']:
                    if r_key in s_reason: cost += 500
                cost += (len(c_info['students']) * 10) 
            elif priority_mode == "REAL_COUNT_BALANCE":
                real_cnt = len([sid for sid in c_info['students'] if sid not in transfer_ids])
                cost += (c_info['virtual_cnt'] * 10000)
                g_cnt = c_info['m'] if s_gender == '남' else c_info['f']
                cost += (g_cnt * 1000)
            elif priority_mode == "CUSHION_BALANCE":
                cost += (len(c_info['students']) * 1000)
                g_cnt = c_info['m'] if s_gender == '남' else c_info['f']
                cost += (g_cnt * 500)
            
            if s_prev:
                same_origin_cnt = 0
                for exist_id in c_info['students']:
                    if id_to_prev.get(exist_id) == s_prev:
                        same_origin_cnt += 1
                cost += (same_origin_cnt * 100)

            if row['is_transfer']:
                transfer_cnt = 0
                for exist_id in c_info['students']:
                    if df.loc[df['Internal_ID'] == exist_id, 'is_transfer'].values[0]:
                        transfer_cnt += 1
                cost += (transfer_cnt * 5000)

            class_costs.append((cost, c_name))
            
        class_costs.sort(key=lambda x: x[0])
        best_class = random.choice(list(classes.keys())) if class_costs[0][0] == float('inf') else class_costs[0][1]
        
    c = classes[best_class]
    c['students'].append(s_id); c['conflict_ids'].add(s_id)
    
    if is_special:
        c['virtual_cnt'] += 2
        c['has_special'] = True
    else:
        c['virtual_cnt'] += 1

    if s_gender == '남': c['m'] += 1
    else: c['f'] += 1
    if not row['is_transfer']:
        c['score_sum'] += s_score
        if s_reason:
            reasons = [r.strip() for r in s_reason.split(',') if r.strip()]
            for r in reasons:
                if r not in c['reasons']: c['reasons'][r] = 0
                c['reasons'][r] += 1

st.write("")
col_btn_start, _ = st.columns([1.5, 8.5]) 
with col_btn_start:
    if st.button("🚀 자동 반편성 시작", type="primary", use_container_width=False):
        if 'student_data' in st.session_state:
            st.session_state['assigned_data'] = run_assignment(st.session_state['student_data'], target_class_names)
        else: st.warning("파일을 업로드하세요.")

# --- 6. 결과 화면 ---
if 'assigned_data' in st.session_state:
    st.divider()
    df = st.session_state['assigned_data']
    conflict_pairs, separation_pairs, together_pairs, _ = build_conflict_map(df)
    current_map = df.set_index('Internal_ID')['배정반'].to_dict()
    df['gender_rank'] = df['성별'].map({'여': 1, '남': 2}).fillna(3)
    df['display_icon'] = ""
    
    for idx, row in df.iterrows():
        s_id = row['Internal_ID']; my_cls = row['배정반']; icon = ""
        is_separated_ok = False
        for pair in separation_pairs:
            if s_id in pair:
                others = [x for x in pair if x != s_id]
                if others and others[0] in current_map:
                    if current_map[others[0]] != my_cls: is_separated_ok = True
                    else: icon = "⚡"; is_separated_ok = False; break
        for pair in conflict_pairs:
            if s_id in pair:
                others = [x for x in pair if x != s_id]
                if others and others[0] in current_map and current_map[others[0]] == my_cls: icon = "⚡"; break
        for pair in together_pairs:
            if s_id in pair:
                others = [x for x in pair if x != s_id]
                if others and others[0] in current_map:
                    if current_map[others[0]] != my_cls: icon = "⚡"; break
        df.at[idx, 'display_icon'] = icon

    # 1. 시각화 보드
    col_h_1, col_h_2, col_h_3, col_h_spacer = st.columns([1.5, 2.5, 4.0, 2.0], gap="small")
    with col_h_1: st.markdown("<div class='header-title-text'>👀 학급별 구성</div>", unsafe_allow_html=True)
    
    # 엑셀 저장
    with col_h_2:
        output_assigned = io.BytesIO()
        export_cols = ['배정반', '번호', '이름', '성별', '현재반', '비고', '곤란도', '쌍생아_이름', '분리희망학생_이름']
        save_df_assigned = df.sort_values(['배정반', 'is_transfer', 'gender_rank', '이름']).copy()
        save_df_assigned['번호'] = save_df_assigned.groupby('배정반').cumcount() + 1
        valid_cols = [c for c in export_cols if c in save_df_assigned.columns]
        save_df_assigned = save_df_assigned[valid_cols]
        with pd.ExcelWriter(output_assigned, engine='xlsxwriter') as writer:
            save_df_assigned.to_excel(writer, index=False, sheet_name='전체')
            for cls in target_class_names:
                cls_df = save_df_assigned[save_df_assigned['배정반'] == cls]
                cls_df.to_excel(writer, index=False, sheet_name=f'{cls}반')
            for sheet in writer.sheets.values():
                for i, col in enumerate(save_df_assigned.columns): sheet.set_column(i, i, 12)
                
        output_current = io.BytesIO()
        df['current_class_int'] = pd.to_numeric(df['현재반'], errors='coerce').fillna(999).astype(int)
        df['current_num_int'] = pd.to_numeric(df['번호'], errors='coerce').fillna(999).astype(int)
        save_df_current = df.sort_values(['current_class_int', 'current_num_int'])
        current_export_cols = ['현재반', '번호', '이름', '성별', '배정반', '비고', '곤란도']
        valid_curr_cols = [c for c in current_export_cols if c in save_df_current.columns]
        save_df_current_final = save_df_current[valid_curr_cols]
        with pd.ExcelWriter(output_current, engine='xlsxwriter') as writer:
            save_df_current_final.to_excel(writer, index=False, sheet_name='전체 명단')
            unique_classes = sorted(df['current_class_int'].unique())
            for c_num in unique_classes:
                if c_num == 999: continue
                c_df = save_df_current_final[save_df_current['current_class_int'] == c_num]
                if not c_df.empty: c_df.to_excel(writer, index=False, sheet_name=f'{c_num}반')
            for sheet in writer.sheets.values():
                for i, col in enumerate(save_df_current_final.columns): sheet.set_column(i, i, 12)

        c_btn1, c_btn2 = st.columns(2)
        c_btn1.download_button("📥 배정반\u00A0기준\n명단", output_assigned.getvalue(), "반편성_배정반기준.xlsx", type="primary", use_container_width=True)
        c_btn2.download_button("📥 현재반\u00A0기준\n명단", output_current.getvalue(), "반편성_현재반기준.xlsx", type="primary", use_container_width=True)

    with col_h_3:
        st.markdown("""<div style="margin-top: 10px; font-weight: 600; font-size: 13px; color: #555; white-space: nowrap;">
            <span style='display:inline-block; margin-right:5px;'>범례:</span>
            <span style='color:#C2185B; background-color:#FCE4EC; border:1px solid #EC407A; padding: 2px 4px; border-radius:4px;'>■ 여학생</span>
            <span style='color:#1565C0; background-color:#E3F2FD; border:1px solid #90CAF9; padding: 2px 4px; border-radius:4px; margin-left:3px;'>■ 남학생</span>
            <span style='color:#78909C; margin-left:5px; font-size:11px;'>*이름(숫자)는 이전 반</span>
            <span style='color:#78909C; margin-left:5px; font-size:11px;'>*곤란도(점수)</span>
            </div>""", unsafe_allow_html=True)
    with col_h_spacer: st.empty()

    n_classes = len(target_class_names)
    if n_classes == 1: content_cols = [st.columns([3,1,3])[1]]
    else: content_cols = st.columns(n_classes, gap="small")

    for i, cls in enumerate(target_class_names):
        c_df = df[df['배정반'] == cls]
        score = int(c_df['곤란도점수'].sum())
        m_total = len(c_df[c_df['성별']=='남']); f_total = len(c_df[c_df['성별']=='여'])
        m_real = len(c_df[(c_df['성별']=='남') & (~c_df['is_transfer'])])
        f_real = len(c_df[(c_df['성별']=='여') & (~c_df['is_transfer'])])
        transfer_cnt = len(c_df[c_df['is_transfer']])
        real_cnt = m_real + f_real 
        
        badges_html = ""
        if transfer_cnt > 0: badges_html += f"<span class='transfer-badge'>전출:{transfer_cnt}</span>"
        
        all_reasons = []
        for r_str in c_df['곤란도'].dropna():
            if r_str.strip():
                all_reasons.extend([x.strip() for x in r_str.split(',') if x.strip()])
        reason_counts = pd.Series(all_reasons).value_counts()
        
        for reason, count in reason_counts.items():
            badges_html += f"<span class='stat-badge'>{reason}:{count}</span>"
        
        count_html = f"<div class='count-text'>여 {f_total}명 / 남 {m_total}명</div><div class='count-sub'>(전출제외: 여 {f_real} / 남 {m_real})</div>"

        with content_cols[i]:
            st.markdown(f"""<div class="class-header"><div class="class-title">{cls}반 <span class="real-count-tag">({real_cnt}명)</span></div><div class="score-text">곤란도: {score}점</div>{count_html}<div class="badge-container">{badges_html}</div></div>""", unsafe_allow_html=True)
            
            f_rows = c_df[c_df['성별'] == '여'].sort_values(['is_transfer', '이름'])
            m_rows = c_df[c_df['성별'] == '남'].sort_values(['is_transfer', '이름'])
            
            max_len = max(len(f_rows), len(m_rows))
            cards_html = ""
            for j in range(max_len):
                if j < len(f_rows):
                    r = f_rows.iloc[j]
                    bg_class = "bg-female"
                    conflict = "card-conflict" if "⚡" in r['display_icon'] else ""
                    p_disp = f"<span class='prev-class'>({str(int(float(r['현재반'])))})</span>" if pd.notna(r['현재반']) and str(r['현재반']).strip() else ""
                    
                    badges_str = ""
                    if r['is_transfer']: badges_str += "<span class='badge-in-card badge-transfer'>전출</span>"
                    if pd.notna(r['분리희망학생_이름']) and str(r['분리희망학생_이름']).strip() != "":
                        badges_str += "<span class='badge-in-card badge-separation'>분리희망</span>"
                    
                    note = r['곤란도'] if r['곤란도'] else ""; sc = int(r['곤란도점수'])
                    rem = str(r['비고']).replace("전출예정","").strip() if pd.notna(r['비고']) else ""
                    
                    if "쌍생아" in rem:
                        twin_text = "쌍생아"
                        if pd.notna(r['쌍생아반편성']):
                            if r['쌍생아반편성'] == "분반희망": twin_text = "쌍생아(분반)"
                            elif r['쌍생아반편성'] == "합반희망": twin_text = "쌍생아(합반)"
                        badges_str += f"<span class='badge-in-card badge-twin'>{twin_text}</span>"
                        rem = rem.replace("쌍생아", "").strip()

                    note_badges = ""
                    if note:
                        reasons = [x.strip() for x in note.split(',') if x.strip()]
                        for rea in reasons:
                            note_badges += f"<span class='badge-in-card badge-difficulty'>{rea}</span>"
                        if sc > 0: note_badges += f"<span style='font-size:10px; font-weight:bold; color:#E65100; margin-left:2px;'>({sc})</span>"

                    if rem: note_badges += f" <span style='font-size:10px; font-weight:bold; color:#D81B60;'>{rem}</span>"
                    
                    final_note = badges_str + note_badges
                    cards_html += f"""<div class="student-card {bg_class} {conflict}"><div class="std-name">{r['display_icon']} {r['이름']}{p_disp}</div><div style='margin-top:2px; line-height:1.2;'>{final_note}</div></div>"""
                else: cards_html += """<div class="empty-card"></div>"""
                
                if j < len(m_rows):
                    r = m_rows.iloc[j]
                    bg_class = "bg-male"
                    conflict = "card-conflict" if "⚡" in r['display_icon'] else ""
                    p_disp = f"<span class='prev-class'>({str(int(float(r['현재반'])))})</span>" if pd.notna(r['현재반']) and str(r['현재반']).strip() else ""
                    
                    badges_str = ""
                    if r['is_transfer']: badges_str += "<span class='badge-in-card badge-transfer'>전출</span>"
                    if pd.notna(r['분리희망학생_이름']) and str(r['분리희망학생_이름']).strip() != "":
                        badges_str += "<span class='badge-in-card badge-separation'>분리희망</span>"

                    note = r['곤란도'] if r['곤란도'] else ""; sc = int(r['곤란도점수'])
                    rem = str(r['비고']).replace("전출예정","").strip() if pd.notna(r['비고']) else ""
                    
                    if "쌍생아" in rem:
                        twin_text = "쌍생아"
                        if pd.notna(r['쌍생아반편성']):
                            if r['쌍생아반편성'] == "분반희망": twin_text = "쌍생아(분반)"
                            elif r['쌍생아반편성'] == "합반희망": twin_text = "쌍생아(합반)"
                        badges_str += f"<span class='badge-in-card badge-twin'>{twin_text}</span>"
                        rem = rem.replace("쌍생아", "").strip()

                    note_badges = ""
                    if note:
                        reasons = [x.strip() for x in note.split(',') if x.strip()]
                        for rea in reasons:
                            note_badges += f"<span class='badge-in-card badge-difficulty'>{rea}</span>"
                        if sc > 0: note_badges += f"<span style='font-size:10px; font-weight:bold; color:#E65100; margin-left:2px;'>({sc})</span>"

                    if rem: note_badges += f" <span style='font-size:10px; font-weight:bold; color:#D81B60;'>{rem}</span>"
                    
                    final_note = badges_str + note_badges
                    cards_html += f"""<div class="student-card {bg_class} {conflict}"><div class="std-name">{r['display_icon']} {r['이름']}{p_disp}</div><div style='margin-top:2px; line-height:1.2;'>{final_note}</div></div>"""
                else: cards_html += """<div class="empty-card"></div>"""
            st.markdown(f"""<div class="student-grid">{cards_html}</div>""", unsafe_allow_html=True)

    # 2. 1:1 학생 교환
    st.divider()
    st.subheader("🔀 1:1 학생 교환")
    
    with st.container(border=True):
        if 'swap_source_class' not in st.session_state: st.session_state['swap_source_class'] = target_class_names[0]
        if 'swap_target_class' not in st.session_state: st.session_state['swap_target_class'] = target_class_names[1] if len(target_class_names) > 1 else target_class_names[0]
        c1, col_swap_left, col_swap_action, col_swap_right, c5 = st.columns([1, 2.5, 0.5, 2.5, 1])
        with col_swap_left:
            st.markdown("<div class='swap-label'>📤 보내는 반 (Source)</div>", unsafe_allow_html=True)
            s_cls = st.selectbox("반 선택 (보냄)", target_class_names, key="s_cls_key", label_visibility="collapsed")
            s_students_df = df[df['배정반'] == s_cls].sort_values(['이름'])
            s_std_name = st.selectbox("학생 선택 (보냄)", s_students_df['이름'].tolist(), key="s_std_key", label_visibility="collapsed") if not s_students_df.empty else None
            if s_std_name:
                s_row = df[(df['배정반'] == s_cls) & (df['이름'] == s_std_name)].iloc[0]
                st.info(f"👤 {s_row['성별']} | 📊 {int(s_row['곤란도점수'])}점 | 📝 {s_row['곤란도']}")
        with col_swap_right:
            st.markdown("<div class='swap-label'>📥 받는 반 (Target)</div>", unsafe_allow_html=True)
            t_cls = st.selectbox("반 선택 (받음)", target_class_names, index=1 if len(target_class_names)>1 else 0, key="t_cls_key", label_visibility="collapsed")
            t_students_df = df[df['배정반'] == t_cls].sort_values(['이름'])
            t_student_list = ["(선택 안 함 - 이동만 하기)"] + t_students_df['이름'].tolist()
            t_std_name = st.selectbox("학생 선택 (받음/교환)", t_student_list, key="t_std_key", label_visibility="collapsed")
            if t_std_name and t_std_name != "(선택 안 함 - 이동만 하기)":
                t_row = df[(df['배정반'] == t_cls) & (df['이름'] == t_std_name)].iloc[0]
                st.info(f"👤 {t_row['성별']} | 📊 {int(t_row['곤란도점수'])}점 | 📝 {t_row['곤란도']}")
            elif t_std_name == "(선택 안 함 - 이동만 하기)": st.success("👉 왼쪽 학생을 이 반으로 보냅니다.")
        with col_swap_action:
            st.write(""); st.write(""); st.write("") 
            if st.button("🔄", type="primary", use_container_width=True, help="실행"):
                if s_cls == t_cls: st.warning("같은 반입니다.")
                elif not s_std_name: st.warning("학생을 선택하세요.")
                else:
                    s_id = df[(df['배정반'] == s_cls) & (df['이름'] == s_std_name)]['Internal_ID'].values[0]
                    if t_std_name and t_std_name != "(선택 안 함 - 이동만 하기)":
                        t_id = df[(df['배정반'] == t_cls) & (df['이름'] == t_std_name)]['Internal_ID'].values[0]
                        st.session_state['assigned_data'].loc[st.session_state['assigned_data']['Internal_ID'] == s_id, '배정반'] = t_cls
                        st.session_state['assigned_data'].loc[st.session_state['assigned_data']['Internal_ID'] == t_id, '배정반'] = s_cls
                        st.toast(f"🔄 {s_std_name} ↔ {t_std_name} 교환 완료!")
                    else:
                        st.session_state['assigned_data'].loc[st.session_state['assigned_data']['Internal_ID'] == s_id, '배정반'] = t_cls
                        st.toast(f"👉 {s_std_name} 이동 완료!")
                    time.sleep(0.5); st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # 3. 이동 작업대
    st.write("")
    with st.expander("📋 전체 명단 상세 편집 열기"):
        col_f1, col_f2, col_f3 = st.columns([1, 1, 1])
        with col_f1: search_name = st.text_input("🔍 이름 검색")
        with col_f2: filter_new_cls = st.multiselect("배정반", target_class_names)
        with col_f3: 
            prev_classes = sorted([str(int(float(x))) for x in df['현재반'].unique() if pd.notna(x) and str(x).strip() != ""])
            filter_prev_cls = st.multiselect("현재반", prev_classes)
        view_df = df.copy()
        if 'gender_rank' not in view_df.columns: view_df['gender_rank'] = view_df['성별'].map({'여': 1, '남': 2}).fillna(3)
        
        def get_status_str(row):
            statuses = []
            if row['is_transfer']: statuses.append("🟦 전출")
            if pd.notna(row['분리희망학생_이름']) and str(row['분리희망학생_이름']).strip() != "":
                statuses.append("🟧 분리희망")
            rem = str(row['비고'])
            if "쌍생아" in rem or (pd.notna(row['쌍생아_이름']) and str(row['쌍생아_이름']).strip() != ""):
                mode = row['쌍생아반편성'] if pd.notna(row['쌍생아반편성']) else ""
                if mode == "분반희망": statuses.append("🟩 쌍생아(분반)")
                elif mode == "합반희망": statuses.append("🟩 쌍생아(합반)")
                else: statuses.append("🟩 쌍생아")
            return " ".join(statuses)

        view_df['상태'] = view_df.apply(get_status_str, axis=1)

        if search_name: view_df = view_df[view_df['이름'].str.contains(search_name)]
        if filter_prev_cls: 
            view_df['temp_prev'] = view_df['현재반'].apply(lambda x: str(int(float(x))) if pd.notna(x) and str(x).strip()!="" else "")
            view_df = view_df[view_df['temp_prev'].isin(filter_prev_cls)]
        if filter_new_cls: view_df = view_df[view_df['배정반'].isin(filter_new_cls)]
        view_df = view_df.sort_values(['배정반', 'gender_rank', 'is_transfer', '이름'])
        
        editor_cols = ['현재반', '이름', '상태', '성별', '배정반', '곤란도', '곤란도점수', '분리희망학생_이름', '분리희망학생_반', '비고', 'Internal_ID']
        edited_df = st.data_editor(view_df[editor_cols], key="main_editor", hide_index=True, column_config={
            "현재반": st.column_config.NumberColumn("이전 반", width="small", disabled=True, format="%d"),
            "이름": st.column_config.TextColumn("이름", width="small", disabled=True),
            "상태": st.column_config.TextColumn("상태", width="medium", disabled=True),
            "성별": st.column_config.TextColumn("성별", width="small", disabled=True),
            "배정반": st.column_config.SelectboxColumn("배정반", width="small", options=target_class_names, required=True),
            "곤란도": st.column_config.TextColumn("곤란도", width="medium", disabled=True),
            "곤란도점수": st.column_config.NumberColumn("점수", width="small", disabled=True),
            "분리희망학생_이름": st.column_config.TextColumn("분리학생이름", width="medium", disabled=True),
            "분리희망학생_반": st.column_config.TextColumn("분리학생이전반", width="small", disabled=True),
            "비고": st.column_config.TextColumn("비고", width="medium", disabled=True),
            "Internal_ID": None
        }, use_container_width=True, height=600)
        
        is_changed = False
        for idx, row in edited_df.iterrows():
            s_id = row['Internal_ID']; new_val = row['배정반']
            old_val = df.loc[df['Internal_ID']==s_id, '배정반'].values[0]
            if new_val != old_val:
                st.session_state['assigned_data'].loc[st.session_state['assigned_data']['Internal_ID']==s_id, '배정반'] = new_val
                is_changed = True
        if is_changed: st.rerun()
