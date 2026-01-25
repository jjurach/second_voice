import os
import time
from typing import Optional

try:
    import rich
    from rich.console import Console
    from rich.panel import Panel
    from rich.layout import Layout
    from rich.text import Text
except ImportError:
    # Fallback to a minimal implementation
    rich = None

from .base import BaseMode

class TUIMode(BaseMode):
    """
    Full-screen Terminal User Interface (TUI) mode.
    Uses Rich library for advanced terminal rendering.
    """

    def __init__(self, config, recorder, processor):
        """
        Initialize TUI mode.

        :param config: Configuration manager
        :param recorder: Audio recorder
        :param processor: AI processor
        """
        if rich is None:
            raise ImportError("Rich library not installed. Cannot use TUI mode.")
        
        super().__init__(config, recorder, processor)
        
        self.console = Console()
        self.layout = Layout()
        self._setup_layout()

    def _setup_layout(self):
        """
        Create a split-pane layout for TUI.
        """
        # Create layout with status, transcript, output, and context panes
        self.layout.split_column(
            Layout(name="status", size=3),  # Status bar
            Layout(name="transcript"),      # Transcription display
            Layout(name="output"),          # LLM output
            Layout(name="context", size=5)  # Context display
        )

    def start_recording(self) -> Optional[str]:
        """
        Record audio with TUI recording indicator.
        Waits for KeyboardInterrupt to stop recording.

        :return: Path to recorded audio file
        """
        import signal
        
        self.show_status("🎤 Recording... (press Ctrl+C to stop)")
        
        # Capture original signal handler
        original_sigint = signal.getsignal(signal.SIGINT)
        
        try:
            # Temporarily replace SIGINT handler
            def sigint_handler(signum, frame):
                raise KeyboardInterrupt("Recording stopped")
            signal.signal(signal.SIGINT, sigint_handler)
            
            self.recorder.start_recording()
            
            # Use Live display for VU meter
            while True:
                amp = self.recorder.get_amplitude()
                bar_len = int(amp * 20)
                vu_bar = "█" * bar_len + "░" * (20 - bar_len)
                self.show_status(f"🎤 Recording: [{vu_bar}] (Ctrl+C to stop)")
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            audio_path = self.recorder.stop_recording()
            return audio_path

            
        finally:
            # Restore original signal handler
            signal.signal(signal.SIGINT, original_sigint)


    def show_transcription(self, text: str):
        """
        Display transcription in transcript pane.

        :param text: Transcribed text
        """
        self.layout["transcript"].update(
            Panel(
                Text(text, style="bold"),
                title="Transcription"
            )
        )
        self.console.print(self.layout)

    def review_output(self, text: str, context: Optional[str] = None) -> str:
        """
        Review and potentially edit output.

        :param text: LLM output text
        :param context: Optional previous context
        :return: Edited or original output
        """
        edit_file = self._create_temp_file()
        
        with open(edit_file, 'w') as f:
            f.write(text)
        
        # Launch editor (reuse base class method)
        edited_text = self._launch_editor(edit_file)
        
        # Update output pane
        self.layout["output"].update(
            Panel(
                Text(edited_text, style="dim"),
                title="Processed Output"
            )
        )
        self.console.print(self.layout)
        
        return edited_text

    def show_status(self, message: str):
        """
        Update status pane.

        :param message: Status message to display
        """
        self.layout["status"].update(
            Panel(
                Text(message, style="green"),
                title="Status"
            )
        )
        self.console.print(self.layout)

    def run(self):
        """
        Main TUI workflow using Live display.
        """
        from rich.live import Live
        import time

        context = None
        self.show_status("Ready")
        
        # Check for input file from CLI args
        input_file = self.config.get('input_file')
        first_run = True

        with Live(self.layout, console=self.console, screen=True, refresh_per_second=4):
            while True:
                try:
                    # In a real TUI we'd have an event loop, 
                    # but for this version we'll stick to a sequential flow 
                    # with visual updates.
                    
                    audio_path = None
                    
                    # Handle input file for first run if provided
                    if first_run and input_file and os.path.exists(input_file):
                        self.show_status(f"Processing input file: {input_file}")
                        audio_path = input_file
                        # Don't set first_run to False yet, we do it after processing to avoid loop
                    else:
                        # Wait for user to be ready for next command (simulated)
                        # For now, it just auto-starts recording for demonstration 
                        # or we could wait for a keypress if we had a non-blocking input
                        
                        # Record audio
                        self.show_status("Press Ctrl+C to stop recording...")
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
                            # Note: review_output might break the Live display if it launches an editor
                            # We should probably stop Live before launching editor
                            self.show_status("Opening editor for review...")
                            edited_output = self.review_output(output, context)
                            
                            # Update context
                            context = edited_output
                            self.processor.save_context(context)
                        
                        # Clean up temporary audio file (only if it's not the input file)
                        if audio_path != input_file and os.path.exists(audio_path):
                            # We still check keep_files in the main cleanup, but for per-loop temp files:
                            if not self.config.get('keep_files'):
                                os.unlink(audio_path)
                        
                        # If we processed an input file, we might want to exit or wait
                        if first_run and input_file:
                            first_run = False
                            # For one-shot file processing, we might want to just exit or pause
                            self.show_status("Input file processed. Waiting 5s then exiting loop (or switching to mic)...")
                            time.sleep(5)
                            # Let's switch to mic for next rounds unless user interrupts
                            # or just continue loop
                        else:
                            self.show_status("Done. Waiting 2s...")
                            time.sleep(2)
                            self.show_status("Ready for next round")

                except KeyboardInterrupt:
                    break
                except Exception as e:
                    self.show_status(f"Error: {e}")
                    time.sleep(3)


        # Cleanup resources
        self.cleanup()
