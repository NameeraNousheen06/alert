import streamlit as st
import boto3

REGION = 'us-east-1'
SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:980921742685:gstreminder'
dynamodb = boto3.resource('dynamodb', region_name=REGION)
sns = boto3.client('sns', region_name=REGION)
table = dynamodb.Table('gstreminders')

st.set_page_config(page_title="GST Reminder System", page_icon="📧", layout="centered")
st.title("GST Reminder System")
st.write("Enter your GST details below to set a reminder and receive a professional email notification.")

with st.form("gst_form"):
    user_id = st.text_input("User ID")
    due_date = st.date_input("GST Due Date")
    amount = st.number_input("GST Amount", min_value=0, step=1)
    submitted = st.form_submit_button("Set Reminder")

    if submitted:
        if not user_id or not due_date or not amount:
            st.error("All fields are required!")
        else:
            try:
                table.put_item(Item={
                    'user_id': user_id,
                    'due_date': str(due_date),
                    'amount': int(amount)
                })
                response = table.get_item(Key={'user_id': user_id})
                item = response.get('Item', {})
                email_subject = "GST Payment Due Reminder"
                email_body = f"""
Dear GST Payer,\n\nThis is a friendly reminder that your GST payment is due soon. Please find your GST details below:\n\nUser ID: {item.get('user_id', user_id)}\nGST Due Date: {item.get('due_date', due_date)}\nGST Amount: ₹{item.get('amount', amount):,}\n\nPlease ensure timely payment to avoid any penalties.\nAnother reminder will be sent a day before the due date.\n\nThank you,\nGST Alert System
"""
                sns.publish(
                    TopicArn=SNS_TOPIC_ARN,
                    Subject=email_subject,
                    Message=email_body
                )
                st.success("Reminder set and professional email sent!")
            except Exception as e:
                st.error(f"Error: {str(e)}") 