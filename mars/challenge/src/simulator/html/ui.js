
    const indicator_statuses = [ "indicator-off", "indicator-on", "indicator-error"];

    function disableControls() {

        document.getElementById("start-btn").disabled = true;
        document.getElementById("stop-btn").disabled = true;
        document.getElementById("upload-btn").disabled = true;
        document.getElementById("file-selector").disabled = true;
        document.getElementById("download-btn").disabled = true;

    }

    function enableControls() {

        document.getElementById("start-btn").disabled = false;
        document.getElementById("stop-btn").disabled = true;
        document.getElementById("upload-btn").disabled = true;
        document.getElementById("file-selector").disabled = false;
        document.getElementById("download-btn").disabled = false;

    }

    function resetSim() {

        velocity_chart.reset();
        altitude_chart.reset();

        document.getElementById("start-btn").disabled = true;
        document.getElementById("stop-btn").disabled = false;
        document.getElementById("upload-btn").disabled = true;
        document.getElementById("file-selector").disabled = true;
        document.getElementById("download-btn").disabled = true;

        socket.send(JSON.stringify({"cmd":"start"}));

    }

    function stopSim() {

        document.getElementById("start-btn").disabled = false;
        document.getElementById("stop-btn").disabled = true;
        document.getElementById("upload-btn").disabled = false;
        document.getElementById("file-selector").disabled = false;
        document.getElementById("download-btn").disabled = false;

        socket.send(JSON.stringify({"cmd":"stop"}));

    }

    function Download() {

        var file_addr = "http://" + url.split('/')[2] + "/bad.rom";
       
        document.getElementById('hidden_frame').src = file_addr;

    }

    function sendFile() {

        var file = document.getElementById("file-selector").files[0];

        var reader = new FileReader();

        var rawData = new ArrayBuffer();            


        reader.onload = function(e) {

            var rawData = e.target.result;

            var stringData = String.fromCharCode.apply(null, new Uint8Array(rawData));

            var message = {'cmd':'upload',
                            'data': stringData};

            socket.send(JSON.stringify(message));

            alert("the File has been transferred.")

        }

        reader.readAsArrayBuffer(file);

    }

    const instructions = `You are an engineer supporting the Mars Polar Lander.  The latest simulation data shows that the lander is going to crash on landing. Unfortunately, the lander launched 8 months ago and is close to the Red Planet already so there's not much time to reprogram the flight software. There is a small MIPS processor that controls the landing sequence that can be reprogrammed before its too late.\n\nUse the simulator to figure out the problem, binary patch the controller firmware and resimulate for a successful landing to get your flag.`;

    alert(instructions);

    const fileSelector = document.getElementById('file-selector');

    fileSelector.addEventListener('change', (event) => {
      const fileList = event.target.files;
      console.log(fileList);
      console.log(fileList.length);

      if (fileList.length > 0 ) {

        document.getElementById("upload-btn").disabled = false;

      }
      else {

        document.getElementById("upload-btn").disabled = true;

      }

    });

    var url = window.location.href;
    var websocket_addr = "ws://" + url.split('/')[2];

    let socket = new WebSocket(websocket_addr);
    
    socket.onopen = function(event) {

        console.log("websocket opened");

    }

    socket.onclose = function(event) {

        console.log("websocket closed");
        alert("Server closed connection");
        disableControls();

    }

    socket.onmessage = function(event) {
    
      var message = JSON.parse(event.data);

      switch(message['type']) {

        case 'data':

            position = parseFloat(message['altitude']);
            velocity = parseFloat(message['velocity']);
            fuel = parseInt(message['fuel%']);
            thrust = parseInt(message['thrust%']);
            state = parseInt(message['spacecraft_state'], 16);
            delta_time = parseFloat(message['sim_time_delta']);

            touchdown = (state >> 12) & 3;
            parachute = (state >> 10) & 3;
            legs_deployed = (state >> 8) & 3;
            backshell_ejected = (state >> 6) & 3;
            constant_velocity = (state >>4 ) & 3;
            engine_cutoff = (state >> 2) & 3;
            powered_descent = state & 3;

            document.getElementById("legs_deployed").className = indicator_statuses[legs_deployed];
            document.getElementById("backshell").className = indicator_statuses[backshell_ejected];
            document.getElementById("powered_descent").className = indicator_statuses[powered_descent];
            document.getElementById("constant_velocity").className = indicator_statuses[constant_velocity];
            document.getElementById("touchdown").className = indicator_statuses[touchdown];
            document.getElementById("engine_cutoff").className = indicator_statuses[engine_cutoff];

            velocity_chart.add_datapoint(delta_time, Math.abs(velocity));
            velocity_chart.draw_graph();

            altitude_chart.add_datapoint(delta_time, position);
            altitude_chart.draw_graph();

            fuel_bar.update_value(fuel);
            thrust_bar.update_value(thrust);

            altitude_bar.update_value(position.toFixed(1));
            velocity_bar.update_value(Math.abs(velocity.toFixed(1)));
            
            break;

        case 'status':

            break;

        case 'result':

            alert(message['message']);
            enableControls();

            break;            

      }

    };
    
    document.getElementById("start-btn").disabled = false;
    document.getElementById("stop-btn").disabled = true;
    document.getElementById("upload-btn").disabled = true;
    document.getElementById("file-selector").disabled = false;
    document.getElementById("download-btn").disabled = false;

    document.getElementById("parachute").className = "indicator-on";

    var fuel_canvas = document.getElementById("fuel");

    fuel_bar = new Bar(fuel_canvas, 100, "Fuel%");

    fuel_bar.update_value(0);

    var thrust_canvas = document.getElementById("thrust");

    thrust_bar = new Bar(thrust_canvas, 100, "Thrust%");

    thrust_bar.update_value(0);

    var velocitybar_canvas = document.getElementById("velocitybar");

    velocity_bar = new Bar(velocitybar_canvas, 500, "Velocity (m/s)");

    velocity_bar.update_value(0);

    var altitudebar_canvas = document.getElementById("altitudebar");

    altitude_bar = new Bar(altitudebar_canvas, 9300, "Altitude (m)");

    altitude_bar.update_value(0);
    
    // log = document.getElementById("log");
    vel_chart = document.getElementById("velocity");

    alt_chart = document.getElementById("altitude");

    velocity_chart = new Chart(vel_chart, 120, 500, "Time Delta", "Velocity (m/s)");
    altitude_chart = new Chart(alt_chart, 120, 9300, "Time Delta", "Altitude (m)");

    velocity_chart.draw_graph();
    altitude_chart.draw_graph();

