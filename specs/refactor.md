## PyQt5 Smart Clock Dashboard - Best Practices Review & Refactoring Plan

### Current Issues Identified

**Critical Issues:**
1. **Monolithic Structure**: All GUI code is in a single 396-line file with global variables
2. **No MVC Pattern**: Business logic, GUI, and data management are all mixed together
3. **Missing Main Window Class**: No QMainWindow or proper window class structure
4. **Global State**: Heavy use of global variables (`lastmin`, `lastday`, `clock_hands`, etc.)
5. **Hard-coded Values**: Latitude, longitude, API keys, paths all hard-coded
6. **No Layout Managers**: All widgets use absolute positioning (.setGeometry)
7. **Poor Separation of Concerns**: Weather API calls mixed with GUI code
8. **No Error Handling**: Network requests lack proper error handling
9. **Unused Code**: Files in smrtclk and src directories aren't integrated

**Code Quality Issues:**
10. **Inconsistent Naming**: Mix of snake_case and camelCase
11. **Missing Type Hints**: Functions lack return type annotations
12. **Repeated Style Strings**: StyleSheet strings duplicated throughout
13. **Magic Numbers**: No constants for sizing, colors, timing intervals

---

## Recommended Architecture

```
smrt-clk-dashboard/
├── run.py                          # Entry point (minimal)
├── config/
│   ├── __init__.py
│   ├── settings.py                 # Configuration management
│   └── constants.py                # Application constants
├── smrtclk/
│   ├── __init__.py
│   ├── models/                     # Data models
│   │   ├── __init__.py
│   │   ├── clock_model.py         # Clock state and logic
│   │   └── weather_model.py       # Weather data handling
│   ├── views/                      # GUI components
│   │   ├── __init__.py
│   │   ├── main_window.py         # Main QMainWindow
│   │   ├── clock_widget.py        # Clock display widget
│   │   ├── weather_widget.py      # Weather display widget
│   │   └── styles.py              # Centralized styling
│   ├── controllers/                # Application logic
│   │   ├── __init__.py
│   │   ├── clock_controller.py    # Clock update logic
│   │   └── weather_controller.py  # Weather API integration
│   └── weather/                    # Weather API (already exists)
│       ├── __init__.py
│       ├── weather_api.py
│       └── weather_api_nws.py
```

---

## Detailed Task Breakdown

### **Phase 1: Configuration & Constants (High Priority)**
**Estimated Time: 2-3 hours**

- [ ] **Task 1.1**: Create configuration system
  - Create `config/settings.py` with configuration class
  - Load API keys from environment variables or config file
  - Add latitude/longitude to configuration
  - Support multiple display resolutions

- [ ] **Task 1.2**: Extract constants
  - Create `config/constants.py` for colors, paths, timings
  - Define `WEATHER_UPDATE_INTERVAL = 5 * 60 * 1000` (5 minutes)
  - Define `CLOCK_UPDATE_INTERVAL = 1000` (1 second)
  - Extract image paths, colors, font sizes

- [ ] **Task 1.3**: Environment-based configuration
  - Add `.env.example` file
  - Update `keys.py` to use `python-dotenv`
  - Document required environment variables in README

---

### **Phase 2: Model Layer (High Priority)**
**Estimated Time: 3-4 hours**

- [ ] **Task 2.1**: Create ClockModel
  - Extract time-tracking logic from global variables
  - Add properties: `current_time`, `last_minute`, `last_day`
  - Add method: `calculate_hand_angle(hand_type: str) -> float`
  - Add signals for time updates using `pyqtSignal`

- [ ] **Task 2.2**: Create WeatherModel
  - Define data class for weather information
  - Properties: temperature (current/min/max), precipitation, sun times
  - Parse weather API responses into structured data
  - Add validation for weather data

- [ ] **Task 2.3**: Integrate existing WeatherAPI
  - Wire up `WeatherAPINWS` from weather
  - Replace OpenWeatherMap with NWS API (no API key needed)
  - Add adapter pattern for multiple weather services

---

### **Phase 3: View Layer Refactoring (Critical)**
**Estimated Time: 6-8 hours**

- [ ] **Task 3.1**: Create MainWindow class
  ```python
  class ClockMainWindow(QMainWindow):
      def __init__(self, config: Config):
          super().__init__(parent=None)
          self.config = config
          self._setupWindow()
          self._createCentralWidget()
          self._createWidgets()
  ```

- [ ] **Task 3.2**: Create ClockWidget
  - Encapsulate clock face, hands, and date display
  - Use custom QWidget with proper parent-child relationships
  - Extract `move_hand()` logic into widget methods
  - Use layout managers instead of absolute positioning (QVBoxLayout/QHBoxLayout)

- [ ] **Task 3.3**: Create WeatherWidget
  - Encapsulate temperature/precipitation displays
  - Create reusable slider components
  - Use QFormLayout or QGridLayout for weather elements
  - Separate sunrise/sunset display

- [ ] **Task 3.4**: Centralize styling
  - Create `views/styles.py` with style constants
  - Use QSS (Qt Style Sheets) in separate file or methods
  - Remove inline style strings
  - Support theme/color customization

