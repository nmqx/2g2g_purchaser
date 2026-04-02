# 2Good2Go Bot

An automated tool to search, monitor, and interact with the Too Good To Go application locally.

## Quickstart

```bash
pip install -r requirements.txt
python main.py 
```

**That's it !** You will be instantly thrust into the CLI Bot Runner.

---

## Features

You interface with the system entirely through the `main.py` entrypoint, which hosts an interactive menu with the following features:

### 1. Mode Finder (Dashboard Interface)
Launches a visual dashboard in your browser. It maps out TGTG offers around your specified location, allowing you to easily sort, search, and view available Surprise Bags visually. 
  
### 2. Mode Autobuy
*(Coming soon!)* — Will allow you to seamlessly automate the purchasing process of Surprise Bags as soon as they become available.
  
### 3. Mode Notification (Poll & Webhook)
Runs a continuous background monitor. You give it a specific Item ID from the Dashboard, and it watches the stock silently. The moment the item's available quantity jumps above 0, it sends an alert directly to your Discord via Webhook.
  
### 4. Account Login
Initiates the email and PIN login mechanism to securely authenticate your session and saves the necessary access data locally to `config.json`.
  
### 5. Settings Menu
Allows you to configure your local environment variables:
  * **Webhook Setup**: Store the Discord webhook link used for the Notification Mode alerts.
  * **Location Setup (Address)**: Pre-set your default street address and city so the Dashboard loads instantly without asking for your location every time.
  * **Check Payment Methods**: Lists the saved payment cards currently attached to your account profile.

---

### Requirements
* Python 3.9+
* Internet Connection

*Disclaimer: This repository is intended for experimental educational purposes.*