import PyInstaller.__main__
import os
import shutil

APP_NAME = "VoiceToText"
SCRIPT_NAME = "voice_to_text.py"

def build():
    print("🚀 Starting build process...")
    
    # specific hidden imports that whisper/opencc often need
    hidden_imports = [
        'faster_whisper',
        'opencc', 
        'pynput.keyboard._darwin', 
        'pynput.mouse._darwin'
    ]
    
    args = [
        SCRIPT_NAME,
        '--name=%s' % APP_NAME,
        '--windowed',  # specific for Mac OS .app
        '--noconfirm',
        '--clean',
        
        # Hooks and Hidden Imports
        '--collect-all=faster_whisper',
        '--collect-all=opencc',
    ]
    
    for lib in hidden_imports:
        args.append(f'--hidden-import={lib}')
        
    print(f"📦 Packaging {APP_NAME}...")
    PyInstaller.__main__.run(args)
    
    print("✅ Build complete!")
    print(f"📂 You can find your app in: {os.path.abspath('dist/' + APP_NAME + '.app')}")

if __name__ == "__main__":
    # check if PyInstaller is installed
    try:
        import PyInstaller
        build()
    except ImportError:
        print("❌ PyInstaller not found. Please install it with: pip install pyinstaller")
