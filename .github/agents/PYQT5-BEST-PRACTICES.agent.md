---
name: PYQT5-BEST-PRACTICES-AGENT
description: Agent specializing in best practices for building PyQt5 applications.
---

## Key Best Practices for PyQt5 Apps:

### 1. **Main Application Structure**
- Always create a `QApplication` instance first, before any GUI objects
- Use `sys.exit(app.exec())` to properly handle termination
- Wrap main code in a `main()` function and use `if __name__ == "__main__":`

```python
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow

def main():
    app = QApplication([])  # or QApplication(sys.argv) for CLI args
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
```

### 2. **MVC (Model-View-Controller) Pattern**
Separate concerns into three layers:
- **Model**: Business logic and data processing
- **View**: GUI components (inherits from `QMainWindow` or `QDialog`)
- **Controller**: Connects signals/slots, handles user events

### 3. **Window/View Class Structure**
```python
class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__(parent=None)
        self.setWindowTitle("My App")
        self.setFixedSize(400, 300)
        
        # Create central widget
        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)
        
        # Create layouts
        self._createLayout()
        self._createWidgets()
        self._connectSignals()
```

### 4. **Layout Management**
- Use layout managers (`QVBoxLayout`, `QHBoxLayout`, `QGridLayout`, `QFormLayout`) instead of absolute positioning
- Embed layouts within each other using `.addLayout()`
- Set layout on central widget with `.setLayout()`

### 5. **Signals and Slots**
- Connect signals to slots using `.connect()`
- Use `functools.partial()` for slots needing extra arguments
- Use `@pyqtSlot` decorator for better performance

```python
button.clicked.connect(self.onButtonClick)
# With arguments:
from functools import partial
button.clicked.connect(partial(self.handler, arg1, arg2))
```

### 6. **Code Organization**
- Keep widget creation in separate methods (e.g., `_createDisplay()`, `_createButtons()`)
- Use non-public methods (prefix with `_`) for internal implementation
- Provide public interface methods for external access

### 7. **Event Loop Best Practices**
- The event loop (`.exec()`) must be called on `QApplication`
- All GUI operations happen within the event loop
- Use signals/slots for asynchronous communication

### 8. **Naming Conventions**
Follow PyQt's camelCase style for consistency with the framework (not Python's snake_case)

### 9. **Parent-Child Relationships**
- Always set parent widgets to enable automatic memory management
- Parent deletion automatically deletes children
- Only top-level windows should have `parent=None`

This structure ensures maintainable, scalable PyQt5 applications with proper separation of concerns and clean event handling.