- [ ] **Task 3.5**: Fix layout system
  - Replace all `.setGeometry()` with layout managers
  - Create responsive layouts that adapt to window size
  - Use `QVBoxLayout`, `QHBoxLayout`, `QGridLayout` appropriately
  - Remove hard-coded pixel positions

---

### **Phase 4: Controller Layer (High Priority)**
**Estimated Time: 4-5 hours**

- [ ] **Task 4.1**: Create ClockController
  - Manage QTimer for clock updates
  - Connect to ClockModel for time data
  - Update ClockWidget through signals/slots
  - Remove global `tick()` function

- [ ] **Task 4.2**: Create WeatherController
  - Manage QNetworkAccessManager properly
  - Handle weather API requests asynchronously
  - Update WeatherModel with fetched data
  - Add retry logic and error handling
  - Remove global `get_weather()` and `wxupdate()`

- [ ] **Task 4.3**: Implement proper signal/slot architecture
  - Use `@pyqtSlot` decorators for performance
  - Connect model changes to view updates
  - Use `functools.partial` for parameterized slots
  - Document signal/slot connections

---

### **Phase 5: Entry Point & Lifecycle (Medium Priority)**
**Estimated Time: 2 hours**

- [ ] **Task 5.1**: Refactor run.py
  ```python
  def main():
      app = QApplication(sys.argv)
      config = Config.from_env()
      window = ClockMainWindow(config)
      window.show()
      sys.exit(app.exec())
  
  if __name__ == "__main__":
      main()
  ```

- [ ] **Task 5.2**: Add proper cleanup
  - Stop timers on application exit
  - Close network connections gracefully
  - Add `closeEvent()` handler in MainWindow

- [ ] **Task 5.3**: Add command-line arguments
  - Support `--config` flag for config file path
  - Add `--debug` flag for development mode
  - Use `argparse` for CLI handling

---

### **Phase 6: Error Handling & Robustness (Medium Priority)**
**Estimated Time: 3-4 hours**

- [ ] **Task 6.1**: Add network error handling
  - Graceful degradation when weather API fails
  - Display error states in UI
  - Log errors appropriately
  - Implement exponential backoff for retries

- [ ] **Task 6.2**: Add resource validation
  - Check for missing image files on startup
  - Provide fallback behavior for missing resources
  - Add logging system (use `logging` module)

- [ ] **Task 6.3**: Add input validation
  - Validate latitude/longitude ranges
  - Validate configuration values
  - Type checking with proper type hints

---

### **Phase 7: Testing & Documentation (Low-Medium Priority)**
**Estimated Time: 4-5 hours**

- [ ] **Task 7.1**: Add unit tests
  - Test models independently (ClockModel, WeatherModel)
  - Test weather API parsing
  - Test angle calculations
  - Use existing `pytest` setup

- [ ] **Task 7.2**: Add integration tests
  - Test controller-model interactions
  - Mock network requests for weather tests
  - Test signal/slot connections

- [ ] **Task 7.3**: Update documentation
  - Document MVC architecture in README
  - Add code comments and docstrings
  - Create developer setup guide
  - Document configuration options

---

### **Phase 8: Code Quality & Polish (Low Priority)**
**Estimated Time: 2-3 hours**

- [ ] **Task 8.1**: Apply consistent naming conventions
  - Use camelCase for PyQt5 methods/properties
  - Use snake_case for internal Python logic
  - Follow PEP 8 guidelines

- [ ] **Task 8.2**: Add type hints throughout
  - All function signatures should have type hints
  - Use `typing` module for complex types
  - Run `mypy` for type checking

- [ ] **Task 8.3**: Code formatting
  - Run `black` formatter (already in dependencies)
  - Configure line length and formatting rules
  - Add pre-commit hooks

---

## Priority Implementation Order

**Immediate (Week 1):**
1. Phase 1: Configuration & Constants
2. Phase 2: Model Layer
3. Phase 5: Entry Point (Task 5.1)

**High Priority (Week 2-3):**
4. Phase 3: View Layer (Tasks 3.1-3.3)
5. Phase 4: Controller Layer

**Medium Priority (Week 4):**
6. Phase 3: View Layer (Tasks 3.4-3.5)
7. Phase 6: Error Handling
8. Phase 5: Cleanup & CLI

**Low Priority (Ongoing):**
9. Phase 7: Testing & Documentation
10. Phase 8: Code Quality

---

## Expected Benefits

✅ **Maintainability**: Clear separation of concerns, easy to locate and modify code  
✅ **Testability**: Each component can be tested independently  
✅ **Scalability**: Easy to add new features (additional weather services, themes, widgets)  
✅ **Reusability**: Components can be reused in other projects  
✅ **Performance**: Proper use of signals/slots, efficient updates  
✅ **Reliability**: Better error handling, graceful degradation  
✅ **Developer Experience**: Standard PyQt5 patterns, easier onboarding

---

## Estimated Total Time

- **Minimum (core refactoring)**: 18-22 hours
- **Complete implementation**: 28-35 hours

Would you like me to begin implementing any specific phase, or would you prefer to start with a particular task?