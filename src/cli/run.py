import argparse
import sys
import os
import subprocess
from pathlib import Path

# Ensure src directory is in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.abspath(os.path.join(current_dir, '../'))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from second_voice.core.config import ConfigurationManager
from second_voice.core.recorder import AudioRecorder
from second_voice.core.processor import AIProcessor
from second_voice.modes import detect_mode, get_mode


# Phase 2: Validation Helper Functions

def validate_pipeline_mode_args(args):
    """Validate pipeline mode arguments and their dependencies."""
    # Only validate if we have actual pipeline mode attributes (not None or mock objects)
    if not hasattr(args, 'transcribe_only'):
        return

    if getattr(args, 'transcribe_only', False) and not getattr(args, 'audio_file', None):
        print("Error: --transcribe-only requires --audio-file")
        print("\nUsage: second-voice --transcribe-only --audio-file <path> [--text-file <path>]")
        sys.exit(3)

    if getattr(args, 'translate_only', False) and not getattr(args, 'text_file', None):
        print("Error: --translate-only requires --text-file")
        print("\nUsage: second-voice --translate-only --text-file <path> [--output-file <path>]")
        sys.exit(3)

    # Validate input provider arguments
    input_provider = getattr(args, 'input_provider', 'default')
    keep_remote = getattr(args, 'keep_remote', False)
    record_only = getattr(args, 'record_only', False)
    audio_file = getattr(args, 'audio_file', None)

    if keep_remote and input_provider != 'google-drive':
        print("Error: --keep-remote only valid with --input-provider google-drive")
        sys.exit(3)

    if input_provider == 'google-drive':
        if record_only:
            print("Error: --input-provider google-drive conflicts with --record-only")
            sys.exit(3)
        if audio_file:
            print("Error: --input-provider google-drive conflicts with --audio-file")
            sys.exit(3)


def validate_output_file(file_path, operation_name):
    """Validate output file doesn't already exist."""
    if os.path.exists(file_path):
        print(f"Error: Output file already exists: {file_path}")
        print(f"\nCannot overwrite existing file in {operation_name} mode.")
        print(f"\nSuggestion: Use a different filename or remove the existing file first.")
        sys.exit(2)


def resolve_file_path(file_path):
    """Resolve and validate file path."""
    if not file_path:
        return None

    # Resolve to absolute path
    abs_path = os.path.abspath(file_path)

    # Validate parent directory exists
    parent_dir = os.path.dirname(abs_path)
    if parent_dir and not os.path.exists(parent_dir):
        print(f"Error: Parent directory does not exist: {parent_dir}")
        sys.exit(1)

    return abs_path


def invoke_editor(file_path, config, args):
    """Invoke editor on specified file."""
    # Determine editor command using resolution chain: CLI → Config → $EDITOR → default
    editor_cmd = None

    if args.editor_command:
        editor_cmd = args.editor_command
    elif config.get('editor_command'):
        editor_cmd = config.get('editor_command')
    elif 'EDITOR' in os.environ:
        editor_cmd = os.environ['EDITOR']
    else:
        # System default
        editor_cmd = 'nano'

    # Construct full command
    full_cmd = f'{editor_cmd} "{file_path}"'

    # Execute
    try:
        subprocess.run(full_cmd, shell=True, check=False)
    except Exception as e:
        print(f"Warning: Error invoking editor: {e}")


# Phase 3: Pipeline Mode Implementation Functions

def run_record_only(config, args, recorder):
    """Execute record-only pipeline mode."""
    # Determine output path
    if args.audio_file:
        output_path = args.audio_file
    else:
        # Generate temp file
        from second_voice.utils.timestamp import create_recording_filename
        temp_dir = config.get('temp_dir', './tmp')
        output_path = create_recording_filename(temp_dir)

    # Record
    print(f"Recording to: {output_path}")
    try:
        recorder.record(output_path)
        print(f"Recorded: {output_path}")
        return 0
    except Exception as e:
        print(f"Error: Recording failed: {e}")
        return 1


