# XimeHelper

An AI-powered file management and automation platform.

## Setup

1. Create and activate virtual environment:
```bash
python -m venv ximehelper
source ximehelper/bin/activate  # On macOS/Linux
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Setup configuration:
   - Copy `config/base.ini.example` to `config/base.ini`
   - Copy `config/autofile.ini.example` to `config/autofile.ini`
   - Generate a secret key:
     ```bash
     python -c "import secrets; print(secrets.token_hex(16))"
     ```
   - Create `.env` file and add your secret key:
     ```
     SECRET_KEY=your-generated-key
     OPENAI_API_KEY=your-openai-key
     ```
   - Modify configuration files according to your needs

4. Run the application:
```bash
python run.py
```

## Configuration

The application uses a modular configuration system:

- `config/base.ini`: Platform-level configuration (logging, security, API)
- `config/autofile.ini`: File management specific configuration

Each module can have its own configuration file in the `config` directory.

