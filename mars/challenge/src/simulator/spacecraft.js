const { lstat, write, symlinkSync } = require('fs');
const { spawn } = require('child_process');
const { timeStamp } = require('console');
const lander_leg = require('./lander_leg');
const { exit } = require('process');
const fs = require('fs');

class Spacecraft {

    #last_altitude = 0.0;

    current_velocity = 0.0;
    #last_velocity = 0.0;

    current_acceleration = 0.0;

    #drag_constant1 = 41;
    #drag_constant2 = 10;
    #current_drag_constant = 0.0;

    fuel_weight = 0.0;

    #planet;

    #max_thrust;

    parachute_deployed = 1;
    lander_legs_deployed = 0;
    backshell_ejected = 0;
    constant_velocity_phase = 0;
    #engine_cutoff_enable = 0;
    engine_cutoff = 0;
    engine_cutoff_state = 0;
    powered_descent = 0;
    #radar_lock = 0;
    #radar_altitude;
    #pid_controller;
    spacecraft_touchdown;
    leg1;
    leg2;
    leg3;
    #deploy_legs_commanded;
    landing_velocity;
    landing_time;
    #sim_start_time;

    pid_input_buffer = [];
    pid_input_buffer_ptr = 0;

    constructor(altitude, velocity, max_thrust, atmosphere_model) {

        this.leg1 = new lander_leg(8.0);
        this.leg2 = new lander_leg(10.0);
        this.leg3 = new lander_leg(11.0);

        this.starting_altitude = altitude;  // meters
        this.current_altitude = altitude;
        this.starting_velocity = velocity;  // meters/sec
        this.starting_mass = 420.9; // kg
        this.starting_thrust = 0.0; // 0.0 through 1.0
        this.planet = atmosphere_model;
        this.starting_fuel_weight = 65000.0; // grams
        this.max_thrust = max_thrust;
        this.max_fuel_consumption = 131.0 * 12; // grams/sec
        this.thruster_setting = 0.0;
        this.waiting_for_touchdown = true;
        this.spacecraft_final_state = 0;

        this.spawn_start;
    }

    reset() {

        this.#sim_start_time = Date.now();

        this.current_altitude = this.starting_altitude;
        this.current_velocity = this.starting_velocity;
        this.lander_mass = this.starting_mass;
        this.fuel_weight = this.starting_fuel_weight;
        this.thrust = this.starting_thrust;
        this.#current_drag_constant = this.#drag_constant1;
        this.lander_legs_deployed = 0;
        this.#deploy_legs_commanded = 0;
        this.#radar_lock = 0;
        this.spacecraft_touchdown = 0;
        this.spacecraft_final_state = 0;
        this.constant_velocity_phase = 0;
        this.backshell_ejected = 0;
        this.#engine_cutoff_enable = 0;
        this.engine_cutoff_state = 0;
        this.landing_time = 0;
        this.landing_velocity = 0;
        this.powered_descent = 0;
        this.waiting_for_touchdown = true;
        this.leg1.reset();
        this.leg2.reset();
        this.leg3.reset();
        this.create_controller();

    }

    create_controller() {

        // just in case the controller is already running
        try {

            this.#pid_controller.kill();
        }
        catch (error) {

        }

        // use a ROM that the user has uploaded if it exists
        var romfile = '/tmp/newrom';

        try {

            const stats = fs.statSync(romfile);

            if (stats.isFile() == false) {

                romfile = 'bad.rom';

            }
            else if (stats.size > 30000 ) {

                romfile = 'bad.rom';

            }
            
        }
        catch(err) {

            var romfile = 'bad.rom';

        }


        this.#pid_controller = spawn('./vmips',
                ['-o', 'fpu', '-o', 'memsize=3000000', romfile]);

        this.spawn_start = Date.now();

        this.#pid_controller.stdout.setEncoding('utf8');

        this.#pid_controller.stdout.on('data', (data) => {