def run_transcribe_only(config, args, processor):
    """Execute transcribe-only pipeline mode."""
    # Input file already validated in Phase 2
    audio_path = args.audio_file

    # Determine output path
    if args.text_file:
        output_path = args.text_file
    else:
        # Generate temp file
        from second_voice.utils.timestamp import create_whisper_filename, get_timestamp
        temp_dir = config.get('temp_dir', './tmp')
        timestamp = get_timestamp()
        output_path = create_whisper_filename(temp_dir, timestamp)

    # Transcribe
    print(f"Transcribing: {audio_path}")
    try:
        transcript = processor.transcribe(audio_path)

        if not transcript:
            print("Error: Transcription failed")
            return 1

        # Save transcript
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(transcript)

        print(f"Transcribed: {output_path}")
        return 0
    except Exception as e:
        print(f"Error: Transcription failed: {e}")
        return 1


def run_translate_only(config, args, processor):
    """Execute translate-only pipeline mode."""
    # Input file already validated in Phase 2
    text_path = args.text_file

    # Read input text
    try:
        with open(text_path, 'r', encoding='utf-8') as f:
            transcript = f.read()
    except Exception as e:
        print(f"Error reading text file: {e}")
        return 1

    # Determine output path
    if args.output_file:
        output_path = args.output_file
    else:
        # Generate temp file with output suffix
        from second_voice.utils.timestamp import get_timestamp
        temp_dir = config.get('temp_dir', './tmp')
        timestamp = get_timestamp()
        output_path = os.path.join(temp_dir, f"output-{timestamp}.md")

    # Process/translate
    print(f"Processing: {text_path}")
    try:
        result = processor.process_with_headers_and_fallback(transcript, context=text_path)

        if not result:
            print("Error: Translation/processing failed")
            return 1

        # Save result
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result)

        print(f"Processed: {output_path}")
        return 0
    except Exception as e:
        print(f"Error: Translation/processing failed: {e}")
        return 1


def get_audio_file(args, config):
    """Determine audio file source based on input provider.

    Args:
        args: Parsed command-line arguments.
        config: ConfigurationManager instance.

    Returns:
        Path to audio file, or None if no file available.
    """
    input_provider = getattr(args, 'input_provider', 'default')
    keep_remote = getattr(args, 'keep_remote', False)
    audio_file = getattr(args, 'audio_file', None)

    if input_provider == 'google-drive':
        from second_voice.providers import GoogleDriveProvider
        try:
            provider = GoogleDriveProvider(config, keep_remote=keep_remote)
            archive_path = provider.fetch_and_archive()
            if archive_path is None:
                print("No files found in Google Drive folder")
                return None
            print(f"Fetched from Google Drive: {archive_path}")
            return archive_path
        except Exception as e:
            print(f"Error fetching from Google Drive: {e}")
            return None

    elif audio_file:
        return Path(audio_file)

    else:
        # Default: record via mic (existing behavior)
        return None  # Signals to use recording


