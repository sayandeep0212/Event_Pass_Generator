import streamlit as st
import json
import smtplib
import os
import qrcode
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import time
import io
import random
import math

# ================= CONFIGURATION =================
PASS_SIZE = (1600, 900)  # 16:9 aspect ratio for modern look
BG_COLOR_1 = "#0a0c1c"  # Dark blue-black
BG_COLOR_2 = "#1a1f3a"  # Deep purple-blue
ACCENT_COLOR = "#ff3366"  # Neon pink
ACCENT_COLOR_2 = "#33ccff"  # Neon blue
GOLD_COLOR = "#ffcc00"  # Gold
TEXT_COLOR = "#ffffff"
SECONDARY_TEXT = "#b8b8ff"

SOCIAL_LINKS = {
    "GitHub": "https://github.com/gameliminals",
    "Discord": "https://discord.gg/7szdDMp4Hv",
    "Instagram": "https://www.instagram.com/gameliminals?igsh=b2V3NzRidDd3OHF6",
    "LinkedIn": "https://www.linkedin.com/company/gameliminals/",
    "Youtube": "https://www.youtube.com/@GameLiminals",
    "Facebook": "https://www.facebook.com/gameliminals"
}

# ================= LOGIC FUNCTIONS =================
def create_gradient(width, height, colors):
    """Create multi-color gradient"""
    base = Image.new('RGB', (width, height), colors[0])
    if len(colors) < 2:
        return base
    
    # Create gradient with multiple color stops
    for i in range(1, len(colors)):
        overlay = Image.new('RGB', (width, height), colors[i])
        mask = Image.new('L', (width, height))
        mask_data = []
        
        # Vertical gradient with some diagonal influence
        for y in range(height):
            progress = y / height
            # Add some horizontal variation for diagonal effect
            for x in range(width):
                x_progress = x / width
                mix = (progress + x_progress * 0.3) / 1.3
                mask_val = int(255 * mix)
                mask_data.append(mask_val)
        
        mask.putdata(mask_data)
        base.paste(overlay, (0, 0), mask)
    
    return base

def draw_circuit_lines(draw, width, height):
    """Draw circuit board style lines"""
    lines_color = (100, 200, 255, 40)
    
    # Horizontal lines with nodes
    for y in range(100, height-100, 80):
        points = []
        for x in range(50, width-50, 60):
            points.append((x, y + random.randint(-5, 5)))
        
        if len(points) > 1:
            for i in range(len(points)-1):
                draw.line([points[i], points[i+1]], fill=lines_color, width=1)
                # Draw nodes
                draw.ellipse([points[i][0]-3, points[i][1]-3, points[i][0]+3, points[i][1]+3], 
                           fill=(0, 255, 255, 80))

