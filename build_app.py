import PyInstaller.__main__
import os
import shutil
import subprocess

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
        
        # macOS specific options for permissions
        '--osx-bundle-identifier=com.voicetotext.app',
        '--osx-entitlements-file=entitlements.plist',
    ]
    
    for lib in hidden_imports:
        args.append(f'--hidden-import={lib}')
        
    print(f"📦 Packaging {APP_NAME}...")
    PyInstaller.__main__.run(args)
    
    # Post-build: Re-sign with hardened runtime
    app_path = os.path.abspath(f'dist/{APP_NAME}.app')
    print(f"🔐 Code signing with entitlements...")
    
    try:
        # Ad-hoc signing with hardened runtime and entitlements
        subprocess.run([
            'codesign',
            '--force',
            '--deep',
            '--sign', '-',  # Ad-hoc signature
            '--options', 'runtime',  # Hardened runtime
            '--entitlements', 'entitlements.plist',
            app_path
        ], check=True)
        print("✅ Code signing completed!")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Code signing failed: {e}")
        print("App may not have full permissions until signed properly.")
    
    print("✅ Build complete!")
    print(f"📂 You can find your app in: {app_path}")
    print("\n⚠️  IMPORTANT: After first launch, you may need to:")
    print("   1. Go to System Settings → Privacy & Security → Accessibility")
    print("   2. Remove VoiceToText.app from the list")
    print("   3. Re-add it and enable the toggle")

if __name__ == "__main__":
    # check if PyInstaller is installed
    try:
        import PyInstaller
        build()
    except ImportError:
        print("❌ PyInstaller not found. Please install it with: pip install pyinstaller")