def main():
    parser = argparse.ArgumentParser(
        description="Second Voice - AI Assistant",
        epilog="""
Pipeline mode examples:
  second-voice --record-only --audio-file recording.wav
  second-voice --transcribe-only --audio-file recording.wav --text-file transcript.txt
  second-voice --translate-only --text-file transcript.txt --output-file final.md
        """
    )

    # Mode and interaction options
    parser.add_argument('--mode', choices=['auto', 'gui', 'tui', 'menu'], default='menu',
                        help="Interaction mode (default: menu)")

    # Pipeline mode options (mutually exclusive)
    pipeline_group = parser.add_mutually_exclusive_group()
    pipeline_group.add_argument('--record-only', action='store_true',
                                help="Record audio and exit (no transcription or translation)")
    pipeline_group.add_argument('--transcribe-only', action='store_true',
                                help="Transcribe existing audio file (requires --audio-file)")
    pipeline_group.add_argument('--translate-only', action='store_true',
                                help="Translate/process existing text file (requires --text-file)")

    # Input provider options
    input_group = parser.add_argument_group("Input Provider")
    input_group.add_argument('--input-provider',
                            choices=['default', 'google-drive'],
                            default='default',
                            help="Input source: 'default' (record), 'google-drive' (fetch from Drive)")
    input_group.add_argument('--keep-remote',
                            action='store_true',
                            help="Keep remote file after download (only with --input-provider google-drive)")

    # File parameters
    parser.add_argument('--file', type=str,
                        help="Input audio file to process (bypasses recording)")
    parser.add_argument('--audio-file', type=str,
                        help="Audio file path (input for --transcribe-only, output for --record-only)")
    parser.add_argument('--text-file', type=str,
                        help="Text file path (input for --translate-only, output for --transcribe-only)")
    parser.add_argument('--output-file', type=str,
                        help="Output file path (for --translate-only)")

    # Editor options
    parser.add_argument('--editor-command', type=str,
                        help="Editor command to use (e.g., 'code --wait', 'emacs')")
    parser.add_argument('--no-edit', action='store_true',
                        help="Skip editor after file processing")

    # General options
    parser.add_argument('--keep-files', action='store_true',
                        help="Keep temporary files after execution")
    parser.add_argument('--debug', action='store_true',
                        help="Enable debug logging")
    parser.add_argument('--verbose', action='store_true',
                        help="Enable verbose output")

    args = parser.parse_args()

    # Helper function to get string args safely (handling mocks)
    def get_str_arg(obj, attr_name, default=None):
        """Get string argument from args, returns None if not a real string."""
        val = getattr(obj, attr_name, default)
        # Check if it's a real string, not a mock or None
        return val if isinstance(val, str) else default

    # Validate pipeline mode arguments (check for required dependencies)
    validate_pipeline_mode_args(args)

    # Resolve file paths (only for actual string paths, not None or mock objects)
    audio_file = get_str_arg(args, 'audio_file')
    text_file = get_str_arg(args, 'text_file')
    output_file = get_str_arg(args, 'output_file')

    if audio_file and isinstance(audio_file, str):
        args.audio_file = resolve_file_path(audio_file)
    if text_file and isinstance(text_file, str):
        args.text_file = resolve_file_path(text_file)
    if output_file and isinstance(output_file, str):
        args.output_file = resolve_file_path(output_file)

    # Validate output files don't exist (overwrite protection)
    record_only = getattr(args, 'record_only', False)
    transcribe_only = getattr(args, 'transcribe_only', False)
    translate_only = getattr(args, 'translate_only', False)
    editor_command = get_str_arg(args, 'editor_command')

    if record_only is True and audio_file and isinstance(audio_file, str):
        validate_output_file(audio_file, "record-only")
    if transcribe_only is True and text_file and isinstance(text_file, str):
        validate_output_file(text_file, "transcribe-only")
    if translate_only is True and output_file and isinstance(output_file, str):
        validate_output_file(output_file, "translate-only")

    # Init config
    config = ConfigurationManager()

    # Set editor command if provided (only if it's a real string, not a mock)
    if editor_command:
        config.set('editor_command', editor_command)

    # Override config with CLI args if provided
    if args.mode != 'auto':
        config.set('mode', args.mode)

    if args.keep_files:
        config.set('keep_files', True)

    if args.debug:
        config.set('debug', True)
        # Enable debug logging
        import logging
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logging.debug("Debug mode enabled")

    if args.verbose:
        config.set('verbose', True)
        print("Verbose mode enabled")

    if args.no_edit:
        config.set('no_edit', True)

    # Store output file in config for menu mode access
    if output_file and isinstance(output_file, str):
        config.set('output_file', output_file)

    # Handle --file as alias for --audio-file (for backward compatibility)
    file_arg = get_str_arg(args, 'file')
    if file_arg and not audio_file:
        audio_file = file_arg
        args.audio_file = file_arg

    # Get input file from provider (for normal mode, not pipeline modes)
    input_provider = getattr(args, 'input_provider', 'default')
    if not (record_only is True or transcribe_only is True or translate_only is True):
        if input_provider == 'google-drive':
            # Fetch from Google Drive
            fetched_file = get_audio_file(args, config)
            if fetched_file:
                config.set('input_file', str(fetched_file))
        elif audio_file and isinstance(audio_file, str):
            # Validate and set input file for normal mode
            input_file_path = audio_file

            # Validate file exists for input mode
            if not os.path.exists(input_file_path):
                print(f"Error: Input file not found: {input_file_path}")
                sys.exit(1)

            # Validate file is readable
            if not os.access(input_file_path, os.R_OK):
                print(f"Error: Input file not readable: {input_file_path}")
                sys.exit(1)

            # Validate file format (handle both soundfile and AAC formats)
            try:
                from second_voice.audio.aac_handler import AACHandler
                import soundfile as sf

                # Check if it's an AAC file
                if AACHandler.is_aac_file(input_file_path):
                    # Validate AAC file
                    valid, error_msg = AACHandler.validate_aac_file(input_file_path)
                    if not valid:
                        print(f"Error: {error_msg}")
                        sys.exit(1)

                    # Get AAC file info if verbose
                    if args.verbose:
                        duration = AACHandler.get_duration(input_file_path)
                        if duration:
                            print(f"Detected AAC audio: {duration:.1f}s")
                        else:
                            print(f"Detected AAC audio file")
                else:
                    # Use soundfile for other formats
                    info = sf.info(input_file_path)
                    if args.verbose:
                        print(f"Detected audio: {info.samplerate}Hz, {info.channels}ch, {info.duration:.1f}s")
            except Exception as e:
                print(f"Error: Invalid audio file: {e}")
                sys.exit(1)

            config.set('input_file', input_file_path)

    # Init engine
    try:
        recorder = AudioRecorder(config)
        processor = AIProcessor(config)
    except Exception as e:
        print(f"Error initializing engine: {e}")
        sys.exit(1)

    # Handle pipeline modes (fire and forget) - only if boolean flags are set
    if record_only is True:
        exit_code = run_record_only(config, args, recorder)
        sys.exit(exit_code)

    if transcribe_only is True:
        exit_code = run_transcribe_only(config, args, processor)
        sys.exit(exit_code)

    if translate_only is True:
        exit_code = run_translate_only(config, args, processor)
        sys.exit(exit_code)

    # Normal mode handling (interactive workflow)
    # Detect mode
    try:
        mode_name = detect_mode(config)
        print(f"Starting in {mode_name} mode...")
    except Exception as e:
        print(f"Error detecting mode: {e}")
        mode_name = 'menu' # Fallback
        print(f"Falling back to {mode_name} mode...")

    # GUI mode doesn't support --file input
    if mode_name == 'gui' and config.get('input_file'):
        print("Warning: --file not supported in GUI mode. Falling back to menu mode...")
        mode_name = 'menu'
        config.set('mode', 'menu')

    # Run mode
    try:
        mode = get_mode(mode_name, config, recorder, processor)
        output_file = mode.run()
    except Exception as e:
        print(f"Error initializing mode {mode_name}: {e}")
        sys.exit(1)
    finally:
        # Cleanup
        if 'recorder' in locals():
            if not config.get('keep_files'):
                recorder.cleanup_temp_files()
            else:
                # List files being kept
                temp_dir = config.get('temp_dir')
                # Only list files if temp_dir is a valid string path
                if temp_dir and isinstance(temp_dir, str) and os.path.exists(temp_dir):
                    try:
                        files = [f for f in os.listdir(temp_dir) if os.path.isfile(os.path.join(temp_dir, f))]
                        if files:
                            print(f"Keeping temporary files:")
                            for filename in sorted(files):
                                file_path = os.path.join(temp_dir, filename)
                                print(f"  {file_path}")
                    except (OSError, TypeError):
                        pass

if __name__ == "__main__":
    main()