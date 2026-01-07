@st.dialog("👋 환영합니다! 자동 반편성 기능 안내")
def show_help_popup():
    # HTML/CSS를 사용하여 여백을 확 줄이고 가독성을 높였습니다.
    st.markdown("""
    <style>
        .info-box { 
            margin-bottom: 10px; /* 항목 사이 간격 좁힘 */
            background-color: #f8f9fa; 
            padding: 8px 12px; 
            border-radius: 5px; 
            border-left: 4px solid #5DADEC; /* 포인트 컬러 */
        }
        .info-title { 
            font-weight: bold; 
            font-size: 15px; 
            color: #333; 
            margin-bottom: 2px;
        }
        .info-desc { 
            font-size: 13px; 
            color: #555; 
            line-height: 1.4; 
        }
    </style>

    <div class="info-box">
        <div class="info-title">1. ⚡ 분리희망학생 자동 반편성</div>
        <div class="info-desc">서로 피하고 싶은 학생은 <b>1순위로</b> 다른 반에 배정합니다.</div>
    </div>

    <div class="info-box">
        <div class="info-title">2. 👯‍♀️ 쌍생아 분반/합반 자동 반편성</div>
        <div class="info-desc">합반/분반 희망을 최우선 반영하며, <b>특정 반에 쌍생아가 몰리지 않도록</b> 분산 배정합니다.</div>
    </div>

    <div class="info-box">
        <div class="info-title">3. 📛 동명이인 자동 반편성</div>
        <div class="info-desc">이름이 같은 학생이 한 반에 배정되지 않도록 자동으로 흩어놓습니다.</div>
    </div>

    <div class="info-box">
        <div class="info-title">4. ⚖️ 성별 및 인원 균형</div>
        <div class="info-desc">남/여 성비와 학급별 총 인원수를 최대한 균등하게 맞춥니다.</div>
    </div>

    <div class="info-box">
        <div class="info-title">5. 📊 곤란도 점수별 자동 반편성</div>
        <div class="info-desc">생활지도/학습부진 등 <b>곤란도 점수 총합</b>이 특정 반에 쏠리지 않게 분산합니다.</div>
    </div>

    <div class="info-box">
        <div class="info-title">6. 🏫 출신 학급 안배</div>
        <div class="info-desc">이전 학년의 같은 반 친구들이 한 곳에 너무 많이 몰리지 않도록 섞어줍니다.</div>
    </div>

    <div class="info-box">
        <div class="info-title">7. 📉 특수/통합 학급 정원 감축</div>
        <div class="info-desc">해당 학급은 인원을 적게 배정하며, <b>특수/통합 학생끼리는 서로 겹치지 않게</b> 분산합니다.</div>
    </div>
    """, unsafe_allow_html=True)
