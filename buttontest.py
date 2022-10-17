import RPi.GPIO as GPIO 

BTN1 = 21
BTN2 = 20
LED1 = 14
LED2 = 15
GPIO.setmode(GPIO.BCM)
GPIO.setup(BTN1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BTN2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LED1, GPIO.OUT)
GPIO.setup(LED2, GPIO.OUT)
def btn1(channel):
    print(channel,"btn1 pressed")
    
def btn2(channel):
    print(channel,"btn2 pressed")
def main():
    while True:
        #print(GPIO.input(BTN1))
        GPIO.output(LED2, GPIO.HIGH)
        GPIO.output(LED1, GPIO.HIGH)
        pass

if __name__ == "__main__":
    GPIO.add_event_detect(BTN1, GPIO.RISING, callback=btn1, bouncetime=2000)
    GPIO.add_event_detect(BTN2, GPIO.RISING, callback=btn2, bouncetime=2000)
    try:
        main()
    except:
        pass
    
    GPIO.cleanup()