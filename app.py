import streamlit as st
import json
import smtplib
import qrcode
from PIL import Image, ImageDraw, ImageFont, ImageOps
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import time
import io
import platform

# ================= CONFIGURATION =================
PASS_SIZE = (1200, 700)
BG_COLOR_1 = "#0f172a"
BG_COLOR_2 = "#1e293b"
ACCENT_COLOR = "#6366f1"
TEXT_COLOR = "#f1f5f9"
GOLD_COLOR = "#fbbf24"

SOCIAL_LINKS = {
    "GitHub": "https://github.com/gameliminals",
    "Discord": "https://discord.com/invite/5hZsZmcC",
    "Instagram": "https://www.instagram.com/gameliminals?igsh=b2V3NzRidDd3OHF6",
    "LinkedIn": "https://www.linkedin.com/company/gameliminals/",
    "Youtube": "https://www.youtube.com/@GameLiminals",
    "Facebook": "https://www.facebook.com/gameliminals"
}

# ================= HELPER FUNCTIONS =================

def load_best_font(size):
    """
    Tries to load font.ttf first. 
    If missing, tries system fonts (Arial/DejaVu).
    """
    fonts_to_try = ["font.ttf", "arial.ttf", "Arial.ttf", "DejaVuSans-Bold.ttf", "robot.ttf"]
    
    for font_name in fonts_to_try:
        try:
            return ImageFont.truetype(font_name, size)
        except OSError:
            continue
            
    # Final fallback (will be tiny, but we try to avoid this)
    return ImageFont.load_default()

def make_rounded_logo(img, radius=20):
    """
    Rounds the corners of the logo to make it look cleaner
    even if it has a white background.
    """
    img = img.convert("RGBA")
    
    # Create a mask (white circle/rounded box)
    mask = Image.new('L', img.size, 0)
    draw = ImageDraw.Draw(mask)
    
    # Draw rounded rectangle on mask
    draw.rounded_rectangle([(0, 0), img.size], radius=radius, fill=255)
    
    # Apply mask
    output = ImageOps.fit(img, img.size, centering=(0.5, 0.5))
    output.putalpha(mask)
    return output

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
    # 1. Background
    img = create_gradient(PASS_SIZE[0], PASS_SIZE[1], BG_COLOR_1, BG_COLOR_2)
    draw = ImageDraw.Draw(img)
    
    # 2. Decorations
    draw.rectangle([(0, 0), (30, PASS_SIZE[1])], fill=ACCENT_COLOR)
    draw.pieslice([(PASS_SIZE[0]-200, -200), (PASS_SIZE[0]+100, 100)], 180, 270, fill=ACCENT_COLOR)

    # 3. Fonts (Now using the smart loader)
    font_header = load_best_font(60)
    font_sub = load_best_font(40)
    font_bold = load_best_font(50)
    font_small = load_best_font(30)

    # 4. Logos (Now with auto-rounding)
    try:
        # Adamas Logo
        logo_uni = Image.open("au_logo.jpg").convert("RGBA")
        logo_uni = make_rounded_logo(logo_uni.resize((100, 100))) # Resize before pasting
        img.paste(logo_uni, (60, 40), logo_uni)
        
        # GameLiminals Logo
        logo_club = Image.open("logo.png").convert("RGBA")
        logo_club = make_rounded_logo(logo_club.resize((100, 100))) # Resize before pasting
        img.paste(logo_club, (PASS_SIZE[0] - 160, 40), logo_club)
    except Exception as e:
        print(f"Logo error: {e}")
        draw.text((60, 50), "ADAMAS", font=font_small, fill=TEXT_COLOR)

    # 5. Text Details
    # Event Name
    draw.text((PASS_SIZE[0]//2, 80), str(event_name).upper(), font=font_header, fill=TEXT_COLOR, anchor="ms")
    draw.text((PASS_SIZE[0]//2, 140), "OFFICIAL EVENT PASS", font=font_small, fill=ACCENT_COLOR, anchor="ms")
    
    # Divider Line
    draw.line([(100, 180), (PASS_SIZE[0]-100, 180)], fill="#334155", width=3)

    # Attendee Name
    draw.text((100, 250), "ATTENDEE", font=font_small, fill="#94a3b8")
    draw.text((100, 290), str(member_data['name']).upper(), font=font_bold, fill=GOLD_COLOR)

    # Role / Team
    draw.text((100, 380), "ROLE / TEAM", font=font_small, fill="#94a3b8")
    role_text = f"{member_data.get('role', 'Participant')} | {team_name}"
    draw.text((100, 420), role_text, font=font_sub, fill=TEXT_COLOR)

    # Registration ID
    draw.text((100, 520), "REGISTRATION ID", font=font_small, fill="#94a3b8")
    draw.text((100, 560), str(reg_id), font=font_sub, fill=TEXT_COLOR)

    # 6. QR Code
    qr = qrcode.QRCode(box_size=10, border=2)
    qr.add_data(str(reg_id))
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").resize((220, 220))
    
    # Paste QR Code
    img.paste(qr_img, (PASS_SIZE[0] - 320, 350))
    draw.text((PASS_SIZE[0] - 210, 600), "SCAN TO VERIFY", font=font_small, fill=ACCENT_COLOR, anchor="ms")
    
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

with st.sidebar:
    st.header("🔐 Email Credentials")
    st.info("Enter the club's Gmail details here.")
    sender_email = st.text_input("Sender Email", value="adamasgamingclub@gmail.com")
    sender_pass = st.text_input("App Password", type="password")
    st.divider()
    st.caption("Developed by Sayandeep Pradhan | Technical Lead")

uploaded_file = st.file_uploader("Upload Registration JSON", type=['json'])

if uploaded_file is not None:
    try:
        data = json.load(uploaded_file)
        registrations = data if isinstance(data, list) else data.get('registrations', [])
        
        st.success(f"✅ Loaded {len(registrations)} registrations!")
        
        if len(registrations) > 0:
            st.subheader("👁️ Preview First Pass")
            st.info("If the text below looks tiny, please download 'Montserrat-Bold.ttf' and rename it to 'font.ttf' in this folder.")
            
            first_reg = registrations[0]
            first_member = first_reg['members'][0]
            
            preview_img = generate_pass_image(
                first_member, 
                first_reg.get('eventName', 'Event'), 
                first_reg.get('registrationID', '000'), 
                first_reg.get('teamName', 'N/A')
            )
            st.image(preview_img, caption="Preview of generated pass", width=800)

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
                            pass_img = generate_pass_image(member, event_name, reg_id, team_name)
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
                                
                            current_idx += 1
                            progress_bar.progress(min(current_idx / total, 1.0))
                            time.sleep(1)
                            
                status_text.text("✅ Process Complete!")
                st.success(f"Done! Sent: {success_count} | Failed: {fail_count}")
                st.balloons()
                
    except Exception as e:
        st.error(f"Error reading JSON: {e}")