def draw_glowing_effects(draw, width, height):
    """Draw glowing neon effects"""
    # Central glow
    for i in range(3):
        alpha = 30 - i * 8
        size = 600 - i * 50
        draw.ellipse([width//2 - size//2, height//2 - size//2,
                     width//2 + size//2, height//2 + size//2],
                     fill=(255, 100, 200, alpha))
    
    # Corner glows
    corners = [(0, 0), (width, 0), (0, height), (width, height)]
    colors = [(255, 50, 150, 30), (50, 200, 255, 30), (200, 100, 255, 30), (255, 200, 50, 30)]
    
    for (cx, cy), color in zip(corners, colors):
        for i in range(3):
            alpha = color[3] - i * 8
            size = 400 - i * 30
            draw.ellipse([cx - size//2, cy - size//2, cx + size//2, cy + size//2],
                        fill=(color[0], color[1], color[2], alpha))

def create_hex_pattern(draw, width, height):
    """Create hexagonal tech pattern"""
    hex_size = 50
    hex_color = (100, 150, 255, 15)
    
    for row in range(-2, height // hex_size + 2):
        for col in range(-2, width // hex_size + 2):
            x = col * hex_size * 1.5
            y = row * hex_size * 1.732 + (col % 2) * hex_size * 0.866
            
            if 0 <= x <= width and 0 <= y <= height:
                points = []
                for i in range(6):
                    angle = math.radians(60 * i - 30)
                    px = x + hex_size * math.cos(angle)
                    py = y + hex_size * math.sin(angle)
                    points.append((px, py))
                
                draw.polygon(points, outline=hex_color, width=1)

def generate_pass_image(member_data, event_name, reg_id, team_name):
    # Create base canvas with enhanced gaming background
    width, height = 1600, 900
    colors = ["#0a0c1c", "#1a1f3a", "#2a1f4a", "#1f2a4a"]
    img = create_gradient(width, height, colors)
    draw = ImageDraw.Draw(img, 'RGBA')
    
    # Add various tech effects
    create_hex_pattern(draw, width, height)
    draw_circuit_lines(draw, width, height)
    draw_glowing_effects(draw, width, height)
    
    # Load Fonts with fallback
    try:
        font_path = "font.ttf"
        # Main title font
        font_title = ImageFont.truetype(font_path, 70)
        # Attendee Name - Large and bold
        font_name = ImageFont.truetype(font_path, 100)
        # Subtitle font
        font_subtitle = ImageFont.truetype(font_path, 45)
        # Regular text
        font_regular = ImageFont.truetype(font_path, 35)
        # Small text
        font_small = ImageFont.truetype(font_path, 25)
    except:
        font_title = ImageFont.load_default()
        font_name = ImageFont.load_default()
        font_subtitle = ImageFont.load_default()
        font_regular = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # ===== TOP SECTION WITH EVENT NAME AND LOGOS =====
    # Top gradient bar
    draw.rectangle([0, 0, width, 120], fill=(10, 15, 30, 220))
    draw.line([(0, 120), (width, 120)], fill=(255, 51, 102, 255), width=4)
    
    # Event name with glow effect
    for offset in [(2,2), (-2,-2), (2,-2), (-2,2)]:
        draw.text((width//2 + offset[0], 50 + offset[1]), event_name.upper(), 
                 font=font_title, fill=(255, 200, 200, 100), anchor="mm")
    draw.text((width//2, 50), event_name.upper(), font=font_title, 
             fill="#FFFFFF", anchor="mm")
    
    # ===== MAIN CONTENT AREA WITH GLASS MORPHISM =====
    # Main glass panel
    panel_y_start = 150
    panel_y_end = 750
    
    # Outer glow
    for i in range(5, 0, -1):
        alpha = 30 - i * 5
        draw.rectangle([300 - i, panel_y_start - i, width-300 + i, panel_y_end + i],
                      outline=(100, 200, 255, alpha), width=2)
    
    # Main panel
    draw.rectangle([300, panel_y_start, width-300, panel_y_end],
                  fill=(20, 25, 45, 200), outline=(255, 51, 102, 150), width=3)
    
    # Inner decorative lines
    draw.line([320, panel_y_start+20, width-320, panel_y_start+20],
             fill=(255, 255, 255, 50), width=1)
    draw.line([320, panel_y_end-20, width-320, panel_y_end-20],
             fill=(255, 255, 255, 50), width=1)
    
    # ===== LEFT SIDE - ATTENDEE INFO =====
    # "ATTENDEE" label with tech style
    draw.text((350, panel_y_start + 50), "▸ ATTENDEE IDENTITY ◂", 
             font=font_regular, fill="#33ccff")
    
    # Attendee Name with 3D effect
    name_text = member_data['name'].upper()
    if len(name_text) > 20:
        name_text = name_text[:18] + "..."
    
    # Shadow effect for name
    for i in range(5, 0, -1):
        draw.text((450 + i, 300 + i), name_text, font=font_name, 
                 fill=(255, 51, 102, 50), anchor="lt")
    
    # Main name
    draw.text((450, 300), name_text, font=font_name, fill="#FFFFFF", anchor="lt")
    
    # Role with gradient effect
    role_text = member_data.get('role', 'PARTICIPANT')
    draw.text((450, 430), role_text, font=font_subtitle, fill="#ffcc00", anchor="lt")
    
    # Team name with icon
    draw.text((450, 490), f"⚔️ TEAM: {team_name}", font=font_regular, 
             fill="#b8b8ff", anchor="lt")
    
    # ===== RIGHT SIDE - QR CODE =====
    qr_box_size = 300
    qr_x = width - 550
    qr_y = panel_y_start + 120
    
    # QR frame with neon effect
    for i in range(3):
        offset = i * 3
        draw.rectangle([qr_x - offset, qr_y - offset, 
                       qr_x + qr_box_size + offset, qr_y + qr_box_size + offset],
                      outline=(0, 255, 255, 100 - i*30), width=2)
    
    # Scan text
    draw.text((qr_x + qr_box_size//2, qr_y - 40), "⚡ SCAN TO VERIFY ⚡", 
             font=font_small, fill="#33ccff", anchor="mm")
    
    # QR Code Generation
    qr = qrcode.QRCode(
        version=1,
        box_size=12,
        border=2,
        error_correction=qrcode.constants.ERROR_CORRECT_H
    )
    qr.add_data(str(reg_id))
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
    
    # Create cool QR with logo in center (optional)
    qr_img = qr_img.resize((qr_box_size, qr_box_size))
    
    # Add a small GameLiminals logo in QR center (if available)
    try:
        logo = Image.open("logo.png").convert("RGBA")
        logo.thumbnail((80, 80))
        
        # Create circular mask for logo
        mask = Image.new('L', logo.size, 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0, logo.size[0], logo.size[1]), fill=255)
        
        # Calculate position
        logo_pos = (qr_x + qr_box_size//2 - logo.size[0]//2,
                   qr_y + qr_box_size//2 - logo.size[1]//2)
        
        # Paste with mask
        img.paste(logo, logo_pos, mask)
    except:
        pass
    
    # Paste QR
    img.paste(qr_img, (qr_x, qr_y))
    
    # ===== BOTTOM SECTION - REGISTRATION ID =====
    id_y = panel_y_end - 80
    
    # ID label
    draw.text((450, id_y), "REGISTRATION ID", font=font_small, fill="#8888ff", anchor="lt")
    
    # ID with fancy styling
    id_text = f"#{reg_id}"
    for offset in [(1,1), (2,2)]:
        draw.text((450 + offset[0], id_y + 30 + offset[1]), id_text,
                 font=font_subtitle, fill=(255, 200, 200, 100), anchor="lt")
    draw.text((450, id_y + 30), id_text, font=font_subtitle, fill="#FFFFFF", anchor="lt")
    
    # ===== ADD LOGOS =====
    try:
        # Club Logo with effects
        logo = Image.open("logo.png").convert("RGBA")
        logo.thumbnail((100, 100))
        
        # Add glow behind logo
        glow_size = 120
        draw.ellipse([10, 10, 10+glow_size, 10+glow_size],
                    fill=(255, 51, 102, 100))
        
        img.paste(logo, (20, 15), logo)
    except:
        pass
    
    try:
        # AU Logo with effects
        au_logo = Image.open("au_logo.jpg").convert("RGBA")
        au_logo.thumbnail((180, 80))
        
        # Add glow behind logo
        glow_size = 200
        draw.ellipse([width-210, 15, width-10, 115],
                    fill=(51, 204, 255, 100))
        
        img.paste(au_logo, (width-190, 25))
    except:
        pass
    
    # ===== ADDITIONAL GAMING ELEMENTS =====
    # Corner accents
    corner_size = 50
    # Top-left corner
    draw.line([(20, 20), (70, 20)], fill="#ff3366", width=4)
    draw.line([(20, 20), (20, 70)], fill="#ff3366", width=4)
    # Top-right corner
    draw.line([(width-70, 20), (width-20, 20)], fill="#33ccff", width=4)
    draw.line([(width-20, 20), (width-20, 70)], fill="#33ccff", width=4)
    # Bottom-left corner
    draw.line([(20, height-70), (20, height-20)], fill="#33ccff", width=4)
    draw.line([(20, height-20), (70, height-20)], fill="#33ccff", width=4)
    # Bottom-right corner
    draw.line([(width-70, height-20), (width-20, height-20)], fill="#ff3366", width=4)
    draw.line([(width-20, height-70), (width-20, height-20)], fill="#ff3366", width=4)
    
    return img

def send_single_email(smtp_host, smtp_port, sender_email, sender_pass, to_email, name, event_name, pass_image):
    msg = MIMEMultipart()
    msg['From'] = f"GameLiminals Club <{sender_email}>"
    msg['To'] = to_email
    msg['Subject'] = f"🎮 Your Gaming Pass: {event_name}"

    social_html = "".join([f'<a href="{link}" style="margin:0 10px;color:#ff3366;text-decoration:none;font-weight:bold;">{p}</a>' for p, link in SOCIAL_LINKS.items()])

    body = f"""
    <html>
      <head>
        <style>
          @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
        </style>
      </head>
      <body style="font-family: 'Orbitron', sans-serif; background: linear-gradient(135deg, #0a0c1c 0%, #1a1f3a 100%); margin:0; padding:20px;">
        <div style="max-width:600px; margin:0 auto; background: rgba(20, 25, 45, 0.95); border-radius:20px; padding:30px; border:2px solid #ff3366; box-shadow: 0 0 30px rgba(255,51,102,0.3);">
            <div style="text-align:center; margin-bottom:30px;">
                <h1 style="color:#ff3366; text-shadow: 0 0 10px #ff3366; font-size:36px; margin:0;">🎮 GAMELIMINALS</h1>
                <p style="color:#33ccff; font-size:14px; letter-spacing:2px;">PLAYERS INTO CREATORS</p>
            </div>
            
            <h2 style="color:#ffffff; text-align:center; border-bottom:2px solid #33ccff; padding-bottom:15px;">Welcome to {event_name}!</h2>
            
            <div style="background: rgba(0,0,0,0.3); border-radius:15px; padding:20px; margin:20px 0; border-left:4px solid #33ccff;">
                <p style="color:#ffffff; font-size:18px;">Hello <strong style="color:#ffcc00;">{name}</strong>,</p>
                <p style="color:#b8b8ff;">Your registration is confirmed! Your digital gaming pass is attached below.</p>
            </div>
            
            <div style="background: linear-gradient(90deg, #ff3366, #33ccff); padding:20px; border-radius:10px; text-align:center;">
                <p style="color:#ffffff; margin:0 0 15px 0; font-weight:bold;">CONNECT WITH US</p>
                <div style="display:flex; flex-wrap:wrap; justify-content:center; gap:10px;">
                    {social_html}
                </div>
            </div>
            
            <p style="color:#8888ff; text-align:center; margin-top:20px; font-size:12px;">
                Show your pass at the venue for quick entry!
            </p>
        </div>
      </body>
    </html>
    """
    msg.attach(MIMEText(body, 'html'))

    # Convert PIL Image to Bytes
    img_byte_arr = io.BytesIO()
    pass_image.save(img_byte_arr, format='PNG', quality=95, optimize=True)
    img_byte_arr.seek(0)
    
    part = MIMEBase("application", "octet-stream")
    part.set_payload(img_byte_arr.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename="GamingPass-{name.split()[0]}.png"')
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
st.set_page_config(
    page_title="GameLiminals Gaming Pass Mailer", 
    page_icon="🎮", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for gaming theme
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0a0c1c 0%, #1a1f3a 100%);
    }
    .main-header {
        text-align: center;
        padding: 20px;
        background: rgba(255,51,102,0.1);
        border-radius: 10px;
        border: 2px solid #ff3366;
        margin-bottom: 30px;
    }
    .main-header h1 {
        color: #ff3366;
        text-shadow: 0 0 20px #ff3366;
        font-size: 48px;
    }
    .stButton button {
        background: linear-gradient(90deg, #ff3366, #33ccff);
        color: white;
        font-weight: bold;
        border: none;
        padding: 10px 30px;
        border-radius: 5px;
        transition: all 0.3s;
    }
    .stButton button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 20px #ff3366;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header"><h1>🎮 GameLiminals Gaming Pass Mailer</h1></div>', unsafe_allow_html=True)

# Sidebar for Credentials
with st.sidebar:
    st.markdown("## 🔐 Email Credentials")
    st.info("Use App Password for security")
    sender_email = st.text_input("Sender Email", value="adamasgamingclub@gmail.com")
    sender_pass = st.text_input("App Password", type="password")
    
    st.markdown("---")
    st.markdown("### 🎯 Quick Tips")
    st.markdown("""
    - Upload JSON file
    - Preview first pass
    - Send in bulk
    - Each pass is unique
    """)
    
    st.markdown("---")
    st.caption("Developed by Sayandeep Pradhan | Technical Lead")
    st.caption("© 2024 GameLiminals Club")

# Main Area
col1, col2 = st.columns([2, 1])

with col1:
    uploaded_file = st.file_uploader("📁 Upload Registration JSON", type=['json'], help="Upload the JSON file from registration portal")

with col2:
    if uploaded_file is not None:
        st.info("✨ File uploaded successfully!")

if uploaded_file is not None:
    try:
        data = json.load(uploaded_file)
        registrations = data if isinstance(data, list) else data.get('registrations', [])
        
        st.success(f"✅ Loaded {len(registrations)} registrations with {sum(len(r.get('members', [])) for r in registrations)} attendees!")
        
        # Preview Section
        if len(registrations) > 0:
            st.markdown("---")
            st.markdown("### 👁️ Preview Generated Pass")
            
            first_reg = registrations[0]
            first_member = first_reg['members'][0]
            
            # Generate preview
            preview_img = generate_pass_image(
                first_member, 
                first_reg.get('eventName') or first_reg.get('event_name') or 'GAMING EVENT', 
                first_reg.get('registrationID') or first_reg.get('id') or 'GAME001', 
                first_reg.get('teamName') or first_reg.get('team_name') or 'SOLO PLAYER'
            )
            
            # Display preview in columns
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.image(preview_img, caption="🎮 Your Gaming Pass Preview", use_column=True)

        # Sending Section
        st.markdown("---")
        st.markdown("### 🚀 Bulk Email Sending")
        
        col1, col2, col3 = st.columns(3)
        with col2:
            send_button = st.button("🔥 START SENDING PASSES", type="primary", use_container_width=True)
        
        if send_button:
            if not sender_pass:
                st.error("⚠️ Please enter the Email Password in the sidebar first!")
            else:
                progress_bar = st.progress(0)
                status_text = st.empty()
                success_count = 0
                fail_count = 0
                
                total = 0
                for reg in registrations:
                    total += len(reg.get('members', []))
                
                current_idx = 0
                
                # Create expandable log section
                with st.expander("📋 Sending Log", expanded=True):
                    log_area = st.empty()
                    logs = []
                
                for reg_idx, reg in enumerate(registrations):
                    event_name = reg.get('eventName') or reg.get('event_name') or 'GAMING EVENT'
                    reg_id = reg.get('registrationID') or reg.get('id') or f'GAME{reg_idx+1:03d}'
                    team_name = reg.get('teamName') or reg.get('team_name') or 'SOLO PLAYER'
                    
                    for member in reg.get('members', []):
                        email = member.get('email')
                        name = member.get('name')
                        
                        if email and name:
                            status_text.text(f"⚡ Processing: {name}")
                            logs.append(f"📧 Sending to {name} ({email})...")
                            log_area.code("\n".join(logs[-10:]))  # Show last 10 logs
                            
                            # Generate gaming pass
                            pass_img = generate_pass_image(member, event_name, reg_id, team_name)
                            
                            # Send email
                            sent, msg = send_single_email(
                                "smtp.gmail.com", 465, 
                                sender_email, sender_pass, 
                                email, name, event_name, pass_img
                            )
                            
                            if sent:
                                success_count += 1
                                logs.append(f"✅ Sent to {email}")
                            else:
                                fail_count += 1
                                logs.append(f"❌ Failed: {email} - {msg}")
                            
                            # Update Progress
                            current_idx += 1
                            progress_bar.progress(current_idx / total)
                            time.sleep(1)  # Delay to avoid rate limiting
                
                status_text.text("🎉 PROCESS COMPLETE!")
                progress_bar.progress(1.0)
                
                # Show final statistics
                st.markdown("---")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📨 Total Sent", success_count)
                with col2:
                    st.metric("❌ Failed", fail_count)
                with col3:
                    st.metric("✅ Success Rate", f"{(success_count/(success_count+fail_count)*100):.1f}%" if (success_count+fail_count)>0 else "0%")
                
                if fail_count == 0:
                    st.balloons()
                    st.success("🎮 All gaming passes sent successfully! Get ready to game!")
                
    except Exception as e:
        st.error(f"❌ Error: {e}")
        st.exception(e)
