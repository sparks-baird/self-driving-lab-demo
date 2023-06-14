while True:
    # Open Thonny
    myApp = App("C:/Users/sterg/AppData/Local/Programs/Thonny/thonny.exe")
    myApp.open()
    myApp.focus()

    # Install MicroPython
    install_micropython_str = "Install MicroPython..."
    local_interpreter_str = "Local Python 3"
    micropython_interpreter_str = "MicroPython (Raspberry Pi Pico)"

    if exists(local_interpreter_str):
        click(local_interpreter_str)
    else:
        click(micropython_interpreter_str)
        click(local_interpreter_str)
        click(local_interpreter_str)

    while True:
        if exists(install_micropython_str):
            click(install_micropython_str)
            break
        else:
            # reload the interpeter window to see if a fresh device has been plugged in
            type(Key.ESC)
            click("1678427836698.png")
            if exists(local_interpreter_str):
                click(local_interpreter_str)
            else:
                click(micropython_interpreter_str)
                # click(local_interpreter_str)
            sleep(2.0)

    sleep(5.0)
    click("1678399573235.png")
    click("Pico W / Pico WH")
    click("1678399873957.png")
    wait(Pattern("1678414306280.png").similar(0.85), 30)
    # wait("Done!", 60)
    sleep(2.0)
    click(Pattern("1678400018710.png").similar(0.85))

    # Upload sdl_demo.zip files
    if exists(local_interpreter_str):
        click(local_interpreter_str)
    else:
        click(micropython_interpreter_str)
    click(Pattern("1678415086018.png").targetOffset(0, 20))
    click("1678400910559.png")
    keyDown(Key.CTRL)
    click("1678400953811.png")
    click("1678400961127.png")
    click("1678400969208.png")
    keyUp()
    rightClick("1678401002281.png")
    click("Upload to /")
    sleep(1.0)
    if exists("1678417403293.png"):
        type(Key.ENTER)

    sleep(1.0)
    waitVanish("1678418294521.png", 60)

    # Run main.py
    doubleClick("1678409089151.png")
    sleep(2.0)
    click(Pattern("1678414445048.png").similar(0.90))
    # wait("1678418458931.png", 60)
    wait("Waiting for experiment requests", 30)

    # Retrieve the Pico ID
    mqtt_prefix_base = "PICO_ID: "
    line = findLine(mqtt_prefix_base)
    prefix_str = line.text()
    print(prefix_str)
    pico_id = prefix_str.split(mqtt_prefix_base)[1]

    # Switch to Chrome screen (assumes that ALT+TAB takes you there)
    type(Key.TAB, Key.ALT)

    # replace the Pico ID
    click(Pattern("1679637694679.png").similar(0.74).targetOffset(0, 0))
    type("a", Key.CTRL)
    type(pico_id)

    # run Jupyter cell
    type(Key.ENTER, Key.CTRL)
    wait("1678405217742.png", 30)
    myApp.focus()


# %% Code Graveyard

# autoplay = "autoplay.png"
# local_interpreter = "local_interpreter.png"
# install_micropython = "install_micropython.png"

# autoplay_pattern = Pattern(autoplay).similar(0.5)
# local_interpreter_pattern = Pattern(local_interpreter).similar(0.75)
# install_micropython_pattern = Pattern(install_micropython).similar(0.75)

# wait(autoplay_pattern, 10)
# click(autoplay_pattern)
# sleep(0.5)
# type(Key.ESC)

# num_clicks = click(local_interpreter_pattern)
# print(num_clicks)

#    if exists(install_micropython_pattern):
#        click(install_micropython_pattern)

# click(local_interpreter_pattern)

# type("c", Key.CTRL)

# sleep(1.0)

# "1678402391409.png"
