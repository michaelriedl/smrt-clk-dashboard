# smrt-clk-dashboard
![Testing](https://github.com/michaelriedl/smrt-clk-dashboard/actions/workflows/pytest.yml/badge.svg)
![Linting](https://github.com/michaelriedl/smrt-clk-dashboard/actions/workflows/ruff.yml/badge.svg)
![Type Checking](https://github.com/michaelriedl/smrt-clk-dashboard/actions/workflows/ty.yml/badge.svg)

The dashboard implementation for the SMRT CLK hardware.

# Running the Dashboard on a Raspberry Pi SMRT CLK
Here are the instructions to run the dashboard on a Raspberry Pi SMRT CLK. This guide assumes you have basic knowledge of using a Raspberry Pi and are comfortable with command-line operations.

## Prerequisites
There are a few prerequisites to run the dashboard on a Raspberry Pi SMRT CLK. Make sure you perform the following steps before proceeding:
1. **Set Up the Raspberry Pi**: Ensure that your Raspberry Pi is set up with the necessary operating system (we assume Raspberry Pi OS Trixie) and is connected to the internet.
2. **Update the System**: It's always a good idea to update your system before installing new software.

   ```bash
   sudo apt update && sudo apt upgrade -y
   ```
3. **Upload and Compile the .dts Files**: Ensure that the necessary Device Tree Source (.dts) files are uploaded and compiled. This step is required for the screen and touch functionality to work correctly.
4. **Update the ``/boot/firmware/config.txt``**: Make sure to update the ``/boot/firmware/config.txt`` file with the necessary configurations for the SMRT CLK hardware.
    
    You must remove the other existing settings for VC4.
    ```
    Configuring DPI (Display Parallel Interface) screens on Raspberry Pi OS Trixie (based on Debian 13) generally requires using the `vc4-kms-dpi-generic` overlay in `/boot/firmware/config.txt`. Trixie uses the `{Link: Wayland display server https://forums.raspberrypi.com/viewtopic.php?t=392500}` and a new [Control Center](https://www.neowin.net/news/raspberry-pi-os-trixie-unveils-new-control-center-and-future-proof-design/), making manual DPI configuration via `kanshi` or `config.txt` for specific screen timings necessary if auto-detection fails.
    ```
5. **Reboot the Raspberry Pi**: After making the necessary changes, reboot your Raspberry Pi to apply the configurations.

   ```bash
   sudo reboot
   ```
   
   After rebooting, ensure that the screen and touch functionality are working correctly before proceeding to run the dashboard.

## Dashboard Setup Instructions

To run the dashboard on a Raspberry Pi SMRT CLK, follow these steps:

1. **Clone the Repository**: Clone this repository to your Raspberry Pi.

   ```bash
   git clone https://github.com/michaelriedl/smrt-clk-dashboard.git
   cd smrt-clk-dashboard
   ```

# Development Setup

This project uses [uv](https://docs.astral.sh/uv/) for dependency management:

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh  # Unix/macOS
# or
irm https://astral.sh/uv/install.ps1 | iex  # Windows

# Install dependencies
uv sync --all-extras

# Run tests
uv run pytest

# Run linter
uv run ruff check .

# Run formatter
uv run ruff format .

# Run type checker
uv run ty check .
```
