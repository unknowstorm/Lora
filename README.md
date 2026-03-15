# Lora: Local Virtual Assistant

Lora is a personal assistant designed to automate routine tasks and enhance your leisure time. Unlike Siri or Google Assistant, it works completely offline, ensuring the absolute security of your data.

<p align="center">
  <img src="https://github.com/user-attachments/assets/917718b9-b8ed-47af-8c0e-4b02cd8718f5" width="1200" height="800" alt="Lora Banner">
</p>


## 🌟 Key Features

* 🔒 **Privacy:** All data (notes, settings) is stored locally in JSON. No clouds. Everything stays with you.
* 🌐 **Full Autonomy:** Works without an internet connection.
* ⚙️ **Deep Integration:** Scans the system PATH, allowing you to launch program presets.
* 🐧 **Cross-platform:** Runs on Windows and Linux (tested on Debian). Bug fixes are currently in progress. :)
* ✨ **Visuals:** Lora's model is an animated character without a background. She blinks, moves across the screen, and reacts to the mouse, creating a sense of presence. You can redesign her at any time however you like.

---

## 🛠 Functionality

* **Notes and Reminders:** A smart storage system using `reminders.json`.
* **Timing System:** Uses the `QTimer` library for accurate notification delivery.
* **Application Presets:** Create sets of programs (e.g., "Work" or "Study") and launch multiple apps with a single click.
* **Quick Search:** Rapid search functionality on the internet.

---

## 📸 Gallery

![Interface Showcase](https://github.com/HunterXG/Lora/blob/b6521a2b938ececa8acd725fdf8ab32a7e3e6eef/%23buildobject/screenshotn1.png)

---

## 🚀 How to Install

### Windows
1.  Download the archive.
2.  Extract and run `Lora.exe`.
3.  **Note:** Please disable your antivirus. Since Lora scans the system for applications (PATH), some antiviruses may trigger. Don't worry, there are no viruses—I haven't learned how to write them yet.

### Linux
1.  Install additional libraries (if not already installed):
    ```bash
    sudo apt update
    sudo apt install python3-venv python3-pip
    ```
2.  Install the core library:
    ```bash
    sudo pip install PyQt5
    ```
3.  3.  Navigate to the directory:
    ```bash
    cd /path_to_Lora_folder
    ```
4.  Run with sudo (required for system functions to work correctly):
    ```bash
    sudo python3 assistant.py
    ```

---

## ⚠️ Project Status: Alpha_0.5
The project is under active development. We apologize in advance for any bugs or "rawness"—we are working on it! :3

---

## 💬 A Word from the Author: by unknowstorm

Greetings, dear friends!

Before you begin, answer one question: how often do you find yourself drowning in routine, wishing for a little helper?

**Lora** was born out of my time spent in the game *Voice of the Void* (shoutout to MrDrNose!). After crafting the Omega-Kerfur, I realized how much an assistant could spice up boring tasks. I wanted to create something similar for real life.

So, please welcome project "Lora," which serves as a handy companion in your daily work routine.

### Project Team:
* **unknowstorm:** Concept author and sprite artist.
* **HunterXG:** Lead developer.

Huge thanks for the help with the implementation, as I'm not very strong in coding and deadlines were biting (but you don't really need to know that :3).

I hope you enjoy Lora. Happy using!

**P.S. The cake is not a lie.**
