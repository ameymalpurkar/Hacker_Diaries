# 🖥️ Hacker Diaries - AI-Powered Journal CLI

**Hacker Diaries** is a powerful command-line journaling application designed for developers and tech enthusiasts who want to document their coding journey, track personal growth, and gain deeper insights into their daily experiences.

Built with Python and powered by Google's Gemini AI, this intelligent terminal-based tool transforms simple journal entries into meaningful self-discovery. The app features a beautiful, colorful console interface that makes journaling feel natural and engaging, while AI analysis helps you understand patterns in your mood, productivity, and personal development.

Whether you're logging your latest coding challenges, managing daily tasks, or reflecting on personal goals, Hacker Diaries combines the simplicity of command-line efficiency with the power of artificial intelligence. Get personalized writing prompts, emotional insights, and productivity recommendations that evolve with your unique story – because every developer's journey deserves to be remembered and understood.

---

## 🌟 Features

### 📝 **Smart Journaling**
- **Rich Console Interface** - Beautiful, colorful terminal UI with panels and tables
- **Quick Entry System** - Add multiple entries with comma separation
- **Timestamped Entries** - Automatic date/time tracking for every entry
- **Easy Management** - View, delete, and organize your thoughts effortlessly

### 🤖 **AI-Powered Insights** 
- **Journal Analysis** - Deep insights into your thoughts, patterns, and emotional trends
- **Mood Tracking** - AI-powered mood analysis with wellbeing scoring (1-10)
- **Personal Growth** - Track development, learning, and progress over time
- **Smart Prompts** - AI-generated journal prompts based on your focus areas
- **Reflection Questions** - Thoughtful questions for deeper self-discovery

### ✅ **Task Management**
- **Priority System** - High, medium, low priority task organization
- **Status Tracking** - Mark tasks as done or not done
- **AI Task Analysis** - Get insights on productivity and time management
- **Smart Suggestions** - AI-generated task recommendations based on your goals
- **Bulk Operations** - Add, delete, and modify multiple tasks efficiently

### ⚙️ **Easy Configuration**
- **Multiple API Key Input Methods** - Direct paste, file import, or secure password mode
- **Persistent Settings** - JSON-based configuration storage
- **One-Time Setup** - Configure once, use forever
- **Security First** - API keys stored locally, never transmitted

---

## 🚀 Quick Start

### 1. **Installation**

```bash
# Clone the repository
git clone https://github.com/ameymalpurkar/Hacker_Diaries.git
cd journaling_CLI

# Install dependencies
pip install rich google-generativeai
```

### 2. **Get Your AI API Key**
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key for setup

### 3. **Launch the Application**

```bash
python journal_cli.py secret
```

### 4. **Configure AI (First Time)**

```bash
# Choose any method:
config → api → [paste your key]           # Direct paste
config → file → [create api_key.txt]      # File-based import
```

---

## 🎯 Usage Guide

### **Main Commands**

| Command | Description | Example |
|---------|-------------|---------|
| `add` | Add journal entries | Multiple entries: "Had coffee, Read a book, Feeling great" |
| `show` | View all journal entries | Displays beautiful table with dates and entries |
| `delete` | Remove specific entries | Select by number: "1,3,5" |
| `task` | Open task management | Full task system with AI assistance |
| `ai` | Access AI assistant | Analysis, suggestions, and insights |
| `journal-ai` | Direct journal AI | Quick access to journal analysis |
| `config` | Configuration menu | API key setup and management |
| `exit` | Graceful exit | Save and quit |
| `404` | Quick quit | Immediate termination |

### **AI Features**

#### 🧠 **Journal AI Menu** (`journal-ai`)
- **`analyze`** - Comprehensive analysis of your journal entries
- **`mood`** - Emotional patterns and wellbeing tracking  
- **`prompts`** - Personalized writing suggestions based on your focus

#### 🤖 **Full AI Menu** (`ai`)
- **`tasks`** → `analyze` - Productivity insights and task patterns
- **`tasks`** → `suggest` - AI-generated task recommendations
- **`journal`** - Complete journal analysis suite
- **`config`** - AI settings and API key management

---

---

---

## 🛠️ Technical Details

### **Architecture**
- **Frontend**: Rich Console UI with beautiful formatting
- **Backend**: Python 3.8+ with modular function design
- **AI Integration**: Google Gemini 1.5 Flash for analysis
- **Data Storage**: Local JSON and text files
- **Security**: Local API key storage, no data transmission

### **Dependencies**
- rich
- google-generativeai (optional, for AI features)

### **File Structure**
```
journaling_CLI/
├── journal_cli.py              # Main application
├── journal.txt                 # Your journal entries
├── tasks.txt                   # Task management data
├── config.json                 # Configuration & API keys
└── README.md                   # This file
```

---

## 🧪 Testing & Quality

This project includes comprehensive testing with **95% coverage**:

- ✅ **32/32 test cases passing**
- ✅ **Core functionality validated**
- ✅ **AI integration tested**
- ✅ **Error handling verified**
- ✅ **Security assessment complete**

Run tests:
```bash
python test_app_comprehensive.py    # Core functionality
python validate_app.py             # Production readiness
```

View full test report: [COMPREHENSIVE_TEST_REPORT.md](COMPREHENSIVE_TEST_REPORT.md)

---

## 🔒 Privacy & Security

### **Data Privacy**
- 🔐 **Local Storage Only** - All data stays on your machine
- 🔐 **No Cloud Sync** - Your thoughts remain private
- 🔐 **API Key Security** - Stored locally, never transmitted
- 🔐 **No Logging** - Personal data never logged or tracked

### **Security Features**
- Secure API key storage in JSON format
- Automatic cleanup of temporary files
- Input validation and sanitization
- Graceful error handling without data exposure

---

## 🎨 Customization

### **Activation Code**
Change the secret activation code by modifying:
```python
ACTIVATION_CODE = "your_secret_word"
```

### **File Paths**
Customize storage locations:
```python
JOURNAL_FILE = 'your_journal.txt'
TASK_FILE = 'your_tasks.txt'
CONFIG_FILE = 'your_config.json'
```

### **AI Model**
Switch between Gemini models:
```python
model = genai.GenerativeModel("gemini-1.5-pro")  # More capable
model = genai.GenerativeModel("gemini-1.5-flash") # Faster (default)
```

---

---

## � Privacy

- All data is stored locally (plain text files)
- API key (if used) is stored locally in config.json
- No analytics or tracking
