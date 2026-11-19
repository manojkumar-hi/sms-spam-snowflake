import json
import os
import streamlit as st

st.set_page_config(page_title="SMS Spam Classifier", page_icon="📩", layout="centered")
st.title("📩 SMS Spam Classifier")
st.caption("Powered by Snowflake Model Registry (`SMS_SPAM_MODEL` V2)")

conn = st.connection("snowflake", ttl=os.getenv("SNOWFLAKE_CONNECTION_TTL"))
session = conn.session()

col1, col2 = st.columns(2)
if col1.button("Load Sample Spam"):
    st.session_state["sms_input"] = "Congratulations! You won a free $1000 gift card. Reply CLAIM now!"
if col2.button("Load Sample Normal SMS"):
    st.session_state["sms_input"] = "Hey, are we still meeting for coffee at 5 PM?"

message = st.text_area(
    "Enter an SMS message to classify:",
    key="sms_input",
    height=120,
    placeholder="Type or paste an SMS message here..."
)

if st.button("Check Message", type="primary"):
    if not message.strip():
        st.warning("Please enter a message first.")
    else:
        safe_text = message.replace("'", "''")
        query = f"""
            SELECT SPAM_ML_DB.MODELS.SMS_SPAM_MODEL!PREDICT('{safe_text}') AS PREDICTION
        """
        raw_res = session.sql(query).collect()[0]["PREDICTION"]
        result = json.loads(raw_res) if isinstance(raw_res, str) else raw_res
        val = result.get("RESULT", result.get("output_feature_0"))

        if val in ("Spam", 1):
            st.error("🚨 **Result: Spam**")
        else:
            st.success("✅ **Result: Not Spam**")