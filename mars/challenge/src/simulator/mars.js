
class Mars {


    Gsubm = -3.7245;

    atmosphere_density(altitude) {

        var temp;

        if (altitude > 7000.0) {

            temp = -23.4 - .00222 * altitude;
        }
        else {

            temp = -31.0 - .000998 * altitude;
        }

        var pressure = .699 * Math.exp( -.00009 * altitude);
        var density = pressure / ( .1921 * (temp+273.1))

        return density;
    }

    gravity_acceleration() {

        return this.Gsubm;

    }

    atmosphere_drag(altitude, velocity, drag_constant, mass) {

        // console.error(`drag_constant = ${drag_constant}`);

        var density = this.atmosphere_density(altitude);

        // console.error(`density = ${density}`);

        var drag_coefficient = density * drag_constant;
        // console.error(`drag_coefficient = ${drag_coefficient}`);

        var drag_force = 0.5 * drag_coefficient * velocity * velocity;
        // console.error(`drag_force = ${drag_force}`);

        var drag_accel = drag_force / mass;
        // console.error(`drag_accel = ${drag_accel}`);

        return drag_accel;
    }
}

module.exports = Mars