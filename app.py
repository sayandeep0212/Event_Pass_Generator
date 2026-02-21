import streamlit as st
import json
import smtplib
import os
import qrcode
from PIL import Image, ImageDraw, ImageFont
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import time
import io

# ================= CONFIGURATION =================
PASS_SIZE = (1200, 700)
BG_COLOR_1 = "#0f172a"
BG_COLOR_2 = "#1e293b"
ACCENT_COLOR = "#6366f1"
TEXT_COLOR = "#f1f5f9"
GOLD_COLOR = "#fbbf24"

SOCIAL_LINKS = {
    "GitHub": "https://github.com/gameliminals",
    "Discord": "https://discord.gg/7szdDMp4Hv",
    "Instagram": "https://www.instagram.com/gameliminals?igsh=b2V3NzRidDd3OHF6",
    "LinkedIn": "https://www.linkedin.com/company/gameliminals/",
    "Youtube": "https://www.youtube.com/@GameLiminals",
    "Facebook": "https://www.facebook.com/gameliminals"
}

# ================= LOGIC FUNCTIONS =================
def create_gradient(width, height, c1, c2):
    base = Image.new('RGB', (width, height), c1)
    top = Image.new('RGB', (width, height), c2)
    mask = Image.new('L', (width, height))
    mask_data = []
    for y in range(height):
        mask_data.extend([int(255 * (y / height))] * width)
    mask.putdata(mask_data)
    base.paste(top, (0, 0), mask)
    return base

