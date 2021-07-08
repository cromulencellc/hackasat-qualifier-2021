
const flag = process.env.FLAG;
const service_port = process.env.SERVICE_PORT
const service_host = process.env.SERVICE_HOST

if (!flag) {

  console.error("Flag variable is not defined and is required");
  process.exit(-1);

}

function killApp() {

  process.exit(-1);

}

timeoutTimer = setTimeout(killApp, 200000);

const port = 3000;

const fs = require('fs');
const ws = require('ws');
const express = require('express')
const spacecraft = require('./spacecraft')
const planet = require('./mars')

const mars = new planet();

// declare these as constants just for documenation reasons
const starting_altitude = 9000;
const starting_velocity = -500;
const thruster_power = 268;
const thruster_count = 12;

const max_thrust = thruster_power * thruster_count;

const lander = new spacecraft(starting_altitude, starting_velocity, max_thrust, mars);

// update the simulation every 100 ms
const updateInterval_ms = 100;

// after touching down, need to run a few more iterations
var terminalCount = 0;

// total iterations so we can limit how long it runs overall
var stepCount = 0;

// a periodic timer to run the simulation in realtime
var simTimer;


process.stdout.write("\nPoint your browser at http://" + service_host + ":" + service_port + "\n");

var app = express();

app.use(express.static('html'));

const ws_server = new ws.Server( { noServer: true });

ws_server.on('connection', function(socket) {

  // console.error("Connection received");
  // clearTimeout(timeoutTimer);

  try {
    // debug_log(LOG_PRIORITY_HIGH, "p_error = %d, i_error = %d, d_error = %d, PID_OUTPUT = %d", 
            // (int)position_error, (int)p_integral_error, (int)derivative_error, (int)(pid_output*100));
    fs.unlinkSync('/tmp/newrom');

  }
  catch {


  }

  socket.on('message', function(msg) {

    let message;
    let type;

    try {

      message = JSON.parse(msg);
      type = message['cmd'];

    }
    catch {

      // console.error("Badly formatted message");
      return;

    }

    if (type == 'start') {

      // console.error("Got a start command");

      lander.reset();
      last_update = Date.now();

      terminalCount = 0;
      stepCount = 0;

      simTimer = setInterval(updateSim, updateInterval_ms, socket);

    }
    else if (type == 'stop') {

      // console.error("Got a stop command");
      clearInterval(simTimer);

    }
    else if (type == 'upload') {

      // console.error("Got an upload");

      let data;
      try {

        data = message['data'];

      }
      catch {

        // console.error("Badly formatted message");
        return;

      }

      // TODO: validate the receive data to ensure its a valid ROM image as best we can
      fs.writeFileSync('/tmp/newrom', data, 'ascii');

    }
  });

  socket.on('close', function() {

    // console.error("connection closed");
    clearInterval(simTimer);
    process.exit(0);

  });

});

const server = app.listen(port);

server.on('upgrade', (request, socket, head) => {

  ws_server.handleUpgrade(request, socket, head, socket => {

    ws_server.emit('connection', socket, request);

  });
});

function updateSim(socket) {

  let message;

  // console.error("updateSim called");
  let now = Date.now();

  // since the timer interval is not guaranteed, see what the actual interval has been
  let interval = now - last_update;

  // updates in milliseconds
  lander.update(interval);

  last_update = now;

  stepCount += 1;

  if ( stepCount > 50000 ) {

    message = {'type':'status',
              'status': 'fail',
              'message': 'Simulation stopped after too many iterations'};

    socket.send(JSON.stringify(message));

  }

    // only sending updates to the UI every 10 intervals, i.e. once per second
  // if ( stepCount % 10 == 0 ) {
    stats = lander.get_current_stats();

    socket.send(stats);

  // }

  // once the sim get to the ground, run for 5 more iterations to give the controller 
  // a chance to do its thing after touchdown
  if (lander.current_altitude <= 0.0 ) {

    terminalCount += 1;
  }

  if (terminalCount > 10) {

      // console.error(`Simulation complete.`);

      if (lander.spacecraft_touchdown == 1 && lander.engine_cutoff_state == 1) {

        let status;

        // console.error("Success!!!!");

        message = {
          'type': 'result',
          'status': 'success',
          'message': `Here's your flag: ${flag}`
        };

      }
      else {

        message = {
          'type': 'result',
          'status': 'fail',
          'message': "No flag for you this time"
        };

      }

      let data = JSON.stringify(message);

      socket.send(data);

      clearInterval(simTimer);
  
  }

}

