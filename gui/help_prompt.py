from PySide6.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox, QLabel
import gui.built_in as built_in


class HelpPrompt(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.setWindowTitle("About")
        self.setWindowIcon(built_in.icon(self, 'MessageBoxQuestion'))

        """Main text"""
        text = 'You can create a new data file (CTRL+N) or open a preexisting one to append or plot (CTRL+O).\n' \
               'The "Stop" button will close file you are working with.\n\n' \
               'The Tabs allow you to navigate between the data stream, the plot,' \
               'and controls over your instruments.\n' \
               'Press and hold ALT to reveal shortcuts to the tab. Continue to hold ALT and press a key to navigate' \
               'to that tab.\n\n' \
               'Tap ALT to reveal shortcuts in the menu bar. Followup with the key to open that menu.\n\n'
        main_label = QLabel(text)

        """Place button at end"""
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.reject)

        main_layout = QVBoxLayout()
        main_layout.addWidget(main_label)
        main_layout.addWidget(button_box)

        self.setLayout(main_layout)
