def read_ds_sensor():
  roms = ds_sensor.scan()
  print('Found DS devices: ', roms)
  print('Temperatures: ')
  ds_sensor.convert_temp()
  for rom in roms:
    temp = ds_sensor.read_temp(rom)
    if isinstance(temp, float):
      msg = round(temp, 2)
      print(temp, end=' ')
      print('Valid temperature')
      return msg
  return b'0.0'
 
def html_page():
  temp = read_ds_sensor()
  html = """
    <!DOCTYPE HTML>
    <html>

    <head>
        <meta http-equiv="refresh" content="30"/>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.7.2/css/all.css" integrity="sha384-fnmOCqbTlWIlj8LyTjo7mOUStjsKC4pOpQbqyi7RrhN7udi9RwhKkMHpvLbHG9Sr" crossorigin="anonymous">
        <style>
            html { font-family: Arial; display: inline-block; margin: 0px auto; text-align: center; }
                h2 { font-size: 3.0rem; } p { font-size: 3.0rem; } .units { font-size: 1.2rem; } 
                .ds-labels{ font-size: 1.5rem; vertical-align:middle; padding-bottom: 15px; }
        </style>
    </head>

    <body>
        <h2>ESP32 DS18B20 WebServer</h2>
        <p><i class="fas fa-thermometer-half" style="color:#059e8a;"></i>
            <span class="ds-labels">Temperature</span>
            <span id="temperature">""" + str(temp) + """</span>
            <sup class="units">&deg;C</sup>
        </p>
        <p>
		      <button onClick="location.reload()">Refresh</button>
	      </p>
    </body>

    </html>
  """
  return html

def json_page():
  temp = read_ds_sensor()
  json = '{"temperature": %.2f}' % temp
  return json
 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)
 
while True:
  try:
    if gc.mem_free() < 102000:
      gc.collect()
    conn, addr = s.accept()
    conn.settimeout(3.0)
    print('Got a connection from %s' % str(addr))
    request = conn.recv(1024)
    conn.settimeout(None)
    request = ''.join(map(chr, request))
    print('Content = %s' % request)
    if (request.find('Accept: application/json') == -1):
      response = html_page()
      conn.send('HTTP/1.1 200 OK\n')
      conn.send('Content-Type: text/html\n')
      conn.send('Connection: close\n\n')
      conn.sendall(response)
      conn.close()
    else:
      response = json_page()
      conn.send('HTTP/1.1 200 OK\n')
      conn.send('Content-Type: application/json\n')
      conn.send('Connection: close\n\n')
      conn.sendall(response)
      conn.close()
  except OSError as e:
    conn.close()
    print('Connection closed')
