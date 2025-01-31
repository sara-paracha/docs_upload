import os
import requests
# from msal import PublicClientApplication
from msal import ConfidentialClientApplication
import time
import sys
import streamlit as st
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# Set page configuration
st.set_page_config(
    page_title="Custom Page",
    page_icon="🌟",
    layout="centered",  # Options: "centered", "wide"
    initial_sidebar_state="collapsed"
)


st.header('E-Manifest Tracker')


# Directory to save uploaded files


tab1, tab2, tab3= st.tabs(['DOCS UPLOAD', "PARS (ACI)", "PAPS (ACE)"])


with tab1:
    UPLOAD_DIR = "C:/Users/sarap/manifest_tracker/uploaded_pdfs"   #"C:/Users/sarap/OneDrive - parachas/Attachments" 
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    with st.form("file_upload_form"):
        truck_number = st.text_input("Enter Truck Number:")
        driver_name = st.text_input("Enter Driver Name:")
        uploaded_file = st.file_uploader("Upload a file", type=["pdf"])
        submitted = st.form_submit_button("Submit")

        def send_email(sender_email, sender_password, recipient_email, subject, message):
            # Create a multipart message object
            msg = MIMEMultipart('alternative')
            msg['From'] = sender_email
            msg['To'] = recipient_email
            msg['Subject'] = subject

            # Create both plain text and HTML versions of the email
            text = 'This is a plain text email.'
            html = f'<html><body><>{message}</h1></body></html>'

            # Attach the plain text and HTML versions to the email
            part1 = MIMEText(text, 'plain')
            part2 = MIMEText(html, 'html')
            msg.attach(part1)
            msg.attach(part2)

            # SMTP server settings for Outlook
            smtp_server = 'smtp.office365.com'
            smtp_port = 587

            try:
                # Create a secure SSL/TLS connection to the SMTP server
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()

                # Login to your Outlook email account
                server.login(sender_email, sender_password)

                # Send the email
                server.sendmail(sender_email, recipient_email, msg.as_string())

                print("Email sent successfully!")

            except smtplib.SMTPException as e:
                print("Error sending email:", str(e))

            finally:
                # Close the connection to the SMTP server
                server.quit()

        # Example usage
        sender_email = 'palwashap@palwp.onmicrosoft.com'
        sender_password = 'Pokemon45678930'
        recipient_email = 'sara.paracha@outlook.com'
        subject = f"{truck_number}_{driver_name}"
        message = 'This is an HTML email sent using smtplib and Outlook.'


        if submitted:
            if uploaded_file is not None and truck_number.strip() and driver_name.strip():
                # Get current date
                current_date = datetime.now().strftime("%Y-%m-%d")

                # Create the new file name
                file_extension = uploaded_file.name.split(".")[-1]
                new_file_name = f"{truck_number}_{driver_name}_{current_date}.{file_extension}"

                # Save the file locally with the new name
                file_path = os.path.join(UPLOAD_DIR, new_file_name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                st.success(f"File uploaded successfully and saved as '{new_file_name}'!")
                send_email(sender_email, sender_password, recipient_email, subject, message)

                # Azure app credentials
                CLIENT_ID = "212851f3-cff3-4c39-8a42-1ec610fe567b"  # Replace with your app's client ID
                CLIENT_SECRET = "wnh8Q~U9arlam12woOZxMW6yRtB5qOIV.SDzeaSS"  # Replace with your app's client secret
                TENANT_ID = "bc90d3ec-dd7f-4f1e-9be7-9934c9d8aa34"  # Replace with your tenant ID
                # Microsoft Graph endpoints
                AUTHORITY_URL = f"https://login.microsoftonline.com/{TENANT_ID}"
                GRAPH_API_BASE_URL = "https://graph.microsoft.com/v1.0"
                UPLOAD_PATH = "/users/palwashap@palwp.onmicrosoft.com/drive/root:/Documents/"  # Target folder in OneDrive
                # File to upload
                FILE_PATH = file_path  # Replace with the path to your file
                def get_access_token():
                    """Authenticate using the Client Credential Flow and get an access token."""
                    app = ConfidentialClientApplication(
                        CLIENT_ID,
                        authority=AUTHORITY_URL,
                        client_credential=CLIENT_SECRET,
                    )
                    result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
                    # print(result)
                    if "access_token" in result:
                        return result["access_token"]
                    else:
                        print(f"Error: {result.get('error')}")
                        print(f"Error Description: {result.get('error_description')}")
                        raise Exception("Could not obtain access token.")

                def upload_file_to_onedrive(access_token, file_path, upload_path):
                    """Upload a file to OneDrive using Microsoft Graph API."""
                    file_name = os.path.basename(file_path)
                    upload_url = f"{GRAPH_API_BASE_URL}{upload_path}{file_name}:/content"

                    # Read file content
                    with open(file_path, "rb") as file:
                        file_data = file.read()

                    # Send the PUT request to upload the file
                    headers = {"Authorization": f"Bearer {access_token}"}
                    response = requests.put(upload_url, headers=headers, data=file_data)

                    if response.status_code in [200, 201]:
                        print("File uploaded successfully!")
                        # print("Response:", response.json())
                    else:
                        print("Failed to upload file")
                        # print("Response:", response.json())

                if __name__ == "__main__":
                    if os.path.exists(FILE_PATH):
                        try:
                            # Get an access token
                            token = get_access_token()

                            # Upload the file to OneDrive
                            upload_file_to_onedrive(token, FILE_PATH, UPLOAD_PATH)
                        except Exception as e:
                            print(f"An error occurred: {e}")
                    else:
                        print(f"File '{FILE_PATH}' not found.")


            else:
                st.error("Please fill in all fields and upload a valid file.")