            this.read_pid_outputs(data);

        });

        this.#pid_controller.stderr.on('data', (data) => {

            // console.error(`stderr: ${data}`);

        });

        this.#pid_controller.on('close', (code) => {

            // console.error("controller closed");

        });

    }

    read_pid_outputs(data) {

        var backshell_eject;
        var legs_deploy;
        var engine_cutoff;
        var engine_thrust;


        for (const item of data) {

            if ( item == 'Z' ) {

                this.pid_input_buffer_ptr = 1;
                // console.error("found the start byte");

                this.pid_input_buffer = [];
            }
            else {

                this.pid_input_buffer.push(item);
                this.pid_input_buffer_ptr++;

            }

        }

        if (this.pid_input_buffer_ptr == 3) {

            // console.error("time to process the message")
            var byte1 = this.pid_input_buffer[0].charCodeAt(0);
            var byte2 = this.pid_input_buffer[1].charCodeAt(0);
            this.pid_input_buffer_ptr = 0;
        }
        else {

            return;
        }

        // console.error(` bytes 1 = ${byte1}`);
        // console.error(` bytes 2 = ${byte2}`);
        backshell_eject = byte1 & 0x01;
        legs_deploy = (byte1 >> 1) & 0x01;
        engine_cutoff = (byte1 >> 2) & 0x01;

        engine_thrust = byte2/100.0;



        // console.error(`backshell = ${backshell_eject}, legs = ${legs_deploy}, engine_cutoff = ${engine_cutoff}, thrust = ${engine_thrust}`)


        if (legs_deploy == 1 && this.#deploy_legs_commanded != 1 ) {

            this.deploy_legs();
            this.#deploy_legs_commanded = 1;
        }

        this.thruster_setting = engine_thrust;

        if (backshell_eject == 1) {

            this.backshell_ejected = 1;
            this.#current_drag_constant = this.#drag_constant2;

        }

        if (engine_cutoff == 1 && this.#engine_cutoff_enable == 1 && this.engine_cutoff == 0) {

            // console.error("*************************************************************disabling engines");

            // let stop_time = Date.now();

            // let interval = stop_time - this.spawn_start;

            // console.error(`Total sim time = ${interval}`);

            // this.powered_descent = 0;
            var engine_cutoff_time_delta = Date.now() - this.landing_time;

            if (engine_cutoff_time_delta <= 200 ) {

                this.engine_cutoff_state = 1;
            }
            else {

                this.engine_cutoff_state = 2;
                // console.error(`Engine cutoff time = ${engine_cutoff_time_delta}`);

            }

            this.engine_cutoff = 1;
        }
        else if ( engine_cutoff == 0 ) {

            this.powered_descent = 1;
            this.engine_cutoff = 0;
        }

    }

    send_pid_inputs(time_delta_millisecs) {

        let inputs = this.get_controller_inputs(time_delta_millisecs);

        const buffer = Buffer.from(inputs);

        this.#pid_controller.stdin.write(buffer);

        // console.error(buffer);

        return
    }



    dump_state() {

        console.error('altitude: ' + this.current_altitude);
        console.error('velocity: ' + this.current_velocity);
        console.error('fuel weight: ' + this.fuel_weight);
        console.error('lander_mass: ' + this.lander_mass);

    }

    calc_thrust(time_delta) {

        // no fuel, no thrust
        if (this.fuel_weight == 0.0 || this.engine_cutoff == 1) {

            return 0;
        }

        var fuel_needs = this.max_fuel_consumption * this.thruster_setting * time_delta;

        if (fuel_needs > this.fuel_weight) {

            fuel_needs = this.fuel_weight;
        }

        var thrust_force = this.max_thrust * this.thruster_setting;
        var thrust_acceleration = thrust_force / this.lander_mass;

        this.fuel_weight -= fuel_needs;

        // console.error(`Remaining fuel = ${this.fuel_weight}`)

        return thrust_acceleration;

    }

    deploy_legs() {

        // console.error("Time to deploy the legs");
        this.leg1.deploy();
        this.leg2.deploy();
        this.leg3.deploy();

    }

    update_altitude(time_delta) {

        var atmospheric_drag = this.planet.atmosphere_drag( this.current_altitude, 
                                                        this.current_velocity, 
                                                        this.#current_drag_constant,
                                                        this.lander_mass);

        var thruster_acceleration = this.calc_thrust(time_delta);

        // console.error(`acceleration = ${atmospheric_drag}`);

        var new_acceleration = this.planet.gravity_acceleration() + atmospheric_drag + thruster_acceleration;
        var new_velocity = this.current_velocity + (new_acceleration + this.current_acceleration) * time_delta * 0.5;
        var new_altitude = (this.current_altitude + this.current_velocity * time_delta + 0.5 * new_acceleration * time_delta * time_delta);

        // console.error(`altitude = ${this.current_altitude}, velocity = ${this.current_velocity}`);
        // console.error(`new_altitude = ${new_altitude}, new_velocity = ${new_velocity}`);

        if (new_altitude < 0.0) {

            new_altitude = 0.0;
        }

        // this is the instance it touches down so be sure to grab the landing velocity
        if ( this.waiting_for_touchdown && this.current_altitude > 0.0 && new_altitude <= 0.0) {

            this.waiting_for_touchdown = false;
            this.landing_velocity = new_velocity;
            this.landing_time = Date.now();

            // console.error(`Landing velocity = ${new_velocity}`)
            // if the landing is too fast, its a crash
            if (Math.abs(new_velocity) > 2.6) {

                this.spacecraft_touchdown = 2;

            }
            else {

                this.spacecraft_touchdown = 1;
            }

            // if the legs weren't fully deployed, its an error and a crash
            if (this.lander_legs_deployed != 1 ) {

                this.spacecraft_touchdown = 2;
                this.lander_legs_deployed = 2;
            }

        }

        if (new_altitude < 1425.0 & new_altitude > 0.0) {

            this.#radar_lock = 1;
            this.#radar_altitude = new_altitude;
        }
        else {

            this.#radar_lock = 0;
            this.#radar_altitude = Math.random() * 4000;
        }

        if (new_altitude <= 0.0) {

            new_altitude = 0.0;
            new_velocity = 0.0;
            new_acceleration = 0.0;
        }

        this.current_acceleration = new_acceleration;
        this.current_altitude = new_altitude;
        this.current_velocity = new_velocity;

        if (this.current_altitude <= 40.0 ) {

            this.#engine_cutoff_enable = 1;
        }

        if (this.current_velocity >= -2.41) {

            this.constant_velocity_phase = 1;

        }

    }

    update(time_delta_millisecs) {

        let time_delta_secs = time_delta_millisecs/1000.0;
        this.update_altitude(time_delta_secs);
        this.leg1.update(time_delta_secs, this.current_altitude);
        this.leg2.update(time_delta_secs, this.current_altitude);
        this.leg3.update(time_delta_secs, this.current_altitude);

        if (this.leg3.lander_leg_deployed == 1 && this.leg2.lander_leg_deployed == 1 && this.leg1.lander_leg_deployed == 1) {

            this.lander_legs_deployed = 1;

        }

        if (this.landing_time > 0 ) {

            var current_time = Date.now();

            if (current_time - this.landing_time > 200 && this.engine_cutoff == 0) {

                // console.error(`Engine cuttof not performed in time ${current_time - this.landing_time}`)
                this.engine_cutoff_state = 2;
            }
        }

        this.send_pid_inputs(time_delta_millisecs);

    }

    get_current_stats() {

        var current_time = Date.now();

        var spacecraft_state = 0;

        spacecraft_state |= (this.spacecraft_touchdown & 3) << 12;
        spacecraft_state |= (this.parachute_deployed & 3 ) <<10;
        spacecraft_state |= (this.lander_legs_deployed & 3 ) << 8;
        spacecraft_state |= (this.backshell_ejected & 3 ) << 6;
        spacecraft_state |= (this.constant_velocity_phase & 3 ) << 4;
        spacecraft_state |= (this.engine_cutoff_state & 3 ) << 2;
        spacecraft_state |= (this.powered_descent);

        var hexvalue = spacecraft_state.toString(16);

        // console.error(`spacecraft state = ${hexvalue}`);

        var stats = {
            'type': 'data',
            'altitude': this.current_altitude,
            'velocity': this.current_velocity,
            'fuel%': this.fuel_weight/this.starting_fuel_weight * 100,
            'thrust%': this.thruster_setting * 100,
            'spacecraft_state': hexvalue,
            'sim_time_delta': (current_time - this.#sim_start_time) / 1000.0
        };

        var data = JSON.stringify(stats);

        // console.error(data);

        return data;

    }

    get_controller_inputs(time_delta_millisecs) {

        // let value =  `${this.#radar_lock},${this.#radar_altitude},${this.current_velocity},${this.leg1.leg_touchdown},${this.leg2.leg_touchdown},${this.leg3.leg_touchdown},${this.#engine_cutoff_enable}\n`
        var buffer = new ArrayBuffer(8);
        var view = new DataView(buffer);

        var flags = this.#radar_lock << 4 | this.#engine_cutoff_enable << 3 | this.leg3.leg_touchdown  <<2 | this.leg2.leg_touchdown <<1 | this.leg1.leg_touchdown 
        view.setUint8(0, 0xa5);
        view.setUint8(1, 0x5a);
        view.setInt16(2, Math.round(this.current_velocity));
        view.setUint16(4, Math.round(this.#radar_altitude));
        view.setUint16(6, flags);
        // view.setUint16(8, time_delta_millisecs);

        return buffer;
    }
}

module.exports = Spacecraft
