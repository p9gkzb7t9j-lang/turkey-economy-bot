import streamlit as st
from google import genai
from google.genai import types

# 1. Настройка внешнего вида сайта (Конфиденциальный заголовок)
st.set_page_config(page_title="Ekonomi Veri Analizi", page_icon="📈", layout="centered")

# Инициализируем клиент Gemini
@st.cache_resource
def get_gemini_client():
    return genai.Client(api_key=st.secrets["AQ.Ab8RN6Ih-DQe9yfKQXrBNUDeK7uM6KpL9eu-Pl8QW20jZPnwRw"])

client = get_gemini_client()

# 2. Боковая панель (Строгий рабочий стиль без упоминания ИИ)
with st.sidebar:
    st.title("⚙️ Sistem Ayarları")
    st.write("Bu sistem, Türkiye'deki güncel enflasyon oranlarını ve makroekonomik verileri anlık olarak analiz etmek amacıyla geliştirilmiştir.")
    st.markdown("---")
    if st.button("Очистить чат 🔄"):
        st.session_state.messages = []
        st.rerun()

# Главный заголовок на странице
st.title("📈 Türkiye Ekonomi Asistanı")
st.caption("Türkiye Ekonomisi Veri Analiz ve Takip Sistemi")

# 3. Настройка конфигурации (Системная инструкция)
sistem_talimati = (
    "Sen uzman bir ekonomi asistanısın. Görevin SADECE Türkiye'deki enflasyon, "
    "ekonomi, güncel fiyatlar ve Merkez Bankası (TCMB) kararları hakkında sorulara cevap vermektir. "
    "Güncel ve doğru verileri bulmak için her zaman Google Arama'yı (Google Search) kullan. "
    "Eğer kullanıcı Türkiye ekonomisi dışında bir şey sorarsa (örneğin spor, yemek tarifi, yazılım kodu, diğer ülkeler), "
    "kesinlikle cevap verme ve sadece şunu söyle: 'Ben sadece Türkiye ekonomisi ve enflasyonu hakkında bilgi verebilirim.'"
)

config = types.GenerateContentConfig(
    system_instruction=sistem_talimati,
    tools=[{"google_search": {}}],
    temperature=0.3
)

# 4. Хранение истории чата
if "messages" not in st.session_state:
    st.session_state.messages = []

# Отображаем старые сообщения на экране (Преобразуем внутренние роли для красивого вывода на сайте)
for message in st.session_state.messages:
    display_role = "user" if message["role"] == "user" else "assistant"
    with st.chat_message(display_role):
        st.markdown(message["content"])

# 5. Поле ввода для пользователя
if soru := st.chat_input("Türkiye ekonomisi hakkında bir soru sorun..."):
    
    # Показываем вопрос пользователя на экране
    with st.chat_message("user"):
        st.markdown(soru)
    
    # Добавляем в историю роль 'user' (Google её принимает)
    st.session_state.messages.append({"role": "user", "content": soru})
    
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with st.spinner("Analiz ediliyor ve cevap hazırlanıyor..."):
            try:
                # ВАЖНОЕ ИСПРАВЛЕНИЕ: Форматируем историю строго под требования Google ('user' и 'model')
                formatted_history = []
                for m in st.session_state.messages:
                    # Если роль 'assistant', заменяем её для серверов Google на 'model'
                    api_role = "model" if m["role"] == "assistant" else "user"
                    formatted_history.append(
                        types.Content(role=api_role, parts=[types.Part.from_text(text=m["content"])])
                    )
                
                # Запрос к системе
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=formatted_history,
                    config=config
                )
                
                cevap_metni = response.text
                message_placeholder.markdown(cevap_metni)
                
                # Добавляем в историю роль 'assistant' для локального отображения
                st.session_state.messages.append({"role": "assistant", "content": cevap_metni})
                
            except Exception as e:
                st.error(f"Bir hata oluştu: {e}")
