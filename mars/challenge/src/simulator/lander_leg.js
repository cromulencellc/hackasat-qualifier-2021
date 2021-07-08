
class Lander_Leg {

    #lander_leg_position = 0;  // 0  stowed, 1.0 = fuly deployed
    lander_leg_deployed;
    #lander_leg_deploy_time_sec;
    #deploy_leg_commanded = 0;
    leg_touchdown;

    constructor(deploy_time_sec ) {

        this.#lander_leg_deploy_time_sec = deploy_time_sec;
    }

    reset() {

        this.#lander_leg_position = 0;
        this.#deploy_leg_commanded = 0;
        this.lander_leg_deployed = 0;
        this.leg_touchdown = 0;

    }

    deploy() {

        this.#deploy_leg_commanded = 1;
    }

    update(time_delta, altitude) {

        // console.error(`Updating leg position: commanded: ${this.#deploy_leg_commanded} ${this.#lander_leg_position}`);

        if (this.#deploy_leg_commanded == 1 && this.#lander_leg_position < 1.0 ) {

            // console.error("Updating leg position");

            this.#lander_leg_position += 1.0 / this.#lander_leg_deploy_time_sec * time_delta;

            if ( this.#lander_leg_position > 0.9 && this.#lander_leg_position < 0.95 ) {

                this.leg_touchdown = 1;
            }
            else {

                this.leg_touchdown = 0;
            }

            if ( this.#lander_leg_position >= 1.0 ) {

                this.lander_leg_deployed = 1;
            }

            // console.error(`Leg position = ${this.#lander_leg_position}`);
        }


        if ( altitude <= 0.0 ) {

            this.leg_touchdown = 1;

        }

    }

}

module.exports = Lander_Leg;