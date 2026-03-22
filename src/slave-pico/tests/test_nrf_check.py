from machine import Pin, SPI
csn = Pin(1, Pin.OUT, value=1)
spi = SPI(0, baudrate=4000000, sck=Pin(2), mosi=Pin(3), miso=Pin(16))
csn.value(0)
spi.write(bytes([0x07]))
s = spi.read(1)[0]
csn.value(1)
print("nRF status: 0x{:02X}".format(s))
print("PASS" if s not in (0x00, 0xFF) else "FAIL - check wiring")
