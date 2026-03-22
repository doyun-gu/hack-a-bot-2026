"""
GridBox — SSD1306 OLED Driver
I2C driver for 128x64 SSD1306 OLED display using framebuf.
"""

from machine import I2C
import framebuf
import time

# ============ SSD1306 COMMANDS ============
SET_CONTRAST = 0x81
ENTIRE_DISPLAY_ON = 0xA4
SET_NORM_INV = 0xA6
SET_DISPLAY_OFF = 0xAE
SET_DISPLAY_ON = 0xAF
SET_MEM_ADDR_MODE = 0x20
SET_COL_ADDR = 0x21
SET_PAGE_ADDR = 0x22
SET_DISPLAY_START_LINE = 0x40
SET_SEG_REMAP = 0xA0
SET_MUX_RATIO = 0xA8
SET_COM_OUT_DIR = 0xC0
SET_DISPLAY_OFFSET = 0xD3
SET_COM_PIN_CFG = 0xDA
SET_DISPLAY_CLK_DIV = 0xD5
SET_PRECHARGE = 0xD9
SET_VCOM_DESEL = 0xDB
SET_CHARGE_PUMP = 0x8D


class SSD1306:
    """SSD1306 128x64 OLED display driver using framebuf."""

    def __init__(self, i2c, width=128, height=64, addr=0x3C):
        self.i2c = i2c
        self.addr = addr
        self.width = width
        self.height = height
        self.pages = height // 8

        # Framebuffer
        self.buffer = bytearray(self.pages * width)
        self.fb = framebuf.FrameBuffer(self.buffer, width, height, framebuf.MONO_VLSB)

        # Init sequence
        self._init_display()

    def _cmd(self, cmd):
        """Send a command byte."""
        self.i2c.writeto(self.addr, bytes([0x00, cmd]))

    def _init_display(self):
        """Send init sequence to SSD1306."""
        cmds = [
            SET_DISPLAY_OFF,
            SET_DISPLAY_CLK_DIV, 0x80,
            SET_MUX_RATIO, self.height - 1,
            SET_DISPLAY_OFFSET, 0x00,
            SET_DISPLAY_START_LINE | 0x00,
            SET_CHARGE_PUMP, 0x14,          # enable charge pump
            SET_MEM_ADDR_MODE, 0x00,        # horizontal addressing
            SET_SEG_REMAP | 0x01,           # column 127 = SEG0
            SET_COM_OUT_DIR | 0x08,         # scan from COM[N-1] to COM0
            SET_COM_PIN_CFG, 0x12 if self.height == 64 else 0x02,
            SET_CONTRAST, 0xCF,
            SET_PRECHARGE, 0xF1,
            SET_VCOM_DESEL, 0x40,
            ENTIRE_DISPLAY_ON,              # output follows RAM
            SET_NORM_INV | 0x00,            # normal display
            SET_DISPLAY_ON,
        ]
        for c in cmds:
            self._cmd(c)
        self.clear()

    def show(self):
        """Push framebuffer to display."""
        self._cmd(SET_COL_ADDR)
        self._cmd(0)
        self._cmd(self.width - 1)
        self._cmd(SET_PAGE_ADDR)
        self._cmd(0)
        self._cmd(self.pages - 1)

        # Send data in chunks (I2C max transfer)
        buf = self.buffer
        chunk_size = 128  # safe chunk size
        for i in range(0, len(buf), chunk_size):
            chunk = buf[i:i + chunk_size]
            self.i2c.writeto(self.addr, b'\x40' + chunk)

    def fill(self, color):
        """Fill entire screen with color (0=black, 1=white)."""
        self.fb.fill(color)

    def clear(self):
        """Clear screen (fill black) and update display."""
        self.fill(0)
        self.show()

    def text(self, string, x, y, color=1):
        """Draw text at position. 8x8 pixel font."""
        self.fb.text(string, x, y, color)

    def pixel(self, x, y, color=1):
        """Set a single pixel."""
        self.fb.pixel(x, y, color)

    def line(self, x1, y1, x2, y2, color=1):
        """Draw a line."""
        self.fb.line(x1, y1, x2, y2, color)

    def rect(self, x, y, w, h, color=1):
        """Draw rectangle outline."""
        self.fb.rect(x, y, w, h, color)

    def fill_rect(self, x, y, w, h, color=1):
        """Draw filled rectangle."""
        self.fb.fill_rect(x, y, w, h, color)

    def hline(self, x, y, w, color=1):
        """Draw horizontal line."""
        self.fb.hline(x, y, w, color)

    def vline(self, x, y, h, color=1):
        """Draw vertical line."""
        self.fb.vline(x, y, h, color)

    def contrast(self, value):
        """Set display contrast/brightness (0-255)."""
        self._cmd(SET_CONTRAST)
        self._cmd(value)

    def invert(self, on):
        """Invert display (True=inverted, False=normal)."""
        self._cmd(SET_NORM_INV | (1 if on else 0))

    def poweroff(self):
        """Turn off display."""
        self._cmd(SET_DISPLAY_OFF)

    def poweron(self):
        """Turn on display."""
        self._cmd(SET_DISPLAY_ON)

    def scroll_h(self, direction='left'):
        """Start horizontal scroll (left or right)."""
        cmd = 0x27 if direction == 'left' else 0x26
        self._cmd(cmd)
        self._cmd(0x00)  # dummy
        self._cmd(0x00)  # start page
        self._cmd(0x07)  # interval (fastest)
        self._cmd(0x07)  # end page
        self._cmd(0x00)  # dummy
        self._cmd(0xFF)  # dummy
        self._cmd(0x2F)  # activate scroll

    def scroll_stop(self):
        """Stop scrolling."""
        self._cmd(0x2E)


if __name__ == "__main__":
    from machine import Pin
    import config

    print("=" * 40)
    print("  SSD1306 OLED Driver Test")
    print("=" * 40)

    i2c = I2C(config.I2C_ID, sda=Pin(config.I2C_SDA),
              scl=Pin(config.I2C_SCL), freq=config.I2C_FREQ)

    try:
        oled = SSD1306(i2c, width=config.OLED_WIDTH,
                       height=config.OLED_HEIGHT, addr=config.SSD1306_ADDR)
        print(f"OLED initialised: {config.OLED_WIDTH}x{config.OLED_HEIGHT}")

        # Draw border
        oled.rect(0, 0, 128, 64, 1)

        # Title
        oled.text("GridBox SCADA", 12, 4, 1)
        oled.hline(4, 14, 120, 1)

        # Mock status
        oled.text("Motor 1: OK", 8, 20, 1)
        oled.text("Motor 2: OK", 8, 32, 1)
        oled.text("Bus: 4.9V", 8, 44, 1)

        oled.show()
        print("Display showing test screen")

    except OSError as e:
        print(f"I2C error: {e}")
        print("Check OLED wiring: SDA=GP4, SCL=GP5, VCC=3.3V, GND=GND")
