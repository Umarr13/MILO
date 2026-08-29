# 🚀 Complete AWS Deployment Guide for Milo Analytics

This guide will walk you through exactly how to take the Milo Analytics backend from your local machine and deploy it to the live internet using Amazon Web Services (AWS).

---

### Step 1: Spin up the EC2 Server
1. Go to [aws.amazon.com](https://aws.amazon.com/) and log in (or create a free tier account).
2. Search for **EC2** in the top search bar and click on it.
3. Click the bright orange **Launch Instance** button.
4. **Name**: Type `Milo-Backend`.
5. **OS Image (AMI)**: Select **Ubuntu** (Ubuntu Server 24.04 LTS is perfect).
6. **Instance Type**: Select **t2.micro** (this is usually labeled "Free tier eligible").
7. **Key Pair**: Click **Create new key pair**. 
   - Name it `milo-key`. 
   - Select **RSA** and **.pem**. 
   - Click Create. *This will download a file named `milo-key.pem` to your computer. DO NOT lose this file.*
8. **Network Settings**: Check the following boxes:
   - ✅ Allow SSH traffic from Anywhere
   - ✅ Allow HTTP traffic from the internet (Crucial for the API to work)
   - ✅ Allow HTTPS traffic from the internet
9. Click **Launch Instance** in the bottom right.

---

### Step 2: Connect to your Server (SSH)
1. Wait a minute for the instance to say "Running". Click on the Instance ID to view its details.
2. Find the **Public IPv4 address** (e.g., `54.123.45.67`) and copy it.
3. On your local Windows machine, open PowerShell and navigate to where your `milo-key.pem` file downloaded (usually your Downloads folder).
   ```bash
   cd ~/Downloads
   ```
4. Run the SSH command to connect to your server:
   ```bash
   ssh -i milo-key.pem ubuntu@<YOUR_PUBLIC_IP>
   ```
   *Type `yes` if it asks if you want to continue connecting.* You are now inside the Linux server!

---

### Step 3: Install Docker & Clone the Code
Run these exact commands one by one inside the AWS terminal to prep the server:

1. Update the server:
   ```bash
   sudo apt-get update && sudo apt-get upgrade -y
   ```
2. Install Docker and Docker Compose:
   ```bash
   sudo apt-get install docker.io docker-compose -y
   ```
3. Enable Docker to run on startup:
   ```bash
   sudo systemctl enable docker
   sudo systemctl start docker
   ```
4. Clone your Milo repository:
   ```bash
   git clone https://github.com/Umarr13/MILO.git
   cd MILO
   ```

---

### Step 4: Launch the Backend
Because I already wrote the `Dockerfile` and `docker-compose.yml` for you, launching the whole AI backend takes exactly one command.

Inside the `MILO` folder on your AWS server, run:
```bash
sudo docker-compose up -d --build
```
*Wait a few minutes while it downloads Python, installs the ML libraries, and boots up Nginx.*

To verify it is running, type:
```bash
sudo docker ps
```
You should see `milo_backend` and `milo_nginx` running. Your API is now live on the internet! 🌐

---

### Step 5: Connect the Flutter App
Now that the server is live, we need to point the mobile app to it.

1. On your Windows machine, open `app/lib/api/milo_api.dart`.
2. Find line 6:
   ```dart
   baseUrl: 'http://10.0.2.2:8000',
   ```
3. Change it to your new AWS Public IP address without the 8000 port (Nginx handles the port routing on port 80 natively now). Example:
   ```dart
   baseUrl: 'http://54.123.45.67',
   ```
4. Save the file and push your code to GitHub:
   ```bash
   git add app/lib/api/milo_api.dart
   git commit -m "chore: point app to live aws server"
   git push
   ```

GitHub Actions will automatically build a fresh APK for you. When you install that APK on your phone, it will seamlessly talk to your live AWS artificial intelligence engine!
