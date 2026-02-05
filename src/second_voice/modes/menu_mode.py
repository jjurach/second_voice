import os
import time
import signal
import sys
from typing import Optional

from .base import BaseMode

class MenuMode(BaseMode):
    """
    Text-based menu mode for Second Voice.
    Minimal dependencies, works over SSH, supports $EDITOR.
    """

    def __init__(self, config, recorder, processor):
        """
        Initialize menu mode.

        :param config: Configuration manager
        :param recorder: Audio recorder
        :param processor: AI processor
        """
        super().__init__(config, recorder, processor)
        
        # Capture original signal handler
        self._original_sigint = signal.getsignal(signal.SIGINT)

    def start_recording(self) -> Optional[str]:
        """
        Start audio recording with a text countdown and VU meter.

        :return: Path to recorded audio file or None
        """
        self.show_status("🎤 Recording... (press Ctrl+C to stop)")
        
        try:
            # Temporarily replace SIGINT handler to allow controlled interrupt
            def sigint_handler(signum, frame):
                raise KeyboardInterrupt("Recording stopped by user")
            signal.signal(signal.SIGINT, sigint_handler)
            
            self.recorder.start_recording()
            
            while True:
                amp = self.recorder.get_amplitude()
                bar_len = min(int(amp * 50), 10)
                vu_bar = "#" * bar_len + "-" * (10 - bar_len)
                sys.stdout.write(f"\rLevel: [{vu_bar}] ")
                sys.stdout.flush()
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            audio_path = self.recorder.stop_recording()
            print("\nRecording stopped.")
            
        finally:
            # Restore original signal handler
            signal.signal(signal.SIGINT, self._original_sigint)
        
        if audio_path:
            self.show_status(f"✓ Recorded audio: {os.path.basename(audio_path)}")
        
        return audio_path


    def show_transcription(self, text: str):
        """
        Display transcription in text mode.

        :param text: Transcribed text
        """
        print(f"📝 Transcribed: {text}")

    def review_output(self, text: str, context: Optional[str] = None) -> str:
        """
        Allow user to review/edit output using $EDITOR.

        :param text: LLM output text
        :param context: Optional previous context
        :return: Edited or original output
        """
        # Create a temporary file for editing
        edit_file = self._create_temp_file()
        
        with open(edit_file, 'w') as f:
            if context:
                f.write("# Previous Context:\n")
                f.write(context + "\n\n")
            f.write("# Output:\n")
            f.write(text)
        
        # Launch editor
        edited_text = self._launch_editor(edit_file)
        
        # Extract output section (after "# Output:\n")
        output_marker_index = edited_text.find("# Output:\n")
        if output_marker_index != -1:
            edited_text = edited_text[output_marker_index + len("# Output:\n"):].strip()
        
        return edited_text

    def show_status(self, message: str):
        """
        Display status message in text mode.

        :param message: Status message
        """
        print(message)

    def _display_menu(self):
        """
        Display the main menu.
        """
        print("\nSecond Voice - Menu Mode")
        print("========================")
        print("[1] Record audio")
        print("[2] Show context")
        print("[3] Clear context")
        print("[4] Quit")

    def _save_output_for_google_drive(self, output: str, audio_path: str) -> Optional[str]:
        """Save output .md file to inbox directory with timestamp from audio file.

        Args:
            output: The final output text to save
            audio_path: Path to the archived audio file

        Returns:
            Path to saved output file, or None if saving failed
        """
        try:
            from pathlib import Path
            audio_file = Path(audio_path)

            # Extract timestamp and base name from audio file
            # Expected format: YYYY-MM-DD_HH-MM-SS_name.ext
            stem = audio_file.stem
            parts = stem.split('_', 2)  # Split into [YYYY-MM-DD, HH-MM-SS, name]

            if len(parts) >= 2:
                # Reconstruct timestamp and name
                timestamp = f"{parts[0]}_{parts[1]}"
                name = parts[2] if len(parts) > 2 else "recording"
            else:
                # Fallback if filename doesn't match expected format
                from ..utils.timestamp import get_timestamp
                timestamp = get_timestamp()
                name = stem

            # Create output filename in inbox directory
            inbox_dir = Path(self.config.get('google_drive.inbox_dir', 'dev_notes/inbox'))
            inbox_dir.mkdir(parents=True, exist_ok=True)

            output_filename = f"{timestamp}_{name}.md"
            output_path = inbox_dir / output_filename

            # Ensure unique filename
            counter = 1
            while output_path.exists():
                output_filename = f"{timestamp}_{name}-{counter}.md"
                output_path = inbox_dir / output_filename
                counter += 1

            # Save output
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(output)

            print(f"✓ Output saved: {output_path}")
            return str(output_path)
        except Exception as e:
            print(f"Warning: Could not save output to inbox: {e}")
            return None

    def run(self):
        """
        Main menu-driven workflow for Second Voice.
        """
        import logging
        logger = logging.getLogger(__name__)

        context = None
        output_file = None

        # Check for input file and output file from CLI
        input_file = self.config.get('input_file')
        cli_output_file = self.config.get('output_file')
        is_google_drive_input = input_file and str(input_file).startswith(
            str(self.config.get('google_drive.archive_dir', 'dev_notes/inbox-archive'))
        )

        # Debug logging
        if self.config.get('debug'):
            logger.debug(f"MenuMode.run() starting")
            logger.debug(f"  input_file: {input_file}")
            logger.debug(f"  cli_output_file: {cli_output_file}")
            logger.debug(f"  is_google_drive_input: {is_google_drive_input}")
            logger.debug(f"  no_edit: {self.config.get('no_edit')}")
            logger.debug(f"  keep_files: {self.config.get('keep_files')}")

        if input_file and os.path.exists(input_file):
            print(f"Processing input file: {input_file}")
            # Process the file directly as if option 1 was selected
            try:
                self.show_status("⌛ Transcribing...")
                # Generate timestamp for external file to ensure transcription is saved
                from ..utils.timestamp import get_timestamp
                file_timestamp = get_timestamp()
                transcription = self.processor.transcribe(input_file, file_timestamp)

                if transcription:
                    self.show_transcription(transcription)

                    # Process with LLM
                    self.show_status("⌛ Processing...")
                    output = self.processor.process_with_headers_and_fallback(
                        transcription,
                        recording_path=input_file,
                        context=context
                    )

                    # Determine where to save output
                    # Priority: CLI --output-file > Google Drive inbox > None
                    if cli_output_file:
                        output_file = cli_output_file
                    elif is_google_drive_input:
                        output_file = self._save_output_for_google_drive(output, input_file)

                    # Save output to file if specified
                    if output_file:
                        try:
                            os.makedirs(os.path.dirname(output_file) or '.', exist_ok=True)
                            with open(output_file, 'w', encoding='utf-8') as f:
                                f.write(output)
                            print(f"✓ Output saved: {output_file}")
                        except Exception as e:
                            print(f"Warning: Could not save output file: {e}")
                            output_file = None

                    # Skip editor if --no-edit flag is set
                    if self.config.get('no_edit'):
                        if not output_file:
                            print(f"📋 Output: {output}")
                        self.cleanup()
                        return output_file

                    # Review output
                    edited_output = self.review_output(output, context)

                    # Update context
                    context = edited_output
                    self.processor.save_context(context)

                    # Update output file with edited content if file was specified
                    if output_file:
                        try:
                            with open(output_file, 'w', encoding='utf-8') as f:
                                f.write(edited_output)
                            print(f"✓ Output updated: {output_file}")
                        except Exception as e:
                            print(f"Warning: Could not update output file: {e}")

                print("\nInput file processed.")
                # We don't delete the input file
                return output_file

            except Exception as e:
                # Check if transcription file exists for recovery
                from ..utils.timestamp import create_whisper_filename
                whisper_file = create_whisper_filename(self.processor.config.get('temp_dir', './tmp'), file_timestamp)
                if os.path.exists(whisper_file):
                    print(f"Error processing input file: {e}")
                    print(f"✓ Transcription saved to: {whisper_file}")
                else:
                    print(f"Error processing input file: {e}")
                return None

        while True:
            try:
                self._display_menu()
                choice = input("Choice: ").strip()

                if choice == '1':  # Record
                    audio_path = self.start_recording()
                    if audio_path:
                        # Generate timestamp for whisper file tracking
                        from ..utils.timestamp import get_timestamp, create_whisper_filename
                        recording_timestamp = get_timestamp()

                        # Transcribe
                        self.show_status("⌛ Transcribing...")
                        try:
                            transcription = self.processor.transcribe(audio_path, recording_timestamp)

                            if transcription:
                                self.show_transcription(transcription)

                                # Process with LLM
                                self.show_status("⌛ Processing...")
                                output = self.processor.process_with_headers_and_fallback(
                                    transcription,
                                    recording_path=audio_path,
                                    context=context
                                )

                                # Save to CLI output file if specified
                                if cli_output_file:
                                    try:
                                        os.makedirs(os.path.dirname(cli_output_file) or '.', exist_ok=True)
                                        with open(cli_output_file, 'w', encoding='utf-8') as f:
                                            f.write(output)
                                        print(f"✓ Output saved: {cli_output_file}")
                                        output_file = cli_output_file
                                    except Exception as e:
                                        print(f"Warning: Could not save output file: {e}")

                                # Skip editor if --no-edit flag is set
                                if self.config.get('no_edit'):
                                    if not cli_output_file:
                                        print(f"📋 Output: {output}")
                                    # Update context even without editing
                                    context = output
                                    self.processor.save_context(context)
                                else:
                                    # Review output
                                    edited_output = self.review_output(output, context)

                                    # Update context
                                    context = edited_output
                                    self.processor.save_context(context)

                                    # Update CLI output file with edited content if specified
                                    if cli_output_file:
                                        try:
                                            with open(cli_output_file, 'w', encoding='utf-8') as f:
                                                f.write(edited_output)
                                            print(f"✓ Output updated: {cli_output_file}")
                                        except Exception as e:
                                            print(f"Warning: Could not update output file: {e}")

                                # Clean up temporary audio file (but protect user-provided input files)
                                input_file = self.config.get('input_file')
                                if not self.config.get('keep_files'):
                                    if audio_path != input_file:
                                        os.unlink(audio_path)
                            else:
                                # Transcription failed - keep files for debugging
                                print(f"⚠️ Transcription failed - keeping audio file: {audio_path}")
                                whisper_file = create_whisper_filename(self.processor.config.get('temp_dir', './tmp'), recording_timestamp)
                                if os.path.exists(whisper_file):
                                    print(f"⚠️ Kept whisper output: {whisper_file}")
                        except Exception as e:
                            # Processing failed - keep files for debugging
                            print(f"⚠️ Error during processing: {e}")
                            print(f"⚠️ Kept audio file for debugging: {audio_path}")
                            whisper_file = create_whisper_filename(self.processor.config.get('temp_dir', './tmp'), recording_timestamp)
                            if os.path.exists(whisper_file):
                                print(f"⚠️ Kept whisper output: {whisper_file}")

                elif choice == '2':  # Show context
                    current_context = context or self.processor.load_context()
                    if current_context:
                        print(f"Current Context ({len(current_context)} chars):")
                        print(current_context)
                    else:
                        print("No context available.")

                elif choice == '3':  # Clear context
                    context = None
                    self.processor.save_context('')
                    print("Context cleared.")

                elif choice == '4':  # Quit
                    self.cleanup()
                    break

                else:
                    print("Invalid choice. Please select 1-4.")

            except KeyboardInterrupt:
                print("\nExiting...")
                self.cleanup()
                break
            except Exception as e:
                print(f"An error occurred: {e}")

        # Restore resources
        self.cleanup()
