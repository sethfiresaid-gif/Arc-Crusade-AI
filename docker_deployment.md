# Arc Crusade AI - Website Deployment Opties

## 1. Docker Container (Voor eigen server)

### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Docker Commands
```bash
# Build container
docker build -t arc-crusade-ai .

# Run container
docker run -p 8501:8501 -e OPENAI_API_KEY="your_key" arc-crusade-ai
```

## 2. Website Integratie Opties

### A. Iframe Embedding
```html
<!DOCTYPE html>
<html>
<head>
    <title>Arc Crusade AI - Private Tool</title>
    <style>
        body { margin: 0; padding: 20px; }
        .app-container { 
            width: 100%; 
            height: 90vh; 
            border: none; 
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 20px;
            color: #2E86AB;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🏰 Arc Crusade AI - Manuscript Analyzer</h1>
        <p>Private Tool - Authorized Access Only</p>
    </div>
    
    <iframe 
        class="app-container"
        src="https://your-streamlit-app.streamlit.app"
        title="Arc Crusade AI">
    </iframe>
</body>
</html>
```

### B. Custom Domain Setup
```nginx
# Nginx config voor reverse proxy
server {
    listen 80;
    server_name jouwwebsite.com;
    
    location /arc-crusade {
        proxy_pass http://localhost:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 3. Beveiliging & Privacy

### Environment Variables
```bash
# Server environment
OPENAI_API_KEY=your_openai_key
ALLOWED_USERS=user1,user2,user3
ADMIN_PASSWORD=secure_password
```

### Simple Authentication
```python
# Voeg toe aan streamlit_app.py
import streamlit as st

def check_password():
    def password_entered():
        if st.session_state["password"] == "jouw_wachtwoord":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Wachtwoord", type="password", 
                     on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Wachtwoord", type="password", 
                     on_change=password_entered, key="password")
        st.error("😕 Wachtwoord incorrect")
        return False
    else:
        return True

# Gebruik in main app
if check_password():
    # Hier komt je bestaande app code
    main_app()
```

## 4. Website Platform Specifieke Oplossingen

### WordPress
- Plugin: "Embed Iframe"
- Custom HTML widget

### Wix/Squarespace
- HTML embed component
- Custom code sectie

### Eigen Website (PHP/HTML)
```php
<?php
// Simpele PHP authenticatie
session_start();
if (!isset($_SESSION['authenticated'])) {
    // Toon login form
    if ($_POST['password'] === 'jouw_wachtwoord') {
        $_SESSION['authenticated'] = true;
    } else {
        echo "Toegang geweigerd";
        exit;
    }
}
?>

<iframe src="https://your-app.streamlit.app" 
        width="100%" height="800px"></iframe>
```

## 5. Voordelen per Methode

### Streamlit Cloud + Iframe
✅ Makkelijk te implementeren
✅ Geen server beheer nodig
✅ Automatische updates
❌ Minder controle over domein

### Eigen Server
✅ Volledige controle
✅ Custom domein
✅ Eigen beveiliging
❌ Server beheer vereist
❌ Meer technische kennis nodig

## Aanbeveling
Voor de meeste gevallen: **Streamlit Cloud + Custom Domain + Iframe embedding**
- Beste balans tussen gemak en controle
- Professionele uitstraling
- Minimaal onderhoud