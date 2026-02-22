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

def draw_gaming_background(width, height):
    # Deep midnight gradient
    img = create_gradient(width, height, "#020617", "#0f172a")
    draw = ImageDraw.Draw(img, 'RGBA')
    
    # 1. Subtle Tech Grid
    grid_spacing = 60
    grid_color = (99, 102, 241, 30) # Indigo with low alpha
    for x in range(0, width, grid_spacing):
        draw.line([(x, 0), (x, height)], fill=grid_color, width=1)
    for y in range(0, height, grid_spacing):
        draw.line([(0, y), (width, y)], fill=grid_color, width=1)
        
    # 2. Techy Accent Shapes
    # Corner Accents
    accent_color = (99, 102, 241, 80)
    draw.polygon([(0, 0), (150, 0), (0, 150)], fill=accent_color)
    draw.polygon([(width, height), (width-150, height), (width, height-150)], fill=accent_color)
    
    # 3. Glowing Neon Lines
    cyan_neon = (34, 211, 238, 150)
    gold_neon = (251, 191, 36, 150)
    
    # Top tech bar
    draw.rectangle([0, 0, width, 80], fill=(15, 23, 42, 200)) # Semi-transparent top bar
    draw.line([(0, 80), (width, 80)], fill=cyan_neon, width=3)
    
    # Side accents
    draw.line([(40, 120), (40, height-40)], fill=gold_neon, width=2)
    draw.line([(width-40, 120), (width-40, height-40)], fill=cyan_neon, width=2)

    return img

def generate_pass_image(member_data, event_name, reg_id, team_name):
    # Base Dynamic Gaming Canvas (1600x600 for wide aspect ratio)
    width, height = 1600, 600
    img = draw_gaming_background(width, height)
    draw = ImageDraw.Draw(img, 'RGBA')

    # Load Fonts
    try:
        font_path = "font.ttf"
        font_main = ImageFont.truetype(font_path, 80) # Attendee Name
        font_sub = ImageFont.truetype(font_path, 35)  # Team/Role
        font_id = ImageFont.truetype(font_path, 32)   # Reg ID
        font_title = ImageFont.truetype(font_path, 45) # Event Name
        font_label = ImageFont.truetype(font_path, 22) # Small Labels
    except:
        font_main = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_id = ImageFont.load_default()
        font_title = ImageFont.load_default()
        font_label = ImageFont.load_default()

    # 1. Top Section - Event Info
    draw.text((width//2, 40), str(event_name).upper(), font=font_title, fill="#FFFFFF", anchor="mm")
    
    # 2. Main Center Section
    # Glassmorphism effect for the name area
    draw.rectangle([300, 180, width-300, 420], fill=(30, 41, 59, 180), outline=(99, 102, 241, 100), width=2)
    
    # Labels
    draw.text((320, 200), "ATTENDEE", font=font_label, fill="#94a3b8")
    
    # Attendee Name
    draw.text((width//2, 280), str(member_data['name']).upper(), font=font_main, fill="#FFFFFF", anchor="mm")
    
    # Role / Team
    role_text = f"{member_data.get('role', 'PARTICIPANT')} | {team_name}"
    draw.text((width//2, 360), role_text, font=font_sub, fill="#F5D372", anchor="mm") 

    # 3. Bottom Section - ID and QR
    # ID Box
    draw.rectangle([70, height-100, 400, height-40], fill=(15, 23, 42, 200), outline="#fbbf24", width=2)
    draw.text((235, height-70), f"ID: {reg_id}", font=font_id, fill="#FFFFFF", anchor="mm")

    # QR Box
    qr_box_size = 180
    qr_x, qr_y = width - 250, height - 250
    # Scanner Frame
    draw.rectangle([qr_x-10, qr_y-10, qr_x+qr_box_size+10, qr_y+qr_box_size+10], fill=(15, 23, 42, 220), outline="#22d3ee", width=3)
    draw.text((qr_x + qr_box_size//2, qr_y - 30), "SCAN FOR ENTRY", font=font_label, fill="#22d3ee", anchor="mm")

    # QR Generation
    qr = qrcode.QRCode(box_size=10, border=1)
    qr.add_data(str(reg_id))
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    qr_img = qr_img.resize((qr_box_size, qr_box_size))
    img.paste(qr_img, (qr_x, qr_y))

    # 4. Logos
    try:
        # Club Logo (top left)
        logo = Image.open("logo.png").convert("RGBA")
        logo.thumbnail((80, 80))
        img.paste(logo, (20, 0), logo)
    except: pass
    
    try:
        # AU Logo (top right)
        au_logo = Image.open("au_logo.jpg").convert("RGB")
        au_logo.thumbnail((120, 60))
        img.paste(au_logo, (width-140, 10))
    except: pass

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
                first_reg.get('eventName') or first_reg.get('event_name') or 'Event', 
                first_reg.get('registrationID') or first_reg.get('id') or '000', 
                first_reg.get('teamName') or first_reg.get('team_name') or 'N/A'
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
                    # Defensive key reading
                    event_name = reg.get('eventName') or reg.get('event_name') or 'Event'
                    reg_id = reg.get('registrationID') or reg.get('id') or 'N/A'
                    team_name = reg.get('teamName') or reg.get('team_name') or 'Individual'
                    
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
