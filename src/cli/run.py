import argparse
import sys
import os

# Ensure src directory is in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.abspath(os.path.join(current_dir, '../'))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from second_voice.core.config import ConfigurationManager
from second_voice.core.recorder import AudioRecorder
from second_voice.core.processor import AIProcessor
from second_voice.modes import detect_mode, get_mode

def main():
    parser = argparse.ArgumentParser(description="Second Voice - AI Assistant")
    parser.add_argument('--mode', choices=['auto', 'gui', 'tui', 'menu'], default='auto', help="Interaction mode")
    parser.add_argument('--keep-files', action='store_true', help="Keep temporary files after execution")
    parser.add_argument('--file', type=str, help="Input audio file to process (bypasses recording)")
    parser.add_argument('--debug', action='store_true', help="Enable debug logging")
    parser.add_argument('--verbose', action='store_true', help="Enable verbose output")
    args = parser.parse_args()

    # Init config
    config = ConfigurationManager()
    
    # Override config with CLI args if provided
    if args.mode != 'auto':
        config.set('mode', args.mode)
    
    if args.keep_files:
        config.set('keep_files', True)
        
    if args.file:
        config.set('input_file', os.path.abspath(args.file))

    if args.debug:
        config.set('debug', True)
        
    if args.verbose:
        config.set('verbose', True)

    # Init engine
    try:
        recorder = AudioRecorder(config)
        processor = AIProcessor(config)
    except Exception as e:
        print(f"Error initializing engine: {e}")
        sys.exit(1)

    # Detect mode
    try:
        mode_name = detect_mode(config)
        print(f"Starting in {mode_name} mode...")
    except Exception as e:
        print(f"Error detecting mode: {e}")
        mode_name = 'menu' # Fallback
        print(f"Falling back to {mode_name} mode...")

    # Run mode
    try:
        mode = get_mode(mode_name, config, recorder, processor)
        mode.run()
    except Exception as e:
        print(f"Error initializing mode {mode_name}: {e}")
        sys.exit(1)
    finally:
        # Cleanup
        if 'recorder' in locals():
            if not config.get('keep_files'):
                recorder.cleanup_temp_files()
            else:
                print(f"Keeping temporary files in {config.get('temp_dir')}")

if __name__ == "__main__":
    main()