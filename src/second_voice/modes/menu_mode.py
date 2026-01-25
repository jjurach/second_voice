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
                bar_len = int(amp * 10)
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

    def run(self):
        """
        Main menu-driven workflow for Second Voice.
        """
        context = None

        while True:
            try:
                self._display_menu()
                choice = input("Choice: ").strip()

                if choice == '1':  # Record
                    audio_path = self.start_recording()
                    if audio_path:
                        # Transcribe
                        self.show_status("⌛ Transcribing...")
                        transcription = self.processor.transcribe(audio_path)
                        
                        if transcription:
                            self.show_transcription(transcription)
                            
                            # Process with LLM
                            self.show_status("⌛ Processing...")
                            output = self.processor.process_text(transcription, context)
                            
                            # Review output
                            edited_output = self.review_output(output, context)
                            
                            # Update context
                            context = edited_output
                            self.processor.save_context(context)
                        
                        # Clean up temporary audio file
                        os.unlink(audio_path)

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