def generate_pass_image(member_data, event_name, reg_id, team_name):
    try:
        # Load the template image
        img = Image.open("demo_pass.jpeg").convert("RGB")
    except Exception as e:
        st.warning(f"Template demo_pass.jpeg not found, using fallback. Error: {e}")
        img = create_gradient(1600, 517, BG_COLOR_1, BG_COLOR_2)
    
    draw = ImageDraw.Draw(img)
    width, height = img.size

    # Load Font
    try:
        # User provided font.ttf in the same directory
        font_path = "font.ttf"
        font_main = ImageFont.truetype(font_path, 60)
        font_sub = ImageFont.truetype(font_path, 35)
        font_id = ImageFont.truetype(font_path, 30)
    except:
        font_main = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_id = ImageFont.load_default()

    # Overlay Text - Adjusting for 1600x517
    # Assuming the left side is for details and right side for QR
    
    # Attendee Name
    draw.text((80, 200), str(member_data['name']).upper(), font=font_main, fill="#FFFFFF")
    
    # Role / Team
    role_text = f"{member_data.get('role', 'PARTICIPANT')} | {team_name}"
    draw.text((80, 280), role_text, font=font_sub, fill="#F5D372") # Using GOLD accent
    
    # Registration ID
    draw.text((80, 420), f"REG ID: {reg_id}", font=font_id, fill="#FFFFFF")
    
    # QR Code
    qr = qrcode.QRCode(box_size=8, border=2)
    qr.add_data(str(reg_id))
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    
    # Position QR code on the right side
    # Resize to fit nicely (e.g., 250x250)
    qr_img = qr_img.resize((280, 280))
    img.paste(qr_img, (width - 380, 100))
    
    # Optional: Event Name overlay if required
    draw.text((width // 2, 50), str(event_name).upper(), font=font_sub, fill="#FFFFFF", anchor="mt")

    return img

def send_single_email(smtp_host, smtp_port, sender_email, sender_pass, to_email, name, event_name, pass_image):
    msg = MIMEMultipart()
    msg['From'] = f"GameLiminals Club <{sender_email}>"
    msg['To'] = to_email
    msg['Subject'] = f"🎟️ Your Digital Pass: {event_name}"

    social_html = "".join([f'<a href="{link}" style="margin:0 10px;color:#6366f1;text-decoration:none;font-weight:bold;">{p}</a> | ' for p, link in SOCIAL_LINKS.items()]).rstrip(" | ")

    body = f"""
    <html>
      <body style="font-family: sans-serif; color: #333;">
        <div style="max-width:600px; margin:0 auto; padding:20px; border:1px solid #eee; border-radius:10px;">
            <h2 style="color:#4f46e5; text-align:center;">Welcome to {event_name}!</h2>
            <p>Hello <strong>{name}</strong>,</p>
            <p>Your official registration is confirmed. Please find your Digital Event Pass attached.</p>
            <div style="background-color:#f8fafc; padding:15px; border-radius:8px; text-align:center; margin-top:20px;">
                <p>Stay updated with GameLiminals:</p>
                {social_html}
            </div>
        </div>
      </body>
    </html>
    """
    msg.attach(MIMEText(body, 'html'))

    # Convert PIL Image to Bytes
    img_byte_arr = io.BytesIO()
    pass_image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    part = MIMEBase("application", "octet-stream")
    part.set_payload(img_byte_arr.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename="EventPass-{name.split()[0]}.png"')
    msg.attach(part)

    try:
        server = smtplib.SMTP_SSL(smtp_host, smtp_port)
        server.login(sender_email, sender_pass)
        server.send_message(msg)
        server.quit()
        return True, "Sent"
    except Exception as e:
        return False, str(e)

# ================= WEBSITE UI =================
st.set_page_config(page_title="GameLiminals Mailer", page_icon="🎟️", layout="wide")

st.title("🎟️ GameLiminals Event Pass Mailer")
st.markdown("Upload the JSON file from the portal to generate and send passes automatically.")

# Sidebar for Credentials
with st.sidebar:
    st.header("🔐 Email Credentials")
    st.info("Enter the club's Gmail details here. Use App Password, not login password.")
    sender_email = st.text_input("Sender Email", value="adamasgamingclub@gmail.com")
    sender_pass = st.text_input("App Password", type="password")
    
    st.divider()
    st.caption("Developed by Sayandeep Pradhan | Technical Lead")

# Main Area
uploaded_file = st.file_uploader("Upload Registration JSON", type=['json'])

if uploaded_file is not None:
    try:
        data = json.load(uploaded_file)
        registrations = data if isinstance(data, list) else data.get('registrations', [])
        
        st.success(f"✅ Loaded {len(registrations)} registrations!")
        
        # Preview Section
        if len(registrations) > 0:
            st.subheader("👁️ Preview First Pass")
            first_reg = registrations[0]
            first_member = first_reg['members'][0]
            
            preview_img = generate_pass_image(
                first_member, 
                first_reg.get('eventName', 'Event'), 
                first_reg.get('registrationID', '000'), 
                first_reg.get('teamName', 'N/A')
            )
            st.image(preview_img, caption="Preview of generated pass", width=600)

        # Sending Section
        st.divider()
        st.subheader("🚀 Bulk Sending")
        
        if st.button("Start Sending Emails", type="primary"):
            if not sender_pass:
                st.error("Please enter the Email Password in the sidebar first!")
            else:
                progress_bar = st.progress(0)
                status_text = st.empty()
                success_count = 0
                fail_count = 0
                
                total = 0
                # Calculate total members first
                for reg in registrations:
                    total += len(reg.get('members', []))
                
                current_idx = 0
                
                for reg in registrations:
                    event_name = reg.get('eventName', 'Event')
                    reg_id = reg.get('registrationID', 'N/A')
                    team_name = reg.get('teamName', 'Individual')
                    
                    for member in reg.get('members', []):
                        email = member.get('email')
                        name = member.get('name')
                        
                        if email:
                            status_text.text(f"Generating & Sending to: {name}...")
                            
                            # Generate
                            pass_img = generate_pass_image(member, event_name, reg_id, team_name)
                            
                            # Send
                            sent, msg = send_single_email(
                                "smtp.gmail.com", 465, 
                                sender_email, sender_pass, 
                                email, name, event_name, pass_img
                            )
                            
                            if sent:
                                success_count += 1
                            else:
                                st.error(f"Failed to send to {email}: {msg}")
                                fail_count += 1
                                
                            # Update Progress
                            current_idx += 1
                            progress_bar.progress(current_idx / total)
                            time.sleep(1) # Safety delay
                            
                status_text.text("✅ Process Complete!")
                st.success(f"Done! Sent: {success_count} | Failed: {fail_count}")
                st.balloons()
                
    except Exception as e:
        st.error(f"Error reading JSON: {e}")
