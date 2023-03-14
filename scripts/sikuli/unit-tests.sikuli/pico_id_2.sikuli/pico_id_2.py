# Retrieve the Pico ID
wait("Waiting for experiment requests", 5)
mqtt_prefix_base = "PICO_ID:"
line = findLine(mqtt_prefix_base)
prefix_str = line.text()
print(prefix_str)
pico_id = prefix_str.split(mqtt_prefix_base)[1].split(" =====")[0]
print(pico_id)
