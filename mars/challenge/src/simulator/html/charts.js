class Chart {

    constructor(canvas, max_x, max_y, x_label, y_label) {

        this.max_x_value = max_x;
        this.max_y_value = max_y;
        this.x_label = x_label;
        this.y_label = y_label;

        this.context = canvas.getContext('2d');

        this.canvas_width  = this.context.canvas.width;
        this.canvas_height = this.context.canvas.height;

        this.graph_start_x = 40;
        this.graph_start_y = 50;
        this.graph_width = this.canvas_width - 55;
        this.graph_heigth = this.canvas_height - 80;

        this.datapoints = [];
        this.timesaxis = [];
        this.datapoint_count = 0;
    }

    reset() {

        this.datapoints = [];
        this.timesaxis = [];
        this.datapoint_count = 0;
        this.context.setTransform(1, 0, 0, 1, 0, 0);
        this.context.clearRect(0, 0, this.canvas_width, this.canvas_height);

    }

    add_datapoint(x, y) {

        this.datapoints.push(y);
        this.timesaxis.push(x);
        this.datapoint_count += 1;

        if ( x > this.max_x_value ) {

            this.max_x_value = x * 1.1;
            this.context.setTransform(1, 0, 0, 1, 0, 0);
            this.context.clearRect(0, 0, this.canvas_width, this.canvas_height);

        }
    }

    draw_graph() {


        this.context.font="14px verdana";
        this.context.strokeRect(this.graph_start_x, this.graph_start_y, this.graph_width, this.graph_heigth);

        this.context.textAlign = "center";   
        this.context.fillText( this.x_label, this.graph_width/2 + this.graph_start_x, this.canvas_height - 15 );

        this.context.rotate( Math.PI / 2);
        this.context.fillText( this.y_label, -(this.graph_width/2 + this.graph_start_y), 30 );

        if (this.datapoint_count > 1) {

            this.context.beginPath();

            var i;
            var scaled_x;
            var scaled_y;

            for (i=1; i < this.datapoint_count; ++i) {

                scaled_y = this.datapoints[i-1]/this.max_y_value * this.graph_heigth;
                scaled_x = this.timesaxis[i-1]/this.max_x_value * this.graph_width;
                this.context.moveTo(this.graph_start_x + scaled_x, this.graph_start_y + this.graph_heigth - scaled_y);

                scaled_y = this.datapoints[i]/this.max_y_value * this.graph_heigth;
                scaled_x = this.timesaxis[i]/this.max_x_value * this.graph_width;
                this.context.lineTo(this.graph_start_x + scaled_x, this.graph_start_y + this.graph_heigth - scaled_y);

            }

            this.context.closePath();
            this.context.stroke();

        }
    }

};

class Bar {

    constructor(canvas, max_value, title) {


        this.background_color = 'white';
        this.foreground_color = 'blue';
        
        this.max_value = max_value;
        this.title = title;

        this.current_value = 0;
        this.last_value = 0;

        this.context = canvas.getContext('2d');

        this.canvas_width  = this.context.canvas.width;
        this.canvas_height = this.context.canvas.height;

        this.bar_base = this.canvas_height - 21;

        this.bar_height = this.canvas_height - 20 - 41;

        this.bar_width = this.canvas_width - 40;

        this.context.strokeRect(0, 0, this.canvas_width, this.canvas_height);

        this.context.font="14px verdana";

        this.context.textAlign = "center";   
        this.context.fillText( this.title, 50, 20 );
    }


    update_value(value) {

        this.last_value = self.current_value;
        this.current_value = value;

        this.update_bar();
    }

    update_bar() {

        this.context.clearRect(25, 35, 50, 20);
        this.context.fillText(this.current_value, 50, 50);

        this.context.fillStyle = 'white';

        this.context.fillRect(20, 60, this.bar_width, this.bar_height);

        this.context.fillStyle = 'blue';

        var bar_length = this.bar_height * this.current_value/this.max_value;


        this.context.fillRect(20, this.bar_height-bar_length + 60, this.bar_width, this.bar_height * this.current_value/this.max_value);

    }

}

