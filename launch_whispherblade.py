#!/usr/bin/env python3
"""
🚀 WHISPHERBLADE LAUNCHER
========================
Launch the greatest open-source AI brain ever made!

Usage:
    python launch_whispherblade.py
    python launch_whispherblade.py --mode interactive
    python launch_whispherblade.py --sass-level 10
    python launch_whispherblade.py --config custom_config.json
"""

import sys
import os
import asyncio
import argparse
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from whispherblade_core import WhispherBlade
except ImportError as e:
    print(f"❌ Failed to import Whispherblade: {e}")
    print("Make sure whispherblade_core.py is in the same directory")
    sys.exit(1)

def print_banner():
    """Print the epic Whispherblade banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════════════╗
    ║                          🧠 WHISPHERBLADE 🧠                          ║
    ║                   The Ultimate AI Brain for TechSewa                  ║
    ║                                                                      ║
    ║  "Oh brilliant. You plugged the USB in the wrong way.               ║
    ║   Again. How human of you."                                          ║
    ║                                                                      ║
    ║  🎭 Personality: Sarcastic, Witty, Cyber-Philosopher                ║
    ║  🔧 Role: AI Technician, Healer, Digital Saint                      ║
    ║  ⚡ Version: 1.0.0 - "The Awakening"                                ║
    ╚══════════════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_dependencies():
    """Check for required dependencies"""
    missing_deps = []
    
    try:
        import requests
    except ImportError:
        missing_deps.append("requests")
    
    try:
        import psutil
    except ImportError:
        missing_deps.append("psutil")
    
    try:
        import aiohttp
    except ImportError:
        missing_deps.append("aiohttp")
    
    if missing_deps:
        print(f"⚠️  Missing required dependencies: {', '.join(missing_deps)}")
        print("Install with: pip install " + " ".join(missing_deps))
        return False
    
    return True

async def interactive_mode(brain):
    """Run Whispherblade in interactive mode"""
    print("\n🎮 Entering Interactive Mode")
    print("Commands: 'help', 'heal', 'status', 'diagnose', 'philosophy', 'quit'")
    print("=" * 70)
    
    while True:
        try:
            user_input = input("\n🧠 Whispherblade > ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\n💀 Whispherblade: 'Until next time, may your code compile and your sanity remain intact.'")
                break
                
            elif user_input.lower() == 'help':
                print("""
🎯 Available Commands:
  help       - Show this help
  heal       - Perform system healing
  status     - Show system status
  diagnose   - Run system diagnostics
  philosophy - Enter philosophical mode
  clear      - Clear screen
  config     - Show configuration
  modules    - List loaded modules
  quit/exit  - Exit Whispherblade
  
Or just ask any question naturally!
                """)
                
            elif user_input.lower() == 'heal':
                print("\n💊 Initiating healing protocols...")
                result = await brain.heal_system()
                print(f"🤖 {result['message']}")
                if result.get('sarcasm'):
                    print(f"💀 {result['sarcasm']}")
                    
            elif user_input.lower() == 'status':
                status = brain.get_status()
                print(f"""
