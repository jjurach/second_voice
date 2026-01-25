from abc import ABC, abstractmethod
import os
import tempfile

class BaseMode(ABC):
    """
    Abstract base class defining the interface for different interaction modes.
    Ensures consistent behavior across GUI, TUI, and Menu modes.
    """

    def __init__(self, config, recorder, processor):
        """
        Initialize the base mode with shared engine components.

        :param config: Configuration manager
        :param recorder: Audio recorder instance
        :param processor: AI processing pipeline
        """
        self.config = config
        self.recorder = recorder
        self.processor = processor

        # Create a temporary directory for this mode
        self.temp_dir = os.path.join(config.get('temp_dir', './tmp'), 'mode_tmp')
        os.makedirs(self.temp_dir, exist_ok=True)

    def _create_temp_file(self, prefix='second_voice_', suffix='.md'):
        """
        Create a safe temporary file in the mode's temp directory.

        :param prefix: Prefix for the temporary file
        :param suffix: Suffix for the temporary file
        :return: Path to the created temporary file
        """
        temp_file_path = os.path.join(
            self.temp_dir,
            f'{prefix}{os.getpid()}_{int(os.times()[4])}{suffix}'
        )
        return temp_file_path

    def _launch_editor(self, file_path, editor=None):
        """
        Launch an editor for file review/editing.

        :param file_path: Path to the file to edit
        :param editor: Optional editor path. Uses $EDITOR or system defaults.
        :return: Edited file contents
        """
        # Determine editor
        if not editor:
            editor = os.environ.get('EDITOR', 'nano')

        # Run editor
        os.system(f'{editor} {file_path}')

        # Read edited contents
        with open(file_path, 'r') as f:
            return f.read()

    @abstractmethod
    def start_recording(self) -> str:
        """
        Start audio recording.

        :return: Path to recorded audio file
        """
        pass

    @abstractmethod
    def show_transcription(self, text: str):
        """
        Display the transcribed text.

        :param text: Transcribed text to display
        """
        pass

    @abstractmethod
    def review_output(self, text: str, context: str = None) -> str:
        """
        Allow user to review and potentially edit LLM output.

        :param text: Raw LLM output
        :param context: Optional previous context
        :return: Final output after potential user edits
        """
        pass

    @abstractmethod
    def show_status(self, message: str):
        """
        Display a status message.

        :param message: Status message to display
        """
        pass

    @abstractmethod
    def run(self):
        """
        Main event loop for this mode.
        Implements the core workflow: record → transcribe → process → review
        """
        pass

    def cleanup(self):
        """
        Cleanup temporary files and resources.
        """
        if self.config.get('keep_files'):
            print(f"Keeping mode temporary files in {self.temp_dir}")
            return

        # Remove temporary files
        for filename in os.listdir(self.temp_dir):
            file_path = os.path.join(self.temp_dir, filename)
            try:
                os.unlink(file_path)
            except Exception as e:
                print(f"Could not remove {file_path}: {e}")
