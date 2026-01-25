import os
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

        :return: Path to recorded audio file
        """
        with self.console.status("[bold green]Recording..."):
            return self.recorder.start_recording()

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
        Main TUI workflow.
        """
        context = None

        while True:
            try:
                # Render initial layout
                self.console.print(self.layout)

                # Record audio
                audio_path = self.start_recording()
                if audio_path:
                    # Transcribe
                    self.show_status("Transcribing...")
                    transcription = self.processor.transcribe(audio_path)
                    
                    if transcription:
                        self.show_transcription(transcription)
                        
                        # Process with LLM
                        self.show_status("Processing...")
                        output = self.processor.process_text(transcription, context)
                        
                        # Review output
                        edited_output = self.review_output(output, context)
                        
                        # Update context
                        context = edited_output
                        self.processor.save_context(context)
                    
                    # Clean up temporary audio file
                    os.unlink(audio_path)

            except KeyboardInterrupt:
                break
            except Exception as e:
                self.show_status(f"Error: {e}")

        # Cleanup resources
        self.cleanup()