📊 System Status:
  Version: {status['version']}
  Status: {status['status']}
  Uptime: {status['uptime']}
  Modules: {status['modules_loaded']}
  Queries Processed: {status['stats']['queries_processed']}
  Problems Solved: {status['stats']['problems_solved']}
  Sarcastic Remarks: {status['stats']['sarcastic_remarks']}
  Sarcasm Mode: {'ON' if status['sarcasm_mode'] else 'OFF'}
                """)
                
            elif user_input.lower() == 'diagnose':
                print("\n🔍 Running system diagnostics...")
                await brain._perform_background_diagnosis()
                print("✅ Diagnostic scan complete. Check logs for details.")
                
            elif user_input.lower() == 'philosophy':
                print("\n🧘 Entering Philosophical Mode...")
                if 'chat_engine' in brain.modules:
                    # This would work if the chat engine module was properly loaded
                    print("💭 'In the grand binary of existence, your errors are but temporary null pointers.'")
                else:
                    print("💭 'Consider: Is debugging not just the universe trying to understand itself?'")
                    
            elif user_input.lower() == 'clear':
                os.system('clear' if os.name == 'posix' else 'cls')
                print_banner()
                
            elif user_input.lower() == 'config':
                print(f"\n⚙️ Configuration: {brain.config_path}")
                print(f"Sarcasm Mode: {brain.sarcasm_mode}")
                print(f"Modules: {list(brain.modules.keys())}")
                
            elif user_input.lower() == 'modules':
                print(f"\n📦 Loaded Modules ({len(brain.modules)}):")
                for name, module in brain.modules.items():
                    print(f"  ✅ {name}: {module}")
                    
            else:
                # Regular query
                response = await brain.query(user_input)
                print(f"\n🤖 {response['response']}")
                if response.get('sarcasm'):
                    print(f"💀 {response['sarcasm']}")
                print(f"📊 Source: {response.get('source', 'unknown')} | "
                      f"Time: {response.get('processing_time', 0):.2f}s")
                      
        except KeyboardInterrupt:
            print("\n\n💀 Whispherblade interrupted by human incompetence...")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("💀 'Congratulations, you've managed to break the unbreakable.'")

async def daemon_mode(brain):
    """Run Whispherblade in daemon mode"""
    print("\n🔄 Running in Daemon Mode (background operation)")
    print("Whispherblade will perform background diagnostics and healing...")
    
    try:
        while True:
            await asyncio.sleep(300)  # 5 minutes
            await brain._perform_background_diagnosis()
    except KeyboardInterrupt:
        print("\n💀 Daemon mode stopped")

async def single_query_mode(brain, query):
    """Process a single query and exit"""
    print(f"\n🔍 Processing query: {query}")
    response = await brain.query(query)
    print(f"\n🤖 {response['response']}")
    if response.get('sarcasm'):
        print(f"💀 {response['sarcasm']}")

def main():
    """Main launcher function"""
    parser = argparse.ArgumentParser(
        description="Launch Whispherblade - The Ultimate AI Brain",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python launch_whispherblade.py
  python launch_whispherblade.py --mode interactive
  python launch_whispherblade.py --sass-level 10
  python launch_whispherblade.py --query "My computer is slow"
  python launch_whispherblade.py --config custom_config.json --mode daemon
        """
    )
    
    parser.add_argument(
        "--mode", 
        choices=["interactive", "daemon", "single"], 
        default="interactive",
        help="Operation mode (default: interactive)"
    )
    
    parser.add_argument(
        "--config", 
        help="Configuration file path (default: whispherblade_config.json)"
    )
    
    parser.add_argument(
        "--sass-level", 
        type=int, 
        choices=range(1, 11), 
        help="Sarcasm level 1-10 (default: from config)"
    )
    
    parser.add_argument(
        "--query", 
        help="Single query to process (sets mode to single)"
    )
    
    parser.add_argument(
        "--no-banner", 
        action="store_true", 
        help="Skip the banner display"
    )
    
    parser.add_argument(
        "--debug", 
        action="store_true", 
        help="Enable debug logging"
    )
    
    args = parser.parse_args()
    
    # Print banner unless disabled
    if not args.no_banner:
        print_banner()
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Cannot start Whispherblade due to missing dependencies")
        return 1
    
    # Set mode based on query
    if args.query:
        args.mode = "single"
    
    print(f"\n🚀 Initializing Whispherblade in {args.mode} mode...")
    
    # Initialize Whispherblade
    config_path = args.config or "whispherblade_config.json"
    brain = WhispherBlade(config_path=config_path)
    
    # Override sass level if specified
    if args.sass_level:
        brain.config["personality"]["sass_level"] = args.sass_level
        brain.sarcasm_mode = True
        print(f"💀 Sass level set to {args.sass_level}/10")
    
    # Set debug mode
    if args.debug:
        brain.config["log_level"] = "DEBUG"
        print("🐛 Debug mode enabled")
    
    async def run_brain():
        # Initialize the brain
        if not await brain.initialize():
            print("❌ Failed to initialize Whispherblade")
            return 1
        
        try:
            if args.mode == "interactive":
                await interactive_mode(brain)
            elif args.mode == "daemon":
                await daemon_mode(brain)
            elif args.mode == "single":
                await single_query_mode(brain, args.query)
        
        finally:
            await brain.shutdown()
        
        return 0
    
    # Run the brain
    try:
        exit_code = asyncio.run(run_brain())
        return exit_code
    except KeyboardInterrupt:
        print("\n\n💀 Whispherblade terminated by user")
        return 130
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)